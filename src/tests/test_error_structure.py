# path: src/tests/test_error_structure.py
from pytuin_desktop.errors import AtrbError

def test_atrb_error_has_message_suggestion_context():
    e = AtrbError("Problem", suggestion="Try this", context={"a": 1})
    s = str(e)
    assert e.message == "Problem"
    assert e.suggestion == "Try this"
    assert e.context == {"a": 1}
    assert "Suggestion:" in s and "Context:" in s
