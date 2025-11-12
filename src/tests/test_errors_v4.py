# path: tests/test_errors_v4.py
from pytuin_desktop.errors import AtrbError

def test_error_shape_and_str():
    e = AtrbError("Oops", suggestion="Try again", context={"x": 1})
    s = str(e)
    assert e.message == "Oops" and "Suggestion:" in s and "Context:" in s
