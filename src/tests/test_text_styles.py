# tests/test_text_styles.py
"""Test text styles template."""
from __future__ import annotations

import yaml
from pathlib import Path


from templateer import discover_templates  # from the installed package

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
# print(f"Discovering templates in: {TEMPLATES_DIR}")

templates = discover_templates(TEMPLATES_DIR)
TextStylesTemplate = templates.TextStylesTemplate  # class reference


def test_text_styles_default():
    """Test TextStylesTemplate renders with defaults."""
    template = TextStylesTemplate()
    rendered = template.render()
    
    # Should be valid YAML
    data = yaml.safe_load(rendered)
    
    assert data["bold"] is False
    assert data["italic"] is False
    assert data["underline"] is False
    assert data["strikethrough"] is False
    assert data["code"] is False


def test_text_styles_custom():
    """Test TextStylesTemplate with custom values."""
    template = TextStylesTemplate(bold=True, italic=True)
    rendered = template.render()
    
    data = yaml.safe_load(rendered)
    
    assert data["bold"] is True
    assert data["italic"] is True
    assert data["underline"] is False


def test_text_styles_all_enabled():
    """Test all styles enabled."""
    template = TextStylesTemplate(
        bold=True,
        italic=True,
        underline=True,
        strikethrough=True,
        code=True
    )
    rendered = template.render()
    data = yaml.safe_load(rendered)
    
    assert all(data.values())