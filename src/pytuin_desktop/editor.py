# src/pytuin_desktop/editor.py
from __future__ import annotations

from uuid import uuid4
from pathlib import Path

from pytuin_desktop.models.document import AtrbDocument
from pytuin_desktop.models.blocks import AnyBlock
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.writer import AtrbWriter


class DocumentEditor:
    """Editor for manipulating AtrbDocument structure."""

    def __init__(self, document: AtrbDocument):
        """
        Initialize editor with a document.

        Args:
            document: The document to edit
        """
        self.document = document

    @classmethod
    def from_file(cls, filepath: str | Path) -> DocumentEditor:
        """
        Load a document from file for editing.

        Args:
            filepath: Path to the .atrb file

        Returns:
            DocumentEditor instance
        """
        document = AtrbParser.parse_file(filepath)
        return cls(document)

    @classmethod
    def create(cls, name: str, version: int = 1) -> DocumentEditor:
        """
        Create a new empty document.

        Args:
            name: Document name
            version: Document version

        Returns:
            DocumentEditor instance with empty document
        """
        document = AtrbDocument(id=uuid4(), name=name, version=version, content=[])
        return cls(document)

    @classmethod
    def from_template(cls, template_path: str | Path, new_name: str) -> DocumentEditor:
        """
        Create a new document from a template file.

        Args:
            template_path: Path to template .atrb file
            new_name: Name for the new document

        Returns:
            DocumentEditor instance with copied template
        """
        template = AtrbParser.parse_file(template_path)
        new_doc = AtrbDocument(
            id=uuid4(),
            name=new_name,
            version=template.version,
            content=template.content.copy(),
        )
        return cls(new_doc)

    def add_block(self, block: AnyBlock, index: int | None = None) -> DocumentEditor:
        """
        Add a block to the document.

        Args:
            block: Block to add
            index: Position to insert at (None = append to end)

        Returns:
            Self for chaining
        """
        if index is None:
            self.document.content.append(block)
        else:
            self.document.content.insert(index, block)
        return self

    def remove_block(self, block_id: str) -> DocumentEditor:
        """
        Remove a block by ID.

        Args:
            block_id: UUID of block to remove

        Returns:
            Self for chaining

        Raises:
            ValueError: If block not found
        """
        for i, block in enumerate(self.document.content):
            if str(block.id) == block_id:
                self.document.content.pop(i)
                return self
        raise ValueError(f"Block with id {block_id} not found")

    def remove_block_at(self, index: int) -> DocumentEditor:
        """
        Remove a block by index.

        Args:
            index: Position of block to remove

        Returns:
            Self for chaining
        """
        self.document.content.pop(index)
        return self

    def move_block(self, from_index: int, to_index: int) -> DocumentEditor:
        """
        Move a block from one position to another.

        Args:
            from_index: Current position
            to_index: Target position

        Returns:
            Self for chaining
        """
        block = self.document.content.pop(from_index)
        self.document.content.insert(to_index, block)
        return self

    def swap_blocks(self, index1: int, index2: int) -> DocumentEditor:
        """
        Swap two blocks by their indices.

        Args:
            index1: First block index
            index2: Second block index

        Returns:
            Self for chaining
        """
        self.document.content[index1], self.document.content[index2] = (
            self.document.content[index2],
            self.document.content[index1],
        )
        return self

    def get_block(self, index: int) -> AnyBlock:
        """
        Get a block by index.

        Args:
            index: Block position

        Returns:
            Block at the specified index
        """
        return self.document.content[index]

    def find_block(self, block_id: str) -> tuple[int, AnyBlock] | None:
        """
        Find a block by ID.

        Args:
            block_id: UUID to search for

        Returns:
            Tuple of (index, block) or None if not found
        """
        for i, block in enumerate(self.document.content):
            if str(block.id) == block_id:
                return (i, block)
        return None

    def save(self, filepath: str | Path) -> None:
        """
        Save the document to a file.

        Args:
            filepath: Where to save the file
        """
        AtrbWriter.write_file(self.document, filepath)

    def to_string(self) -> str:
        """
        Convert document to YAML string.

        Returns:
            YAML representation
        """
        return AtrbWriter.to_string(self.document)

    def __len__(self) -> int:
        """Return number of blocks in document."""
        return len(self.document.content)

    def __iter__(self):
        """Iterate over blocks in document."""
        return iter(self.document.content)
