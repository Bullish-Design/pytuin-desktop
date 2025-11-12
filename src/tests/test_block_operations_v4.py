# path: src/tests/test_block_operations_v4.py
from uuid import uuid4
from pytuin_desktop import DocumentEditor, BlockBuilder, AtrbParser

def test_editor_add_move_replace(tmp_path):
    ed = DocumentEditor.create("Ops")
    ed.add_block(BlockBuilder.paragraph("First"))
    ed.add_block(BlockBuilder.paragraph("Second"))
    ed.add_block(BlockBuilder.paragraph("Third"))
    ed.move_block(0, 2)
    ed.replace_block_at(1, BlockBuilder.heading("Middle"))
    p = tmp_path / "ops.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    assert len(doc.content) == 3
    assert doc.content[1].type == "heading"

def test_editor_find_by_type_and_id(tmp_path):
    ed = DocumentEditor.create("Find")
    ed.add_block(BlockBuilder.heading("Title"))
    ed.add_block(BlockBuilder.paragraph("Body"))
    p = tmp_path / "find.atrb"
    ed.save(p)

    ed2 = DocumentEditor.from_file_with_blocks(p)
    heads = ed2.find_blocks_by_type("heading")
    assert len(heads) == 1 and heads[0][1].type == "heading"

    # locate id from parsed doc
    doc = AtrbParser.parse_file(p)
    bid = doc.content[0].id
    res = ed2.find_block_by_id(bid)
    assert res and res[0] == 0 and res[1].id == bid
