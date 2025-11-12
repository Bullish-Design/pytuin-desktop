# path: src/tests/test_models_enum_coercion.py
from uuid import uuid4
import pytest
from pytuin_desktop.models import BaseBlock
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_baseblock_coerces_string_to_text_alignment():
    block = BaseBlock(id=uuid4(), type="paragraph", props={"text_alignment": "center"})
    assert block.props["text_alignment"] == TextAlignment.center

def test_baseblock_accepts_enum_instances():
    block = BaseBlock(id=uuid4(), type="paragraph", props={"text_color": ColorToken.primary})
    assert block.props["text_color"] == ColorToken.primary

def test_baseblock_coercion_case_insensitive():
    block = BaseBlock(id=uuid4(), type="heading", props={"textAlign": "CENTER"})
    assert block.props["textAlign"] == TextAlignment.center

def test_baseblock_invalid_enum_raises_helpful_error():
    with pytest.raises(ValueError) as exc_info:
        BaseBlock(id=uuid4(), type="paragraph", props={"text_color": "invalid"})
    assert "Invalid ColorToken value" in str(exc_info.value)

def test_baseblock_wrong_type_for_enum_raises():
    with pytest.raises(ValueError) as exc_info:
        BaseBlock(id=uuid4(), type="paragraph", props={"text_alignment": 123})
    assert "must be a string or TextAlignment" in str(exc_info.value)
