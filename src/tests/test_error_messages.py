# path: src/tests/test_error_messages.py
import pytest, yaml
from uuid import uuid4
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.errors import AtrbParseError, AtrbSchemaError, AtrbValidationError
from pytuin_desktop.validator import AtrbValidator
from pytuin_desktop.models import AtrbDocument, BaseBlock

def test_schema_error_includes_context():
    data = {"id": str(uuid4()), "name": "X", "version": 1, "content": "not a list"}
    with pytest.raises(AtrbSchemaError) as exc:
        AtrbParser.parse_dict(data)
    err = exc.value
    assert isinstance(err.context, dict)
    assert "found_type" in err.context

def test_validation_error_for_duplicate_ids():
    from uuid import uuid4 as u
    bid = u()
    data = {"id": str(u()), "name": "T", "version": 1, "content": [
        {"id": str(bid), "type": "paragraph", "props": {}, "content": [], "children": []},
        {"id": str(bid), "type": "heading", "props": {}, "content": [], "children": []},
    ]}
    with pytest.raises(AtrbValidationError) as exc:
        AtrbParser.parse_dict(data)
    assert str(bid) in str(exc.value)

def test_validation_error_for_invalid_heading_level():
    from uuid import uuid4 as u
    data = {"id": str(u()), "name": "T", "version": 1, "content": [{
        "id": str(u()), "type": "heading", "props": {"level": 10}, "content": [], "children": []
    }]}
    with pytest.raises(AtrbValidationError):
        doc = AtrbParser.parse_dict(data, validate=False)
        AtrbValidator.validate(doc)
