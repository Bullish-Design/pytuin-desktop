# path: src/tests/test_services_v4.py
from io import StringIO
from uuid import uuid4, UUID

from pytuin_desktop import DocumentEditor, AtrbParser
from pytuin_desktop.services import DocumentLoader, DocumentSerializer
from pytuin_desktop.enums import ColorToken

def test_document_loader_from_file(tmp_path):
    ed = DocumentEditor.create("Test")
    ed.add_block(ed._templates.ParagraphBlockTemplate(block_id=str(uuid4())))
    fp = tmp_path / "doc.atrb"
    ed.save(fp)

    loader = DocumentLoader()
    doc = loader.load_from_file(fp)
    assert doc.name == "Test"
    assert len(doc.content) == 1

def test_document_serializer_helpers_and_yaml_roundtrip():
    s = DocumentSerializer()

    # newline normalization
    assert s.ensure_single_trailing_newline("") == "\n"
    assert s.ensure_single_trailing_newline("x") == "x\n"
    assert s.ensure_single_trailing_newline("x\n\n") == "x\n"

    # to_jsonable primitives
    data = {"uuid": UUID(int=123), "color": ColorToken.success}
    j = s.to_jsonable(data)
    assert j == {"uuid": str(UUID(int=123)), "color": "success"}

    # yaml dump
    text = s.dumps_yaml({"a": 1, "b": [2,3]})
    assert isinstance(text, str) and "a:" in text and "- 2" in text

    # stream dump
    buf = StringIO()
    s.dump_yaml({"x": True}, buf, sort_keys=False)
    assert "x: true" in buf.getvalue()
