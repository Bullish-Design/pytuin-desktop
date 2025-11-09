#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pydantic>=2.0.0",
#     "pyyaml>=6.0.0",
# ]
# ///

# demo.py
"""Demo script showing atrb-parser usage."""

from __future__ import annotations

from pathlib import Path
import sys

# Add src to path for demo purposes
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pytuin_desktop import AtrbParser
from pytuin_desktop.models import (
    HeadingBlock,
    EditorBlock,
    ToggleListItemBlock,
    ParagraphBlock,
)


block_spec = "/home/andrew/Documents/Projects/pytuin-desktop/src/tests/Block_Spec.atrb"


def main():
    # Parse the Block_Spec.atrb file
    doc = AtrbParser.parse_file(block_spec)

    print(f"Document: {doc.name}")
    print(f"Version: {doc.version}")
    print(f"Total blocks: {len(doc.content)}\n")

    # Show first heading
    first_heading = next(b for b in doc.content if isinstance(b, HeadingBlock))
    print(f"First heading: {first_heading.content[0].text}")
    print(f"  Level: {first_heading.props.level}\n")

    # Show editor blocks
    editor_blocks = [b for b in doc.content if isinstance(b, EditorBlock)]
    print(f"Found {len(editor_blocks)} editor block(s):")
    for editor in editor_blocks:
        print(f"  - {editor.props.name} ({editor.props.language})")
        print(f"    Code: {editor.props.code[:50]}...\n")

    # Show nested toggles
    toggles = [b for b in doc.content if isinstance(b, ToggleListItemBlock)]
    if toggles:
        print(f"Found {len(toggles)} toggle block(s)")
        first_toggle = toggles[0]
        print(f"  First toggle: {first_toggle.content[0].text}")
        print(f"  Has {len(first_toggle.children)} children\n")

    # Show empty blocks
    empty_paragraphs = [
        b for b in doc.content if isinstance(b, ParagraphBlock) and not b.content
    ]
    print(f"Found {len(empty_paragraphs)} empty paragraph(s)\n")

    # Type checking works!
    for block in doc.content[:5]:
        if isinstance(block, HeadingBlock):
            # IDE knows about .props.level
            print(f"Heading level {block.props.level}")
        elif isinstance(block, EditorBlock):
            # IDE knows about .props.language
            print(f"Editor in {block.props.language}")


if __name__ == "__main__":
    main()
