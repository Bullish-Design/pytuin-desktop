# path: tests/conftest.py
import os
import pytest

@pytest.fixture(autouse=True)
def _restore_env():
    old = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)
