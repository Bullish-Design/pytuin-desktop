# path: pytuin_desktop/models.py
"""Pydantic models (v4 Phase 2 - typed blocks).
Adds type-specific block models and a discriminated union `Block`.
"""
from __future__ import annotations
from typing import Any, Literal, Annotated
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .enums import TextAlignment, ColorToken
from .block_props import (
    HeadingProps, ParagraphProps, ScriptProps, EditorProps,
    TerminalProps, EnvironmentProps, VariableProps, DirectoryProps,
    HorizontalRuleProps
)


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


# ----- Typed block models -----

class HeadingBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["heading"] = "heading"
    props: HeadingProps = Field(default_factory=HeadingProps)
    content: list[dict[str, Any]] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class ParagraphBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["paragraph"] = "paragraph"
    props: ParagraphProps = Field(default_factory=ParagraphProps)
    content: list[dict[str, Any]] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class ScriptBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["script"] = "script"
    props: ScriptProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class EditorBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["editor"] = "editor"
    props: EditorProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class TerminalBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["run"] = "run"
    props: TerminalProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class EnvironmentBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["env"] = "env"
    props: EnvironmentProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class VariableBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["var"] = "var"
    props: VariableProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class DirectoryBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["directory"] = "directory"
    props: DirectoryProps
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class HorizontalRuleBlock(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    type: Literal["horizontal_rule"] = "horizontal_rule"
    props: HorizontalRuleProps = Field(default_factory=HorizontalRuleProps)
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


# Discriminated union. Unknown types can still be represented by BaseBlock.
Block = Annotated[    HeadingBlock | ParagraphBlock | ScriptBlock | EditorBlock | TerminalBlock |     EnvironmentBlock | VariableBlock | DirectoryBlock | HorizontalRuleBlock | BaseBlock,    Field(discriminator="type")]


class AtrbDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: UUID
    name: str
    version: int
    content: list[Block] = Field(default_factory=list)
