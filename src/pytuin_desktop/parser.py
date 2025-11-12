"""Parser for validating and loading .atrb files (v3 Step 7-ready)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO
from uuid import UUID
from logging import Logger

import yaml

from .models import AtrbDocument, BaseBlock
from .logger import logger as _default_logger
from .enums import TextAlignment, ColorToken
from .errors import AtrbValidationError


class AtrbParser:
    """Load and validate .atrb YAML documents into Pydantic models.

    Public API:
    - parse_file(path) -> AtrbDocument
    - parse_stream(stream) -> AtrbDocument
    - parse_dict(data) -> AtrbDocument
    - validate(path) -> bool
    """

    # ---- Public API -----------------------------------------------------
    @staticmethod
    def parse_file(filepath: str | Path, *, logger: Logger | None = None) -> AtrbDocument:
        lg = logger or _default_logger
        path = Path(filepath)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            lg.error("parser.error.read_failed", extra={"path": str(path), "error": str(e)})
            raise

        return AtrbParser.parse_stream(text, logger=lg)

    @staticmethod
    def parse_stream(stream: str | TextIO, *, logger: Logger | None = None) -> AtrbDocument:
        lg = logger or _default_logger
        try:
            if hasattr(stream, "read"):
                data = yaml.safe_load(stream.read())  # type: ignore[arg-type]
            else:
                data = yaml.safe_load(stream)  # type: ignore[arg-type]
        except Exception as e:
            lg.error("parser.error.yaml_load_failed", extra={"error": str(e)})
            raise

        if not isinstance(data, dict):
            lg.error("parser.error.root_not_mapping")
            raise ValueError("Top-level YAML must be a mapping/object")

        return AtrbParser._parse_document(data, logger=lg)

    @staticmethod
    def parse_dict(data: dict[str, Any], *, logger: Logger | None = None) -> AtrbDocument:
        lg = logger or _default_logger
        if not isinstance(data, dict):
            lg.error("parser.error.root_not_mapping")
            raise ValueError("Top-level data must be a dict")
        return AtrbParser._parse_document(data, logger=lg)

    @staticmethod
    def validate(filepath: str | Path, *, logger: Logger | None = None) -> bool:
        lg = logger or _default_logger
        try:
            AtrbParser.parse_file(filepath, logger=lg)
            return True
        except Exception as exc:
            lg.debug("parser.validate_failed", extra={"path": str(Path(filepath).absolute()), "error": str(exc)})
            return False

    # ---- Internals ------------------------------------------------------
    @staticmethod
    def _coerce_enums_on_props(props: dict) -> dict:
        """Normalize known enum-bearing properties to *canonical strings*.

        Accepts enum instances or strings (case-insensitive). Raises
        AtrbValidationError if an invalid token is supplied.
        """
        mapping: dict[str, type] = {
            "text_alignment": TextAlignment,
            "textAlign": TextAlignment,  # tolerate camelCase if present
            "text_color": ColorToken,
            "background_color": ColorToken,
            "color": ColorToken,  # generic alias
        }
        out = dict(props or {})
        for key, enum_cls in mapping.items():
            if key in out and out[key] is not None:
                val = out[key]
                if isinstance(val, enum_cls):
                    out[key] = val.value
                    continue
                if isinstance(val, str):
                    token = val.strip().lower()
                    try:
                        out[key] = enum_cls(token).value
                    except Exception as e:
                        raise AtrbValidationError(f"Invalid {enum_cls.__name__} value for '{key}': {val!r}") from e
                else:
                    raise AtrbValidationError(f"Expected string or {enum_cls.__name__} for '{key}', got {type(val).__name__}")
        return out

    @staticmethod
    def _parse_document(data: dict[str, Any], *, logger: Logger | None = None) -> AtrbDocument:
        """Convert raw dict (from YAML) into typed Pydantic models."""
        lg = logger or _default_logger

        # Parse blocks list safely
        blocks: list[BaseBlock] = []
        for raw in data.get("content", []) or []:
            if not isinstance(raw, dict):
                lg.error("parser.error.block_not_mapping")
                raise ValueError("Block entries must be mappings/objects")

            bid = raw.get("id")
            btype = raw.get("type")
            if bid is None or btype is None:
                lg.error("parser.error.block_missing_keys")
                raise ValueError("Block missing required keys: id, type")

            # Normalize properties (including enum tokens)
            raw_props = AtrbParser._coerce_enums_on_props(raw.get("props", {}) or {})

            block = BaseBlock(
                id=UUID(str(bid)),
                type=str(btype),
                props=raw_props,
                content=list(raw.get("content", []) or []),
                children=list(raw.get("children", []) or []),
            )
            blocks.append(block)

        did = data.get("id")
        name = data.get("name")
        version = data.get("version")
        if did is None or name is None or version is None:
            lg.error("parser.error.doc_missing_keys")
            raise ValueError("Document missing one of required fields: id, name, version")

        doc = AtrbDocument(
            id=UUID(str(did)),
            name=str(name),
            version=int(version),
            content=blocks,
        )
        return doc
