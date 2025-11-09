# tests/test_writer.py
from __future__ import annotations

from uuid import uuid4

import pytest
import yaml

from pytuin_desktop.writer import AtrbWriter
from pytuin_desktop.models import (
    AtrbDocument,
    HeadingBlock,
    ParagraphBlock,
    HorizontalRuleBlock,
)
from pytuin_desktop.models.content import TextContent
from pytuin_desktop.models.props import HeadingProps, TextProps
from pytuin_desktop.parser import AtrbParser


class TestAtrbWriter:
    """Test suite for AtrbWriter."""

    def test_write_file(self, simple_document, temp_dir):
        """Test writing document to file."""
        output_file = temp_dir / "test.atrb"

        AtrbWriter.write_file(simple_document, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_to_string_generates_yaml(self, simple_document):
        """Test to_string generates valid YAML."""
        yaml_str = AtrbWriter.to_string(simple_document)

        parsed = yaml.safe_load(yaml_str)
        assert parsed["name"] == "Test Document"
        assert parsed["version"] == 1
        assert "content" in parsed

    def test_uuid_serialization(self, simple_document):
        """Test UUIDs serialize as strings, not objects."""
        yaml_str = AtrbWriter.to_string(simple_document)

        # Should not contain Python object markers
        assert "!!python/object:uuid.UUID" not in yaml_str

        # Should contain valid UUID strings
        parsed = yaml.safe_load(yaml_str)
        assert isinstance(parsed["id"], str)
        assert isinstance(parsed["content"][0]["id"], str)

    def test_camel_case_field_names(self, simple_document):
        """Test field names are camelCase in output."""
        yaml_str = AtrbWriter.to_string(simple_document)
        parsed = yaml.safe_load(yaml_str)

        block = parsed["content"][0]
        assert "textColor" in block["props"]
        assert "backgroundColor" in block["props"]
        assert "text_color" not in block["props"]

    def test_empty_arrays_preserved(self):
        """Test empty content/children arrays are preserved."""
        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                ParagraphBlock(
                    id=uuid4(),
                    props=TextProps(),
                    content=[],
                )
            ],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        assert parsed["content"][0]["content"] == []
        assert parsed["content"][0]["children"] == []

    def test_nested_blocks_serialization(self):
        """Test nested blocks (children) serialize correctly."""
        from pytuin_desktop.models import ToggleListItemBlock

        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                ToggleListItemBlock(
                    id=uuid4(),
                    props=TextProps(),
                    content=[TextContent(text="Toggle")],
                    children=[
                        ParagraphBlock(
                            id=uuid4(),
                            props=TextProps(),
                            content=[TextContent(text="Nested")],
                        )
                    ],
                )
            ],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        assert len(parsed["content"][0]["children"]) == 1
        assert parsed["content"][0]["children"][0]["type"] == "paragraph"

    def test_horizontal_rule_props(self):
        """Test HorizontalRuleBlock with empty props dict."""
        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[HorizontalRuleBlock(id=uuid4())],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        # Props should be empty dict
        assert parsed["content"][0]["props"] == {}

    def test_text_styles_serialization(self):
        """Test text styles serialize with all boolean fields."""
        from pytuin_desktop.models.content import TextStyles

        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                ParagraphBlock(
                    id=uuid4(),
                    props=TextProps(),
                    content=[
                        TextContent(
                            text="Bold text",
                            styles=TextStyles(bold=True, italic=False),
                        )
                    ],
                )
            ],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        styles = parsed["content"][0]["content"][0]["styles"]
        assert styles["bold"] is True
        assert styles["italic"] is False

    def test_special_characters_preserved(self):
        """Test special characters in text are preserved."""
        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                ParagraphBlock(
                    id=uuid4(),
                    props=TextProps(),
                    content=[TextContent(text="😀 Special: <>&'\"")],
                )
            ],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        assert parsed["content"][0]["content"][0]["text"] == "😀 Special: <>&'\""

    def test_roundtrip_preserves_data(self, simple_document, temp_dir):
        """Test write then parse preserves all data."""
        output_file = temp_dir / "roundtrip.atrb"

        AtrbWriter.write_file(simple_document, output_file)
        reloaded = AtrbParser.parse_file(output_file)

        assert reloaded.name == simple_document.name
        assert reloaded.version == simple_document.version
        assert len(reloaded.content) == len(simple_document.content)

    def test_dependency_string_preserved(self):
        """Test dependency fields preserved as string '{}'."""
        from pytuin_desktop.models import ScriptBlock
        from pytuin_desktop.models.props import ScriptProps

        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                ScriptBlock(
                    id=uuid4(),
                    props=ScriptProps(
                        name="Test Script",
                        code="echo test",
                        interpreter="/bin/bash",
                        outputVariable="",
                        outputVisible=True,
                        dependency="{}",
                    ),
                )
            ],
        )

        yaml_str = AtrbWriter.to_string(doc)
        parsed = yaml.safe_load(yaml_str)

        assert parsed["content"][0]["props"]["dependency"] == "{}"
