# .templateer/content.py
"""Content templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel


TEXT_STYLES_TEMPLATE = """bold: {{ bold|lower }}
italic: {{ italic|lower }}
underline: {{ underline|lower }}
strikethrough: {{ strikethrough|lower }}
code: {{ code|lower }}"""


class TextStylesTemplate(TemplateModel):
    """Template for text styles in .atrb format."""
    
    __template__ = TEXT_STYLES_TEMPLATE
    
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    code: bool = False
    

TEXT_CONTENT_TEMPLATE = """type: text
text: {{ text|tojson }}
styles:
{{ styles|indent(2, true) }}"""


class TextContentTemplate(TemplateModel):
    """Template for inline text content with styles."""
    
    __template__ = TEXT_CONTENT_TEMPLATE
    
    text: str
    styles: TextStylesTemplate