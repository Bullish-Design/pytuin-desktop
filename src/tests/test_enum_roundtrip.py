# path: src/tests/test_enum_roundtrip.py
from pytuin_desktop import DocumentEditor, BlockBuilder, AtrbParser
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_enum_roundtrip_through_editor(tmp_path):
    ed = DocumentEditor.create("Enum Test")
    para = BlockBuilder.paragraph(text="Test", text_alignment=TextAlignment.center, text_color=ColorToken.primary)
    ed.add_block(para)
    path = tmp_path / "enum_test.atrb"
    ed.save(path)
    doc = AtrbParser.parse_file(path)
    
    block = doc.content[0]
    print(f"\nDocument content after roundtrip: {doc}\n")
    print(f"\nBlock props after roundtrip: {block.props}\n")
    assert block.props["text_alignment"] == TextAlignment.center
    assert block.props["text_color"] == ColorToken.primary
