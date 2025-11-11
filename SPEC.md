# Pytuin Desktop Library Specification

## Overview

Pytuin Desktop is a Python library for parsing, editing, and generating Atuin Desktop `.atrb` files. It is built on top of **Templateer**, using its Pydantic-to-Jinja2 templating system as the core generation engine.

## Core Architecture

### Foundation: Templateer
- **Dependency**: Templateer provides `TemplateModel`, `discover_templates()`, and template composition
- **Templates**: `.templateer/` directory contains all .atrb generation templates
- **Integration**: Pytuin Desktop extends Templateer's functionality with .atrb-specific features

### Pytuin Desktop Layers
1. **Templates** (`.templateer/`) - Generate .atrb YAML components using Templateer
2. **Parser** - Validate and load .atrb files into Pydantic models
3. **Editor** - Manipulate documents using templates and models
4. **Builders** - Convenience wrappers around templates

---

## MVP Version Requirements

### 1. Templateer Integration

**Dependencies:**
```toml
dependencies = [
    "templateer>=0.3.1",
    "pydantic>=2.12.4",
    "pyyaml>=6.0",
]
```

**Must Have:**
- Import and use Templateer's `TemplateModel` directly
- Use Templateer's `discover_templates()` for finding templates
- All templates in `.templateer/` directory

### 2. Core .atrb Templates

**Must Have in `.templateer/`:**

**Document Templates:**
```python
# .templateer/document.py
class EmptyDocumentTemplate(TemplateModel)  # Empty document
class DocumentTemplate(TemplateModel)       # Document with blocks
```

**Content Templates:**
```python
# .templateer/content.py
class TextStylesTemplate(TemplateModel)     # Text styling
class TextContentTemplate(TemplateModel)    # Inline text content
```

**Block Templates:**
```python
# .templateer/blocks.py
class ParagraphBlockTemplate(TemplateModel)
class HeadingBlockTemplate(TemplateModel)
class HorizontalRuleTemplate(TemplateModel)
class ScriptBlockTemplate(TemplateModel)
class EditorBlockTemplate(TemplateModel)
class VarBlockTemplate(TemplateModel)
```

Each template must:
- Generate valid YAML for .atrb format
- Support nested composition via `__str__()`
- Use Jinja2 filters (indent, tojson, etc.)
- Accept Pydantic-validated parameters

**Example Structure:**
```python
from templateer import TemplateModel

PARAGRAPH_TEMPLATE = """id: "{{ block_id }}"
type: paragraph
props:
  textColor: {{ text_color }}
  backgroundColor: {{ background_color }}
content:
{% for item in content %}
  - {{ item|indent(4, true) }}
{% endfor %}
children: []"""

class ParagraphBlockTemplate(TemplateModel):
    __template__ = PARAGRAPH_TEMPLATE
    
    block_id: str
    text_color: str = "default"
    background_color: str = "default"
    content: list[TextContentTemplate] = []
```

### 3. Parser (Validation Layer)

**Must Have:**
```python
# src/pytuin_desktop/parser.py
class AtrbParser:
    @staticmethod
    def parse_file(filepath: str | Path) -> AtrbDocument
    
    @staticmethod
    def parse_string(content: str) -> AtrbDocument
    
    @staticmethod
    def validate_atrb(filepath: str | Path) -> bool
```

**Purpose:**
- Validate template-generated .atrb files
- Parse existing .atrb files into Pydantic models
- Provide error reporting for invalid files

**Minimal Models:**
```python
# src/pytuin_desktop/models.py
class BaseBlock(BaseModel)      # Generic block structure
class AtrbDocument(BaseModel)   # Document structure
```

Models are intentionally minimal - templates handle generation.

### 4. Template Discovery

**Must Have:**
```python
# src/pytuin_desktop/discovery.py
from templateer import discover_templates

def load_atrb_templates(template_dir: str | Path = ".templateer"):
    """Load .atrb templates using Templateer's discovery."""
    return discover_templates(template_dir)
```

**Usage:**
```python
from pytuin_desktop import load_atrb_templates

templates = load_atrb_templates()
doc = templates.DocumentTemplate(
    document_id=str(uuid4()),
    name="My Doc",
    blocks=[...]
)
doc.write_to("output.atrb")
```

### 5. Document Editor

**Must Have:**
```python
# src/pytuin_desktop/editor.py
class DocumentEditor:
    def __init__(self, document: AtrbDocument)
    
    @classmethod
    def create(cls, name: str) -> DocumentEditor
    
    @classmethod
    def from_file(cls, filepath: str | Path) -> DocumentEditor
    
    def add_block(self, block_template: TemplateModel) -> DocumentEditor
    def remove_block(self, block_id: str) -> DocumentEditor
    def save(self, filepath: str | Path) -> None
```

**Key Features:**
- Accepts `TemplateModel` instances (not raw models)
- Renders templates to YAML internally
- Maintains document structure
- Fluent API for chaining

**Example:**
```python
editor = DocumentEditor.create("Setup Guide")

# Add using templates
templates = load_atrb_templates()
editor.add_block(templates.HeadingBlockTemplate(
    block_id=str(uuid4()),
    level=1,
    content=[templates.TextContentTemplate(text="Title", styles=...)]
))

editor.save("guide.atrb")
```

### 6. Builder Helpers

**Must Have:**
```python
# src/pytuin_desktop/builders.py
class BlockBuilder:
    @staticmethod
    def paragraph(text: str, **kwargs) -> ParagraphBlockTemplate
    
    @staticmethod
    def heading(text: str, level: int = 1) -> HeadingBlockTemplate
    
    @staticmethod
    def script(name: str, code: str, **kwargs) -> ScriptBlockTemplate
```

**Purpose:**
- Convenience wrappers that create template instances
- Reasonable defaults for common use cases
- Returns `TemplateModel` instances ready for editor

**Example:**
```python
from pytuin_desktop import BlockBuilder

block = BlockBuilder.paragraph("Hello world", bold=True)
# Returns ParagraphBlockTemplate instance
editor.add_block(block)
```

### MVP Testing Requirements

**Test Structure:**
```
tests/
├── v1/                          # Generated MVP .atrb files
│   ├── empty.atrb
│   ├── single_paragraph.atrb
│   ├── heading.atrb
│   ├── script.atrb
│   └── complete_runbook.atrb
├── test_templates.py            # Template rendering tests
├── test_generation.py           # Generate .atrb files
├── test_validation.py           # Validate all generated files
└── test_editor.py               # Editor functionality tests
```

**Coverage:**
- Each template tested individually
- Each template generates valid .atrb file
- All generated files parsed successfully
- 90%+ code coverage

---

## Full Version Requirements

### 1. Complete Block Templates

**Add to `.templateer/blocks.py`:**
```python
class RunBlockTemplate(TemplateModel)
class EnvBlockTemplate(TemplateModel)
class LocalVarBlockTemplate(TemplateModel)
class VarDisplayBlockTemplate(TemplateModel)
class DirectoryBlockTemplate(TemplateModel)
class LocalDirectoryBlockTemplate(TemplateModel)
class DropdownBlockTemplate(TemplateModel)
class SQLiteBlockTemplate(TemplateModel)
class PostgresBlockTemplate(TemplateModel)
class HttpBlockTemplate(TemplateModel)
class QuoteBlockTemplate(TemplateModel)
class ToggleListItemBlockTemplate(TemplateModel)
class NumberedListItemBlockTemplate(TemplateModel)
class BulletListItemBlockTemplate(TemplateModel)
class CheckListItemBlockTemplate(TemplateModel)
class CodeBlockTemplate(TemplateModel)
class TableBlockTemplate(TemplateModel)
class ImageBlockTemplate(TemplateModel)
class VideoBlockTemplate(TemplateModel)
class AudioBlockTemplate(TemplateModel)
class FileBlockTemplate(TemplateModel)
```

### 2. Advanced Content Templates

```python
# .templateer/content.py
class RunbookLinkTemplate(TemplateModel)
class TableContentTemplate(TemplateModel)
class TableRowTemplate(TemplateModel)
class TableCellTemplate(TemplateModel)
```

### 3. Enhanced Editor

**Add:**
```python
# src/pytuin_desktop/editor.py
class DocumentEditor:
    def replace_block(self, block_id: str, new_block: TemplateModel)
    def move_block(self, from_idx: int, to_idx: int)
    def find_block(self, block_id: str) -> BaseBlock | None
    def find_blocks_by_type(self, block_type: str) -> list[BaseBlock]
    def filter_blocks(self, predicate: Callable) -> list[BaseBlock]
    def clone_block(self, block_id: str) -> TemplateModel
    def transform_blocks(self, transformer: Callable)
```

### 4. Template-Based Generators

**High-level document generators:**
```python
# src/pytuin_desktop/generators.py
class RunbookGenerator:
    """Generate complete runbooks from high-level specs."""
    
    def __init__(self, templates: TemplateCollection)
    
    def create_deployment_runbook(self, config: DeploymentConfig) -> DocumentTemplate
    def create_troubleshooting_guide(self, steps: list[str]) -> DocumentTemplate
    def create_setup_guide(self, components: list[Component]) -> DocumentTemplate
```

**Example:**
```python
from pytuin_desktop import RunbookGenerator, load_atrb_templates

templates = load_atrb_templates()
generator = RunbookGenerator(templates)

doc = generator.create_deployment_runbook(
    config=DeploymentConfig(
        service="api",
        environment="production",
        steps=["build", "test", "deploy"]
    )
)

doc.write_to("deploy.atrb")
```

### 5. Writer (Template-to-YAML)

```python
# src/pytuin_desktop/writer.py
class AtrbWriter:
    @staticmethod
    def render_template(template: TemplateModel) -> str
    
    @staticmethod
    def write_template(template: TemplateModel, filepath: str | Path)
    
    @staticmethod
    def combine_templates(templates: list[TemplateModel]) -> str
```

**Purpose:**
- Utility functions for template rendering
- Handle template composition
- Batch operations

### 6. Validation and Linting

```python
# src/pytuin_desktop/validation.py
class AtrbValidator:
    @staticmethod
    def validate_document(doc: AtrbDocument) -> list[ValidationError]
    
    @staticmethod
    def validate_block(block: BaseBlock) -> list[ValidationError]
    
    @staticmethod
    def check_references(doc: AtrbDocument) -> list[ReferenceError]
```

### 7. Document Diffing

```python
# src/pytuin_desktop/diff.py
class DocumentDiff:
    @staticmethod
    def compare(doc1: AtrbDocument, doc2: AtrbDocument) -> DiffResult
    
    added_blocks: list[BaseBlock]
    removed_blocks: list[BaseBlock]
    modified_blocks: list[tuple[BaseBlock, BaseBlock]]
```

### Full Version Testing

**Test Structure:**
```
tests/
├── v1/                    # MVP tests
├── v2/                    # Full version tests
│   ├── all_block_types/
│   │   ├── run.atrb
│   │   ├── env.atrb
│   │   ├── table.atrb
│   │   └── ...
│   ├── complex/
│   │   ├── nested_blocks.atrb
│   │   ├── large_document.atrb
│   │   └── real_world_runbook.atrb
│   └── edge_cases/
│       ├── empty_content.atrb
│       ├── deeply_nested.atrb
│       └── special_chars.atrb
├── test_all_templates.py
├── test_generators.py
├── test_advanced_editor.py
└── test_validation.py
```

**Coverage:**
- All block types tested
- Complex compositions tested
- Edge cases handled
- Performance tests for large documents
- 95%+ code coverage

---

## Project Structure

```
pytuin-desktop/
├── .templateer/                    # Templates (using Templateer)
│   ├── __init__.py
│   ├── document.py                 # Document templates
│   ├── content.py                  # Content templates
│   ├── blocks.py                   # Block templates
│   └── props.py                    # Props templates
├── src/
│   └── pytuin_desktop/
│       ├── __init__.py
│       ├── parser.py               # Parse/validate .atrb files
│       ├── editor.py               # Document manipulation
│       ├── builders.py             # Template builder helpers
│       ├── models.py               # Minimal Pydantic models
│       ├── discovery.py            # Template discovery wrapper
│       ├── writer.py               # Template rendering helpers
│       ├── generators.py           # High-level generators (full version)
│       ├── validation.py           # Validation (full version)
│       └── diff.py                 # Diffing (full version)
├── tests/
│   ├── v1/                         # MVP generated .atrb files
│   ├── v2/                         # Full version .atrb files
│   ├── test_templates.py
│   ├── test_generation.py
│   ├── test_validation.py
│   └── test_editor.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_generation.py
├── pyproject.toml
└── README.md
```

---

## API Design Principles

### 1. Templateer-First
All generation goes through Templateer templates. No bypassing the template system.

### 2. Composition Over Inheritance
Use template composition (nested `TemplateModel` instances) rather than complex inheritance.

### 3. Type-Safe at Template Level
Pydantic validation happens at template instantiation, not after rendering.

### 4. Clear Separation of Concerns
- Templates → Generate YAML
- Parser → Validate/Load YAML
- Editor → Manipulate using templates
- Models → Minimal, for parsing only

### 5. Progressive Disclosure
Simple tasks should be simple:
```python
# Simple
from pytuin_desktop import BlockBuilder, DocumentEditor

editor = DocumentEditor.create("Guide")
editor.add_block(BlockBuilder.heading("Setup"))
editor.save("guide.atrb")
```

Complex tasks should be possible:
```python
# Complex
from pytuin_desktop import load_atrb_templates, RunbookGenerator

templates = load_atrb_templates()
generator = RunbookGenerator(templates)
doc = generator.create_deployment_runbook(complex_config)
```

---

## Integration with Templateer

### Direct Usage
```python
from templateer import TemplateModel, discover_templates

# User can use Templateer directly
templates = discover_templates(".templateer")
block = templates.ParagraphBlockTemplate(...)
yaml_output = block.render()
```

### Pytuin Desktop Wrappers
```python
from pytuin_desktop import load_atrb_templates, DocumentEditor

# Or use Pytuin Desktop's conveniences
templates = load_atrb_templates()
editor = DocumentEditor.create("Doc")
editor.add_block(templates.ParagraphBlockTemplate(...))
editor.save("doc.atrb")
```

Both approaches work. Pytuin Desktop adds .atrb-specific features on top of Templateer.

---

## Success Criteria

### MVP
- Templateer integrated as dependency
- Core templates generate valid .atrb files
- Parser validates all template output
- DocumentEditor manipulates documents via templates
- 90%+ test coverage
- All tests generate and validate .atrb files

### Full Version
- All Atuin Desktop block types supported via templates
- High-level generators for common runbook patterns
- Advanced editor operations
- Validation and diffing
- 95%+ test coverage
- Performance acceptable for 1000+ block documents
- Real-world runbook generation examples
