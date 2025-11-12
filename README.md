# Pytuin-Desktop

Fast, typed tools for reading, building, validating, diffing, and writing `.atrb` documents used by the Atuin Desktop app. Pytuin-Desktop wraps Templateer (Pydantic + Jinja2) for code-generated blocks and provides a batteries-included editing and parsing toolkit.

## TL;DR (Quickstart)

```python
from pytuin_desktop import BlockBuilder, DocumentEditor

# 1) Build some blocks via templates in `.templateer/`
heading = BlockBuilder.heading("My session", level=2)
para = BlockBuilder.paragraph("Run this to fetch history.", italic=True)

# 2) Compose a document with the editor
ed = DocumentEditor.create("atuin-setup", version=1)
ed.add_blocks([heading, para])
print(ed.render())          # -> YAML text
ed.save("atuin_setup.atrb") # writes file
```

---

## Installation

Pytuin-Desktop targets Python >=3.11. It depends on Pydantic v2 and PyYAML, and uses Jinja2 through Templateer for code-generated templates.

## What is an `.atrb`?

A single YAML document that describes a page of blocks (e.g., headings, paragraphs, scripts, terminals) the desktop app renders. Minimal shape:

```yaml
id: 6f1e4a24-ea9a-4ab5-9d1a-2b5d9e58f0bd
name: My Doc
version: 1
content:
  - id: 4b52f5e2-5c31-4b3b-9d59-5416f5b0f0aa
    type: heading
    props: { level: 2, isToggleable: false }
    content: [{ text: "Hello", styles: { bold: false } }]
```

You can hand-write these, but most users generate them using template classes in `.templateer/` via `BlockBuilder` APIs.

## Core Concepts

- Typed blocks - Pydantic models for known block kinds and a union type `Block`:
  - `HeadingBlock`, `ParagraphBlock`, `ScriptBlock`, `EditorBlock`, `TerminalBlock` (`type: run`), `EnvironmentBlock` (`type: env`), `VariableBlock` (`type: var`), `DirectoryBlock`, `HorizontalRuleBlock`.
- Enums - `TextAlignment` and `ColorToken` ensure safe values; string inputs are coerced during parsing/validation.
- Templates - Templateer models render block dictionaries (YAML). Discoverable from `.templateer/`.
- Builders - Convenience functions (`BlockBuilder.heading/paragraph/script/...`) that call templates and handle IDs & enums.
- Editor - `DocumentEditor` collects existing+new blocks, validates, renders YAML, and saves to disk.
- Parser - `AtrbParser.parse_file/parse_stream/parse_dict(_typed)` reads `.atrb` into models and validates.
- Diffs - `DocumentDiffer.diff(old, new)` reports added/removed/moved/modified blocks.
- Services - `DocumentLoader` (read) and `DocumentSerializer` (YAML IO helpers) for simple plumbing.
- Metrics & Logging - Hook points across parse/save/edit operations to measure and troubleshoot.

## High-level API

### Block builders

```python
from pytuin_desktop import BlockBuilder, TextAlignment, ColorToken

h = BlockBuilder.heading(
    "Setup", level=1, is_toggleable=True,
    text_alignment=TextAlignment.center, text_color="accent"
)
p = BlockBuilder.paragraph("Install Atuin and sign in", italic=True)

script = BlockBuilder.script(
    name="Install Atuin", code="curl ... | bash", interpreter="bash",
    output_variable="install_log", output_visible=True
)
```

> Builders call into your local `.templateer/` templates. Ensure that directory exists and contains the block templates shipped with your project/app.

### Editing & writing

```python
from pytuin_desktop import DocumentEditor

ed = DocumentEditor.create("getting-started", version=1)
ed.add_blocks([h, p, script])
ed.save("getting_started.atrb")  # validates and writes YAML
```

- `insert_block_at(i, block)` - insert among new blocks.
- `move_block(from_i, to_i)` - reorder within existing or new regions (not across the boundary).
- `replace_block_at(i, block)` - remove then insert as new at the same index.
- `remove_block_at(i)` / `remove_blocks_at([...])`
- `find_blocks_by_type("heading")`, `find_block_by_id(uuid)`, `get_block_index(uuid)`.

### Parsing & validating

```python
from pytuin_desktop import AtrbParser

doc = AtrbParser.parse_file("getting_started.atrb")  # returns AtrbDocument
```

Validation catches:
- Missing document keys (`id`, `name`, `version`).
- Duplicate block IDs, non-UUIDs, empty types.
- Typed block rules (e.g., heading level 1-6, non-empty script name/code).
- Enum normalization/guarantees for color/alignment.

### Diffing

```python
from pytuin_desktop import DocumentDiffer

before = AtrbParser.parse_file("v1.atrb")
after = AtrbParser.parse_file("v2.atrb")
diff = DocumentDiffer.diff(before, after)

print(diff.added_count, diff.removed_count, diff.modified_count, diff.moved_count)
for c in diff.changes:
    print(c.change_type, c.block_id, c.property_changes)
```

### Loading & serialization services

```python
from pytuin_desktop import DocumentLoader, DocumentSerializer

loader = DocumentLoader()
doc = loader.load_from_file("doc.atrb")

ser = DocumentSerializer()
yaml_text = ser.dumps_yaml({"hello": "world"})
```

## Template discovery

Templates live under `.templateer/`. The library discovers them and caches the namespace for reuse:

```python
from pytuin_desktop import load_atrb_templates, clear_template_cache

T = load_atrb_templates(".templateer")  # raises TemplateDiscoveryError if folder missing
clear_template_cache()                  # bust cache (e.g., after writing new files)
```

## Environment & configuration

- `PYTUIN_TEMPLATE_DIR` - sets the default template directory looked up by builders/editor.
- `PYTUIN_LOG_LEVEL` - logger level (default `WARNING`).

## Exceptions you might see

- `AtrbParseError`, `AtrbSchemaError`, `AtrbValidationError` - parsing/shape/semantic issues.
- `TemplateDiscoveryError` - missing or unreadable `.templateer` directory.

## Metrics & Logging

Operations record durations and counters via the pluggable `MetricsCollector` and log via a standard `logging.Logger`. For in-memory inspection:

```python
from pytuin_desktop import InMemoryMetricsCollector, set_default_collector

mc = InMemoryMetricsCollector()
set_default_collector(mc)
```

## Minimal end-to-end example

```python
from pytuin_desktop import (
    BlockBuilder, DocumentEditor, AtrbParser,
    DocumentDiffer, InMemoryMetricsCollector, set_default_collector
)

set_default_collector(InMemoryMetricsCollector())

ed = DocumentEditor.create("demo", version=1)
ed.add_block(BlockBuilder.heading("Demo", level=1))
ed.add_block(BlockBuilder.paragraph("Hello Atuin!"))
ed.save("demo.atrb")

parsed = AtrbParser.parse_file("demo.atrb")
print(len(parsed.content))  # -> 2
```

## FAQ

- Do I have to use builders? No. You can hand-craft YAML or use your own Templateer models. Builders are convenience wrappers around the same templates.
- Can I define my own block types? Yes. Unknown types parse as `BaseBlock`. For first-class support, add a typed model + props + templates and extend the union.
- Is write atomic? `DocumentEditor.save()` writes to the target path directly. Wrap at a higher level if you need temp-file atomicity.
- Windows/macOS/Linux? It is pure Python; no platform-specific dependencies.

## Links

- Atuin Desktop: https://github.com/atuinsh/desktop and https://man.atuin.sh/
- Templateer (concepts this library builds on): models + discovery abstraction
