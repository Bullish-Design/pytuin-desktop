# tests/test_v1_empty_document.py
"""Test v1: Generate empty .atrb documents."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys


from templateer import discover_templates  # from the installed package

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
# print(f"Discovering templates in: {TEMPLATES_DIR}")

templates = discover_templates(TEMPLATES_DIR)
EmptyDocumentTemplate = templates.EmptyDocumentTemplate  # class reference


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_empty_document():
    """Generate an empty .atrb document."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    template = EmptyDocumentTemplate(
        document_id=str(uuid4()),
        name="Empty Test Document",
        version=1
    )
    
    output_path = TEST_OUTPUT_DIR / "00_empty.atrb"
    template.write_to(output_path)
    
    # Verify file exists
    assert output_path.exists()
    
    # Verify valid YAML
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["name"] == "Empty Test Document"
    assert data["version"] == 1
    assert data["content"] == []
    assert "id" in data


def test_empty_document_structure():
    """Verify empty document has required fields."""
    template = EmptyDocumentTemplate(
        document_id=str(uuid4()),
        name="Test",
        version=1
    )
    
    rendered = template.render()
    data = yaml.safe_load(rendered)
    
    # Required fields per .atrb spec
    required_fields = ["id", "name", "version", "content"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_empty_document_default_version():
    """Test version defaults to 1."""
    template = EmptyDocumentTemplate(
        document_id=str(uuid4()),
        name="Test"
    )
    
    data = yaml.safe_load(template.render())
    assert data["version"] == 1