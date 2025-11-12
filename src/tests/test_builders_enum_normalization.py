# path: src/tests/test_builders_enum_normalization.py
import pytest
from pytuin_desktop.builders import BlockBuilder
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_normalize_enum_to_instance_with_string():
    r = BlockBuilder._normalize_enum_to_instance("center", TextAlignment)
    assert r is TextAlignment.center

def test_normalize_enum_to_instance_with_enum():
    r = BlockBuilder._normalize_enum_to_instance(ColorToken.primary, ColorToken)
    assert r is ColorToken.primary

def test_normalize_enum_to_instance_case_insensitive():
    r = BlockBuilder._normalize_enum_to_instance("PRIMARY", ColorToken)
    assert r is ColorToken.primary

def test_normalize_enum_to_instance_with_none():
    r = BlockBuilder._normalize_enum_to_instance(None, TextAlignment)
    assert r is None

def test_normalize_enum_to_instance_invalid_raises():
    with pytest.raises(ValueError):
        BlockBuilder._normalize_enum_to_instance("invalid", ColorToken)

def test_normalize_enum_to_instance_wrong_type_raises():
    with pytest.raises(ValueError):
        BlockBuilder._normalize_enum_to_instance(123, TextAlignment)
