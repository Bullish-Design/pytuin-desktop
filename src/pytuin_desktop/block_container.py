# path: src/pytuin_desktop/block_container.py
"""Container for managing block collections in the editor (v4 Phase 3)."""
from __future__ import annotations
from typing import Iterator, Optional, Tuple
from uuid import UUID
from templateer import TemplateModel
from .models import BaseBlock

class BlockContainer:
    def __init__(self) -> None:
        self._existing: list[BaseBlock] = []
        self._new: list[TemplateModel] = []

    def __len__(self) -> int:
        return len(self._existing) + len(self._new)

    def __iter__(self) -> Iterator[BaseBlock | TemplateModel]:
        yield from self._existing
        yield from self._new

    def add_existing(self, block: BaseBlock) -> None:
        self._existing.append(block)

    def add_new(self, template: TemplateModel) -> None:
        self._new.append(template)

    def remove_at(self, index: int) -> None:
        n = len(self._existing)
        if index < 0 or index >= len(self): return
        if index < n: del self._existing[index]
        else: del self._new[index - n]

    def get_at(self, index: int) -> BaseBlock | TemplateModel:
        n = len(self._existing)
        if index < 0 or index >= len(self): raise IndexError(index)
        if index < n: return self._existing[index]
        return self._new[index - n]

    def get_existing_blocks(self) -> list[BaseBlock]:
        return list(self._existing)

    def get_new_templates(self) -> list[TemplateModel]:
        return list(self._new)

    def clear_new(self) -> None:
        self._new.clear()

    def find_by_id(self, block_id: UUID) -> Optional[Tuple[int, BaseBlock]]:
        for i, b in enumerate(self._existing):
            if b.id == block_id: return (i, b)
        return None

    def find_blocks_by_type(self, block_type: str) -> list[tuple[int, BaseBlock]]:
        return [(i, b) for i, b in enumerate(self._existing) if b.type == block_type]

    def move(self, from_index: int, to_index: int) -> None:
        """Move within existing or new region; crossing is invalid.

        Semantics: move(0,1) yields [1,0,...].
        """
        if from_index == to_index: return
        n = len(self._existing); total = len(self)
        if not (0 <= from_index < total and 0 <= to_index < total):
            raise IndexError("from/to out of range")

        if from_index < n and to_index < n:
            item = self._existing.pop(from_index)
            self._existing.insert(to_index, item)
            return
        if from_index >= n and to_index >= n:
            f = from_index - n; t = to_index - n
            item = self._new.pop(f)
            self._new.insert(t, item)
            return
        raise ValueError("Cannot move blocks across existing/new boundary")

    def replace_at(self, index: int, template: TemplateModel) -> None:
        n = len(self._existing)
        if index < 0 or index >= len(self): raise IndexError(index)
        self.remove_at(index)
        insert_pos = max(0, index - n)
        if insert_pos > len(self._new): insert_pos = len(self._new)
        self._new.insert(insert_pos, template)
