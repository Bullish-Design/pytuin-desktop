# Pytuin-Desktop v3

A small, testable toolkit for generating and editing `.atrb` documents. It provides a validated YAML schema, a template-driven block system, and a composable editor with streaming I/O and an extensibility seam for persistence.

## Highlights (v3)

- Streaming read/write for `.atrb` via file paths or text streams.
- Strongly-typed data model with schema validation before write.
- Templated block generation with `templateer` for deterministic output.
- Repository protocol for persistence, plus an in-memory implementation.
- Stable top-level public API with explicit exports and versioning.
- Repeatable tests and minimal dependencies.

## Quick Start

### Create and save a document

```python
from uuid import uuid4
from templateer import TemplateModel
from pytuin_desktop import DocumentEditor

PARA_TMPL = \"\"\"
id: \"{{ block_id }}\"
type: paragraph
props: { }
content:
  - type: text
    text: {{ text|tojson }}
    styles: { bold: false, italic: false, underline: false, strikethrough: false, code: false }
children: []
\"\"\"

class ParagraphBlockTemplate(TemplateModel):
    __template__ = PARA_TMPL
    block_id: str
    text: str

# Create an editor and add blocks
ed = DocumentEditor.create(\"My Doc\")
ed.add_block(ParagraphBlockTemplate(block_id=str(uuid4()), text=\"Hello world\"))

# Save to disk (ensures a single trailing newline)
ed.save(\"example.atrb\")
```

### Parse and validate

```python
from pytuin_desktop import AtrbParser, AtrbValidator

doc = AtrbParser.parse_file(\"example.atrb\")
AtrbValidator.validate(doc)  # raises on schema violations
```

### Stream I/O (stdin/stdout style)

```python
from io import StringIO
from pytuin_desktop import AtrbParser

with open(\"example.atrb\", \"r\", encoding=\"utf-8\") as f:
    doc = AtrbParser.parse_stream(f)
```

### Optional persistence via repository

```python
from pytuin_desktop import DocumentEditor, InMemoryDocumentRepository
from uuid import uuid4

repo = InMemoryDocumentRepository()
ed = DocumentEditor.create(\"Repo Doc\", repository=repo)
ed.add_block(ParagraphBlockTemplate(block_id=str(uuid4()), text=\"Persist me\"))
ed.save(\"repo_doc.atrb\")  # also saved to repo

stored = repo.list()
doc_id = str(stored[0].id)
same_doc = repo.get(doc_id)
```

## Public API (stable)

```python
from pytuin_desktop import (
    # Parsing & validation
    AtrbParser, AtrbValidator,

    # Models
    AtrbDocument, BaseBlock, TextAlignment, ColorToken,

    # Templating & builders
    load_atrb_templates, clear_template_cache, BlockBuilder,

    # Editing
    DocumentEditor,

    # Persistence seam
    DocumentRepository, InMemoryDocumentRepository,

    # Logging
    get_logger,

    # Errors
    AtrbError, AtrbParseError, AtrbSchemaError, AtrbValidationError, TemplateDiscoveryError,

    # Version
    __version__,
)
```

## Document format (`.atrb`)

- UTF‑8 YAML.
- Top-level metadata: `id`, `name`, `version`.
- `content` is an ordered list of block dictionaries.
- Each block has a `type`, `props`, `content` (rich text runs), and `children`.
- Schema is validated prior to writes; invalid documents raise an error.

## Logging

Use `get_logger()` to obtain a preconfigured logger. Editor operations log structured breadcrumbs such as `editor.write_to_stream`, `editor.save`, and `editor.repo_saved` (when a repository is used).

## Versioning

This release identifies as `0.3.0-dev9`. The public API is kept stable within v3; internal modules may change.

## Contributing

- Run the test suite and ensure 100% passing.
- Add tests for new block types, validators, and editor behaviors.
- Keep top-level exports coherent; breaking API changes should be deliberate and documented in the changelog.
