# path: src/tests/test_batch_operations_v4.py
from pytuin_desktop import DocumentEditor, BlockBuilder

def test_add_replace_remove_batches():
    ed = DocumentEditor.create("Batch")
    ed.add_blocks([BlockBuilder.paragraph(f"p{i}") for i in range(5)])
    assert ed.block_count() == 5

    ed.replace_blocks({0: BlockBuilder.heading("H"), 2: BlockBuilder.paragraph("np")})
    assert ed.block_count() == 5  # replace in-place

    ed.remove_blocks_at([1,3])
    assert ed.block_count() == 3
