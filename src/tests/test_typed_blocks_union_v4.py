# path: tests/test_typed_blocks_union_v4.py
import pytest
from uuid import uuid4
from pydantic import ValidationError, TypeAdapter
from pytuin_desktop import (
    AtrbDocument,
    HeadingBlock, HeadingProps,
    ParagraphBlock, ParagraphProps,
    ScriptBlock, ScriptProps,
)
from pytuin_desktop.models import Block

def test_construct_typed_blocks():
    h = HeadingBlock(id=uuid4(), props=HeadingProps(level=2))
    p = ParagraphBlock(id=uuid4(), props=ParagraphProps())
    s = ScriptBlock(id=uuid4(), props=ScriptProps(name="x", code="echo"))

    doc = AtrbDocument(id=uuid4(), name="Doc", version=1, content=[h, p, s])
    assert len(doc.content) == 3 and doc.content[0].type == "heading"

def test_wrong_literal_type_rejected():
    with pytest.raises(ValidationError):
        HeadingBlock(id=uuid4(), type="paragraph", props=HeadingProps(level=1))

def test_block_union_validates_and_creates_instances():
    TA = TypeAdapter(Block)
    h = TA.validate_python({"id": str(uuid4()), "type": "heading", "props": {"level": 1}, "content": [], "children": []})
    p = TA.validate_python({"id": str(uuid4()), "type": "paragraph", "props": {}, "content": [], "children": []})
    assert isinstance(h, HeadingBlock) and isinstance(p, ParagraphBlock)
