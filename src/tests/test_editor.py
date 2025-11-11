"""Step 11: DocumentEditor tests."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pytuin_desktop import DocumentEditor, load_atrb_templates, AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"
TEMPLATE_DIR = Path(__file__).parent.parent.parent / ".templateer"

def test_create_editor():
    editor = DocumentEditor.create("Test Document")
    assert editor.name == "Test Document"
    assert editor.version == 1
    assert isinstance(editor.blocks, list)
    assert len(editor.blocks) == 0


def test_editor_add_block_and_render():
    templates = load_atrb_templates(TEMPLATE_DIR)
    editor = DocumentEditor.create("Add Block Test")

    text = templates.TextContentTemplate(text="Hello via editor", styles=templates.TextStylesTemplate())
    para = templates.ParagraphBlockTemplate(block_id=str(uuid4()), content=[text])

    editor.add_block(para)

    rendered = editor.render()
    assert "Add Block Test" in rendered
    assert "paragraph" in rendered


def test_editor_save_and_parse(tmp_path):
    templates = load_atrb_templates(TEMPLATE_DIR)
    editor = DocumentEditor.create("Save Test")

    text = templates.TextContentTemplate(text="Saved via editor", styles=templates.TextStylesTemplate())
    para = templates.ParagraphBlockTemplate(block_id=str(uuid4()), content=[text])
    editor.add_block(para)

    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    out = TEST_OUTPUT_DIR / "20_editor_test.atrb"
    editor.save(out)

    assert out.exists()
    doc = AtrbParser.parse_file(out)
    assert doc.name == "Save Test"
    assert len(doc.content) == 1


def test_remove_block_at():
    templates = load_atrb_templates(TEMPLATE_DIR)
    editor = DocumentEditor.create("Remove Test")

    para1 = templates.ParagraphBlockTemplate(block_id=str(uuid4()), content=[])
    para2 = templates.ParagraphBlockTemplate(block_id=str(uuid4()), content=[])

    editor.add_block(para1).add_block(para2)
    assert len(editor.blocks) == 2

    editor.remove_block_at(0)
    assert len(editor.blocks) == 1
