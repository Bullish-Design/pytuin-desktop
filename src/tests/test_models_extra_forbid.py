# path: src/tests/test_models_extra_forbid.py
from uuid import uuid4
import pytest
from pydantic import ValidationError
from pytuin_desktop.models import BaseBlock

def test_baseblock_rejects_extra_fields():
    with pytest.raises(ValidationError):
        BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[], unknown_field="should fail")

def test_baseblock_accepts_valid_fields():
    block = BaseBlock(id=uuid4(), type="paragraph", props={"custom_block_prop": "allowed"}, content=[{"type": "text", "text": "hello"}], children=[])
    assert block.type == "paragraph"

def test_baseblock_props_non_string_keys_rejected():
    with pytest.raises(ValueError):
        BaseBlock(id=uuid4(), type="paragraph", props={123: "value"}, content=[], children=[])
