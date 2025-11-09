# src/atrb_parser/parser.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from pytuin_desktop.models.document import AtrbDocument
from pytuin_desktop.models.blocks import AnyBlock


class AtrbParser:
    """Parser for .atrb files into Pydantic models."""

    @staticmethod
    def parse_file(filepath: str | Path) -> AtrbDocument:
        """
        Parse an .atrb file into an AtrbDocument model.

        Args:
            filepath: Path to the .atrb file

        Returns:
            AtrbDocument: Parsed document with typed blocks
        """
        filepath = Path(filepath)
        with filepath.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return AtrbParser._parse_document(data)

    @staticmethod
    def parse_string(content: str) -> AtrbDocument:
        """
        Parse an .atrb string content into an AtrbDocument model.

        Args:
            content: String content of an .atrb file

        Returns:
            AtrbDocument: Parsed document with typed blocks
        """
        data = yaml.safe_load(content)
        return AtrbParser._parse_document(data)

    @staticmethod
    def _parse_document(data: dict[str, Any]) -> AtrbDocument:
        """Parse document data with discriminated union for blocks."""
        content_blocks = []
        for block_data in data.get("content", []):
            parsed_block = AtrbParser._parse_block(block_data)
            content_blocks.append(parsed_block)

        return AtrbDocument(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            content=content_blocks,
        )

    @staticmethod
    def _parse_block(block_data: dict[str, Any]) -> AnyBlock:
        """Parse a block using Pydantic's discriminated union."""
        if "children" in block_data and block_data["children"]:
            parsed_children = [
                AtrbParser._parse_block(child) for child in block_data["children"]
            ]
            block_data = {**block_data, "children": parsed_children}

        from pydantic import TypeAdapter

        adapter = TypeAdapter(AnyBlock)
        return adapter.validate_python(block_data)
