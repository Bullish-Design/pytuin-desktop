# path: src/tests/test_discriminated_blocks.py
from uuid import uuid4
import yaml
from pytuin_desktop import AtrbParser
from pytuin_desktop.models import HeadingBlock, ParagraphBlock, BaseBlock

def test_discriminator_selects_correct_types(tmp_path):
    data = {
        "id": str(uuid4()),
        "name": "Doc",
        "version": 1,
        "content": [
            {"id": str(uuid4()), "type": "heading", "props": {"level": 2}, "content": [], "children": []},
            {"id": str(uuid4()), "type": "paragraph", "props": {}, "content": [], "children": []},
        ]
    }
    p = tmp_path / "d.atrb"
    p.write_text(yaml.safe_dump(data))
    doc = AtrbParser.parse_file_typed(p)
    assert isinstance(doc.content[0], HeadingBlock)
    assert isinstance(doc.content[1], ParagraphBlock)

def test_typed_parse_falls_back_for_unknown(tmp_path):
    data = {
        "id": str(uuid4()),
        "name": "Doc",
        "version": 1,
        "content": [{"id": str(uuid4()), "type": "whoknows", "props": {}, "content": [], "children": []}]
    }
    p = tmp_path / "u.atrb"
    p.write_text(yaml.safe_dump(data))
    # typed parse will produce BaseBlock because unknown type matches last union arm
    doc = AtrbParser.parse_file_typed(p)
    assert isinstance(doc.content[0], BaseBlock)
