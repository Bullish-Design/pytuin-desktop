# path: src/tests/test_typed_validation.py
import pytest
from uuid import uuid4
from pytuin_desktop import AtrbValidator, AtrbDocument, HeadingBlock, HeadingProps, ScriptBlock, ScriptProps
from pytuin_desktop.errors import AtrbValidationError

def test_validator_accepts_valid_typed_doc():
    doc = AtrbDocument(
        id=uuid4(), name="OK", version=1,
        content=[HeadingBlock(id=uuid4(), props=HeadingProps(level=2))]
    )
    AtrbValidator.validate(doc)  # should not raise

def test_validator_catches_heading_level_violation():
    doc = AtrbDocument(
        id=uuid4(), name="Bad", version=1,
        content=[HeadingBlock(id=uuid4(), props=HeadingProps(level=2))]
    )
    # Manually mutate to invalid for semantic check
    doc.content[0].props.level = 9  # type: ignore[attr-defined]
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)

def test_validator_catches_script_empty_fields():
    doc = AtrbDocument(
        id=uuid4(), name="Bad", version=1,
        content=[ScriptBlock(id=uuid4(), props=ScriptProps(name="", code=""))]
    )
    with pytest.raises(AtrbValidationError) as ei:
        AtrbValidator.validate(doc)
    assert "non-empty" in str(ei.value).lower()
