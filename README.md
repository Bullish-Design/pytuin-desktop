# README.md
# atrb-parser

Parser for Atuin Desktop `.atrb` files into Pydantic models.

## Installation

```bash
uv pip install -e .
```

## Usage

```python
from atrb_parser import AtrbParser

# Parse from file
doc = AtrbParser.parse_file("path/to/file.atrb")

# Parse from string
content = """
id: 019a609e-dfe1-7330-8398-81906ac3b0f1
name: Example
version: 1
content: []
"""
doc = AtrbParser.parse_string(content)

# Access typed blocks
for block in doc.content:
    print(f"Block type: {type(block).__name__}")
    print(f"Block ID: {block.id}")
```

## Block Types

All Atuin Desktop block types are supported:

- Text blocks: `ParagraphBlock`, `HeadingBlock`, `QuoteBlock`
- Lists: `BulletListItemBlock`, `NumberedListItemBlock`, `CheckListItemBlock`, `ToggleListItemBlock`
- Code: `EditorBlock`, `CodeBlockBlock`, `ScriptBlock`, `RunBlock`
- Data: `SQLiteBlock`, `PostgresBlock`, `HttpBlock`
- Media: `ImageBlock`, `VideoBlock`, `AudioBlock`, `FileBlock`
- UI: `DropdownBlock`, `DirectoryBlock`, `TableBlock`
- Variables: `VarBlock`, `LocalVarBlock`, `EnvBlock`, `VarDisplayBlock`
- Other: `HorizontalRuleBlock`

## Development

Run tests:
```bash
uv run pytest
```
