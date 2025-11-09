# src/pytuin_desktop/editor.py
from __future__ import annotations

from uuid import uuid4
from pathlib import Path
from typing import Callable, Iterator

from pytuin_desktop.models.document import AtrbDocument
from pytuin_desktop.models.blocks import AnyBlock
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.writer import AtrbWriter


class DocumentEditor:
    """Editor for manipulating AtrbDocument structure."""

    def __init__(self, document: AtrbDocument):
        """Initialize editor with a document."""
        self.document = document
        self._block_index: dict[str, tuple[int, AnyBlock]] = {}
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild the block ID index for fast lookups."""
        self._block_index.clear()
        for i, block in enumerate(self.document.content):
            self._block_index[str(block.id)] = (i, block)

    @classmethod
    def from_file(cls, filepath: str | Path) -> DocumentEditor:
        """Load a document from file for editing."""
        document = AtrbParser.parse_file(filepath)
        return cls(document)

    @classmethod
    def create(cls, name: str, version: int = 1) -> DocumentEditor:
        """Create a new empty document."""
        document = AtrbDocument(id=uuid4(), name=name, version=version, content=[])
        return cls(document)

    @classmethod
    def from_template(cls, template_path: str | Path, new_name: str) -> DocumentEditor:
        """Create a new document from a template file."""
        template = AtrbParser.parse_file(template_path)
        new_doc = AtrbDocument(
            id=uuid4(),
            name=new_name,
            version=template.version,
            content=template.content.copy(),
        )
        return cls(new_doc)

    def add_block(self, block: AnyBlock, index: int | None = None) -> DocumentEditor:
        """Add a block to the document."""
        if index is None:
            self.document.content.append(block)
            self._block_index[str(block.id)] = (len(self.document.content) - 1, block)
        else:
            self.document.content.insert(index, block)
            self._rebuild_index()
        return self

    def remove_block(self, block_id: str) -> DocumentEditor:
        """Remove a block by ID. Raises ValueError if block not found."""
        if block_id not in self._block_index:
            raise ValueError(f"Block with id {block_id} not found")
        index, _ = self._block_index[block_id]
        del self.document.content[index]
        self._rebuild_index()
        return self

    def remove_block_at(self, index: int) -> DocumentEditor:
        """Remove a block at the specified index."""
        if 0 <= index < len(self.document.content):
            del self.document.content[index]
            self._rebuild_index()
        return self

    def get_block(self, index: int) -> AnyBlock:
        """Get block at index."""
        return self.document.content[index]

    # def find_block(self, block_id: str) -> AnyBlock | None:
    #    """Find block by ID. Returns block or None if not found."""
    #    result = self._block_index.get(block_id)
    #    return result[1] if result else None
    def find_block(self, block_id: str) -> tuple[int, AnyBlock] | None:
        """Find block by ID. Returns (index, block) or None."""
        return self._block_index.get(block_id)

    def find_block_by_id(self, block_id: str) -> tuple[int, AnyBlock] | None:
        """Find block by ID. Returns (index, block) or None."""
        return self._block_index.get(block_id)

    def move_block(self, from_index: int, to_index: int) -> DocumentEditor:
        """Move a block from one index to another."""
        if 0 <= from_index < len(self.document.content) and 0 <= to_index < len(
            self.document.content
        ):
            block = self.document.content.pop(from_index)
            self.document.content.insert(to_index, block)
            self._rebuild_index()
        return self

    def swap_blocks(self, index1: int, index2: int) -> DocumentEditor:
        """Swap two blocks."""
        if 0 <= index1 < len(self.document.content) and 0 <= index2 < len(
            self.document.content
        ):
            self.document.content[index1], self.document.content[index2] = (
                self.document.content[index2],
                self.document.content[index1],
            )
            self._rebuild_index()
        return self

    def save(self, filepath: str | Path) -> None:
        """Save the document to a file."""
        AtrbWriter.write_file(self.document, filepath)

    def to_string(self) -> str:
        """Convert document to YAML string."""
        return AtrbWriter.to_string(self.document)

    def __len__(self) -> int:
        """Return number of blocks in document."""
        return len(self.document.content)

    def __iter__(self):
        """Iterate over blocks in document."""
        return iter(self.document.content)

    # Block Traversal Utilities

    def walk_blocks(
        self, include_nested: bool = True
    ) -> Iterator[tuple[AnyBlock, int | None]]:
        """
        Iterate all blocks, optionally including nested children.

        Yields:
            Tuple of (block, depth) where depth is None for top-level blocks,
            and 0+ for nested blocks indicating nesting level.
        """
        for block in self.document.content:
            yield (block, None)
            if include_nested and hasattr(block, "children") and block.children:
                yield from self._walk_children(block.children, depth=0)

    def _walk_children(
        self, children: list[AnyBlock], depth: int
    ) -> Iterator[tuple[AnyBlock, int]]:
        """Recursively walk children blocks."""
        for child in children:
            yield (child, depth)
            if hasattr(child, "children") and child.children:
                yield from self._walk_children(child.children, depth + 1)

    def flatten_blocks(self) -> list[AnyBlock]:
        """Return a flat list of all blocks including nested children."""
        return [block for block, _ in self.walk_blocks(include_nested=True)]

    # Block Filtering Utilities

    def find_blocks(
        self,
        block_type: str | None = None,
        predicate: Callable[[AnyBlock], bool] | None = None,
        include_nested: bool = False,
    ) -> list[AnyBlock]:
        """
        Find blocks matching criteria.

        Args:
            block_type: Filter by block type (e.g., 'heading', 'paragraph')
            predicate: Custom filter function
            include_nested: Whether to search nested children

        Returns:
            List of matching blocks
        """
        results = []

        blocks_to_search = (
            self.walk_blocks(include_nested)
            if include_nested
            else ((block, None) for block in self.document.content)
        )

        for block, _ in blocks_to_search:
            # Check type filter
            if block_type and block.type != block_type:
                continue

            # Check predicate
            if predicate and not predicate(block):
                continue

            results.append(block)

        return results

    def find_blocks_by_property(
        self, prop_name: str, prop_value: any
    ) -> list[AnyBlock]:
        """Find blocks with a specific property value."""

        def has_property(block: AnyBlock) -> bool:
            if not hasattr(block, "props"):
                return False
            props_dict = block.props.model_dump()
            return props_dict.get(prop_name) == prop_value

        return self.find_blocks(predicate=has_property, include_nested=True)

    def find_blocks_with_text(
        self, search_text: str, case_sensitive: bool = False
    ) -> list[AnyBlock]:
        """Find blocks containing specific text."""

        def contains_text(block: AnyBlock) -> bool:
            if not hasattr(block, "content") or not block.content:
                return False

            text_to_search = search_text if case_sensitive else search_text.lower()

            for item in block.content:
                if hasattr(item, "text"):
                    item_text = item.text if case_sensitive else item.text.lower()
                    if text_to_search in item_text:
                        return True
            return False

        return self.find_blocks(predicate=contains_text, include_nested=True)

    def find_named_blocks(self) -> dict[str, AnyBlock]:
        """Find all blocks that have a 'name' property."""
        named = {}
        for block in self.flatten_blocks():
            if hasattr(block, "props") and hasattr(block.props, "name"):
                name = block.props.name
                if name:
                    named[name] = block
        return named

    def count_blocks_by_type(self, include_nested: bool = False) -> dict[str, int]:
        """Count blocks by type."""
        counts: dict[str, int] = {}
        blocks_to_count = (
            self.walk_blocks(include_nested)
            if include_nested
            else ((block, None) for block in self.document.content)
        )

        for block, _ in blocks_to_count:
            counts[block.type] = counts.get(block.type, 0) + 1

        return counts
