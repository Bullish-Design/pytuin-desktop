# path: pytuin_desktop/block_props.py
"""Pydantic models for block-specific properties (v4 Phase 2).
- Introduces typed props for known block types.
- Uses enums from enums.py and Pydantic v2 models/aliases.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from .enums import TextAlignment, ColorToken


class BaseProps(BaseModel):
    """Common properties for text-like blocks."""
    text_color: ColorToken = ColorToken.default
    background_color: ColorToken = ColorToken.default
    text_alignment: TextAlignment = TextAlignment.left


class HeadingProps(BaseProps):
    """Properties for heading blocks."""
    level: Literal[1, 2, 3, 4, 5, 6] = 1
    is_toggleable: bool = Field(default=False, alias="isToggleable")


class ParagraphProps(BaseProps):
    """Properties for paragraph blocks (inherits BaseProps)."""
    pass


class ScriptProps(BaseModel):
    """Properties for script blocks."""
    name: str
    code: str
    interpreter: str = "bash"
    output_variable: str = Field(default="", alias="outputVariable")
    output_visible: bool = Field(default=True, alias="outputVisible")
    # Optional dependency string (JSON-object-as-string pattern used by templates)
    dependency: str = "{}"


class EditorProps(BaseModel):
    """Properties for editor blocks."""
    name: str
    code: str
    language: str = "python"
    variable_name: str = Field(default="", alias="variableName")
    sync_variable: bool = Field(default=False, alias="syncVariable")


class TerminalProps(BaseModel):
    """Properties for terminal/run blocks."""
    name: str
    code: str
    type: str = "bash"  # bash, ssh, etc.
    pty: str = ""
    global_: bool = Field(default=False, alias="global")
    output_visible: bool = Field(default=True, alias="outputVisible")
    dependency: str = "{}"


class EnvironmentProps(BaseModel):
    name: str
    value: str


class VariableProps(BaseModel):
    name: str
    value: str


class LocalVariableProps(BaseModel):
    name: str


class DirectoryProps(BaseModel):
    path: str


class HorizontalRuleProps(BaseModel):
    """Empty props for horizontal rule blocks."""
    pass
