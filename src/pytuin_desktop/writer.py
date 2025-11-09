# src/pytuin_desktop/writer.py
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from pytuin_desktop.models.document import AtrbDocument
from pytuin_desktop.models.blocks import AnyBlock
from pytuin_desktop.models.dependency import DependencySpec


class AtrbWriter:
    """Writer for serializing AtrbDocument models back to .atrb files."""

    @staticmethod
    def write_file(document: AtrbDocument, filepath: str | Path) -> None:
        """Write an AtrbDocument to an .atrb file."""
        filepath = Path(filepath)
        content = AtrbWriter.to_string(document)

        with filepath.open("w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def to_string(document: AtrbDocument) -> str:
        """Convert an AtrbDocument to YAML string."""
        data = AtrbWriter._serialize_document(document)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    @staticmethod
    def _serialize_document(document: AtrbDocument) -> dict[str, Any]:
        """Serialize document to dict with proper field names."""
        return {
            "id": str(document.id),
            "name": document.name,
            "version": document.version,
            "content": [AtrbWriter._serialize_block(block) for block in document.content],
        }

    @staticmethod
    def _serialize_block(block: AnyBlock) -> dict[str, Any]:
        """
        Serialize a block to dict using by_alias for camelCase field names.
        Handles special serialization for DependencySpec and converts all UUIDs to strings.
        """
        # Use mode='json' to get JSON-serializable types (converts UUID to str automatically)
        block_dict = block.model_dump(by_alias=True, exclude_none=True, mode="json")

        # Handle DependencySpec serialization in props
        if "props" in block_dict and isinstance(block_dict["props"], dict):
            props = block_dict["props"]
            if "dependency" in props:
                # If dependency is a dict, convert to DependencySpec and serialize
                if isinstance(props["dependency"], dict):
                    dep_spec = DependencySpec(**props["dependency"])
                    props["dependency"] = dep_spec.to_json_string()

        # Recursively serialize children (no need to convert UUIDs, mode='json' handles it)
        if "children" in block_dict and block_dict["children"]:
            block_dict["children"] = [
                AtrbWriter._serialize_block(child) for child in block.children
            ]

        return block_dict
