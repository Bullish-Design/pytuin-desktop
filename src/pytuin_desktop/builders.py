"""Convenience builders for common block templates (v3 Step 1)."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Union
from uuid import uuid4

from .discovery import load_atrb_templates

PathLike = Union[str, Path]

class BlockBuilder:
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
        text_color: str = "default",
        background_color: str = "default",
        text_alignment: str = "left",
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
            text_color=text_color,
            background_color=background_color,
            text_alignment=text_alignment,
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
        text_color: str = "default",
        background_color: str = "default",
        text_alignment: str = "left",
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
            text_color=text_color,
            background_color=background_color,
            text_alignment=text_alignment,
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
