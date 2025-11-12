"""Parser for validating and loading .atrb files (Step 8, Step 2 logging)."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID
from logging import Logger

import yaml

from .models import AtrbDocument, BaseBlock
from .logger import logger as _default_logger


class AtrbParser:
    """Parse and validate .atrb YAML into Pydantic models."""

    @staticmethod
    def parse_file(filepath: str | Path, logger: Logger | None = None, **_: object) -> AtrbDocument:
        """Read a file from disk and parse it into an AtrbDocument."""
        lg = logger or _default_logger
        p = Path(filepath)
        text = p.read_text(encoding="utf-8")
        lg.info("parser.parse_file", extra={"path": str(p.absolute()), "bytes": len(text)})
        return AtrbParser.parse_string(text, logger=lg)

    @staticmethod
    def parse_string(content: str, logger: Logger | None = None, **_: object) -> AtrbDocument:
        """Parse YAML string content into an AtrbDocument."""
        lg = logger or _default_logger
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            lg.error("parser.error.top_level_not_mapping")
            raise ValueError("Top-level .atrb YAML must be a mapping/object.")
        doc = AtrbParser._parse_document(data, logger=lg)
        lg.debug("parser.parse_ok", extra={"blocks": len(doc.content)})
        return doc

    @staticmethod
    def validate_atrb(filepath: str | Path, logger: Logger | None = None, **_: object) -> bool:
        """Return True iff the file parses without raising an exception."""
        lg = logger or _default_logger
        try:
            AtrbParser.parse_file(filepath, logger=lg)
            return True
        except Exception as exc:
            lg.debug("parser.validate_failed", extra={"path": str(Path(filepath).absolute()), "error": str(exc)})
            return False

    @staticmethod
    def _parse_document(data: dict[str, Any], *, logger: Logger | None = None) -> AtrbDocument:
        """Internal: convert raw dict (from YAML) into typed Pydantic models."""
        lg = logger or _default_logger
        # Parse blocks (robust to missing keys via dict.get with sensible defaults)
        blocks: list[BaseBlock] = []
        for raw in data.get("content", []) or []:
            # Defensive checks: ensure required fields exist
            if not isinstance(raw, dict):
                lg.error("parser.error.block_not_mapping")
                raise ValueError("Each block must be a mapping/object.")
            bid = raw.get("id")
            btype = raw.get("type")
            if bid is None or btype is None:
                lg.error("parser.error.block_missing_keys")
                raise ValueError("Block is missing required 'id' or 'type'.")

            block = BaseBlock(
                id=UUID(str(bid)),
                type=str(btype),
                props=raw.get("props", {}) or {},
                content=raw.get("content", []) or [],
                children=raw.get("children", []) or [],
            )
            blocks.append(block)

        # Build document
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
