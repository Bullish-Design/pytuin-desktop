# path: tests/test_models_enum_coercion_v4.py
from uuid import uuid4
import pytest
from pytuin_desktop.models import BaseBlock
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_string_to_enum_coercion():
    b = BaseBlock(id=uuid4(), type="paragraph", props={"text_alignment": "center"})
    assert b.props["text_alignment"] == TextAlignment.center

def test_case_insensitive_and_alias_key():
    b = BaseBlock(id=uuid4(), type="heading", props={"textAlign": "RIGHT"})
    assert b.props["textAlign"] == TextAlignment.right

def test_accepts_enum_instances():
    b = BaseBlock(id=uuid4(), type="paragraph", props={"text_color": ColorToken.accent})
    assert b.props["text_color"] == ColorToken.accent

def test_invalid_value_raises():
    with pytest.raises(ValueError) as ei:
        BaseBlock(id=uuid4(), type="paragraph", props={"text_color": "nope"})
    assert "Invalid ColorToken" in str(ei.value)

def test_wrong_type_raises():
    with pytest.raises(ValueError) as ei:
        BaseBlock(id=uuid4(), type="paragraph", props={"text_alignment": 123})
    assert "must be a string or TextAlignment" in str(ei.value)
