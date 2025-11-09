# src/pytuin_desktop/models/blocks.py
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from pytuin_desktop.models.base import BaseBlock
from pytuin_desktop.models.content import InlineContent, TableContent
from pytuin_desktop.models.props import (
    CheckListProps,
    CodeBlockProps,
    DirectoryProps,
    DropdownProps,
    EditorProps,
    EnvProps,
    FileProps,
    HeadingProps,
    HttpProps,
    LocalVarProps,
    MediaProps,
    PostgresProps,
    RunProps,
    ScriptProps,
    SQLiteProps,
    TableProps,
    TextProps,
    VarDisplayProps,
    VarProps,
)


class ParagraphBlock(BaseBlock):
    """Paragraph block containing inline content."""

    type: Literal["paragraph"] = "paragraph"
    props: TextProps
    content: list[InlineContent] = Field(default_factory=list)


class HeadingBlock(BaseBlock):
    """Heading block."""

    type: Literal["heading"] = "heading"
    props: HeadingProps
    content: list[InlineContent]


class HorizontalRuleBlock(BaseBlock):
    """Horizontal rule divider."""

    type: Literal["horizontal_rule"] = "horizontal_rule"
    props: dict[str, Any] = Field(default_factory=dict)


class EditorBlock(BaseBlock):
    """Code editor block."""

    type: Literal["editor"] = "editor"
    props: EditorProps


class ScriptBlock(BaseBlock):
    """Script execution block."""

    type: Literal["script"] = "script"
    props: ScriptProps


class RunBlock(BaseBlock):
    """Terminal/bash run block."""

    type: Literal["run"] = "run"
    props: RunProps


class EnvBlock(BaseBlock):
    """Environment variable block."""

    type: Literal["env"] = "env"
    props: EnvProps


class VarBlock(BaseBlock):
    """Variable block."""

    type: Literal["var"] = "var"
    props: VarProps


class LocalVarBlock(BaseBlock):
    """Local variable block."""

    type: Literal["local-var"] = "local-var"
    props: LocalVarProps


class VarDisplayBlock(BaseBlock):
    """Variable display block."""

    type: Literal["var_display"] = "var_display"
    props: VarDisplayProps


class DirectoryBlock(BaseBlock):
    """Directory listing block."""

    type: Literal["directory"] = "directory"
    props: DirectoryProps


class LocalDirectoryBlock(BaseBlock):
    """Local directory block."""

    model_config = ConfigDict(populate_by_name=True)
    type: Literal["local-directory"] = "local-directory"
    # props: dict[str, Any] = Field(default_factory=dict)
    props: DirectoryProps = Field(default_factory=DirectoryProps)


class DropdownBlock(BaseBlock):
    """Dropdown selection block."""

    type: Literal["dropdown"] = "dropdown"
    props: DropdownProps


class SQLiteBlock(BaseBlock):
    """SQLite query block."""

    type: Literal["sqlite"] = "sqlite"
    props: SQLiteProps


class PostgresBlock(BaseBlock):
    """PostgreSQL query block."""

    type: Literal["postgres"] = "postgres"
    props: PostgresProps


class HttpBlock(BaseBlock):
    """HTTP request block."""

    type: Literal["http"] = "http"
    props: HttpProps


class QuoteBlock(BaseBlock):
    """Quote block."""

    type: Literal["quote"] = "quote"
    props: TextProps
    content: list[InlineContent]


class ToggleListItemBlock(BaseBlock):
    """Toggle list item with collapsible children."""

    type: Literal["toggleListItem"] = "toggleListItem"
    props: TextProps
    content: list[InlineContent]
    children: list[AnyBlock] = Field(default_factory=list)


class NumberedListItemBlock(BaseBlock):
    """Numbered list item."""

    type: Literal["numberedListItem"] = "numberedListItem"
    props: TextProps
    content: list[InlineContent]


class BulletListItemBlock(BaseBlock):
    """Bullet list item."""

    type: Literal["bulletListItem"] = "bulletListItem"
    props: TextProps
    content: list[InlineContent]


class CheckListItemBlock(BaseBlock):
    """Checklist item with checked state."""

    type: Literal["checkListItem"] = "checkListItem"
    props: CheckListProps
    content: list[InlineContent]


class CodeBlockBlock(BaseBlock):
    """Code block with syntax highlighting."""

    type: Literal["codeBlock"] = "codeBlock"
    props: CodeBlockProps
    content: list[InlineContent]


class TableBlock(BaseBlock):
    """Table block."""

    type: Literal["table"] = "table"
    props: TableProps
    content: TableContent


class ImageBlock(BaseBlock):
    """Image block."""

    type: Literal["image"] = "image"
    props: MediaProps


class VideoBlock(BaseBlock):
    """Video block."""

    type: Literal["video"] = "video"
    props: MediaProps


class AudioBlock(BaseBlock):
    """Audio block."""

    type: Literal["audio"] = "audio"
    props: MediaProps


class FileBlock(BaseBlock):
    """File attachment block."""

    type: Literal["file"] = "file"
    props: FileProps


AnyBlock = (
    ParagraphBlock
    | HeadingBlock
    | HorizontalRuleBlock
    | EditorBlock
    | ScriptBlock
    | RunBlock
    | EnvBlock
    | VarBlock
    | LocalVarBlock
    | VarDisplayBlock
    | DirectoryBlock
    | LocalDirectoryBlock
    | DropdownBlock
    | SQLiteBlock
    | PostgresBlock
    | HttpBlock
    | QuoteBlock
    | ToggleListItemBlock
    | NumberedListItemBlock
    | BulletListItemBlock
    | CheckListItemBlock
    | CodeBlockBlock
    | TableBlock
    | ImageBlock
    | VideoBlock
    | AudioBlock
    | FileBlock
)


# Update forward references for recursive types
ToggleListItemBlock.model_rebuild()
