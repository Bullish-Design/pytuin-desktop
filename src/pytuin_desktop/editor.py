# path: pytuin_desktop/editor.py
"""Document editor (v4 Phase 1)."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Union, TextIO
from uuid import uuid4
from logging import Logger
from types import SimpleNamespace
from enum import Enum
from yaml import safe_dump, safe_load
from templateer import TemplateModel
from .parser import AtrbParser
from .models import BaseBlock
from .discovery import load_atrb_templates
from .logger import logger as _default_logger
from .validator import AtrbValidator
from .repository import DocumentRepository

yaml = SimpleNamespace(safe_dump=safe_dump, safe_load=safe_load)

def _ensure_single_trailing_newline(text: str) -> str:
    if not text: return "\n"
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

PathLike = Union[str, Path]

class DocumentEditor:
    def __init__(self, document_id: str, name: str, version: int = 1, *, template_dir: Optional[PathLike] = None, logger: Logger | None = None, repository: DocumentRepository | None = None):
        self.document_id = document_id
        self.name = name
        self.version = version
        self.blocks: List[TemplateModel] = []
        self.existing_blocks: List[BaseBlock] = []
        self._template_dir: Optional[PathLike] = template_dir
        self._logger: Logger = logger or _default_logger
        self._templates = load_atrb_templates(template_dir, logger=self._logger)
        self._repo = repository

    @classmethod
    def create(cls, name: str, version: int = 1, *, template_dir: Optional[PathLike] = None, logger: Logger | None = None, repository: DocumentRepository | None = None) -> "DocumentEditor":
        inst = cls(document_id=str(uuid4()), name=name, version=version, template_dir=template_dir, logger=logger, repository=repository)
        inst._logger.info("editor.create", extra={"doc_name": name, "version": version})
        return inst

    @classmethod
    def from_file(cls, filepath: str | Path, *, template_dir: Optional[PathLike] = None, logger: Logger | None = None, repository: DocumentRepository | None = None) -> "DocumentEditor":
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger, repository=repository)
        inst._logger.info("editor.from_file", extra={"path": str(Path(filepath).absolute())})
        return inst

    @classmethod
    def from_file_with_blocks(cls, filepath: str | Path, *, template_dir: Optional[PathLike] = None, logger: Logger | None = None, repository: DocumentRepository | None = None) -> "DocumentEditor":
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger, repository=repository)
        inst.existing_blocks = list(doc.content)
        inst._logger.info("editor.from_file_with_blocks", extra={"path": str(Path(filepath).absolute()), "existing_blocks": len(inst.existing_blocks)})
        return inst

    def add_block(self, block: TemplateModel) -> "DocumentEditor":
        self.blocks.append(block); self._logger.debug("editor.add_block", extra={"count": len(self.blocks)}); return self

    def remove_block_at(self, index: int) -> "DocumentEditor":
        if 0 <= index < len(self.blocks):
            del self.blocks[index]; self._logger.debug("editor.remove_block", extra={"index": index, "count": len(self.blocks)})
        return self

    def get_block(self, index: int) -> TemplateModel:
        return self.blocks[index]

    def _render_template_to_dict(self, template: TemplateModel) -> dict:
        # Prefer model_dump
        try:
            if hasattr(template, "model_dump"):
                data = template.model_dump(mode="python", exclude_none=True)
                if isinstance(data, dict) and "id" in data and "type" in data:
                    return data
        except Exception:
            pass
        # Fallback: YAML
        try:
            rendered = str(template)
            data = getattr(yaml, "safe_load", safe_load)(rendered) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Template rendered to {type(data).__name__}, expected dict")
            return data
        except Exception as e:
            raise ValueError(f"Unable to render template {type(template).__name__} to dict: {e}") from e

    def _render_new_blocks_as_dicts(self) -> list[dict]:
        return [self._render_template_to_dict(t) for t in self.blocks]

    def _build_document_model_for_validation(self) -> "AtrbDocument":
        from uuid import UUID
        from .models import AtrbDocument, BaseBlock
        existing = list(self.existing_blocks)
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

    def render(self) -> str:
        self._logger.debug("editor.render_start", extra={"existing": len(self.existing_blocks), "new": len(self.blocks)})
        content: list[dict] = [b.model_dump(mode="python") for b in self.existing_blocks]
        content.extend(self._render_new_blocks_as_dicts())
        legacy_map = {"id": self.document_id, "name": self.name, "version": self.version, "content": content}
        rendered = getattr(yaml, "safe_dump", safe_dump)(_to_jsonable(legacy_map), sort_keys=False, allow_unicode=True)
        self._logger.info("editor.render_done", extra={"bytes": len(rendered)})
        return rendered

    def write_to_stream(self, stream: TextIO, *, ensure_trailing_newline: bool = True) -> None:
        try:
            _doc = self._build_document_model_for_validation()
            AtrbValidator.validate(_doc)
        except Exception as e:
            self._logger.error("editor.validation_failed", extra={"error": str(e)})
            raise
        text = self.render()
        if ensure_trailing_newline:
            text = _ensure_single_trailing_newline(text)
        stream.write(text)
        try: stream.flush()
        except Exception: pass
        self._logger.info("editor.write_to_stream", extra={"bytes": len(text)})
        try:
            if getattr(self, "_repo", None) is not None:
                _doc = self._build_document_model_for_validation()
                self._repo.save(_doc)  # type: ignore[attr-defined]
                self._logger.info("editor.repo_saved", extra={"doc_id": str(_doc.id)})
        except Exception:
            pass

    def save(self, filepath: str | Path, *, ensure_trailing_newline: bool = True) -> None:
        p = Path(filepath); p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            self.write_to_stream(f, ensure_trailing_newline=ensure_trailing_newline)
        self._logger.info("editor.save", extra={"path": str(p.absolute())})
