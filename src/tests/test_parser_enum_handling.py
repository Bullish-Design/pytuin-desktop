# path: src/tests/test_parser_enum_handling.py
from uuid import uuid4
import yaml
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_parser_delegates_enum_coercion_to_model():
    yaml_content = f"""
id: {uuid4()}
name: Test
version: 1
content:
  - id: {uuid4()}
    type: paragraph
    props:
      text_alignment: left
    content: []
    children: []
"""
    doc = AtrbParser.parse_dict(yaml.safe_load(yaml_content))
    assert doc.content[0].props["text_alignment"] == TextAlignment.left

def test_parser_preserves_enum_instances():
    data = {
        "id": str(uuid4()),
        "name": "Test",
        "version": 1,
        "content": [{
            "id": str(uuid4()),
            "type": "paragraph",
            "props": {"text_color": ColorToken.accent},
            "content": [],
            "children": []
        }]
    }
    doc = AtrbParser.parse_dict(data)
    assert doc.content[0].props["text_color"] == ColorToken.accent
