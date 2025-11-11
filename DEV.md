# Pytuin Desktop Development Guide (Templateer-Integrated)

This guide builds Pytuin Desktop using **Templateer as the core templating engine**. All .atrb generation happens through Templateer templates in `.templateer/`. Testing generates complete, valid `.atrb` files in versioned directories.

---

## Prerequisites

- Python 3.11+
- UV package manager
- pytest and pytest-cov
- Git

---

## Architecture

Pytuin Desktop layers on top of Templateer:

```
┌─────────────────────────────────┐
│  Pytuin Desktop                 │
│  - DocumentEditor               │
│  - BlockBuilder                 │
│  - Parser (validation)          │
└─────────────────────────────────┘
              ↓ uses
┌─────────────────────────────────┐
│  Templates (.templateer/)       │
│  - Document templates           │
│  - Block templates              │
│  - Content templates            │
└─────────────────────────────────┘
              ↓ powered by
┌─────────────────────────────────┐
│  Templateer Library             │
│  - TemplateModel                │
│  - discover_templates()         │
│  - Jinja2 rendering             │
└─────────────────────────────────┘
```

---

## Step 1: Project Setup with Templateer

### Development Tasks

1. **Initialize structure:**
```bash
mkdir pytuin-desktop
cd pytuin-desktop
mkdir -p src/pytuin_desktop .templateer tests/v1
touch README.md
```

2. **Create `pyproject.toml`:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pytuin-desktop"
version = "0.1.0"
description = "Python library for Atuin Desktop .atrb files"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "templateer>=0.3.1",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --cov=src/pytuin_desktop --cov-report=term-missing"
```

3. **Create package structure:**
```python
# src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library built on Templateer."""

__version__ = "0.1.0"
```

```python
# .templateer/__init__.py
"""Templates for .atrb file generation."""
```

### Testing Tasks

1. **Install dependencies:**
```bash
uv pip install -e ".[dev]"
```

2. **Verify Templateer is available:**
```bash
python -c "from templateer import TemplateModel; print('Templateer imported successfully')"
```

3. **Verify project imports:**
```bash
python -c "import pytuin_desktop; print(pytuin_desktop.__version__)"
```

**Success Criteria:**
- Templateer installed and importable
- Package structure created
- All imports work

---

## Step 2: First Template - Text Styles

### Development Tasks

1. **Create content templates:**
```python
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
```

### Testing Tasks

1. **Create template test:**
```python
# tests/test_text_styles.py
"""Test text styles template."""
from __future__ import annotations

import yaml
from pathlib import Path

# Import from .templateer - add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.content import TextStylesTemplate


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
```

2. **Run tests:**
```bash
pytest tests/test_text_styles.py -v
```

**Success Criteria:**
- Template renders valid YAML
- Defaults work correctly
- Custom values work
- All tests pass

---

## Step 3: Text Content Template (Nested Composition)

### Development Tasks

1. **Add TextContentTemplate:**
```python
# .templateer/content.py (add to existing file)

TEXT_CONTENT_TEMPLATE = """type: text
text: {{ text|tojson }}
styles:
{{ styles|indent(2, true) }}"""


class TextContentTemplate(TemplateModel):
    """Template for inline text content with styles."""
    
    __template__ = TEXT_CONTENT_TEMPLATE
    
    text: str
    styles: TextStylesTemplate
```

### Testing Tasks

1. **Test nested composition:**
```python
# tests/test_text_content.py
"""Test text content template."""
from __future__ import annotations

import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.content import TextContentTemplate, TextStylesTemplate


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
```

2. **Run tests:**
```bash
pytest tests/test_text_content.py -v
```

**Success Criteria:**
- Nested template composition works (styles inside content)
- Special characters handled via `tojson` filter
- All tests pass

---

## Step 4: Empty Document Template

### Development Tasks

1. **Create document templates:**
```python
# .templateer/document.py
"""Document templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel


EMPTY_DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
name: "{{ name }}"
version: {{ version }}
content: []
"""


class EmptyDocumentTemplate(TemplateModel):
    """Template for an empty .atrb document."""
    
    __template__ = EMPTY_DOCUMENT_TEMPLATE
    
    document_id: str
    name: str
    version: int = 1
```

### Testing Tasks

1. **Generate first .atrb file:**
```python
# tests/test_v1_empty_document.py
"""Test v1: Generate empty .atrb documents."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.document import EmptyDocumentTemplate


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
```

2. **Run test:**
```bash
pytest tests/test_v1_empty_document.py -v
```

3. **Verify generated file:**
```bash
cat tests/v1/00_empty.atrb
```

**Success Criteria:**
- `tests/v1/00_empty.atrb` created
- File is valid YAML
- Has all required fields
- All tests pass

---

## Step 5: Paragraph Block Template

### Development Tasks

1. **Create block templates:**
```python
# .templateer/blocks.py
"""Block templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel
from templateer.content import TextContentTemplate


PARAGRAPH_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: paragraph
props:
  textColor: {{ text_color }}
  backgroundColor: {{ background_color }}
  textAlignment: {{ text_alignment }}
content:
{% for item in content %}
  - {{ item|indent(4, true) }}
{% endfor %}
children: []"""


class ParagraphBlockTemplate(TemplateModel):
    """Template for paragraph blocks."""
    
    __template__ = PARAGRAPH_BLOCK_TEMPLATE
    
    block_id: str
    text_color: str = "default"
    background_color: str = "default"
    text_alignment: str = "left"
    content: list[TextContentTemplate] = []
```

### Testing Tasks

1. **Test paragraph block structure:**
```python
# tests/test_paragraph_block.py
"""Test paragraph block template."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.blocks import ParagraphBlockTemplate
from templateer.content import TextContentTemplate, TextStylesTemplate


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
```

2. **Run tests:**
```bash
pytest tests/test_paragraph_block.py -v
```

**Success Criteria:**
- Paragraph block template works
- Multiple content items handled
- All tests pass

---

## Step 6: Document with Blocks Template

### Development Tasks

1. **Add DocumentTemplate:**
```python
# .templateer/document.py (add to existing)

DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
name: "{{ name }}"
version: {{ version }}
content:
{% for block in blocks %}
  - {{ block|indent(4, true) }}
{% endfor %}
"""


class DocumentTemplate(TemplateModel):
    """Template for a complete .atrb document with blocks."""
    
    __template__ = DOCUMENT_TEMPLATE
    
    document_id: str
    name: str
    version: int = 1
    blocks: list[TemplateModel] = []
```

### Testing Tasks

1. **Generate document with paragraph:**
```python
# tests/test_v1_single_paragraph.py
"""Test v1: Document with single paragraph."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.document import DocumentTemplate
from templateer.blocks import ParagraphBlockTemplate
from templateer.content import TextContentTemplate, TextStylesTemplate


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
```

2. **Run tests:**
```bash
pytest tests/test_v1_single_paragraph.py -v
```

3. **Verify files:**
```bash
ls -la tests/v1/
cat tests/v1/01_single_paragraph.atrb
```

**Success Criteria:**
- Document with paragraph block generates correctly
- Nested composition works (document → block → content → styles)
- Multiple .atrb files in v1 directory
- All tests pass

---

## Step 7: Additional Block Types (Heading, Script)

### Development Tasks

1. **Add more block templates:**
```python
# .templateer/blocks.py (add to existing)

HEADING_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: heading
props:
  level: {{ level }}
  isToggleable: {{ is_toggleable|lower }}
  textColor: {{ text_color }}
  backgroundColor: {{ background_color }}
  textAlignment: {{ text_alignment }}
content:
{% for item in content %}
  - {{ item|indent(4, true) }}
{% endfor %}
children: []"""


class HeadingBlockTemplate(TemplateModel):
    """Template for heading blocks."""
    
    __template__ = HEADING_BLOCK_TEMPLATE
    
    block_id: str
    level: int = 1
    is_toggleable: bool = False
    text_color: str = "default"
    background_color: str = "default"
    text_alignment: str = "left"
    content: list[TextContentTemplate] = []


HORIZONTAL_RULE_TEMPLATE = """id: "{{ block_id }}"
type: horizontal_rule
props: {}
children: []"""


class HorizontalRuleTemplate(TemplateModel):
    """Template for horizontal rule divider."""
    
    __template__ = HORIZONTAL_RULE_TEMPLATE
    
    block_id: str


SCRIPT_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: script
props:
  interpreter: {{ interpreter }}
  outputVariable: {{ output_variable }}
  name: {{ name }}
  code: {{ code|tojson }}
  outputVisible: {{ output_visible|lower }}
  dependency: {{ dependency|tojson }}
children: []"""


class ScriptBlockTemplate(TemplateModel):
    """Template for script execution blocks."""
    
    __template__ = SCRIPT_BLOCK_TEMPLATE
    
    block_id: str
    name: str
    code: str
    interpreter: str = "bash"
    output_variable: str = ""
    output_visible: bool = True
    dependency: str = '{"pip": [], "npm": []}'
```

### Testing Tasks

1. **Generate documents for each block type:**
```python
# tests/test_v1_block_types.py
"""Test v1: Individual block types."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.document import DocumentTemplate
from templateer.blocks import (
    HeadingBlockTemplate,
    HorizontalRuleTemplate,
    ScriptBlockTemplate
)
from templateer.content import TextContentTemplate, TextStylesTemplate


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_heading_document():
    """Generate document with heading block."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    text = TextContentTemplate(
        text="Main Heading",
        styles=TextStylesTemplate()
    )
    
    heading = HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=1,
        content=[text]
    )
    
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Heading Test",
        version=1,
        blocks=[heading]
    )
    
    output_path = TEST_OUTPUT_DIR / "03_heading.atrb"
    doc.write_to(output_path)
    
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["content"][0]["type"] == "heading"
    assert data["content"][0]["props"]["level"] == 1
    assert data["content"][0]["content"][0]["text"] == "Main Heading"


def test_generate_horizontal_rule_document():
    """Generate document with horizontal rule."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    hr = HorizontalRuleTemplate(block_id=str(uuid4()))
    
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Horizontal Rule Test",
        version=1,
        blocks=[hr]
    )
    
    output_path = TEST_OUTPUT_DIR / "04_horizontal_rule.atrb"
    doc.write_to(output_path)
    
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["content"][0]["type"] == "horizontal_rule"
    assert data["content"][0]["props"] == {}


def test_generate_script_document():
    """Generate document with script block."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="hello_script",
        code="echo 'Hello from script'",
        interpreter="bash"
    )
    
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Script Test",
        version=1,
        blocks=[script]
    )
    
    output_path = TEST_OUTPUT_DIR / "05_script.atrb"
    doc.write_to(output_path)
    
    with output_path.open() as f:
        data = yaml.safe_load(f)
    
    assert data["content"][0]["type"] == "script"
    assert data["content"][0]["props"]["name"] == "hello_script"
    assert data["content"][0]["props"]["interpreter"] == "bash"
    assert "Hello from script" in data["content"][0]["props"]["code"]


def test_heading_levels():
    """Test different heading levels."""
    for level in [1, 2, 3, 4, 5, 6]:
        text = TextContentTemplate(
            text=f"Level {level} Heading",
            styles=TextStylesTemplate()
        )
        
        heading = HeadingBlockTemplate(
            block_id=str(uuid4()),
            level=level,
            content=[text]
        )
        
        data = yaml.safe_load(heading.render())
        assert data["props"]["level"] == level
```

2. **Run tests:**
```bash
pytest tests/test_v1_block_types.py -v
```

3. **Verify all generated files:**
```bash
ls -la tests/v1/
# Should see: 00_empty.atrb, 01_single_paragraph.atrb, 02_styled_paragraph.atrb,
#             03_heading.atrb, 04_horizontal_rule.atrb, 05_script.atrb
```

**Success Criteria:**
- Multiple block types generate correctly
- Each block type has its own .atrb file
- All files are valid YAML
- All tests pass

---

## Step 8: Parser for Validation

### Development Tasks

1. **Create minimal models:**
```python
# src/pytuin_desktop/models.py
"""Minimal Pydantic models for parsing .atrb files."""
from __future__ import annotations

from uuid import UUID
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseBlock(BaseModel):
    """Minimal block model for parsing."""
    
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    
    id: UUID
    type: str
    props: dict[str, Any] = Field(default_factory=dict)
    content: list[Any] = Field(default_factory=list)
    children: list[Any] = Field(default_factory=list)


class AtrbDocument(BaseModel):
    """Minimal document model for parsing."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    id: UUID
    name: str
    version: int
    content: list[BaseBlock] = Field(default_factory=list)
```

2. **Create parser:**
```python
# src/pytuin_desktop/parser.py
"""Parser for validating .atrb files."""
from __future__ import annotations

from pathlib import Path
from uuid import UUID
from typing import Any

import yaml

from pytuin_desktop.models import AtrbDocument, BaseBlock


class AtrbParser:
    """Parse and validate .atrb files."""
    
    @staticmethod
    def parse_file(filepath: str | Path) -> AtrbDocument:
        """Parse an .atrb file into a document model."""
        filepath = Path(filepath)
        
        with filepath.open("r", encoding="utf-8") as f:
            content = f.read()
        
        return AtrbParser.parse_string(content)
    
    @staticmethod
    def parse_string(content: str) -> AtrbDocument:
        """Parse YAML string into a document model."""
        data = yaml.safe_load(content)
        return AtrbParser._parse_document(data)
    
    @staticmethod
    def validate_atrb(filepath: str | Path) -> bool:
        """Validate that a file is a valid .atrb document."""
        try:
            AtrbParser.parse_file(filepath)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _parse_document(data: dict[str, Any]) -> AtrbDocument:
        """Parse document dictionary to model."""
        blocks = []
        for block_data in data.get("content", []):
            blocks.append(BaseBlock(
                id=UUID(block_data["id"]),
                type=block_data["type"],
                props=block_data.get("props", {}),
                content=block_data.get("content", []),
                children=block_data.get("children", []),
            ))
        
        return AtrbDocument(
            id=UUID(data["id"]),
            name=data["name"],
            version=data["version"],
            content=blocks,
        )
```

3. **Update exports:**
```python
# src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library built on Templateer."""

from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.models import AtrbDocument, BaseBlock

__version__ = "0.1.0"

__all__ = [
    "AtrbParser",
    "AtrbDocument",
    "BaseBlock",
]
```

### Testing Tasks

1. **Create validation test:**
```python
# tests/test_v1_validation.py
"""Test v1: Validate all generated .atrb files."""
from __future__ import annotations

from pathlib import Path
import pytest

from pytuin_desktop.parser import AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def get_all_v1_atrb_files():
    """Get all .atrb files in v1 directory."""
    if not TEST_OUTPUT_DIR.exists():
        return []
    return sorted(TEST_OUTPUT_DIR.glob("*.atrb"))


@pytest.mark.parametrize("atrb_file", get_all_v1_atrb_files())
def test_validate_all_generated_files(atrb_file):
    """Validate each generated .atrb file can be parsed."""
    # Should not raise exception
    doc = AtrbParser.parse_file(atrb_file)
    
    # Basic validation
    assert doc.id is not None
    assert doc.name != ""
    assert doc.version >= 1
    assert isinstance(doc.content, list)
    
    print(f"✓ Validated: {atrb_file.name}")


def test_validate_specific_files():
    """Validate specific known files."""
    test_cases = [
        ("00_empty.atrb", 0),  # (filename, expected block count)
        ("01_single_paragraph.atrb", 1),
        ("03_heading.atrb", 1),
        ("04_horizontal_rule.atrb", 1),
        ("05_script.atrb", 1),
    ]
    
    for filename, expected_blocks in test_cases:
        filepath = TEST_OUTPUT_DIR / filename
        if not filepath.exists():
            pytest.skip(f"{filename} not generated yet")
        
        doc = AtrbParser.parse_file(filepath)
        assert len(doc.content) == expected_blocks, f"{filename} should have {expected_blocks} blocks"


def test_parse_validates_structure():
    """Test parser validates required fields."""
    # Missing required field should raise error
    invalid_yaml = """id: "123"
name: "Test"
"""
    
    with pytest.raises(Exception):
        AtrbParser.parse_string(invalid_yaml)
```

2. **Run validation on all generated files:**
```bash
# First ensure all files are generated
pytest tests/test_v1_*.py -v

# Then validate them
pytest tests/test_v1_validation.py -v
```

**Success Criteria:**
- Parser loads all generated .atrb files
- No parsing errors
- All validation tests pass
- Can see validated file count in output

---

## Step 9: Multi-Block Complex Document

### Development Tasks

1. **No new templates needed** - use existing templates

### Testing Tasks

1. **Generate complex multi-block document:**
```python
# tests/test_v1_complex.py
"""Test v1: Complex multi-block documents."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from templateer.document import DocumentTemplate
from templateer.blocks import (
    HeadingBlockTemplate,
    ParagraphBlockTemplate,
    HorizontalRuleTemplate,
    ScriptBlockTemplate,
)
from templateer.content import TextContentTemplate, TextStylesTemplate
from pytuin_desktop.parser import AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_complete_runbook():
    """Generate a complete multi-block runbook."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Title
    title_text = TextContentTemplate(
        text="Server Setup Runbook",
        styles=TextStylesTemplate()
    )
    title = HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=1,
        content=[title_text]
    )
    
    # Introduction
    intro_text = TextContentTemplate(
        text="This runbook guides you through server setup and configuration.",
        styles=TextStylesTemplate()
    )
    intro = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[intro_text]
    )
    
    # Divider
    divider = HorizontalRuleTemplate(block_id=str(uuid4()))
    
    # Prerequisites heading
    prereq_text = TextContentTemplate(
        text="Prerequisites",
        styles=TextStylesTemplate(bold=True)
    )
    prereq_heading = HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=2,
        content=[prereq_text]
    )
    
    # Prerequisites paragraph
    prereq_para_text = TextContentTemplate(
        text="Before starting, ensure you have root access and network connectivity.",
        styles=TextStylesTemplate()
    )
    prereq_para = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[prereq_para_text]
    )
    
    # Installation heading
    install_heading_text = TextContentTemplate(
        text="Installation",
        styles=TextStylesTemplate()
    )
    install_heading = HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=2,
        content=[install_heading_text]
    )
    
    # Update script
    update_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="update_system",
        code="apt-get update && apt-get upgrade -y",
        interpreter="bash"
    )
    
    # Install Docker script
    docker_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="install_docker",
        code="curl -fsSL https://get.docker.com | sh\nsystemctl enable docker\nsystemctl start docker",
        interpreter="bash"
    )
    
    # Verification heading
    verify_heading_text = TextContentTemplate(
        text="Verification",
        styles=TextStylesTemplate()
    )
    verify_heading = HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=2,
        content=[verify_heading_text]
    )
    
    # Verify script
    verify_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="verify_installation",
        code="docker --version\nsystemctl status docker",
        interpreter="bash"
    )
    
    # Build document
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Complete Server Setup Runbook",
        version=1,
        blocks=[
            title,
            intro,
            divider,
            prereq_heading,
            prereq_para,
            install_heading,
            update_script,
            docker_script,
            verify_heading,
            verify_script,
        ]
    )
    
    # Write and validate
    output_path = TEST_OUTPUT_DIR / "10_complete_runbook.atrb"
    doc.write_to(output_path)
    
    # Parse to validate
    parsed_doc = AtrbParser.parse_file(output_path)
    
    assert len(parsed_doc.content) == 10
    assert parsed_doc.content[0].type == "heading"
    assert parsed_doc.content[1].type == "paragraph"
    assert parsed_doc.content[2].type == "horizontal_rule"
    assert parsed_doc.content[6].type == "script"
    assert parsed_doc.content[9].type == "script"


def test_document_with_mixed_styles():
    """Generate document with various text styles."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Paragraph with mixed inline styles
    bold = TextContentTemplate(
        text="Bold text ",
        styles=TextStylesTemplate(bold=True)
    )
    italic = TextContentTemplate(
        text="italic text ",
        styles=TextStylesTemplate(italic=True)
    )
    code = TextContentTemplate(
        text="inline code ",
        styles=TextStylesTemplate(code=True)
    )
    normal = TextContentTemplate(
        text="normal text",
        styles=TextStylesTemplate()
    )
    
    mixed_para = ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[bold, italic, code, normal]
    )
    
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Mixed Styles Test",
        version=1,
        blocks=[mixed_para]
    )
    
    output_path = TEST_OUTPUT_DIR / "11_mixed_styles.atrb"
    doc.write_to(output_path)
    
    # Validate
    parsed = AtrbParser.parse_file(output_path)
    assert len(parsed.content) == 1
    # Parser should preserve content array
    assert len(parsed.content[0].content) == 4
```

2. **Run tests:**
```bash
pytest tests/test_v1_complex.py -v
```

3. **Verify generated files:**
```bash
ls -la tests/v1/
cat tests/v1/10_complete_runbook.atrb
```

**Success Criteria:**
- Complex multi-block document generates correctly
- Multiple block types work together
- Parser validates complex documents
- `tests/v1/` has 10+ .atrb files
- All tests pass

---

## Step 10: Template Discovery Integration

### Development Tasks

1. **Create discovery wrapper:**
```python
# src/pytuin_desktop/discovery.py
"""Template discovery for .atrb templates."""
from __future__ import annotations

from pathlib import Path

from templateer import discover_templates as templateer_discover
from templateer.discovery import TemplateCollection


def load_atrb_templates(template_dir: str | Path = ".templateer") -> TemplateCollection:
    """
    Load .atrb templates using Templateer's discovery system.
    
    Args:
        template_dir: Directory containing template files (default: .templateer)
    
    Returns:
        TemplateCollection with discovered templates
    """
    return templateer_discover(template_dir)
```

2. **Update exports:**
```python
# src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library built on Templateer."""

from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.models import AtrbDocument, BaseBlock
from pytuin_desktop.discovery import load_atrb_templates

__version__ = "0.1.0"

__all__ = [
    "AtrbParser",
    "AtrbDocument",
    "BaseBlock",
    "load_atrb_templates",
]
```

### Testing Tasks

1. **Test discovery:**
```python
# tests/test_discovery.py
"""Test template discovery."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pytuin_desktop import load_atrb_templates


def test_load_atrb_templates():
    """Test loading templates from .templateer/."""
    templateer_dir = Path(__file__).parent.parent / ".templateer"
    
    templates = load_atrb_templates(templateer_dir)
    
    # Should find our templates
    template_names = templates.list_templates()
    
    expected_templates = [
        "EmptyDocumentTemplate",
        "DocumentTemplate",
        "TextStylesTemplate",
        "TextContentTemplate",
        "ParagraphBlockTemplate",
        "HeadingBlockTemplate",
        "HorizontalRuleTemplate",
        "ScriptBlockTemplate",
    ]
    
    for expected in expected_templates:
        assert expected in template_names, f"Missing template: {expected}"


def test_use_discovered_templates():
    """Test using discovered templates."""
    templateer_dir = Path(__file__).parent.parent / ".templateer"
    templates = load_atrb_templates(templateer_dir)
    
    # Create document using discovered templates
    text = templates.TextContentTemplate(
        text="Test",
        styles=templates.TextStylesTemplate()
    )
    
    para = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[text]
    )
    
    doc = templates.DocumentTemplate(
        document_id=str(uuid4()),
        name="Discovery Test",
        version=1,
        blocks=[para]
    )
    
    rendered = doc.render()
    assert "Discovery Test" in rendered
    assert "paragraph" in rendered
```

2. **Run tests:**
```bash
pytest tests/test_discovery.py -v
```

**Success Criteria:**
- Discovery finds all templates in `.templateer/`
- Can instantiate and use discovered templates
- All tests pass

---

## Step 11: Document Editor

### Development Tasks

1. **Create editor:**
```python
# src/pytuin_desktop/editor.py
"""Document editor for manipulating .atrb files."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from templateer import TemplateModel

from pytuin_desktop.models import AtrbDocument
from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.discovery import load_atrb_templates


class DocumentEditor:
    """Edit .atrb documents using templates."""
    
    def __init__(self, document_id: str, name: str, version: int = 1):
        """Initialize editor with document metadata."""
        self.document_id = document_id
        self.name = name
        self.version = version
        self.blocks: list[TemplateModel] = []
        self._templates = load_atrb_templates()
    
    @classmethod
    def create(cls, name: str, version: int = 1) -> DocumentEditor:
        """Create a new empty document."""
        return cls(
            document_id=str(uuid4()),
            name=name,
            version=version
        )
    
    @classmethod
    def from_file(cls, filepath: str | Path) -> DocumentEditor:
        """
        Load a document from file.
        Note: Parsed blocks are not editable as templates.
        Creates new editor with same metadata.
        """
        doc = AtrbParser.parse_file(filepath)
        editor = cls(
            document_id=str(doc.id),
            name=doc.name,
            version=doc.version
        )
        # Note: Cannot reconstruct TemplateModel instances from parsed blocks
        # This is for metadata copying only
        return editor
    
    def add_block(self, block: TemplateModel) -> DocumentEditor:
        """Add a block template to the document."""
        self.blocks.append(block)
        return self
    
    def remove_block_at(self, index: int) -> DocumentEditor:
        """Remove block at index."""
        if 0 <= index < len(self.blocks):
            del self.blocks[index]
        return self
    
    def get_block(self, index: int) -> TemplateModel:
        """Get block at index."""
        return self.blocks[index]
    
    def save(self, filepath: str | Path) -> None:
        """Render and save document to file."""
        doc_template = self._templates.DocumentTemplate(
            document_id=self.document_id,
            name=self.name,
            version=self.version,
            blocks=self.blocks
        )
        doc_template.write_to(filepath)
    
    def render(self) -> str:
        """Render document to YAML string."""
        doc_template = self._templates.DocumentTemplate(
            document_id=self.document_id,
            name=self.name,
            version=self.version,
            blocks=self.blocks
        )
        return doc_template.render()
```

2. **Update exports:**
```python
# src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library built on Templateer."""

from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.models import AtrbDocument, BaseBlock
from pytuin_desktop.discovery import load_atrb_templates
from pytuin_desktop.editor import DocumentEditor

__version__ = "0.1.0"

__all__ = [
    "AtrbParser",
    "AtrbDocument",
    "BaseBlock",
    "load_atrb_templates",
    "DocumentEditor",
]
```

### Testing Tasks

1. **Test editor:**
```python
# tests/test_editor.py
"""Test document editor."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pytuin_desktop import DocumentEditor, load_atrb_templates, AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_create_editor():
    """Test creating new editor."""
    editor = DocumentEditor.create("Test Document")
    
    assert editor.name == "Test Document"
    assert editor.version == 1
    assert len(editor.blocks) == 0


def test_editor_add_block():
    """Test adding blocks to editor."""
    templates = load_atrb_templates()
    editor = DocumentEditor.create("Test")
    
    text = templates.TextContentTemplate(
        text="Test",
        styles=templates.TextStylesTemplate()
    )
    
    para = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[text]
    )
    
    editor.add_block(para)
    
    assert len(editor.blocks) == 1


def test_editor_fluent_api():
    """Test chaining operations."""
    templates = load_atrb_templates()
    
    title_text = templates.TextContentTemplate(
        text="Title",
        styles=templates.TextStylesTemplate()
    )
    
    title = templates.HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=1,
        content=[title_text]
    )
    
    para_text = templates.TextContentTemplate(
        text="Content",
        styles=templates.TextStylesTemplate()
    )
    
    para = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[para_text]
    )
    
    editor = (
        DocumentEditor.create("Fluent Test")
        .add_block(title)
        .add_block(para)
    )
    
    assert len(editor.blocks) == 2


def test_editor_save():
    """Test saving document."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    templates = load_atrb_templates()
    editor = DocumentEditor.create("Editor Test")
    
    text = templates.TextContentTemplate(
        text="Saved via editor",
        styles=templates.TextStylesTemplate()
    )
    
    para = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[text]
    )
    
    editor.add_block(para)
    
    output_path = TEST_OUTPUT_DIR / "20_editor_test.atrb"
    editor.save(output_path)
    
    # Verify saved file
    assert output_path.exists()
    
    # Validate it parses
    doc = AtrbParser.parse_file(output_path)
    assert doc.name == "Editor Test"
    assert len(doc.content) == 1


def test_editor_remove_block():
    """Test removing blocks."""
    templates = load_atrb_templates()
    editor = DocumentEditor.create("Remove Test")
    
    para1 = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[]
    )
    para2 = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),
        content=[]
    )
    
    editor.add_block(para1).add_block(para2)
    assert len(editor.blocks) == 2
    
    editor.remove_block_at(0)
    assert len(editor.blocks) == 1
```

2. **Run tests:**
```bash
pytest tests/test_editor.py -v
```

**Success Criteria:**
- Editor creates documents
- Fluent API works
- Save generates valid .atrb files
- All tests pass

---

## Step 12: Block Builders (Convenience Layer)

### Development Tasks

1. **Create builders:**
```python
# src/pytuin_desktop/builders.py
"""Convenience builders for common block templates."""
from __future__ import annotations

from uuid import uuid4
from typing import Literal

from pytuin_desktop.discovery import load_atrb_templates


class BlockBuilder:
    """Factory methods for creating block templates with sensible defaults."""
    
    _templates = None
    
    @classmethod
    def _get_templates(cls):
        """Lazy load templates."""
        if cls._templates is None:
            cls._templates = load_atrb_templates()
        return cls._templates
    
    @classmethod
    def paragraph(
        cls,
        text: str = "",
        bold: bool = False,
        italic: bool = False,
        code: bool = False,
        text_color: str = "default",
        background_color: str = "default",
    ):
        """Create a paragraph block with text."""
        templates = cls._get_templates()
        
        content = []
        if text:
            styles = templates.TextStylesTemplate(
                bold=bold,
                italic=italic,
                code=code
            )
            content = [templates.TextContentTemplate(text=text, styles=styles)]
        
        return templates.ParagraphBlockTemplate(
            block_id=str(uuid4()),
            text_color=text_color,
            background_color=background_color,
            content=content
        )
    
    @classmethod
    def heading(
        cls,
        text: str,
        level: Literal[1, 2, 3, 4, 5, 6] = 1,
        is_toggleable: bool = False,
    ):
        """Create a heading block."""
        templates = cls._get_templates()
        
        styles = templates.TextStylesTemplate()
        text_content = templates.TextContentTemplate(text=text, styles=styles)
        
        return templates.HeadingBlockTemplate(
            block_id=str(uuid4()),
            level=level,
            is_toggleable=is_toggleable,
            content=[text_content]
        )
    
    @classmethod
    def horizontal_rule(cls):
        """Create a horizontal rule."""
        templates = cls._get_templates()
        return templates.HorizontalRuleTemplate(block_id=str(uuid4()))
    
    @classmethod
    def script(
        cls,
        name: str,
        code: str,
        interpreter: str = "bash",
        output_variable: str = "",
        output_visible: bool = True,
    ):
        """Create a script block."""
        templates = cls._get_templates()
        
        return templates.ScriptBlockTemplate(
            block_id=str(uuid4()),
            name=name,
            code=code,
            interpreter=interpreter,
            output_variable=output_variable,
            output_visible=output_visible
        )
```

2. **Update exports:**
```python
# src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library built on Templateer."""

from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.models import AtrbDocument, BaseBlock
from pytuin_desktop.discovery import load_atrb_templates
from pytuin_desktop.editor import DocumentEditor
from pytuin_desktop.builders import BlockBuilder

__version__ = "0.1.0"

__all__ = [
    "AtrbParser",
    "AtrbDocument",
    "BaseBlock",
    "load_atrb_templates",
    "DocumentEditor",
    "BlockBuilder",
]
```

### Testing Tasks

1. **Test builders:**
```python
# tests/test_builders.py
"""Test block builders."""
from __future__ import annotations

from pathlib import Path

from pytuin_desktop import BlockBuilder, DocumentEditor, AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_build_paragraph():
    """Test building paragraph with builder."""
    block = BlockBuilder.paragraph("Hello world", bold=True)
    
    assert block.__class__.__name__ == "ParagraphBlockTemplate"
    assert len(block.content) == 1
    assert block.content[0].text == "Hello world"
    assert block.content[0].styles.bold is True


def test_build_heading():
    """Test building heading."""
    block = BlockBuilder.heading("Title", level=2)
    
    assert block.__class__.__name__ == "HeadingBlockTemplate"
    assert block.level == 2
    assert block.content[0].text == "Title"


def test_build_horizontal_rule():
    """Test building horizontal rule."""
    block = BlockBuilder.horizontal_rule()
    
    assert block.__class__.__name__ == "HorizontalRuleTemplate"


def test_build_script():
    """Test building script."""
    block = BlockBuilder.script(
        name="test_script",
        code="echo 'test'",
        interpreter="bash"
    )
    
    assert block.__class__.__name__ == "ScriptBlockTemplate"
    assert block.name == "test_script"
    assert block.interpreter == "bash"


def test_builders_with_editor():
    """Test using builders with editor."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    editor = (
        DocumentEditor.create("Builder Test")
        .add_block(BlockBuilder.heading("Setup Guide", level=1))
        .add_block(BlockBuilder.paragraph("This guide shows how to set up the system."))
        .add_block(BlockBuilder.horizontal_rule())
        .add_block(BlockBuilder.heading("Installation", level=2))
        .add_block(BlockBuilder.script(
            name="install",
            code="apt-get install -y docker",
            interpreter="bash"
        ))
    )
    
    output_path = TEST_OUTPUT_DIR / "30_builder_test.atrb"
    editor.save(output_path)
    
    # Validate
    doc = AtrbParser.parse_file(output_path)
    assert len(doc.content) == 5
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"
    assert doc.content[2].type == "horizontal_rule"
    assert doc.content[4].type == "script"
```

2. **Run tests:**
```bash
pytest tests/test_builders.py -v
```

**Success Criteria:**
- All builders create correct template instances
- Builders work seamlessly with editor
- Generated .atrb files are valid
- All tests pass

---

## Step 13: Integration Test and Final Validation

### Development Tasks

No new code - verification step.

### Testing Tasks

1. **Create comprehensive integration test:**
```python
# tests/test_integration.py
"""Integration tests for complete workflows."""
from __future__ import annotations

from pathlib import Path

from pytuin_desktop import (
    DocumentEditor,
    BlockBuilder,
    load_atrb_templates,
    AtrbParser,
)


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_full_workflow_simple():
    """Test simple document creation workflow."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create using builders
    editor = (
        DocumentEditor.create("Simple Workflow Test")
        .add_block(BlockBuilder.heading("Title"))
        .add_block(BlockBuilder.paragraph("Content"))
    )
    
    # Save
    output_path = TEST_OUTPUT_DIR / "40_simple_workflow.atrb"
    editor.save(output_path)
    
    # Load and verify
    doc = AtrbParser.parse_file(output_path)
    assert doc.name == "Simple Workflow Test"
    assert len(doc.content) == 2


def test_full_workflow_complex():
    """Test complex document with templates."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    templates = load_atrb_templates()
    editor = DocumentEditor.create("Complex Workflow Test")
    
    # Mix builders and templates
    editor.add_block(BlockBuilder.heading("Deployment Guide", level=1))
    
    # Custom paragraph with multiple styles
    bold_text = templates.TextContentTemplate(
        text="Important: ",
        styles=templates.TextStylesTemplate(bold=True)
    )
    normal_text = templates.TextContentTemplate(
        text="Read all steps carefully.",
        styles=templates.TextStylesTemplate()
    )
    custom_para = templates.ParagraphBlockTemplate(
        block_id="custom-id-123",
        content=[bold_text, normal_text]
    )
    editor.add_block(custom_para)
    
    # Add more blocks
    editor.add_block(BlockBuilder.horizontal_rule())
    editor.add_block(BlockBuilder.heading("Steps", level=2))
    editor.add_block(BlockBuilder.script(
        name="deploy",
        code="kubectl apply -f deployment.yaml",
        interpreter="bash"
    ))
    
    # Save and validate
    output_path = TEST_OUTPUT_DIR / "41_complex_workflow.atrb"
    editor.save(output_path)
    
    doc = AtrbParser.parse_file(output_path)
    assert len(doc.content) == 5


def test_template_discovery_and_usage():
    """Test discovering and using templates directly."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    
    templates = load_atrb_templates()
    
    # Build document entirely from templates
    from uuid import uuid4
    
    title = templates.HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=1,
        content=[templates.TextContentTemplate(
            text="Direct Template Usage",
            styles=templates.TextStylesTemplate()
        )]
    )
    
    doc = templates.DocumentTemplate(
        document_id=str(uuid4()),
        name="Template Direct Usage Test",
        version=1,
        blocks=[title]
    )
    
    output_path = TEST_OUTPUT_DIR / "42_template_direct.atrb"
    doc.write_to(output_path)
    
    # Validate
    parsed = AtrbParser.parse_file(output_path)
    assert parsed.name == "Template Direct Usage Test"
```

2. **Run all v1 tests:**
```bash
# Run all MVP tests
pytest tests/test_v1_*.py tests/test_*.py -v

# Check coverage
pytest --cov=src/pytuin_desktop --cov=.templateer --cov-report=html

# View coverage report
open htmlcov/index.html
```

3. **Final validation:**
```bash
# Count generated files
ls tests/v1/*.atrb | wc -l

# List all files
ls -lh tests/v1/

# Validate every file parses
python -c "
from pathlib import Path
from pytuin_desktop import AtrbParser

v1_dir = Path('tests/v1')
files = list(v1_dir.glob('*.atrb'))
print(f'Validating {len(files)} .atrb files...')

for f in files:
    try:
        doc = AtrbParser.parse_file(f)
        print(f'✓ {f.name}: {doc.name} ({len(doc.content)} blocks)')
    except Exception as e:
        print(f'✗ {f.name}: ERROR - {e}')
"
```

**Success Criteria:**
- All integration tests pass
- 20+ .atrb files in tests/v1/
- All files parse successfully
- 90%+ code coverage
- No test failures

---

## MVP Complete!

You now have a fully functional MVP of Pytuin Desktop built on Templateer:

**✅ Completed:**
- Templateer integrated as core dependency
- Templates in `.templateer/` generate valid .atrb YAML
- Parser validates all generated files
- DocumentEditor manipulates documents via templates
- BlockBuilder provides convenience layer
- 20+ test .atrb files in versioned directory
- 90%+ test coverage

**Generated Files:**
```
tests/v1/
├── 00_empty.atrb
├── 01_single_paragraph.atrb
├── 02_styled_paragraph.atrb
├── 03_heading.atrb
├── 04_horizontal_rule.atrb
├── 05_script.atrb
├── 10_complete_runbook.atrb
├── 11_mixed_styles.atrb
├── 20_editor_test.atrb
├── 30_builder_test.atrb
├── 40_simple_workflow.atrb
├── 41_complex_workflow.atrb
└── 42_template_direct.atrb
```

---

## Next Steps for Full Version

Continue building on this foundation:

**Step 14: Additional Block Templates**
- EditorBlock, VarBlock, RunBlock, etc.
- Test each in isolation
- Generate v1/50-90 series .atrb files

**Step 15: Table and List Templates**
- TableBlock with rows/cells
- List block templates
- Generate v2/ series .atrb files

**Step 16: Advanced Editor Operations**
- find_block(), replace_block(), move_block()
- Block transformation operations
- Complex editing tests

**Step 17: High-Level Generators**
- RunbookGenerator class
- Pattern-based document generation
- Real-world runbook examples

**Step 18: Validation and Linting**
- Validate block relationships
- Check reference integrity
- Lint for best practices

Each step follows the same pattern: develop → test → generate .atrb files → validate.
