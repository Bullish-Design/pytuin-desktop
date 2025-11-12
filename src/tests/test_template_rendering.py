# path: src/tests/test_template_rendering.py
import pytest
from uuid import uuid4
from templateer import TemplateModel
from pytuin_desktop.editor import DocumentEditor

def test_render_template_to_dict_success():
    ed = DocumentEditor.create("Test")
    class MockTemplate(TemplateModel):
        __template__ = """
id: {{ block_id }}
type: paragraph
props: {}
content: []
children: []
"""
        block_id: str
    t = MockTemplate(block_id=str(uuid4()))
    d = ed._render_template_to_dict(t)
    assert isinstance(d, dict) and d["type"] == "paragraph"

def test_render_template_missing_required_fields_raises():
    ed = DocumentEditor.create("Test")
    class BadTemplate(TemplateModel):
        __template__ = "some: data"
        some: str
    with pytest.raises(ValueError):
        ed._render_template_to_dict(BadTemplate(some="x"))
