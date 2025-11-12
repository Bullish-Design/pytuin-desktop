# path: tests/test_parser_v4.py
from uuid import uuid4
import yaml
import pytest
from pytuin_desktop import AtrbParser
from pytuin_desktop.models import HeadingBlock, ParagraphBlock, BaseBlock

DOC_BASE = lambda: {"id": str(uuid4()), "name": "X", "version": 1}

def test_parse_dict_legacy_builds_baseblocks():
    d = DOC_BASE()
    d["content"] = [{"id": str(uuid4()), "type": "paragraph", "props": {}, "content": [], "children": []}]
    doc = AtrbParser.parse_dict(d)
    assert isinstance(doc.content[0], BaseBlock)

def test_parse_dict_typed_builds_specific_models():
    d = DOC_BASE()
    d["content"] = [
        {"id": str(uuid4()), "type": "heading", "props": {"level": 2}, "content": [], "children": []},
        {"id": str(uuid4()), "type": "paragraph", "props": {}, "content": [], "children": []},
    ]
    doc = AtrbParser.parse_dict_typed(d)
    assert isinstance(doc.content[0], HeadingBlock) and isinstance(doc.content[1], ParagraphBlock)

def test_typed_parse_unknown_type_falls_back_to_baseblock():
    d = DOC_BASE()
    d["content"] = [{"id": str(uuid4()), "type": "mystery", "props": {}, "content": [], "children": []}]
    doc = AtrbParser.parse_dict_typed(d)
    assert isinstance(doc.content[0], BaseBlock)

def test_parse_file_and_stream(tmp_path):
    d = DOC_BASE()
    d["content"] = [{"id": str(uuid4()), "type": "paragraph", "props": {}, "content": [], "children": []}]
    fp = tmp_path / "x.atrb"
    fp.write_text(yaml.safe_dump(d), encoding="utf-8")
    doc = AtrbParser.parse_file(fp)
    doc2 = AtrbParser.parse_file_typed(fp)
    assert doc.name == doc2.name == "X"
