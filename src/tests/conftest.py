# tests/conftest.py
from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from pytuin_desktop.models import AtrbDocument, ParagraphBlock, HeadingBlock
from pytuin_desktop.models.content import TextContent
from pytuin_desktop.models.props import TextProps, HeadingProps


@pytest.fixture
def sample_atrb_file():
    """Path to the Block_Spec.atrb sample file."""
    return Path(__file__).parent.parent / "Block_Spec.atrb"


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def simple_document():
    """Create a simple test document."""
    return AtrbDocument(
        id=uuid4(),
        name="Test Document",
        version=1,
        content=[
            HeadingBlock(
                id=uuid4(),
                props=HeadingProps(level=1),
                content=[TextContent(text="Title")],
            ),
            ParagraphBlock(
                id=uuid4(),
                props=TextProps(),
                content=[TextContent(text="Content")],
            ),
        ],
    )


@pytest.fixture
def sample_yaml():
    """Sample YAML content for testing."""
    return """id: 019a609e-dfe1-7330-8398-81906ac3b0f1
name: Test
version: 1
content:
- id: f6596d68-4414-48f3-b502-eb54c9a00b17
  type: heading
  props:
    textColor: default
    backgroundColor: default
    textAlignment: left
    level: 1
    isToggleable: false
  content:
  - type: text
    text: Test Heading
    styles:
      bold: false
      italic: false
      underline: false
      strikethrough: false
      code: false
  children: []
"""
