# src/pytuin_desktop/models/content.py
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class TextStyles(BaseModel):
    """Styles applied to text content."""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    code: bool = False


class TextContent(BaseModel):
    """Inline text content within a block."""

    type: Literal["text"] = "text"
    text: str
    styles: TextStyles = Field(default_factory=TextStyles)


class RunbookLinkProps(BaseModel):
    """Properties for runbook link content."""

    model_config = ConfigDict(populate_by_name=True)

    runbook_id: UUID = Field(alias="runbookId")
    block_id: UUID | None = Field(alias="blockId", default=None)


class RunbookLinkContent(BaseModel):
    """Link to another runbook or specific block within a runbook."""

    type: Literal["runbook-link"] = "runbook-link"
    props: RunbookLinkProps
    text: str = ""


InlineContent = TextContent | RunbookLinkContent


class TableCell(BaseModel):
    """A cell within a table."""

    type: Literal["tableCell"] = "tableCell"
    content: list[TextContent]
    props: dict[str, Any]


class TableRow(BaseModel):
    """A row within a table."""

    cells: list[TableCell]


class TableContent(BaseModel):
    """Content structure for table blocks."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["tableContent"] = "tableContent"
    column_widths: list[int | None] = Field(alias="columnWidths")
    rows: list[TableRow]
