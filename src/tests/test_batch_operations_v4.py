# path: src/tests/test_batch_operations_v4.py
from pytuin_desktop import DocumentEditor, BlockBuilder, AtrbParser

def test_add_replace_remove_batches(tmp_path):
    ed = DocumentEditor.create("Batch")
    ed.add_blocks([BlockBuilder.paragraph(f"P{i}") for i in range(5)])
    assert ed.block_count() == 5
    ed.replace_blocks({1: BlockBuilder.heading("H1"), 3: BlockBuilder.heading("H3")})
    ed.remove_blocks_at([0, 4])
    p = tmp_path / "batch.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    assert [b.type for b in doc.content] == ["heading", "paragraph", "heading"]
