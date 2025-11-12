# path: tests/test_validator_v4.py
import pytest
from uuid import uuid4
from pytuin_desktop import AtrbValidator, AtrbDocument, HeadingBlock, HeadingProps, ScriptBlock, ScriptProps
from pytuin_desktop.errors import AtrbValidationError

def test_accepts_valid_document():
    doc = AtrbDocument(id=uuid4(), name="ok", version=1, content=[HeadingBlock(id=uuid4(), props=HeadingProps(level=1))])
    AtrbValidator.validate(doc)

def test_rejects_bad_heading_level():
    doc = AtrbDocument(id=uuid4(), name="bad", version=1, content=[HeadingBlock(id=uuid4(), props=HeadingProps(level=1))])
    doc.content[0].props.level = 9  # type: ignore[attr-defined]
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)

def test_rejects_empty_script_fields():
    doc = AtrbDocument(id=uuid4(), name="bad", version=1, content=[ScriptBlock(id=uuid4(), props=ScriptProps(name="", code=""))])
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)
