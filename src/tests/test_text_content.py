# tests/test_text_content.py
"""Test text content template."""
from __future__ import annotations

import yaml
from pathlib import Path
import sys

# sys.path.insert(0, str(Path(__file__).parent.parent))


from templateer import discover_templates  # from the installed package

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
# print(f"Discovering templates in: {TEMPLATES_DIR}")

templates = discover_templates(TEMPLATES_DIR)

TextStylesTemplate = templates.TextStylesTemplate  # class reference
TextContentTemplate = templates.TextContentTemplate  # class reference

# from templateer.content import TextContentTemplate, TextStylesTemplate


def test_text_content_basic():
    """Test TextContentTemplate renders correctly."""
    styles = TextStylesTemplate()
    content = TextContentTemplate(
        text="Hello world",
        styles=styles
    )
    
    rendered = content.render()
    data = yaml.safe_load(rendered)
    
    assert data["type"] == "text"
    assert data["text"] == "Hello world"
    assert "styles" in data


def test_text_content_nested_styles():
    """Test that styles nest correctly via __str__."""
    styles = TextStylesTemplate(bold=True, italic=True)
    content = TextContentTemplate(
        text="Bold and italic",
        styles=styles
    )
    
    rendered = content.render()
    data = yaml.safe_load(rendered)
    
    # Nested template should render inline
    assert data["styles"]["bold"] is True
    assert data["styles"]["italic"] is True


def test_text_content_special_characters():
    """Test text with special characters is properly escaped."""
    styles = TextStylesTemplate()
    content = TextContentTemplate(
        text='Text with "quotes" and\nnewlines',
        styles=styles
    )
    
    rendered = content.render()
    data = yaml.safe_load(rendered)
    
    # Should handle escaping via tojson filter
    assert '"quotes"' in data["text"]
    assert '\n' in data["text"]