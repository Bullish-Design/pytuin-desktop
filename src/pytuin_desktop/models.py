"""Minimal Pydantic models for parsing .atrb files (Step 8)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseBlock(BaseModel):
    """Minimal block model for parsing a single block from a .atrb document."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: UUID
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class AtrbDocument(BaseModel):
    """Minimal document model representing a parsed .atrb file."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    version: int
    content: list[BaseBlock] = Field(default_factory=list)
