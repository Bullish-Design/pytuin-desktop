
"""Validator service for .atrb documents (v3 Step 8)."""
from __future__ import annotations

from typing import Iterable
from uuid import UUID

from .models import AtrbDocument, BaseBlock
from .errors import AtrbSchemaError, AtrbValidationError
from .enums import TextAlignment, ColorToken


class AtrbValidator:
    """Schema + semantic validator for parsed documents.

    Usage:
        AtrbValidator.validate(doc)  # raises on failure
    """

    # ---- Public API -------------------------------------------------
    @staticmethod
    def validate(doc: AtrbDocument) -> None:
        AtrbValidator._validate_doc_header(doc)
        AtrbValidator._validate_blocks(doc.content)

    # ---- Header checks ----------------------------------------------
    @staticmethod
    def _validate_doc_header(doc: AtrbDocument) -> None:
        # id
        if not isinstance(doc.id, UUID):
            raise AtrbSchemaError("Document 'id' must be a UUID")
        # name
        if not isinstance(doc.name, str) or not doc.name.strip():
            raise AtrbSchemaError("Document 'name' must be a non-empty string")
        # version
        if not isinstance(doc.version, int):
            raise AtrbSchemaError("Document 'version' must be an integer")
        if doc.version < 1:
            raise AtrbValidationError("Document 'version' must be >= 1")

    # ---- Block checks -----------------------------------------------
    @staticmethod
    def _validate_blocks(blocks: Iterable[BaseBlock]) -> None:
        seen_ids: set[UUID] = set()
        for idx, block in enumerate(blocks):
            # structure
            if not isinstance(block.id, UUID):
                raise AtrbSchemaError(f"Block[{idx}] 'id' must be a UUID")
            if not isinstance(block.type, str) or not block.type.strip():
                raise AtrbSchemaError(f"Block[{idx}] 'type' must be a non-empty string")
            if block.id in seen_ids:
                raise AtrbValidationError(f"Duplicate block id detected at index {idx}: {block.id}")
            seen_ids.add(block.id)

            # props/container types
            if not isinstance(block.props, dict):
                raise AtrbSchemaError(f"Block[{idx}] 'props' must be a mapping")
            if not isinstance(block.content, list):
                raise AtrbSchemaError(f"Block[{idx}] 'content' must be a list")
            if not isinstance(block.children, list):
                raise AtrbSchemaError(f"Block[{idx}] 'children' must be a list")

            AtrbValidator._validate_enums(block, idx)
            AtrbValidator._validate_known_block_shapes(block, idx)

    @staticmethod
    def _validate_enums(block: BaseBlock, idx: int) -> None:
        """Validate enum-valued properties (accept instances only at this stage)."""
        enum_fields = {
            "text_alignment": TextAlignment,
            "textAlign": TextAlignment,
            "text_color": ColorToken,
            "background_color": ColorToken,
            "color": ColorToken,
        }
        for key, enum_cls in enum_fields.items():
            if key in block.props and block.props[key] is not None:
                val = block.props[key]
                if not isinstance(val, enum_cls):
                    # If a legacy string slipped through, signal a domain error
                    raise AtrbValidationError(
                        f"Block[{idx}] '{key}' must be a {enum_cls.__name__} (got {type(val).__name__})"
                    )

    @staticmethod
    def _validate_known_block_shapes(block: BaseBlock, idx: int) -> None:
        """Lightweight shape checks for known types (best-effort)."""
        t = block.type.lower()

        if t == "heading":
            # Expect a heading 'level' within 1..6 (semantic), if present
            level = block.props.get("level")
            if level is not None:
                if not isinstance(level, int):
                    raise AtrbValidationError(f"Block[{idx}] heading 'level' must be an integer")
                if not (1 <= level <= 6):
                    raise AtrbValidationError(f"Block[{idx}] heading 'level' must be between 1 and 6")

        # Paragraph/script/etc. currently have no strict additional rules here;
        # schema guarantees above are sufficient for step 8.
