# path: pytuin_desktop/models.py
"""Pydantic models (v4 Phase 1)."""
from __future__ import annotations
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .enums import TextAlignment, ColorToken

class BaseBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    id: UUID
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)

    @field_validator("props", mode="before")
    @classmethod
    def _coerce_enum_props(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(v, dict):
            return v
        enum_fields = {
            "text_alignment": TextAlignment,
            "textAlign": TextAlignment,
            "text_color": ColorToken,
            "background_color": ColorToken,
            "color": ColorToken,
        }
        out = dict(v)
        for key, enum_cls in enum_fields.items():
            if key in out and out[key] is not None:
                val = out[key]
                if isinstance(val, enum_cls):
                    continue
                if isinstance(val, str):
                    try:
                        out[key] = enum_cls(val.strip().lower())
                    except Exception as e:
                        raise ValueError(f"Invalid {enum_cls.__name__} value for '{key}': {val!r}") from e
                else:
                    raise ValueError(f"Property '{key}' must be a string or {enum_cls.__name__}, got {type(val).__name__}")
        return out

    @field_validator("props")
    @classmethod
    def _validate_props_dict(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("'props' must be a dictionary")
        for k in v.keys():
            if not isinstance(k, str):
                raise ValueError("'props' keys must be strings")
        return v

class AtrbDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    name: str
    version: int
    content: list[BaseBlock] = Field(default_factory=list)
