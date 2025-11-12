# path: src/tests/test_template_types_roundtrip.py
from pytuin_desktop import DocumentEditor, AtrbParser, BlockBuilder

def test_paragraph_template_roundtrip(tmp_path):
    ed = DocumentEditor.create("Test")
    ed.add_block(BlockBuilder.paragraph("Hello world", bold=True))
    fp = tmp_path / "t.atrb"
    ed.save(fp)
    doc = AtrbParser.parse_file(fp)
    assert len(doc.content) == 1
    assert doc.content[0].type == "paragraph"

def test_heading_template_roundtrip(tmp_path):
    ed = DocumentEditor.create("Test")
    ed.add_block(BlockBuilder.heading("Title", level=2))
    fp = tmp_path / "t2.atrb"
    ed.save(fp)
    doc = AtrbParser.parse_file(fp)
    assert doc.content[0].type == "heading"
    assert doc.content[0].props["level"] == 2
