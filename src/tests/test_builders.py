"""Step 12: BlockBuilder tests."""
from __future__ import annotations

from pathlib import Path

from pytuin_desktop import BlockBuilder, DocumentEditor, AtrbParser

TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_build_paragraph_defaults():
    block = BlockBuilder.paragraph("Hello world", bold=True)
    assert hasattr(block, "content")
    assert block.content[0].text == "Hello world"
    assert block.content[0].styles.bold is True


def test_build_heading_levels():
    h = BlockBuilder.heading("Title", level=2)
    assert hasattr(h, "level") and h.level == 2
    assert h.content[0].text == "Title"


def test_build_horizontal_rule():
    hr = BlockBuilder.horizontal_rule()
    assert hasattr(hr, "block_id")


def test_build_script_block():
    s = BlockBuilder.script(name="demo", code="echo hi", interpreter="bash")
    assert s.name == "demo"
    assert s.interpreter == "bash"


def test_builders_in_editor_roundtrip(tmp_path):
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    editor = (
        DocumentEditor.create("Builder Roundtrip")
        .add_block(BlockBuilder.heading("Setup", level=1))
        .add_block(BlockBuilder.paragraph("This guide shows how to set up the system."))
        .add_block(BlockBuilder.horizontal_rule())
        .add_block(BlockBuilder.heading("Installation", level=2))
        .add_block(BlockBuilder.script(name="install", code="echo install", interpreter="bash"))
    )

    out = TEST_OUTPUT_DIR / "30_builder_test.atrb"
    editor.save(out)

    assert out.exists()
    doc = AtrbParser.parse_file(out)
    assert doc.name == "Builder Roundtrip"
    assert len(doc.content) == 5
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"
    assert doc.content[2].type == "horizontal_rule"
    assert doc.content[4].type == "script"
