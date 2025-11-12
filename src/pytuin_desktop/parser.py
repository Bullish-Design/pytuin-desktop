"""Parser for validating and loading .atrb files."""
from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO
from uuid import UUID
from logging import Logger

import yaml

from .models import AtrbDocument, BaseBlock
from .logger import logger as _default_logger
from .errors import AtrbParseError, AtrbSchemaError, AtrbValidationError
from .enums import TextAlignment, ColorToken
from .validator import AtrbValidator


class AtrbParser:
    """Utilities for reading and validating .atrb documents.

    Emits logging breadcrumbs used by tests:
    - "parser.parse_file" when parsing starts from a file
    - "parser.parse_stream" when parsing starts from a stream
    - "parser.parse_ok" on successful parse
    - "parser.parse_error" on failure
    - "parser.error.*" for schema-level errors
    """

    # ------------------------
    # Public API
    # ------------------------
    @staticmethod
    def parse_file(filepath: str | Path, logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        lg = logger or _default_logger
        path = Path(filepath)
        lg.info("parser.parse_file", extra={"path": str(path.absolute())})
        try:
            with path.open("r", encoding="utf-8") as fh:
                doc = AtrbParser.parse_stream(fh, logger=lg, validate=validate)
            lg.info("parser.parse_ok", extra={"path": str(path.absolute())})
            return doc
        except (AtrbParseError, AtrbSchemaError, AtrbValidationError) as e:
            lg.error("parser.parse_error", extra={"path": str(path.absolute()), "error": str(e)})
            raise
        except Exception as e:  # wrap unknowns as parse error
            lg.error("parser.parse_error", extra={"path": str(path.absolute()), "error": str(e)})
            raise AtrbParseError(str(e)) from e

    @staticmethod
    def parse_stream(stream: TextIO, logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        lg = logger or _default_logger
        lg.debug("parser.parse_stream")
        try:
            data = yaml.safe_load(stream) or {}
        except Exception as e:
            lg.error("parser.error.yaml", extra={"error": str(e)})
            raise AtrbParseError("Invalid YAML") from e
        return AtrbParser.parse_dict(data, logger=lg, validate=validate)

    @staticmethod
    def parse_dict(data: dict[str, Any], logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        lg = logger or _default_logger
        if not isinstance(data, dict):
            lg.error("parser.error.root_not_mapping")
            raise AtrbSchemaError("Top-level YAML must be a mapping")

        # blocks
        content_raw = data.get("content", [])
        if not isinstance(content_raw, list):
            lg.error("parser.error.content_not_list")
            raise AtrbSchemaError("'content' must be a list")
        blocks: list[BaseBlock] = []
        for idx, raw in enumerate(content_raw):
            if not isinstance(raw, dict):
                lg.error("parser.error.block_not_mapping", extra={"index": idx})
                raise AtrbSchemaError(f"Block at index {idx} is not a mapping")
            bid = raw.get("id")
            btype = raw.get("type")
            if bid is None or btype is None:
                lg.error("parser.error.block_missing_keys", extra={"index": idx})
                raise AtrbSchemaError("Block missing required keys 'id' or 'type'")
            props = AtrbParser._coerce_enums_on_props(raw.get("props", {}) or {})
            block = BaseBlock(
                id=UUID(str(bid)),
                type=str(btype),
                props=props,
                content=raw.get("content", []) or [],
                children=raw.get("children", []) or [],
            )
            blocks.append(block)

        # document header
        did = data.get("id")
        name = data.get("name")
        version = data.get("version")
        if did is None or name is None or version is None:
            lg.error("parser.error.doc_missing_keys")
            raise AtrbSchemaError("Document missing required keys 'id', 'name', or 'version'")

        try:
            doc = AtrbDocument(
                id=UUID(str(did)),
                name=str(name),
                version=int(version),
                content=blocks,
            )
        except Exception as e:
            lg.error("parser.error.model", extra={"error": str(e)})
            raise AtrbValidationError(str(e)) from e

        if validate:
            AtrbValidator.validate(doc)
        return doc

    # ------------------------
    # Helpers
    # ------------------------
    @staticmethod
    def _coerce_enums_on_props(props: dict[str, Any]) -> dict[str, Any]:
        """Coerce legacy string values into enums where known.

        Accepts either strings (case-insensitive) or enum instances.
        Stores the enum instance to preserve typing, downstream serializers
        will convert to strings.
        """
        mapping: dict[str, type] = {
            "text_alignment": TextAlignment,
            "textAlign": TextAlignment,
            "text_color": ColorToken,
            "background_color": ColorToken,
            "color": ColorToken,
        }
        out = dict(props or {})
        for key, enum_cls in mapping.items():
            if key in out and out[key] is not None:
                val = out[key]
                if isinstance(val, enum_cls):
                    continue
                if isinstance(val, str):
                    token = val.strip().lower()
                    try:
                        out[key] = enum_cls(token)  # type: ignore[arg-type]
                    except Exception as e:
                        raise AtrbValidationError(f"Invalid {enum_cls.__name__} value for '{key}': {val!r}") from e
                else:
                    raise AtrbValidationError(f"Expected string or {enum_cls.__name__} for '{key}', got {type(val).__name__}")
        return out

    @staticmethod
    def validate_atrb(filepath: str | Path, logger: Logger | None = None, **_: object) -> bool:
        """Return True iff the file parses without raising an exception."""
        lg = logger or _default_logger
        try:
            AtrbParser.parse_file(filepath, logger=lg, validate=True)
            return True
        except Exception as exc:
            lg.debug("parser.validate_failed", extra={"path": str(Path(filepath).absolute()), "error": str(exc)})
            return False
