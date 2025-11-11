"""Parser for validating and loading .atrb files (Step 8)."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

import yaml

from .models import AtrbDocument, BaseBlock


class AtrbParser:
    """Parse and validate .atrb YAML into Pydantic models."""

    @staticmethod
    def parse_file(filepath: str | Path) -> AtrbDocument:
        """Read a file from disk and parse it into an AtrbDocument."""
        p = Path(filepath)
        text = p.read_text(encoding="utf-8")
        return AtrbParser.parse_string(text)

    @staticmethod
    def parse_string(content: str) -> AtrbDocument:
        """Parse YAML string content into an AtrbDocument."""
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            raise ValueError("Top-level .atrb YAML must be a mapping/object.")
        return AtrbParser._parse_document(data)

    @staticmethod
    def validate_atrb(filepath: str | Path) -> bool:
        """Return True iff the file parses without raising an exception."""
        try:
            AtrbParser.parse_file(filepath)
            return True
        except Exception:
            return False

    @staticmethod
    def _parse_document(data: dict[str, Any]) -> AtrbDocument:
        """Internal: convert raw dict (from YAML) into typed Pydantic models."""
        # Parse blocks (robust to missing keys via dict.get with sensible defaults)
        blocks: list[BaseBlock] = []
        for raw in data.get("content", []) or []:
            # Defensive checks: ensure required fields exist
            if not isinstance(raw, dict):
                raise ValueError("Each block must be a mapping/object.")
            bid = raw.get("id")
            btype = raw.get("type")
            if bid is None or btype is None:
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
            raise ValueError("Document missing one of required fields: id, name, version")

        return AtrbDocument(
            id=UUID(str(did)),
            name=str(name),
            version=int(version),
            content=blocks,
        )
