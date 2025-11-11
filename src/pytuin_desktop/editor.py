"""Document editor for manipulating .atrb files (Step 11)."""
from __future__ import annotations

from pathlib import Path
from typing import List
from uuid import uuid4

from templateer import TemplateModel

from .parser import AtrbParser
from .discovery import load_atrb_templates


class DocumentEditor:
    """Edit .atrb documents using Templateer-based templates.

    The editor keeps an in-memory list of TemplateModel instances (blocks).
    Rendering and saving are delegated to the discovered DocumentTemplate.
    """

    def __init__(self, document_id: str, name: str, version: int = 1):
        self.document_id = document_id
        self.name = name
        self.version = version
        self.blocks: List[TemplateModel] = []
        self._templates = load_atrb_templates()

    # ---- Constructors -------------------------------------------------
    @classmethod
    def create(cls, name: str, version: int = 1) -> "DocumentEditor":
        """Create a new empty document."""
        return cls(document_id=str(uuid4()), name=name, version=version)

    @classmethod
    def from_file(cls, filepath: str | Path) -> "DocumentEditor":
        """Load an existing .atrb file and return an editor seeded with its metadata.

        Note: Blocks are not round-tripped into TemplateModel instances; this
        constructor only copies top-level metadata (id/name/version).
        """
        doc = AtrbParser.parse_file(filepath)
        return cls(document_id=str(doc.id), name=doc.name, version=doc.version)

    # ---- Editing API --------------------------------------------------
    def add_block(self, block: TemplateModel) -> "DocumentEditor":
        """Append a block template and return self for fluent chaining."""
        self.blocks.append(block)
        return self

    def remove_block_at(self, index: int) -> "DocumentEditor":
        """Remove a block by index (no-op if out of bounds) and return self."""
        if 0 <= index < len(self.blocks):
            del self.blocks[index]
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
        return self._as_document_template().render()

    def save(self, filepath: str | Path) -> None:
        """Render and write the current document to *filepath*."""
        self._as_document_template().write_to(filepath)
