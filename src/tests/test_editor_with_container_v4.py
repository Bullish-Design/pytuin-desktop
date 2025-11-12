# path: src/tests/test_editor_with_container_v4.py
from uuid import uuid4
from pytuin_desktop import DocumentEditor, BlockBuilder, AtrbParser

def test_editor_block_count_and_get(tmp_path):
    ed = DocumentEditor.create("Test")
    para = BlockBuilder.paragraph("hello")
    ed.add_block(para)
    assert ed.block_count() == 1
    assert ed.get_block(0) is not None
    p = tmp_path / "e.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    assert len(doc.content) == 1

def test_editor_preserves_existing_then_new(tmp_path):
    ed1 = DocumentEditor.create("Doc")
    ed1.add_block(BlockBuilder.heading("Title"))
    p = tmp_path / "d.atrb"
    ed1.save(p)

    ed2 = DocumentEditor.from_file_with_blocks(p)
    ed2.add_block(BlockBuilder.paragraph("Body"))
    ed2.save(p)

    doc = AtrbParser.parse_file(p)
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"

def test_editor_move_and_replace(tmp_path):
    ed = DocumentEditor.create("Ops")
    ed.add_block(BlockBuilder.paragraph("A"))
    ed.add_block(BlockBuilder.paragraph("B"))
    ed.add_block(BlockBuilder.paragraph("C"))
    ed.move_block(1, 2)  # B after C
    ed.replace_block_at(0, BlockBuilder.heading("H"))
    p = tmp_path / "ops.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    # first should now be heading
    assert doc.content[0].type == "heading"
