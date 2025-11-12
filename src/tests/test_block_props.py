# path: src/tests/test_block_props.py
import pytest
from uuid import uuid4
from pydantic import ValidationError
from pytuin_desktop import (
    HeadingProps, ParagraphProps, ScriptProps, EditorProps, TerminalProps,
    EnvironmentProps, VariableProps, DirectoryProps,
    TextAlignment, ColorToken,
)

def test_heading_props_valid_level_and_alias():
    props = HeadingProps(level=3, isToggleable=True)
    assert props.level == 3
    assert props.is_toggleable is True

def test_heading_props_invalid_level_raises():
    with pytest.raises(ValidationError):
        HeadingProps(level=0)
    with pytest.raises(ValidationError):
        HeadingProps(level=7)

def test_paragraph_props_defaults_and_inheritance():
    props = ParagraphProps()
    assert props.text_alignment == TextAlignment.left
    props2 = ParagraphProps(text_color=ColorToken.primary)
    assert props2.text_color == ColorToken.primary

def test_script_props_defaults_and_aliases():
    props = ScriptProps(name="Test", code="echo hi", outputVariable="res")
    assert props.interpreter == "bash"
    assert props.output_variable == "res"
    assert props.output_visible is True

def test_editor_props_defaults():
    props = EditorProps(name="Ed", code="print('x')")
    assert props.language == "python"
    assert props.sync_variable is False

def test_terminal_props_alias_and_defaults():
    props = TerminalProps(name="Run", code="echo", outputVisible=False, **{"global": True})
    assert props.output_visible is False
    assert props.global_ is True

def test_env_and_var_props_required_fields():
    with pytest.raises(ValidationError):
        EnvironmentProps(name="FOO")
    e = EnvironmentProps(name="FOO", value="bar")
    assert e.value == "bar"
    v = VariableProps(name="X", value="1")
    assert v.name == "X"

def test_directory_props():
    d = DirectoryProps(path="/tmp")
    assert d.path == "/tmp"
