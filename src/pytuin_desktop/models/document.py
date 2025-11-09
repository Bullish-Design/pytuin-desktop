# src/pytuin_desktop/models/document.py
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from pytuin_desktop.models.blocks import AnyBlock


class AtrbDocument(BaseModel):
    """Top-level model for an .atrb document."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    version: int
    content: list[AnyBlock]
