# tests/test_paragraph_block.py
"""Test paragraph block template."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys


from templateer import discover_templates  # from the installed package

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
# print(f"Discovering templates in: {TEMPLATES_DIR}")

templates = discover_templates(TEMPLATES_DIR)

TextStylesTemplate = templates.TextStylesTemplate  # class reference
TextContentTemplate = templates.TextContentTemplate  # class reference
ParagraphBlockTemplate = templates.ParagraphBlockTemplate  # class reference



def test_paragraph_block_structure():
    """Test paragraph block renders valid structure."""
    content = TextContentTemplate(
        text="Test paragraph",
        styles=TextStylesTemplate()
    )
    
    block = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[content]
    )
    
    rendered = block.render()
    data = yaml.safe_load(rendered)
    
    # Verify structure
    assert data["type"] == "paragraph"
    assert "id" in data
    assert "props" in data
    assert data["props"]["textColor"] == "default"
    assert "content" in data
    assert len(data["content"]) == 1
    assert "children" in data


def test_paragraph_empty_content():
    """Test paragraph with no content."""
    block = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[]
    )
    
    rendered = block.render()
    data = yaml.safe_load(rendered)
    
    assert len(data["content"]) == 0


def test_paragraph_multiple_content():
    """Test paragraph with multiple text items."""
    contents = [
        TextContentTemplate(
            text="Bold text ",
            styles=TextStylesTemplate(bold=True)
        ),
        TextContentTemplate(
            text="normal text",
            styles=TextStylesTemplate()
        )
    ]
    
    block = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=contents
    )
    
    rendered = block.render()
    data = yaml.safe_load(rendered)
    
    assert len(data["content"]) == 2
    assert data["content"][0]["text"] == "Bold text "
    assert data["content"][0]["styles"]["bold"] is True
    assert data["content"][1]["text"] == "normal text"
    assert data["content"][1]["styles"]["bold"] is False