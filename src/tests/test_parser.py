# tests/test_parser.py
from __future__ import annotations

import json
from pathlib import Path
from pytuin_desktop import AtrbParser
from pytuin_desktop.models import HeadingBlock, ParagraphBlock, EditorBlock


block_spec = "/home/andrew/Documents/Projects/pytuin-desktop/src/tests/Block_Spec.atrb"


def test_parse_block_spec():
    """Test parsing the Block_Spec.atrb file."""
    test_file = Path(block_spec)

    doc = AtrbParser.parse_file(test_file)

    # print(f"\nParsed Document: \n{doc.model_dump_json(indent=2)}\n")
    assert doc.name == "Block_Spec"
    assert doc.version == 1
    assert len(doc.content) > 0

    first_block = doc.content[0]
    assert isinstance(first_block, HeadingBlock)
    assert first_block.props.level == 1
    assert first_block.content[0].text == "Block_Spec"


def test_block_types():
    """Test that different block types are parsed correctly."""
    test_file = Path(block_spec)
    doc = AtrbParser.parse_file(test_file)

    block_types = {type(block).__name__ for block in doc.content}

    expected_types = {
        "HeadingBlock",
        "ParagraphBlock",
        "EditorBlock",
        "ScriptBlock",
        "RunBlock",
        "HorizontalRuleBlock",
    }

    assert expected_types.issubset(block_types)


def test_nested_blocks():
    """Test that nested blocks (toggles) are parsed correctly."""
    test_file = Path(block_spec)
    doc = AtrbParser.parse_file(test_file)

    toggle_blocks = [
        b for b in doc.content if type(b).__name__ == "ToggleListItemBlock"
    ]
    assert len(toggle_blocks) > 0

    first_toggle = toggle_blocks[0]
    assert len(first_toggle.children) > 0


def test_editor_block():
    """Test that editor blocks preserve their properties."""
    test_file = Path(block_spec)
    doc = AtrbParser.parse_file(test_file)

    editor_blocks = [b for b in doc.content if isinstance(b, EditorBlock)]
    assert len(editor_blocks) > 0

    editor = editor_blocks[0]
    assert editor.props.name == "Editor 1"
    assert editor.props.code == "Editor Content"
    assert editor.props.language == "python"


def test_empty_paragraph():
    """Test that empty paragraphs are handled correctly."""
    test_file = Path(block_spec)
    doc = AtrbParser.parse_file(test_file)

    empty_paragraphs = [
        b for b in doc.content if isinstance(b, ParagraphBlock) and len(b.content) == 0
    ]
    assert len(empty_paragraphs) > 0


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
