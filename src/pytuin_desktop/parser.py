# path: src/pytuin_desktop/parser.py
"""Parser for .atrb files (v4 Phase 4 - metrics hooks)."""
from __future__ import annotations
from pathlib import Path
from typing import Any, TextIO
from uuid import UUID
from logging import Logger
import yaml
from pydantic import TypeAdapter
from .models import AtrbDocument, BaseBlock, Block
from .logger import logger as _default_logger
from .errors import AtrbParseError, AtrbSchemaError, AtrbValidationError
from .validator import AtrbValidator
from .metrics import MetricsCollector, get_default_collector, TimingContext

class AtrbParser:
    @staticmethod
    def parse_file(filepath: str | Path, logger: Logger | None = None, *, validate: bool = True, metrics: MetricsCollector | None = None) -> AtrbDocument:
        lg = logger or _default_logger
        mc = metrics or get_default_collector()
        path = Path(filepath)
        lg.info("parser.parse_file", extra={"path": str(path.absolute())})
        with TimingContext(mc, "parse_file"):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    doc = AtrbParser.parse_stream(fh, logger=lg, validate=validate, metrics=mc)
                lg.info("parser.parse_ok", extra={"path": str(path.absolute())})
                mc.increment_counter("documents_parsed")
                mc.record_value("document_block_count", len(doc.content))
                return doc
            except (AtrbParseError, AtrbSchemaError, AtrbValidationError):
                mc.increment_counter("parse_errors")
                raise
            except Exception as e:
                lg.error("parser.parse_error", extra={"path": str(path.absolute()), "error": str(e)})
                mc.increment_counter("parse_errors")
                raise AtrbParseError(str(e)) from e

    @staticmethod
    def parse_stream(stream: TextIO, logger: Logger | None = None, *, validate: bool = True, metrics: MetricsCollector | None = None) -> AtrbDocument:
        lg = logger or _default_logger
        try:
            data = yaml.safe_load(stream) or {}
        except Exception as e:
            lg.error("parser.error.yaml", extra={"error": str(e)})
            raise AtrbParseError("Failed to parse YAML content", suggestion="Check that your .atrb file is valid YAML syntax", context={"yaml_error": str(e)}) from e
        return AtrbParser.parse_dict(data, logger=lg, validate=validate)

    @staticmethod
    def parse_dict(data: dict[str, Any], logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        """Legacy parse path: constructs BaseBlock for each block."""
        lg = logger or _default_logger
        if not isinstance(data, dict):
            lg.error("parser.error.root_not_mapping")
            raise AtrbSchemaError("Top-level YAML must be a mapping", suggestion="Ensure the root of the file is a YAML mapping (key: value)", context={"found_type": type(data).__name__})
        content_raw = data.get("content", [])
        if not isinstance(content_raw, list):
            lg.error("parser.error.content_not_list")
            raise AtrbSchemaError("'content' must be a list of block dictionaries", suggestion="Add 'content: []' at the root and ensure it is a YAML list", context={"found_type": type(content_raw).__name__})
        blocks: list[BaseBlock] = []
        for idx, raw in enumerate(content_raw):
            if not isinstance(raw, dict):
                lg.error("parser.error.block_not_mapping", extra={"index": idx})
                raise AtrbSchemaError(f"Block at index {idx} is not a mapping", suggestion="Each block must be an object with keys like id/type/props", context={"index": idx, "found_type": type(raw).__name__})
            bid = raw.get("id")
            btype = raw.get("type")
            if bid is None or btype is None:
                lg.error("parser.error.block_missing_keys", extra={"index": idx})
                raise AtrbSchemaError(f"Block at index {idx} missing required keys 'id' or 'type'", suggestion="Every block must include both 'id' (UUID) and 'type' (string)", context={"index": idx, "found_keys": list(raw.keys())})
            try:
                block = BaseBlock(
                    id=UUID(str(bid)),
                    type=str(btype),
                    props=raw.get("props", {}) or {},
                    content=raw.get("content", []) or [],
                    children=raw.get("children", []) or [],
                )
            except Exception as e:
                lg.error("parser.error.model", extra={"error": str(e), "index": idx})
                raise AtrbValidationError(f"Block at index {idx} has invalid structure: {e}", context={"index": idx}) from e
            blocks.append(block)
        did = data.get("id"); name = data.get("name"); version = data.get("version")
        if did is None or name is None or version is None:
            lg.error("parser.error.doc_missing_keys")
            raise AtrbSchemaError("Document missing required keys 'id', 'name', or 'version'", suggestion="Add top-level 'id', 'name', and 'version' fields")
        try:
            doc = AtrbDocument(id=UUID(str(did)), name=str(name), version=int(version), content=blocks)
        except Exception as e:
            lg.error("parser.error.model", extra={"error": str(e)})
            raise AtrbValidationError(str(e)) from e
        if validate:
            AtrbValidator.validate(doc)
        return doc

    # ---- Typed parse variants ----

    @staticmethod
    def parse_file_typed(filepath: str | Path, logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        lg = logger or _default_logger
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as fh:
            return AtrbParser.parse_stream_typed(fh, logger=lg, validate=validate)

    @staticmethod
    def parse_stream_typed(stream: TextIO, logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        lg = logger or _default_logger
        try:
            data = yaml.safe_load(stream) or {}
        except Exception as e:
            raise AtrbParseError("Failed to parse YAML content", suggestion="Check that your .atrb file is valid YAML syntax", context={"yaml_error": str(e)}) from e
        return AtrbParser.parse_dict_typed(data, logger=lg, validate=validate)

    @staticmethod
    def parse_dict_typed(data: dict[str, Any], logger: Logger | None = None, *, validate: bool = True) -> AtrbDocument:
        """Typed parse path: passes raw block dicts through the Block union adapter."""
        lg = logger or _default_logger
        if not isinstance(data, dict):
            raise AtrbSchemaError("Top-level YAML must be a mapping")
        content_raw = data.get("content", [])
        if not isinstance(content_raw, list):
            raise AtrbSchemaError("'content' must be a list of block dictionaries")
        adapter = TypeAdapter(Block)
        typed_blocks = []
        for idx, raw in enumerate(content_raw):
            if not isinstance(raw, dict):
                raise AtrbSchemaError(f"Block at index {idx} is not a mapping")
            if "id" not in raw or "type" not in raw:
                raise AtrbSchemaError(f"Block at index {idx} missing required keys 'id' or 'type'")
            try:
                typed_blocks.append(adapter.validate_python(raw))
            except Exception:
                # Fallback to BaseBlock for unknown types or mismatches
                from uuid import UUID as _UUID
                typed_blocks.append(BaseBlock(
                    id=_UUID(str(raw.get("id"))),
                    type=str(raw.get("type")),
                    props=raw.get("props", {}) or {},
                    content=raw.get("content", []) or [],
                    children=raw.get("children", []) or [],
                ))
        did = data.get("id"); name = data.get("name"); version = data.get("version")
        if did is None or name is None or version is None:
            raise AtrbSchemaError("Document missing required keys 'id', 'name', or 'version'")
        try:
            doc = AtrbDocument(id=UUID(str(did)), name=str(name), version=int(version), content=typed_blocks)
        except Exception as e:
            raise AtrbValidationError(str(e)) from e
        if validate:
            AtrbValidator.validate(doc)
        return doc
