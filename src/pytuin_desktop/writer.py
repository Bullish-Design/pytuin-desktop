# src/pytuin_desktop/writer.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from pytuin_desktop.models.document import AtrbDocument
from pytuin_desktop.models.blocks import AnyBlock


class AtrbWriter:
    """Writer for serializing AtrbDocument models back to .atrb files."""

    @staticmethod
    def write_file(document: AtrbDocument, filepath: str | Path) -> None:
        """
        Write an AtrbDocument to an .atrb file.

        Args:
            document: The document to write
            filepath: Path where the file should be written
        """
        filepath = Path(filepath)
        content = AtrbWriter.to_string(document)

        with filepath.open("w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def to_string(document: AtrbDocument) -> str:
        """
        Convert an AtrbDocument to YAML string.

        Args:
            document: The document to serialize

        Returns:
            YAML string representation
        """
        data = AtrbWriter._serialize_document(document)
        return yaml.dump(
            data, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    @staticmethod
    def _serialize_document(document: AtrbDocument) -> dict[str, Any]:
        """Serialize document to dict with proper field names."""
        return {
            "id": str(document.id),
            "name": document.name,
            "version": document.version,
            "content": [
                AtrbWriter._serialize_block(block) for block in document.content
            ],
        }

    @staticmethod
    def _serialize_block(block: AnyBlock) -> dict[str, Any]:
        """
        Serialize a block to dict using by_alias for camelCase field names.

        Args:
            block: Block to serialize

        Returns:
            Dict with YAML-compatible field names
        """
        # Use by_alias to get camelCase names, mode='python' keeps UUID objects
        block_dict = block.model_dump(by_alias=True, exclude_none=True, mode="python")

        # Convert UUID to string
        if "id" in block_dict:
            block_dict["id"] = str(block_dict["id"])

        # Recursively serialize children
        if "children" in block_dict and block_dict["children"]:
            block_dict["children"] = [
                AtrbWriter._serialize_block(child) for child in block.children
            ]

        return block_dict
