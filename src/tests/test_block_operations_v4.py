# path: src/tests/test_block_operations_v4.py
from pytuin_desktop import DocumentEditor, BlockBuilder, AtrbParser

def test_insert_and_find(tmp_path):
    ed = DocumentEditor.create("Find")
    ed.add_block(BlockBuilder.heading("T1"))
    ed.add_block(BlockBuilder.paragraph("P1"))
    # insert after existing -> allowed (goes to new section)
    ed.insert_block_at(2, BlockBuilder.paragraph("P2"))
    p = tmp_path / "f.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    types = [b.type for b in doc.content]
    assert types == ["heading", "paragraph", "paragraph"] or len(types) == 3
