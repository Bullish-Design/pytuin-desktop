# Pytuin Desktop (Templateer-based)

A typed Python toolkit for reading, writing, templating, and editing Atuin Desktop `.atrb` runbooks — powered by Templateer’s type-safe Jinja models.

---

## Overview

Pytuin Desktop integrates directly with Atuin Desktop’s `.atrb` runbook format.  
It provides structured parsing, editing, and templating through a unified Python interface.  
The library utilizes Templateer-based template discovery and rendering for automated runbook generation.

---

## Installation

```bash
uv add pytuin_desktop
```

---

## Quick Start

### 1. Discover Templates

Templates are defined as Python classes under a `.templateer/` folder and are automatically discovered.

```python
from templateer import discover_templates
tpl = discover_templates(".templateer")
```

### 2. Render a Template

Each template is a Pydantic model with a `__template__` Jinja definition.

```python
heading = tpl.HeadingBlockTemplate(text="Deploy Playbook", level=2)
block_yaml = heading.render()
```

### 3. Parse and Edit `.atrb` Files

Use Pytuin’s core parser, writer, and editor to manipulate runbooks.

```python
from pytuin_desktop import AtrbParser, DocumentEditor, BlockBuilder

doc = AtrbParser.parse_file("runbooks/deploy.atrb")
editor = DocumentEditor(doc)

editor.add_block(BlockBuilder.heading("Deploy Playbook", level=2))
editor.save("runbooks/deploy.atrb")
```

---

## Core Concepts

### Templates

- Templates are Python classes inheriting from `TemplateModel`.
- Each class contains a `__template__` attribute with Jinja syntax.
- Fields on the class are substituted into the template during rendering.

Example:

```python
from templateer import TemplateModel

TEMPLATE = """\
type: heading
id: {{ id }}
props:
  level: {{ level }}
content:
  - type: text
    text: {{ text|tojson }}
"""

class HeadingBlockTemplate(TemplateModel):
    __template__ = TEMPLATE
    id: str
    text: str
    level: int = 2
```

### Parser and Writer

- `AtrbParser` reads `.atrb` YAML into validated Pydantic models.
- `AtrbWriter` serializes models back into YAML with deterministic formatting.

### Document Editor

- `DocumentEditor` allows insertion, deletion, and traversal of blocks.
- `BlockBuilder` provides helper constructors for common block types.

---

## CLI (Upcoming)

A Typer-based CLI is planned for template and workspace management:

```
pytuin tpl list
pytuin tpl render TplName ...
pytuin runbook new NAME
pytuin runbook apply TEMPLATE
pytuin ws files ROOT
```

---


## Example Workflow

1. Store templates in `.templateer/`.
2. Render templates to YAML or Python.
3. Parse or validate with `AtrbParser`.
4. Modify or assemble runbooks using `DocumentEditor`.
5. Save or deploy the final `.atrb` output.

---

## License

MIT License.  
Atuin Desktop is a separate application maintained by the Atuin team.
