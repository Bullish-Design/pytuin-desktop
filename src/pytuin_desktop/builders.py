"""Convenience builders for common block templates."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Union
from uuid import uuid4

from .discovery import load_atrb_templates
from .enums import TextAlignment, ColorToken

PathLike = Union[str, Path]

class BlockBuilder:
    
    def _normalize_enum_value(value, enum_cls):
        """Accept either an enum instance or a string (case-insensitive).
        Returns the canonical string value or raises ValueError.
        """
        if value is None:
            return None
        if isinstance(value, enum_cls):
            return value.value
        if isinstance(value, str):
            val = value.strip().lower()
            try:
                return enum_cls(val).value  # type: ignore[arg-type]
            except Exception:
                # Try member-name style (e.g., 'LEFT')
                try:
                    return enum_cls[val].value  # type: ignore[index]
                except Exception as e:
                    raise ValueError(f"Invalid {enum_cls.__name__}: {value!r}") from e
        raise ValueError(f"Invalid {enum_cls.__name__} type: {type(value).__name__}")    
    """Factory methods returning Templateer-based block templates.

    These helpers hide the boilerplate of composing TextStylesTemplate and
    TextContentTemplate, and they assign fresh UUIDs to blocks by default.
    """

    @classmethod
    def _get_templates(cls, template_dir: Optional[PathLike] = None):
        return load_atrb_templates(template_dir)

    # ---- Paragraph ----------------------------------------------------
    @classmethod
    def paragraph(
        cls,
        text: str = "",
        *,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        code: bool = False,
        text_color: ColorToken | str = ColorToken.default,
        background_color: ColorToken | str = ColorToken.default,
        text_alignment: TextAlignment | str = TextAlignment.left,
        template_dir: Optional[PathLike] = None,
    ):
        """Create a paragraph block with optional inline styles.

        Returns a ParagraphBlockTemplate instance.
        """
        T = cls._get_templates(template_dir)

        content = []
        if text:
            styles = T.TextStylesTemplate(
                bold=bold,
                italic=italic,
                underline=underline,
                strikethrough=strikethrough,
                code=code,
            )
            content = [T.TextContentTemplate(text=text, styles=styles)]

        return T.ParagraphBlockTemplate(
            block_id=str(uuid4()),
            text_color=cls._normalize_enum_value(text_color, ColorToken),
            background_color=cls._normalize_enum_value(background_color, ColorToken),
            text_alignment=cls._normalize_enum_value(text_alignment, TextAlignment),
            content=content,
        )

    # ---- Heading ------------------------------------------------------
    @classmethod
    def heading(
        cls,
        text: str,
        *,
        level: Literal[1, 2, 3, 4, 5, 6] = 1,
        is_toggleable: bool = False,
        text_color: ColorToken | str = ColorToken.default,
        background_color: ColorToken | str = ColorToken.default,
        text_alignment: TextAlignment | str = TextAlignment.left,
        template_dir: Optional[PathLike] = None,
    ):
        """Create a heading block with a single text child."""
        T = cls._get_templates(template_dir)
        styles = T.TextStylesTemplate()
        text_content = T.TextContentTemplate(text=text, styles=styles)
        return T.HeadingBlockTemplate(
            block_id=str(uuid4()),
            level=level,
            is_toggleable=is_toggleable,
            text_color=cls._normalize_enum_value(text_color, ColorToken),
            background_color=cls._normalize_enum_value(background_color, ColorToken),
            text_alignment=cls._normalize_enum_value(text_alignment, TextAlignment),
            content=[text_content],
        )

    # ---- Horizontal rule ----------------------------------------------
    @classmethod
    def horizontal_rule(cls, *, template_dir: Optional[PathLike] = None):
        """Create a horizontal rule block."""
        T = cls._get_templates(template_dir)
        return T.HorizontalRuleTemplate(block_id=str(uuid4()))

    # ---- Script -------------------------------------------------------
    @classmethod
    def script(
        cls,
        name: str,
        code: str,
        *,
        interpreter: str = "bash",
        output_variable: str = "",
        output_visible: bool = True,
        dependency: str | None = None,
        template_dir: Optional[PathLike] = None,
    ):
        """Create a script block."""
        T = cls._get_templates(template_dir)
        kwargs = dict(
            block_id=str(uuid4()),
            name=name,
            code=code,
            interpreter=interpreter,
            output_variable=output_variable,
            output_visible=output_visible,
        )
        if dependency is not None:
            kwargs["dependency"] = dependency
        return T.ScriptBlockTemplate(**kwargs)
