# path: pytuin_desktop/builders.py
"""Block builders (v4 Phase 1)."""
from __future__ import annotations
from pathlib import Path
from typing import Literal, Optional, Union
from uuid import uuid4  # deprecated here
from .id_generators import generate_block_id
from .discovery import load_atrb_templates
from .enums import TextAlignment, ColorToken
PathLike = Union[str, Path]

class BlockBuilder:
    @classmethod
    def _get_templates(cls, template_dir: Optional[PathLike] = None):
        return load_atrb_templates(template_dir)

    @classmethod
    def _normalize_enum_to_instance(cls, value, enum_cls):
        if value is None: return None
        if isinstance(value, enum_cls): return value
        if isinstance(value, str):
            token = value.strip().lower()
            try:
                return enum_cls(token)
            except Exception:
                try:
                    return enum_cls[token]  # name access
                except Exception as e:
                    valid = [m.value for m in enum_cls]
                    raise ValueError(f"Invalid {enum_cls.__name__}: {value!r}. Valid values: {valid}") from e
        raise ValueError(f"Invalid {enum_cls.__name__} type: expected string or {enum_cls.__name__}, got {type(value).__name__}")

    @classmethod
    def paragraph(
        cls, text: str = "", *, bold: bool = False, italic: bool = False,
        underline: bool = False, strikethrough: bool = False, code: bool = False,
        text_color: ColorToken | str = ColorToken.default, background_color: ColorToken | str = ColorToken.default,
        text_alignment: TextAlignment | str = TextAlignment.left, template_dir: Optional[PathLike] = None,
    ):
        T = cls._get_templates(template_dir)
        content = []
        if text:
            styles = T.TextStylesTemplate(bold=bold, italic=italic, underline=underline, strikethrough=strikethrough, code=code)
            content = [T.TextContentTemplate(text=text, styles=styles)]
        return T.ParagraphBlockTemplate(
            block_id=str(generate_block_id()),
            text_color=cls._normalize_enum_to_instance(text_color, ColorToken),
            background_color=cls._normalize_enum_to_instance(background_color, ColorToken),
            text_alignment=cls._normalize_enum_to_instance(text_alignment, TextAlignment),
            content=content,
        )

    @classmethod
    def heading(
        cls, text: str, *, level: Literal[1,2,3,4,5,6] = 1, is_toggleable: bool = False,
        text_color: ColorToken | str = ColorToken.default, background_color: ColorToken | str = ColorToken.default,
        text_alignment: TextAlignment | str = TextAlignment.left, template_dir: Optional[PathLike] = None,
    ):
        T = cls._get_templates(template_dir)
        styles = T.TextStylesTemplate()
        text_content = T.TextContentTemplate(text=text, styles=styles)
        return T.HeadingBlockTemplate(
            block_id=str(generate_block_id()), level=level, is_toggleable=is_toggleable,
            text_color=cls._normalize_enum_to_instance(text_color, ColorToken),
            background_color=cls._normalize_enum_to_instance(background_color, ColorToken),
            text_alignment=cls._normalize_enum_to_instance(text_alignment, TextAlignment),
            content=[text_content],
        )

    @classmethod
    def horizontal_rule(cls, *, template_dir: Optional[PathLike] = None):
        T = cls._get_templates(template_dir)
        return T.HorizontalRuleTemplate(block_id=str(generate_block_id()))

    @classmethod
    def script(
        cls, name: str, code: str, *, interpreter: str = "bash", output_variable: str = "", output_visible: bool = True,
        dependency: str | None = None, template_dir: Optional[PathLike] = None,
    ):
        T = cls._get_templates(template_dir)
        kwargs = dict(block_id=str(generate_block_id()), name=name, code=code, interpreter=interpreter, output_variable=output_variable, output_visible=output_visible)
        if dependency is not None:
            kwargs["dependency"] = dependency
        return T.ScriptBlockTemplate(**kwargs)
