# tests/test_v1_single_paragraph.py
"""Test v1: Document with single paragraph."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys


from templateer import discover_templates  # from the installed package

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
# print(f"Discovering templates in: {TEMPLATES_DIR}")

templates = discover_templates(TEMPLATES_DIR)
DocumentTemplate = templates.DocumentTemplate  # class reference
ParagraphBlockTemplate = templates.ParagraphBlockTemplate  # class reference
TextContentTemplate = templates.TextContentTemplate  # class reference
TextStylesTemplate = templates.TextStylesTemplate  # class reference

# from templateer.document import DocumentTemplate
# from templateer.blocks import ParagraphBlockTemplate
# from templateer.content import TextContentTemplate, TextStylesTemplate


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_single_paragraph_document():
    """Generate document with one paragraph block."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Build content
    text_content = TextContentTemplate(
        text="This is a test paragraph with some content.",
        styles=TextStylesTemplate()
    )
    
    # Build block
    para_block = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[text_content]
    )
    
    # Build document
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Single Paragraph Test",
        version=1,
        blocks=[para_block]
    )
    
    # Write file
    output_path = TEST_OUTPUT_DIR / "01_single_paragraph.atrb"
    doc.write_to(output_path)
    
    # Validate
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["name"] == "Single Paragraph Test"
    assert len(data["content"]) == 1
    assert data["content"][0]["type"] == "paragraph"
    assert data["content"][0]["content"][0]["text"] == "This is a test paragraph with some content."


def test_document_with_styled_paragraph():
    """Test document with styled text."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    text_content = TextContentTemplate(
        text="Bold paragraph text",
        styles=TextStylesTemplate(bold=True)
    )
    
    para_block = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[text_content]
    )
    
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Styled Paragraph Test",
        version=1,
        blocks=[para_block]
    )
    
    output_path = TEST_OUTPUT_DIR / "02_styled_paragraph.atrb"
    doc.write_to(output_path)
    
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["content"][0]["content"][0]["styles"]["bold"] is True