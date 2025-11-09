# src/pytuin_desktop/models/base.py
from __future__ import annotations

from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class BaseBlock(BaseModel):
    """Base model for all block types."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    children: list[BaseBlock] = Field(default_factory=list)
