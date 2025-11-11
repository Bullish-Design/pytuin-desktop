# Pytuin-Desktop User Guide

## Overview

Pytuin-Desktop is a Python library designed for generating, editing, and parsing `.atrb` (Atuin block) documents. It provides a structured API for developers to construct, manage, and interpret these documents programmatically.

This guide covers the fundamental usage of the library from a developer’s perspective.

---

## Installation

```bash
pip install pytuin-desktop
```

---

## Getting Started

### Creating a New Document

```python
from pytuin_desktop import DocumentEditor, BlockBuilder

editor = (
    DocumentEditor.create("My First Document")
    .add_block(BlockBuilder.heading("Welcome"))
    .add_block(BlockBuilder.paragraph("This is a paragraph inside the document."))
)

editor.save("my_doc.atrb")
```

### Parsing an Existing Document

```python
from pytuin_desktop import AtrbParser

doc = AtrbParser.parse_file("my_doc.atrb")
print(doc.name)
for block in doc.content:
    print(block.type)
```

### Supported Block Builders

- Heading Block – `BlockBuilder.heading("Title", level=1)`
- Paragraph Block – `BlockBuilder.paragraph("Content")`
- Horizontal Rule – `BlockBuilder.horizontal_rule()`
- Script Block – `BlockBuilder.script(name="Run", code="echo 'Hello'", interpreter="bash")`

---

## Working with Templates Directly

Developers can bypass builders and use templates explicitly:

```python
from pytuin_desktop import load_atrb_templates
from uuid import uuid4

T = load_atrb_templates()

paragraph = T.ParagraphBlockTemplate(
    block_id=str(uuid4()),
    content=[
        T.TextContentTemplate(
            text="Bold text example",
            styles=T.TextStylesTemplate(bold=True),
        )
    ],
)

document = T.DocumentTemplate(
    document_id=str(uuid4()),
    name="Direct Template Example",
    blocks=[paragraph],
)

document.write_to("direct.atrb")
```

---

## Document Structure

An `.atrb` document follows a YAML-based structure:

```yaml
id: "<uuid>"
name: "<document name>"
version: <int>
content:
  - id: "<block uuid>"
    type: <block_type>
    props: { ... }
    content: [ ... ]
    children: []
```

---

## Template Discovery

Templates can be dynamically loaded from the `.templateer` directory:

```python
from pytuin_desktop import discovery

templates = discovery.discover_templates()
print(templates.keys())
```

---

## Summary

Pytuin-Desktop provides a structured interface for producing and managing `.atrb` files through templates and builders. Developers can start quickly using high-level APIs (`DocumentEditor`, `BlockBuilder`) or fine-tune output using template-level control.
