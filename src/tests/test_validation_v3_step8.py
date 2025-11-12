import io
import uuid
import pytest

from pytuin_desktop import AtrbParser, AtrbValidator
from pytuin_desktop.errors import AtrbSchemaError, AtrbValidationError
from pytuin_desktop.models import BaseBlock, AtrbDocument
from pytuin_desktop.enums import TextAlignment, ColorToken


def _mk_block(block_id=None, **props):
    return {
        "id": str(block_id or uuid.uuid4()),
        "type": "paragraph",
        "props": props,
        "content": ["hello"],
        "children": [],
    }


def test_parser_rejects_missing_required_header_keys():
    data = {
        # "id": str(uuid.uuid4()),   # id missing
        "name": "Untitled",
        "version": 1,
        "content": [],
    }
    with pytest.raises(AtrbSchemaError):
        AtrbParser.parse_dict(data, validate=True)


def test_parser_rejects_version_less_than_one():
    data = {
        "id": str(uuid.uuid4()),
        "name": "Doc",
        "version": 0,
        "content": [],
    }
    with pytest.raises(AtrbValidationError):
        AtrbParser.parse_dict(data, validate=True)


def test_validator_rejects_duplicate_block_ids():
    bid = uuid.uuid4()
    doc = AtrbDocument(
        id=uuid.uuid4(),
        name="Dup Blocks",
        version=1,
        content=[
            BaseBlock.model_validate(_mk_block(block_id=bid)),
            BaseBlock.model_validate(_mk_block(block_id=bid)),
        ],
    )
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)


def test_validator_rejects_heading_level_out_of_range():
    # Build document manually to hit semantic rule: level 7 invalid
    block = BaseBlock.model_validate({
        "id": str(uuid.uuid4()),
        "type": "heading",
        "props": {"level": 7},
        "content": ["oops"],
        "children": [],
    })
    doc = AtrbDocument(
        id=uuid.uuid4(),
        name="Bad Heading",
        version=1,
        content=[block],
    )
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)


def test_parser_coerces_enum_strings_then_validates_ok():
    yaml_text = f"""
    id: {uuid.uuid4()}
    name: Colors & Align
    version: 1
    content:
      - id: {uuid.uuid4()}
        type: paragraph
        props:
          text_alignment: "left"
          color: "primary"
        content: ["hi"]
        children: []
    """
    fh = io.StringIO(yaml_text)
    doc = AtrbParser.parse_stream(fh, validate=True)
    # ensure coercion produced enum instances
    props = doc.content[0].props
    assert isinstance(props.get("text_alignment"), TextAlignment)
    assert isinstance(props.get("color"), ColorToken)


def test_parser_rejects_invalid_enum_string():
    yaml_text = f"""
    id: {uuid.uuid4()}
    name: Bad Enum
    version: 1
    content:
      - id: {uuid.uuid4()}
        type: paragraph
        props:
          text_alignment: "diagonal"   # invalid
        content: ["hi"]
        children: []
    """
    fh = io.StringIO(yaml_text)
    with pytest.raises(AtrbValidationError):
        AtrbParser.parse_stream(fh, validate=True)


def test_validator_rejects_string_enum_if_bypassing_parser():
    # If someone constructs BaseBlock with a raw string, validator should refuse
    blk = BaseBlock.model_validate({
        "id": str(uuid.uuid4()),
        "type": "paragraph",
        "props": {"text_alignment": "left"},  # string instead of enum instance
        "content": ["hi"],
        "children": [],
    })
    doc = AtrbDocument(
        id=uuid.uuid4(),
        name="Direct Model",
        version=1,
        content=[blk],
    )
    with pytest.raises(AtrbValidationError):
        AtrbValidator.validate(doc)
