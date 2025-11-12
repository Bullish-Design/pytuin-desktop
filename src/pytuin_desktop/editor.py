"""Document editor for manipulating .atrb files (v3 Step 5 & Step 6 streaming)."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union, TextIO
from uuid import uuid4
from logging import Logger
from types import SimpleNamespace
from enum import Enum

from yaml import safe_dump, safe_load
# Expose a patchable yaml-like namespace for tests
yaml = SimpleNamespace(safe_dump=safe_dump, safe_load=safe_load)

from templateer import TemplateModel

from .parser import AtrbParser
from .models import BaseBlock
from .discovery import load_atrb_templates
from .logger import logger as _default_logger
from .validator import AtrbValidator
from .repository import DocumentRepository


def _ensure_single_trailing_newline(text: str) -> str:
    """Return *text* with exactly one trailing newline (\n)."""
    if not text:
        return "\n"
    return text.rstrip("\n") + "\n"

def _to_jsonable(obj):
    """Recursively convert objects (e.g., UUID) to YAML/JSON-safe primitives."""
    from uuid import UUID
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, UUID):
        return str(obj)
    # Pydantic models with model_dump
    if hasattr(obj, "model_dump"):
        try:
            return _to_jsonable(obj.model_dump(mode="python"))
        except Exception:
            pass
    return obj


PathLike = Union[str, Path]


class DocumentEditor:
    """Edit .atrb documents using Templateer-based templates.

    The editor keeps two in-memory collections:
    - *existing_blocks*: parsed :class:`BaseBlock` instances loaded from an existing file
      when constructed via :meth:`from_file_with_blocks`.
    - *blocks*: new TemplateModel blocks added during this editing session (e.g., via builders).

    Rendering writes a single merged document that preserves the order:
    existing blocks first (unchanged), then newly added blocks in the order they were added.
    """

    def __init__(
        self,
        document_id: str,
        name: str,
        version: int = 1,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
    ):
        self.document_id = document_id
        self.name = name
        self.version = version
        self.blocks: List[TemplateModel] = []
        self.existing_blocks: List[BaseBlock] = []  # <- populated by from_file_with_blocks
        self._template_dir: Optional[PathLike] = template_dir
        self._logger: Logger = logger or _default_logger
        self._templates = load_atrb_templates(template_dir, logger=self._logger)
        self._repo = repository

    # ---- Constructors -------------------------------------------------
    @classmethod
    def create(
        cls,
        name: str,
        version: int = 1,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
        repository: DocumentRepository | None = None,
    ) -> "DocumentEditor":
        """Create a new empty document with an optional explicit template dir."""
        inst = cls(document_id=str(uuid4()), name=name, version=version, template_dir=template_dir, logger=logger, repository=repository)
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
    ) -> "DocumentEditor":
        """Load an existing .atrb file and return an editor seeded with its metadata.

        Note: Blocks are not round-tripped into TemplateModel instances; this
        constructor only copies top-level metadata (id/name/version).
        """
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger, repository=repository)
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
    ) -> "DocumentEditor":
        """Load an existing .atrb file and preserve its parsed blocks.

        This constructor attaches the parsed :class:`BaseBlock` instances to the editor so that
        future renders keep original content and ordering intact while allowing new blocks to be appended.
        """
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger, repository=repository)
        inst.existing_blocks = list(doc.content)  # preserve order
        inst._logger.info(
            "editor.from_file_with_blocks",
            extra={"path": str(Path(filepath).absolute()), "existing_blocks": len(inst.existing_blocks)},
        )
        return inst

    # ---- Editing API --------------------------------------------------
    def add_block(self, block: TemplateModel) -> "DocumentEditor":
        """Append a block template and return self for fluent chaining."""
        self.blocks.append(block)
        self._logger.debug("editor.add_block", extra={"count": len(self.blocks)})
        return self

    def remove_block_at(self, index: int) -> "DocumentEditor":
        """Remove a block by index (no-op if out of bounds) and return self."""
        if 0 <= index < len(self.blocks):
            del self.blocks[index]
            self._logger.debug("editor.remove_block", extra={"index": index, "count": len(self.blocks)})
        return self

    def get_block(self, index: int) -> TemplateModel:
        """Return the block at *index* (IndexError if invalid)."""
        return self.blocks[index]

    # ---- Output helpers ----------------------------------------------
    def _render_new_blocks_as_dicts(self) -> list[dict]:
        """Render newly added TemplateModel blocks to dictionaries by YAML round-trip.

        We render each block template to a YAML string and load it back to a Python mapping.
        This preserves compatibility with whatever template formatting is used while giving
        us a normalized structure for final document emission together with existing blocks.
        """
        dicts: list[dict] = []
        for t in self.blocks:
            try:
                rendered = str(t)
                data = getattr(yaml, "safe_load", safe_load)(rendered) or {}
            except Exception:
                # Fallback to model_dump if rendering failed
                try:
                    data = t.model_dump(mode="python")  # type: ignore[attr-defined]
                except Exception as e:
                    raise ValueError(f"Unable to render block {t!r}: {e}") from e
            if not isinstance(data, dict):
                raise ValueError("Rendered block did not produce a mapping/object.")
            dicts.append(data)
        return dicts


    def _build_document_model_for_validation(self) -> "AtrbDocument":
        """Construct an AtrbDocument from in-memory state for validation before writing."""
        from uuid import UUID
        from .models import AtrbDocument, BaseBlock

        # Existing parsed blocks are already BaseBlock instances
        existing = list(self.existing_blocks)

        # New blocks rendered to dicts -> BaseBlock
        rendered = self._render_new_blocks_as_dicts()
        new_blocks: list[BaseBlock] = []
        for raw in rendered:
            try:
                new_blocks.append(BaseBlock.model_validate(raw))
            except Exception as e:
                raise ValueError(f"New block failed to validate shape: {e}") from e

        all_blocks = existing + new_blocks
        try:
            doc = AtrbDocument(
                id=UUID(str(self.document_id)),
                name=self.name,
                version=int(self.version),
                content=all_blocks,
            )
        except Exception as e:
            raise ValueError(f"Unable to construct document model for validation: {e}") from e
        return doc

    # ---- Output -------------------------------------------------------
    def render(self) -> str:
        """Render the current document using the discovered DocumentTemplate.

        If this editor was created via :meth:`from_file_with_blocks`, previously parsed blocks
        are preserved and emitted first, followed by any new blocks added during this session.
        """
        self._logger.debug(
            "editor.render_start",
            extra={"existing": len(self.existing_blocks), "new": len(self.blocks)},
        )

        # Merge existing parsed blocks with new blocks rendered to dicts.
        content: list[dict] = [b.model_dump(mode="python") for b in self.existing_blocks]
        content.extend(self._render_new_blocks_as_dicts())

        # Build kwargs for DocumentTemplate (new schema) and a legacy mapping for fallback.
        doc_kwargs = {
            "document_id": self.document_id,
            "id": self.document_id,
            "name": self.name,
            "version": self.version,
            "content": content,
            "children": [],
        }
        legacy_map = {
            "id": self.document_id,
            "name": self.name,
            "version": self.version,
            "content": content,
        }

        # Delegate final rendering to the discovered DocumentTemplate so tests can patch it.
        DocT = getattr(self._templates, "DocumentTemplate", None)
        if DocT is None:
            rendered = getattr(yaml, "safe_dump", safe_dump)(_to_jsonable(legacy_map), sort_keys=False, allow_unicode=True)
            self._logger.info("editor.render_done", extra={"bytes": len(rendered)})
            return rendered

        doc = DocT(**doc_kwargs)
        rendered = doc.render()

        # If the templated rendering lost content, fall back to a direct YAML dump.
        try:
            loaded = getattr(yaml, "safe_load", safe_load)(rendered)
        except Exception:
            loaded = None
        if isinstance(loaded, dict) and loaded.get("content") == [] and len(content) > 0:
            rendered = getattr(yaml, "safe_dump", safe_dump)(_to_jsonable(legacy_map), sort_keys=False, allow_unicode=True)

        self._logger.info("editor.render_done", extra={"bytes": len(rendered)})
        return rendered

    def write_to_stream(self, stream: TextIO, *, ensure_trailing_newline: bool = True) -> None:
        """Render the document and write it to an open text stream.

        When *ensure_trailing_newline* is True (default), guarantees the output ends
        with exactly one trailing newline for deterministic diffs.
        """
        # Validate composed document before rendering/writing
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
        try:
            stream.flush()
        except Exception:
            # Not all text streams support flush; ignore.
            pass
        self._logger.info("editor.write_to_stream", extra={"bytes": len(text)})

        # Persist to repository if provided
        try:
            if getattr(self, "_repo", None) is not None:
                _doc = self._build_document_model_for_validation()
                self._repo.save(_doc)  # type: ignore[attr-defined]
                self._logger.info("editor.repo_saved", extra={"doc_id": str(_doc.id)})
        except Exception:
            # Repository failures should not break writes
            pass

    def save(self, filepath: str | Path, *, ensure_trailing_newline: bool = True) -> None:
        """Render and write the current document to *filepath*.

        When *ensure_trailing_newline* is True (default), guarantees the file ends
        with exactly one trailing newline for deterministic diffs.
        """
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            self.write_to_stream(f, ensure_trailing_newline=ensure_trailing_newline)
        self._logger.info("editor.save", extra={"path": str(p.absolute())})
