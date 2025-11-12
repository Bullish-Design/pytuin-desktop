"""Document editor for manipulating .atrb files (v3 Steps 1–2)."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union
from uuid import uuid4
from logging import Logger

from templateer import TemplateModel

from .parser import AtrbParser
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

    The editor keeps an in-memory list of TemplateModel instances (blocks).
    Rendering and saving are delegated to the discovered DocumentTemplate.
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

    # ---- Output -------------------------------------------------------
    def _as_document_template(self) -> TemplateModel:
        """Build a DocumentTemplate instance from current state."""
        DocT = self._templates.DocumentTemplate  # type: ignore[attr-defined]
        return DocT(
            document_id=self.document_id,
            name=self.name,
            version=self.version,
            blocks=self.blocks,
        )

    def render(self) -> str:
        """Render the current document to a YAML string."""
        self._logger.debug("editor.render_start", extra={"blocks": len(self.blocks)})
        rendered = self._as_document_template().render()
        self._logger.info("editor.render_done", extra={"bytes": len(rendered)})
        return rendered

    def save(self, filepath: str | Path, *, ensure_trailing_newline: bool = True) -> None:
        """Render and write the current document to *filepath*.

        When *ensure_trailing_newline* is True (default), guarantees the file ends
        with exactly one trailing newline for deterministic diffs.
        """
        text = self.render()
        if ensure_trailing_newline:
            text = _ensure_single_trailing_newline(text)
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        self._logger.info("editor.save", extra={"path": str(p.absolute()), "bytes": len(text)})
