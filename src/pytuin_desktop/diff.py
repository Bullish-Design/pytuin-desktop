# path: src/pytuin_desktop/diff.py
"""Document diffing and comparison utilities (v4 Phase 4 - Step 12).
- Block-level change detection (added/removed/moved/modified).
- Property- and content-level diffs for modified blocks.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .models import AtrbDocument, BaseBlock, Block


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MOVED = "moved"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class BlockChange:
    change_type: ChangeType
    block_id: UUID
    old_index: int | None = None
    new_index: int | None = None
    old_block: Block | BaseBlock | None = None
    new_block: Block | BaseBlock | None = None
    property_changes: Dict[str, Tuple[Any, Any]] | None = None


@dataclass
class DocumentDiff:
    old_doc: AtrbDocument
    new_doc: AtrbDocument
    changes: List[BlockChange]

    @property
    def has_changes(self) -> bool:
        return any(c.change_type != ChangeType.UNCHANGED for c in self.changes)

    @property
    def added_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.ADDED)

    @property
    def removed_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.REMOVED)

    @property
    def modified_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.MODIFIED)

    @property
    def moved_count(self) -> int:
        return sum(1 for c in self.changes if c.change_type == ChangeType.MOVED)


class DocumentDiffer:
    """Compares two AtrbDocument instances and returns a DocumentDiff."""

    @staticmethod
    def diff(old_doc: AtrbDocument, new_doc: AtrbDocument) -> DocumentDiff:
        # Build id maps
        old_map: Dict[UUID, Tuple[int, Block | BaseBlock]] = {b.id: (i, b) for i, b in enumerate(old_doc.content)}
        new_map: Dict[UUID, Tuple[int, Block | BaseBlock]] = {b.id: (i, b) for i, b in enumerate(new_doc.content)}

        changes: List[BlockChange] = []

        # Removed
        for bid, (idx, blk) in old_map.items():
            if bid not in new_map:
                changes.append(BlockChange(
                    change_type=ChangeType.REMOVED,
                    block_id=bid,
                    old_index=idx,
                    old_block=blk,
                ))

        # Added
        for bid, (idx, blk) in new_map.items():
            if bid not in old_map:
                changes.append(BlockChange(
                    change_type=ChangeType.ADDED,
                    block_id=bid,
                    new_index=idx,
                    new_block=blk,
                ))

        # Moved / Modified
        for bid in old_map.keys() & new_map.keys():
            old_idx, old_blk = old_map[bid]
            new_idx, new_blk = new_map[bid]

            if old_idx != new_idx:
                changes.append(BlockChange(
                    change_type=ChangeType.MOVED,
                    block_id=bid,
                    old_index=old_idx,
                    new_index=new_idx,
                    old_block=old_blk,
                    new_block=new_blk,
                ))
                # If also modified, we emit a separate MODIFIED change entry
                prop_changes = DocumentDiffer._diff_block_props(old_blk, new_blk)
                if prop_changes:
                    changes.append(BlockChange(
                        change_type=ChangeType.MODIFIED,
                        block_id=bid,
                        old_index=old_idx,
                        new_index=new_idx,
                        old_block=old_blk,
                        new_block=new_blk,
                        property_changes=prop_changes,
                    ))
            else:
                prop_changes = DocumentDiffer._diff_block_props(old_blk, new_blk)
                if prop_changes:
                    changes.append(BlockChange(
                        change_type=ChangeType.MODIFIED,
                        block_id=bid,
                        old_index=old_idx,
                        new_index=new_idx,
                        old_block=old_blk,
                        new_block=new_blk,
                        property_changes=prop_changes,
                    ))

        # Order by old->new index for determinism
        changes.sort(key=lambda c: (c.old_index if c.old_index is not None else 10**9,
                                    c.new_index if c.new_index is not None else 10**9))
        return DocumentDiff(old_doc=old_doc, new_doc=new_doc, changes=changes)

    @staticmethod
    def _diff_block_props(old_blk: Block | BaseBlock, new_blk: Block | BaseBlock) -> Dict[str, Tuple[Any, Any]] | None:
        out: Dict[str, Tuple[Any, Any]] = {}

        if getattr(old_blk, "type", None) != getattr(new_blk, "type", None):
            out["type"] = (getattr(old_blk, "type", None), getattr(new_blk, "type", None))

        old_props = getattr(old_blk, "props", {}) or {}
        new_props = getattr(new_blk, "props", {}) or {}
        if isinstance(old_props, dict) and isinstance(new_props, dict):
            keys = set(old_props.keys()) | set(new_props.keys())
            for k in keys:
                ov = old_props.get(k)
                nv = new_props.get(k)
                if ov != nv:
                    out[f"props.{k}"] = (ov, nv)

        # Naive content comparison (stringified for simplicity)
        oc = getattr(old_blk, "content", None)
        nc = getattr(new_blk, "content", None)
        if oc != nc:
            out["content"] = (oc, nc)

        return out or None
