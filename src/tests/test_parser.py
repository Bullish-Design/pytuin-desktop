# tests/test_parser.py
from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.models import (
    HeadingBlock,
    ParagraphBlock,
    EditorBlock,
    ScriptBlock,
    ToggleListItemBlock,
)


class TestAtrbParser:
    """Test suite for AtrbParser."""

    def test_parse_file_basic(self, sample_atrb_file):
        """Test parsing a basic .atrb file."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        assert doc.name == "Block_Spec"
        assert doc.version == 1
        assert isinstance(doc.id, UUID)
        assert len(doc.content) > 0

    def test_parse_string(self, sample_yaml):
        """Test parsing from YAML string."""
        doc = AtrbParser.parse_string(sample_yaml)

        assert doc.name == "Test"
        assert doc.version == 1
        assert len(doc.content) == 1
        assert doc.content[0].type == "heading"

    def test_parse_invalid_file(self, temp_dir):
        """Test parsing invalid file raises appropriate error."""
        invalid_file = temp_dir / "invalid.atrb"
        invalid_file.write_text("not: valid: yaml::")

        with pytest.raises(Exception):
            AtrbParser.parse_file(invalid_file)

    def test_parse_missing_file(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            AtrbParser.parse_file("/nonexistent/file.atrb")

    def test_block_types_parsed_correctly(self, sample_atrb_file):
        """Test different block types are parsed with correct types."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        block_types = {block.type for block in doc.content}

        expected_types = {
            "heading",
            "paragraph",
            "horizontal_rule",
            "editor",
            "script",
            "run",
        }
        assert expected_types.issubset(block_types)

    def test_heading_block_properties(self, sample_atrb_file):
        """Test heading block parsed with correct properties."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        headings = [b for b in doc.content if isinstance(b, HeadingBlock)]
        assert len(headings) > 0

        heading = headings[0]
        assert hasattr(heading.props, "level")
        assert 1 <= heading.props.level <= 6
        assert hasattr(heading.props, "is_toggleable")

    def test_editor_block_properties(self, sample_atrb_file):
        """Test editor block parsed with correct properties."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        editors = [b for b in doc.content if isinstance(b, EditorBlock)]
        assert len(editors) > 0

        editor = editors[0]
        assert hasattr(editor.props, "name")
        assert hasattr(editor.props, "code")
        assert hasattr(editor.props, "language")

    def test_nested_blocks_parsed(self, sample_atrb_file):
        """Test nested blocks (toggles with children) parsed correctly."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        toggles = [b for b in doc.content if isinstance(b, ToggleListItemBlock)]
        assert len(toggles) > 0

        # Find a toggle with children
        toggle_with_children = next((t for t in toggles if len(t.children) > 0), None)
        assert toggle_with_children is not None
        assert len(toggle_with_children.children) > 0

    def test_empty_content_arrays(self, sample_atrb_file):
        """Test blocks with empty content arrays are parsed correctly."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        # Empty paragraphs exist in the spec
        empty_paragraphs = [
            b for b in doc.content if isinstance(b, ParagraphBlock) and len(b.content) == 0
        ]
        assert len(empty_paragraphs) > 0

    def test_uuid_format(self, sample_atrb_file):
        """Test UUIDs are parsed correctly."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        assert isinstance(doc.id, UUID)
        for block in doc.content:
            assert isinstance(block.id, UUID)

    def test_text_content_with_styles(self, sample_atrb_file):
        """Test text content and styles are parsed."""
        doc = AtrbParser.parse_file(sample_atrb_file)

        paragraphs = [
            b for b in doc.content if isinstance(b, ParagraphBlock) and len(b.content) > 0
        ]
        assert len(paragraphs) > 0

        para = paragraphs[0]
        text_content = para.content[0]
        assert hasattr(text_content, "text")
        assert hasattr(text_content, "styles")

    def test_discriminated_union_validation(self, temp_dir):
        """Test that invalid block types are caught by discriminated union."""
        invalid_yaml = """id: 019a609e-dfe1-7330-8398-81906ac3b0f1
name: Test
version: 1
content:
- id: f6596d68-4414-48f3-b502-eb54c9a00b17
  type: invalid_block_type
  props: {}
  content: []
  children: []
"""
        invalid_file = temp_dir / "invalid.atrb"
        invalid_file.write_text(invalid_yaml)

        with pytest.raises(Exception):
            AtrbParser.parse_file(invalid_file)
