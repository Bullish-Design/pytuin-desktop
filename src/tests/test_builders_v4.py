# path: tests/test_builders_v4.py
from pytuin_desktop import BlockBuilder, DocumentEditor, AtrbParser
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_builders_construct_and_roundtrip(tmp_path):
    ed = DocumentEditor.create("Builders")
    ed.add_block(BlockBuilder.heading("Title", level=2))
    ed.add_block(BlockBuilder.paragraph("Hello", text_alignment=TextAlignment.center, text_color=ColorToken.primary))
    ed.add_block(BlockBuilder.horizontal_rule())
    ed.add_block(BlockBuilder.script(name="demo", code="echo hi", interpreter="bash"))
    fp = tmp_path / "b.atrb"
    ed.save(fp)
    doc = AtrbParser.parse_file(fp)
    assert len(doc.content) == 4
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"
