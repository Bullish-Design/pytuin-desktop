# path: pytuin_desktop/validator.py
"""Validator service (v4 Phase 1)."""
from __future__ import annotations
from typing import Iterable
from uuid import UUID
from .models import AtrbDocument, BaseBlock
from .errors import AtrbSchemaError, AtrbValidationError
from .enums import TextAlignment, ColorToken

class AtrbValidator:
    @staticmethod
    def validate(doc: AtrbDocument) -> None:
        AtrbValidator._validate_doc_header(doc)
        AtrbValidator._validate_blocks(doc.content)

    @staticmethod
    def _validate_doc_header(doc: AtrbDocument) -> None:
        if not isinstance(doc.id, UUID):
            raise AtrbSchemaError("Document 'id' must be a UUID", suggestion="Ensure the document ID is a valid UUID string", context={"found_type": type(doc.id).__name__})
        if not isinstance(doc.name, str) or not doc.name.strip():
            raise AtrbSchemaError("Document 'name' must be a non-empty string", suggestion="Provide a descriptive name for the document")
        if not isinstance(doc.version, int):
            raise AtrbSchemaError("Document 'version' must be an integer", context={"found_type": type(doc.version).__name__})
        if doc.version < 1:
            raise AtrbValidationError("Document 'version' must be >= 1", suggestion="Version should be 1 or higher", context={"found_version": doc.version})

    @staticmethod
    def _validate_blocks(blocks: Iterable[BaseBlock]) -> None:
        seen_ids: set[UUID] = set()
        for idx, block in enumerate(blocks):
            if not isinstance(block.id, UUID):
                raise AtrbSchemaError(f"Block[{idx}] 'id' must be a UUID", suggestion="Each block must have a valid UUID", context={"index": idx, "type": getattr(block, 'type', None)})
            if not isinstance(block.type, str) or not block.type.strip():
                raise AtrbSchemaError(f"Block[{idx}] 'type' must be a non-empty string", suggestion="Set 'type' to a meaningful string for the block", context={"index": idx})
            if block.id in seen_ids:
                raise AtrbValidationError(f"Duplicate block ID detected: {block.id}", suggestion="Each block must have a unique UUID. Generate new UUIDs for duplicates.", context={"duplicate_index": idx, "block_type": block.type})
            seen_ids.add(block.id)
            if not isinstance(block.props, dict):
                raise AtrbSchemaError(f"Block[{idx}] 'props' must be a mapping", context={"found_type": type(block.props).__name__})
            if not isinstance(block.content, list):
                raise AtrbSchemaError(f"Block[{idx}] 'content' must be a list", context={"found_type": type(block.content).__name__})
            if not isinstance(block.children, list):
                raise AtrbSchemaError(f"Block[{idx}] 'children' must be a list", context={"found_type": type(block.children).__name__})
            AtrbValidator._validate_enums(block, idx)
            AtrbValidator._validate_known_block_shapes(block, idx)

    @staticmethod
    def _validate_enums(block: BaseBlock, idx: int) -> None:
        enum_fields = {
            "text_alignment": TextAlignment,
            "textAlign": TextAlignment,
            "text_color": ColorToken,
            "background_color": ColorToken,
            "color": ColorToken,
        }
        for key, enum_cls in enum_fields.items():
            if key in block.props and block.props[key] is not None:
                if not isinstance(block.props[key], enum_cls):
                    raise AtrbValidationError(
                        f"Block[{idx}] '{key}' must be a {enum_cls.__name__} (got {type(block.props[key]).__name__}). This indicates a bug in enum coercion."
                    )

    @staticmethod
    def _validate_known_block_shapes(block: BaseBlock, idx: int) -> None:
        t = block.type.lower()
        if t == "heading":
            level = block.props.get("level")
            if level is not None:
                if not isinstance(level, int):
                    raise AtrbValidationError(f"Block[{idx}] heading 'level' must be an integer")
                if not (1 <= level <= 6):
                    raise AtrbValidationError(
                        f"Invalid heading level: {level}",
                        suggestion="Heading levels must be integers between 1 and 6",
                        context={"block_index": idx, "found_level": level, "block_id": str(block.id)},
                    )
