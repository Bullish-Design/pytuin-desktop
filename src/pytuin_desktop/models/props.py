# src/pytuin_desktop/models/props.py
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class TextProps(BaseModel):
    """Props for text-based blocks."""

    model_config = ConfigDict(populate_by_name=True)

    text_color: str = Field(alias="textColor", default="default")
    background_color: str = Field(alias="backgroundColor", default="default")
    text_alignment: Literal["left", "center", "right"] = Field(
        alias="textAlignment", default="left"
    )


class HeadingProps(TextProps):
    """Props for heading blocks."""

    level: Literal[1, 2, 3, 4, 5, 6]
    is_toggleable: bool = Field(alias="isToggleable", default=False)


class EditorProps(BaseModel):
    """Props for editor blocks."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    code: str
    language: str
    variable_name: str = Field(alias="variableName")
    sync_variable: bool = Field(alias="syncVariable", default=False)


class ScriptProps(BaseModel):
    """Props for script execution blocks."""

    model_config = ConfigDict(populate_by_name=True)

    interpreter: str
    output_variable: str = Field(alias="outputVariable", default="")
    name: str
    code: str
    output_visible: bool = Field(alias="outputVisible", default=True)
    dependency: str


class RunProps(BaseModel):
    """Props for terminal/run blocks."""

    model_config = ConfigDict(populate_by_name=True)

    type: str
    name: str
    code: str
    pty: str
    global_: bool = Field(alias="global", default=False)
    output_visible: bool = Field(alias="outputVisible", default=True)
    dependency: str


class EnvProps(BaseModel):
    """Props for environment variable blocks."""

    name: str
    value: str


class VarProps(BaseModel):
    """Props for variable blocks."""

    name: str
    value: str


class LocalVarProps(BaseModel):
    """Props for local variable blocks."""

    name: str


class VarDisplayProps(BaseModel):
    """Props for variable display blocks."""

    name: str


class DirectoryProps(BaseModel):
    """Props for directory blocks."""

    path: str


class DropdownProps(BaseModel):
    """Props for dropdown blocks."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    options: str
    fixed_options: str = Field(alias="fixedOptions")
    variable_options: str = Field(alias="variableOptions")
    command_options: str = Field(alias="commandOptions")
    value: str
    options_type: Literal["fixed", "variable", "command"] = Field(alias="optionsType")
    interpreter: str


class SQLiteProps(BaseModel):
    """Props for SQLite query blocks."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    query: str
    uri: str
    auto_refresh: int = Field(alias="autoRefresh", default=0)
    dependency: str


class PostgresProps(BaseModel):
    """Props for PostgreSQL query blocks."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    query: str
    uri: str
    auto_refresh: int = Field(alias="autoRefresh", default=0)
    dependency: str


class HttpProps(BaseModel):
    """Props for HTTP request blocks."""

    name: str
    url: str
    verb: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
    body: str
    headers: str
    dependency: str


class CheckListProps(TextProps):
    """Props for checklist item blocks."""

    checked: bool


class MediaProps(TextProps):
    """Props for media blocks (image, video, audio)."""

    name: str
    url: str
    caption: str
    show_preview: bool = Field(alias="showPreview", default=True)


class FileProps(BaseModel):
    """Props for file attachment blocks."""

    model_config = ConfigDict(populate_by_name=True)

    background_color: str = Field(alias="backgroundColor", default="default")
    name: str
    url: str
    caption: str


class CodeBlockProps(BaseModel):
    """Props for code block."""

    language: str


class TableProps(BaseModel):
    """Props for table blocks."""

    model_config = ConfigDict(populate_by_name=True)

    text_color: str = Field(alias="textColor", default="default")
