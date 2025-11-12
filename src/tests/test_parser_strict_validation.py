# path: src/tests/test_parser_strict_validation.py
import yaml, pytest
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.errors import AtrbValidationError

def test_parser_rejects_blocks_with_unknown_fields():
    yaml_content = """
id: 12345678-1234-5678-1234-567812345678
name: Test
version: 1
content:
  - id: 87654321-4321-8765-4321-876543218765
    type: paragraph
    props: {}
    content: []
    children: []
    unknown_field: value
"""
    output = AtrbParser.parse_dict(yaml.safe_load(yaml_content))
    print(f"\nParsed document: {output}\n")
    with pytest.raises(AtrbValidationError):
        AtrbParser.parse_dict(yaml.safe_load(yaml_content))

def test_parser_accepts_valid_blocks():
    yaml_content = """
id: 12345678-1234-5678-1234-567812345678
name: Test
version: 1
content:
  - id: 87654321-4321-8765-4321-876543218765
    type: paragraph
    props:
      text_alignment: left
      custom_block_prop: allowed
    content:
      - type: text
        text: Hello
    children: []
"""
    doc = AtrbParser.parse_dict(yaml.safe_load(yaml_content))
    assert len(doc.content) == 1
    assert doc.content[0].props["custom_block_prop"] == "allowed"
