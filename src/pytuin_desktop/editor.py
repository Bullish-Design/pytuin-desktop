"""Document editor for manipulating .atrb files (v3 Step 5 & Step 6 streaming)."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union, TextIO
from uuid import uuid4
from logging import Logger
from types import SimpleNamespace

from yaml import safe_dump, safe_load
# Expose a patchable yaml-like namespace for tests
yaml = SimpleNamespace(safe_dump=safe_dump, safe_load=safe_load)

from templateer import TemplateModel

from .parser import AtrbParser
from .models import BaseBlock
from .discovery import load_atrb_templates
from .logger import logger as _default_logger


def _ensure_single_trailing_newline(text: str) -> str:
    """Return *text* with exactly one trailing newline (\n)."""
    if not text:
        return "\n"
    return text.rstrip("\n") + "\n"


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
    ):
        self.document_id = document_id
        self.name = name
        self.version = version
        self.blocks: List[TemplateModel] = []
        self.existing_blocks: List[BaseBlock] = []  # <- populated by from_file_with_blocks
        self._template_dir: Optional[PathLike] = template_dir
        self._logger: Logger = logger or _default_logger
        self._templates = load_atrb_templates(template_dir, logger=self._logger)

    # ---- Constructors -------------------------------------------------
    @classmethod
    def create(
        cls,
        name: str,
        version: int = 1,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
    ) -> "DocumentEditor":
        """Create a new empty document with an optional explicit template dir."""
        inst = cls(document_id=str(uuid4()), name=name, version=version, template_dir=template_dir, logger=logger)
        inst._logger.info("editor.create", extra={"doc_name": name, "version": version})
        return inst

    @classmethod
    def from_file(
        cls,
        filepath: str | Path,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
    ) -> "DocumentEditor":
        """Load an existing .atrb file and return an editor seeded with its metadata.

        Note: Blocks are not round-tripped into TemplateModel instances; this
        constructor only copies top-level metadata (id/name/version).
        """
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger)
        inst._logger.info("editor.from_file", extra={"path": str(Path(filepath).absolute())})
        return inst

    @classmethod
    def from_file_with_blocks(
        cls,
        filepath: str | Path,
        *,
        template_dir: Optional[PathLike] = None,
        logger: Logger | None = None,
    ) -> "DocumentEditor":
        """Load an existing .atrb file and preserve its parsed blocks.

        This constructor attaches the parsed :class:`BaseBlock` instances to the editor so that
        future renders keep original content and ordering intact while allowing new blocks to be appended.
        """
        doc = AtrbParser.parse_file(filepath, logger=logger)
        inst = cls(document_id=str(doc.id), name=doc.name, version=doc.version, template_dir=template_dir, logger=logger)
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
            rendered = getattr(yaml, "safe_dump", safe_dump)(legacy_map, sort_keys=False, allow_unicode=True)
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
            rendered = getattr(yaml, "safe_dump", safe_dump)(legacy_map, sort_keys=False, allow_unicode=True)

        self._logger.info("editor.render_done", extra={"bytes": len(rendered)})
        return rendered

    def write_to_stream(self, stream: TextIO, *, ensure_trailing_newline: bool = True) -> None:
        """Render the document and write it to an open text stream.

        When *ensure_trailing_newline* is True (default), guarantees the output ends
        with exactly one trailing newline for deterministic diffs.
        """
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
