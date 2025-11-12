# path: src/tests/test_typed_blocks.py
import pytest
from uuid import uuid4
from pydantic import ValidationError, TypeAdapter
from pytuin_desktop import (
    HeadingBlock, HeadingProps, ParagraphBlock, ParagraphProps, ScriptBlock, ScriptProps,
    AtrbDocument
)

def test_heading_block_construction():
    b = HeadingBlock(id=uuid4(), props=HeadingProps(level=2))
    assert b.type == "heading"
    assert b.props.level == 2

def test_heading_block_wrong_type_rejected():
    with pytest.raises(ValidationError):
        HeadingBlock(id=uuid4(), type="paragraph", props=HeadingProps(level=1))

def test_script_block_requires_code():
    with pytest.raises(ValidationError):
        ScriptBlock(id=uuid4(), props=ScriptProps(name="x", code=""))

def test_document_mixed_types():
    doc = AtrbDocument(
        id=uuid4(), name="Mixed", version=1,
        content=[
            HeadingBlock(id=uuid4(), props=HeadingProps(level=1)),
            ParagraphBlock(id=uuid4(), props=ParagraphProps())
        ]
    )
    assert len(doc.content) == 2
