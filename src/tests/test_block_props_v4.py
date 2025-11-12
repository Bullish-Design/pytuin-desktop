# path: tests/test_block_props_v4.py
import pytest
from pydantic import ValidationError
from pytuin_desktop import (
    HeadingProps, ParagraphProps, ScriptProps, EditorProps, TerminalProps,
    EnvironmentProps, VariableProps, DirectoryProps, HorizontalRuleProps,
    TextAlignment, ColorToken
)

def test_heading_props_alias_and_bounds():
    p = HeadingProps(level=3, isToggleable=True, text_alignment=TextAlignment.left)
    assert p.level == 3 and p.is_toggleable is True
    with pytest.raises(ValidationError):
        HeadingProps(level=0)
    with pytest.raises(ValidationError):
        HeadingProps(level=7)

def test_paragraph_defaults_and_colors():
    p = ParagraphProps()
    assert p.text_alignment == TextAlignment.left
    p2 = ParagraphProps(text_color=ColorToken.primary, background_color=ColorToken.default)
    assert p2.text_color == ColorToken.primary

def test_script_editor_terminal_aliases():
    s = ScriptProps(name="n", code="echo ok", outputVariable="X")
    assert s.output_variable == "X" and s.output_visible is True
    e = EditorProps(name="E", code="print()", variableName="v")
    assert e.variable_name == "v" and e.language == "python"
    t = TerminalProps(name="Run", code="echo", **{"global": True}, outputVisible=False)
    assert t.global_ is True and t.output_visible is False

def test_env_var_directory_and_rule():
    env = EnvironmentProps(name="FOO", value="bar")
    var = VariableProps(name="A", value="1")
    dire = DirectoryProps(path="/tmp")
    hr = HorizontalRuleProps()
    assert env.value == "bar" and var.name == "A" and dire.path and isinstance(hr, HorizontalRuleProps)
