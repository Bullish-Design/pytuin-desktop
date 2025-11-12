# path: src/pytuin_desktop/editor.py
"""Document editor (v4 Phase 4 & 5).
- Serializer dependency injection (replaces SimpleNamespace hack).
- Metrics hooks and timing.
- Validation caching to avoid redundant validation.
- Batch edit helpers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional, Union, TextIO
from uuid import uuid4
from logging import Logger
from enum import Enum

from templateer import TemplateModel

from .parser import AtrbParser
from .models import BaseBlock
from .block_container import BlockContainer
from .discovery import load_atrb_templates
from .logger import logger as _default_logger
from .validator import AtrbValidator
from .repository import DocumentRepository
from .serializers import YamlSerializer, get_default_serializer
from .metrics import MetricsCollector, get_default_collector, TimingContext

PathLike = Union[str, Path]


def _ensure_single_trailing_newline(text: str) -> str:
    if not text:
        return "\n"
    return text.rstrip("\n") + "\n"


def _to_jsonable(obj):
    from uuid import UUID
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, UUID):
        return str(obj)
    if hasattr(obj, "model_dump"):
        try:
            return _to_jsonable(obj.model_dump(mode="python"))
        except Exception:
            pass
    return obj


class DocumentEditor:
    def __init__(
        self,
        document_id: str,
        name: str,
        version: int = 1,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
        serializer: YamlSerializer | None = None,
        metrics: MetricsCollector | None = None,
    ):
        self.document_id = document_id
        self.name = name
        self.version = version
        self._container = BlockContainer()
        self._template_dir: Optional[PathLike] = template_dir
        self._logger: Logger = logger or _default_logger
        self._templates = load_atrb_templates(template_dir, logger=self._logger)
        self._repo = repository
        self._serializer: YamlSerializer = serializer or get_default_serializer()
        self._metrics: MetricsCollector = metrics or get_default_collector()

        # Phase 5: validation cache & mod counter
        self._validation_cache: tuple[int, "AtrbDocument"] | None = None
        self._mod_counter: int = 0

    @classmethod
    def create(
        cls,
        name: str,
        version: int = 1,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
        serializer: YamlSerializer | None = None,
        metrics: MetricsCollector | None = None,
    ) -> "DocumentEditor":
        inst = cls(
            document_id=str(uuid4()),
            name=name,
            version=version,
            template_dir=template_dir,
            logger=logger,
            repository=repository,
            serializer=serializer,
            metrics=metrics,
        )
        inst._logger.info("editor.create", extra={"doc_name": name, "version": version})
        return inst

    @classmethod
    def from_file(
        cls,
        filepath: str | Path,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
        serializer: YamlSerializer | None = None,
        metrics: MetricsCollector | None = None,
    ) -> "DocumentEditor":
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(
            document_id=str(doc.id),
            name=doc.name,
            version=doc.version,
            template_dir=template_dir,
            logger=logger,
            repository=repository,
            serializer=serializer,
            metrics=metrics,
        )
        inst._logger.info("editor.from_file", extra={"path": str(Path(filepath).absolute())})
        return inst

    @classmethod
    def from_file_with_blocks(
        cls,
        filepath: str | Path,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
        serializer: YamlSerializer | None = None,
        metrics: MetricsCollector | None = None,
    ) -> "DocumentEditor":
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(
            document_id=str(doc.id),
            name=doc.name,
            version=doc.version,
            template_dir=template_dir,
            logger=logger,
            repository=repository,
            serializer=serializer,
            metrics=metrics,
        )
        for _b in doc.content:
            inst._container.add_existing(_b)
        inst._logger.info(
            "editor.from_file_with_blocks",
            extra={"path": str(Path(filepath).absolute()), "existing_blocks": len(inst._container.get_existing_blocks())},
        )
        return inst

    # ---- block ops ----
    def _touch(self) -> None:
        self._mod_counter += 1
        self._validation_cache = None

    def add_block(self, block: TemplateModel) -> "DocumentEditor":
        self._container.add_new(block)
        self._touch()
        self._logger.debug("editor.add_block", extra={"count": len(self._container)})
        return self

    def add_blocks(self, blocks: list[TemplateModel]) -> "DocumentEditor":
        for b in blocks:
            self._container.add_new(b)
        self._touch()
        self._logger.debug("editor.add_blocks", extra={"added": len(blocks), "count": len(self._container)})
        return self

    def insert_block_at(self, index: int, block: TemplateModel) -> "DocumentEditor":
        existing_len = len(self._container.get_existing_blocks())
        if index < existing_len:
            raise NotImplementedError("Inserting into existing blocks not supported")
        new_list = self._container.get_new_templates()
        pos = min(max(0, index - existing_len), len(new_list))
        new_list.insert(pos, block)
        self._container.clear_new()
        for t in new_list:
            self._container.add_new(t)
        self._touch()
        self._logger.debug("editor.insert_block", extra={"index": index})
        return self

    def move_block(self, from_index: int, to_index: int) -> "DocumentEditor":
        self._container.move(from_index, to_index)
        self._touch()
        self._logger.debug("editor.move_block", extra={"from": from_index, "to": to_index})
        return self

    def replace_block_at(self, index: int, block: TemplateModel) -> "DocumentEditor":
        self._container.replace_at(index, block)
        self._touch()
        self._logger.debug("editor.replace_block", extra={"index": index})
        return self

    def replace_blocks(self, replacements: dict[int, TemplateModel]) -> "DocumentEditor":
        for idx, blk in replacements.items():
            self._container.replace_at(idx, blk)
        self._touch()
        self._logger.debug("editor.replace_blocks", extra={"count": len(replacements)})
        return self

    def remove_block_at(self, index: int) -> "DocumentEditor":
        self._container.remove_at(index)
        self._touch()
        self._logger.debug("editor.remove_block", extra={"index": index, "count": len(self._container)})
        return self

    def remove_blocks_at(self, indices: list[int]) -> "DocumentEditor":
        for i in sorted(indices, reverse=True):
            self._container.remove_at(i)
        self._touch()
        self._logger.debug("editor.remove_blocks", extra={"count": len(indices)})
        return self

    def block_count(self) -> int:
        return len(self._container)

    def get_block(self, index: int):
        return self._container.get_at(index)

    def find_blocks_by_type(self, block_type: str):
        return self._container.find_blocks_by_type(block_type)

    def find_block_by_id(self, block_id):
        return self._container.find_by_id(block_id)

    def get_block_index(self, block_id):
        res = self.find_block_by_id(block_id)
        return res[0] if res else None

    # ---- rendering ----
    def _render_template_to_dict(self, template: TemplateModel) -> dict:
        try:
            if hasattr(template, "model_dump"):
                data = template.model_dump(mode="python", exclude_none=True)
                if isinstance(data, dict) and "id" in data and "type" in data:
                    return data
        except Exception:
            pass
        try:
            rendered = str(template)
            data = self._serializer.loads(rendered) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Template rendered to {type(data).__name__}, expected dict")
            return data
        except Exception as e:
            self._logger.error("editor.render_block_failed", extra={"template_type": type(template).__name__, "error": str(e)})
            raise ValueError(f"Unable to render template {type(template).__name__} to dict: {e}") from e

    def _render_new_blocks_as_dicts(self) -> list[dict]:
        return [self._render_template_to_dict(t) for t in self._container.get_new_templates()]

    def _build_document_model_for_validation(self) -> "AtrbDocument":
        from uuid import UUID
        from .models import AtrbDocument, BaseBlock
        existing = list(self._container.get_existing_blocks())
        rendered = self._render_new_blocks_as_dicts()
        new_blocks: list[BaseBlock] = []
        for idx, raw in enumerate(rendered):
            if "id" not in raw or "type" not in raw:
                raise ValueError(f"Rendered block {idx} missing required fields. Template must produce 'id' and 'type'. Found keys: {list(raw.keys())}")
            try:
                new_blocks.append(BaseBlock.model_validate(raw))
            except Exception as e:
                raise ValueError(f"Rendered block {idx} (type={raw.get('type')}) failed validation: {e}") from e
        all_blocks = existing + new_blocks
        try:
            doc = AtrbDocument(id=UUID(str(self.document_id)), name=self.name, version=int(self.version), content=all_blocks)
        except Exception as e:
            raise ValueError(f"Unable to construct document model for validation: {e}") from e
        return doc

    # Phase 5: cache validated doc to avoid duplicate work
    def _build_and_validate_document(self) -> "AtrbDocument":
        if self._validation_cache is not None and self._validation_cache[0] == self._mod_counter:
            return self._validation_cache[1]
        doc = self._build_document_model_for_validation()
        with TimingContext(self._metrics, "validation"):
            AtrbValidator.validate(doc)
        self._validation_cache = (self._mod_counter, doc)
        return doc

    def render(self) -> str:
        self._logger.debug("editor.render_start", extra={"existing": len(self._container.get_existing_blocks()), "new": len(self._container.get_new_templates())})
        content: list[dict] = [b.model_dump(mode="python") for b in self._container.get_existing_blocks()]
        content.extend(self._render_new_blocks_as_dicts())
        legacy_map = {"id": self.document_id, "name": self.name, "version": self.version, "content": content}
        text = self._serializer.dumps(_to_jsonable(legacy_map), sort_keys=False, allow_unicode=True)
        self._logger.info("editor.render_done", extra={"bytes": len(text)})
        return text

    def write_to_stream(self, stream: TextIO, *, ensure_trailing_newline: bool = True) -> None:
        try:
            _doc = self._build_and_validate_document()
            self._metrics.increment_counter("validations")
        except Exception as e:
            self._logger.error("editor.validation_failed", extra={"error": str(e)})
            raise
        # Build the same legacy structure as render(), but write using the injected serializer
        content: list[dict] = [b.model_dump(mode="python") for b in self._container.get_existing_blocks()]
        content.extend(self._render_new_blocks_as_dicts())
        legacy_map = {"id": self.document_id, "name": self.name, "version": self.version, "content": content}
        from io import StringIO
        _buf = StringIO()
        self._serializer.dump(_to_jsonable(legacy_map), _buf, sort_keys=False, allow_unicode=True)
        text = _buf.getvalue()
        if ensure_trailing_newline:
            text = _ensure_single_trailing_newline(text)
        stream.write(text)
        try:
            stream.flush()
        except Exception:
            pass
        self._logger.info("editor.write_to_stream", extra={"bytes": len(text)})

        try:
            if getattr(self, "_repo", None) is not None:
                _doc = self._build_document_model_for_validation()
                self._repo.save(_doc)  # type: ignore[attr-defined]
                self._logger.info("editor.repo_saved", extra={"doc_id": str(_doc.id)})
        except Exception:
            pass

    def save(self, filepath: str | Path, *, ensure_trailing_newline: bool = True) -> None:
        from pathlib import Path as _P
        p = _P(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        with TimingContext(self._metrics, "editor.save"):
            with p.open("w", encoding="utf-8") as f:
                self.write_to_stream(f, ensure_trailing_newline=ensure_trailing_newline)
        self._metrics.increment_counter("documents_saved")
        try:
            self._metrics.record_value("document_size_bytes", p.stat().st_size)
        except Exception:
            pass
        self._logger.info("editor.save", extra={"path": str(p.absolute())})
