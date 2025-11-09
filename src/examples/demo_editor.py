#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pydantic>=2.0.0",
#     "pyyaml>=6.0.0",
# ]
# ///

# demo_editor.py
"""Demo script showing document editing capabilities."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pytuin_desktop.editor import DocumentEditor
from pytuin_desktop.builders import BlockBuilder


test_dir = "/home/andrew/Documents/Projects/pytuin-desktop/src/tests"
atuin_test_output_dir = "/home/andrew/Documents/Atuin Runbooks/03_Libraries/Testing"

block_spec = f"{test_dir}/Block_Spec.atrb"
demo_output = f"{atuin_test_output_dir}/Edited_spec.atrb"


def demo_add_blocks():
    """Demo adding blocks to existing document."""
    print("=== Demo: Adding Blocks ===\n")

    editor = DocumentEditor.from_file(block_spec)
    print(f"Original document: {len(editor)} blocks\n")

    # Add a new heading at the end
    editor.add_block(BlockBuilder.heading("My New Section", level=2))

    # Add a paragraph after the new heading
    editor.add_block(
        BlockBuilder.paragraph("This is a new paragraph with some content.")
    )

    # Add a code editor at a specific position
    editor.add_block(
        BlockBuilder.editor(
            name="My Script",
            code="print('Hello, world!')",
            language="python",
        ),
        index=5,
    )

    print(f"After additions: {len(editor)} blocks")
    print(f"Block at index 5: {type(editor.get_block(5)).__name__}\n")

    # Save to new file
    editor.save(demo_output)
    print("Saved to modified_spec.atrb\n")


def demo_reorder_blocks():
    """Demo reordering blocks in document."""
    print("=== Demo: Reordering Blocks ===\n")

    editor = DocumentEditor.from_file(block_spec)

    # Show original order
    print("First 5 blocks:")
    for i in range(5):
        block = editor.get_block(i)
        print(f"  {i}: {type(block).__name__}")

    # Move a block
    editor.move_block(from_index=0, to_index=3)

    print("\nAfter moving block 0 to position 3:")
    for i in range(5):
        block = editor.get_block(i)
        print(f"  {i}: {type(block).__name__}")

    # Swap two blocks
    editor.swap_blocks(1, 2)

    print("\nAfter swapping blocks 1 and 2:")
    for i in range(5):
        block = editor.get_block(i)
        print(f"  {i}: {type(block).__name__}")

    print()


def demo_create_from_template():
    """Demo creating new document from template."""
    print("=== Demo: Create from Template ===\n")

    project_name = "My Project"
    # Create new doc based on Block_Spec
    editor = DocumentEditor.from_template(block_spec, project_name)

    # Remove most blocks to start fresh
    while len(editor) > 3:
        editor.remove_block_at(-1)

    # Add our own content
    editor.add_block(BlockBuilder.heading("Project Setup", level=1))
    editor.add_block(BlockBuilder.paragraph("This project demonstrates..."))
    editor.add_block(BlockBuilder.horizontal_rule())
    editor.add_block(BlockBuilder.heading("Installation", level=2))
    editor.add_block(BlockBuilder.code_block("pip install my-package", language="bash"))
    editor.add_block(BlockBuilder.heading("Usage", level=2))

    # Add a toggle with nested content
    toggle = BlockBuilder.toggle_item(
        "Advanced Options",
        children=[
            BlockBuilder.paragraph("These are advanced configuration options."),
            BlockBuilder.bullet_list_item("Option 1"),
            BlockBuilder.bullet_list_item("Option 2"),
        ],
    )
    editor.add_block(toggle)

    print(f"Created new document: {editor.document.name}")
    print(f"Total blocks: {len(editor)}\n")

    # Save
    editor.save(f"{atuin_test_output_dir}/{project_name}.atrb")
    print("Saved to my_project.atrb\n")


def demo_create_empty():
    """Demo creating document from scratch."""
    print("=== Demo: Create Empty Document ===\n")

    editor = DocumentEditor.create("Quick Notes")

    # Build a simple document
    editor.add_block(BlockBuilder.heading("Quick Notes", level=1))
    editor.add_block(BlockBuilder.paragraph("Today's tasks:"))

    # Checklist
    editor.add_block(BlockBuilder.checklist_item("Review pull requests", checked=True))
    editor.add_block(BlockBuilder.checklist_item("Update documentation", checked=False))
    editor.add_block(BlockBuilder.checklist_item("Deploy to staging", checked=False))

    editor.add_block(BlockBuilder.horizontal_rule())
    editor.add_block(BlockBuilder.quote("Remember to take breaks!"))

    print(f"Created: {editor.document.name}")
    print(f"Blocks: {len(editor)}\n")

    # Show YAML output instead of saving
    print("Generated YAML:")
    print(editor.to_string()[:500] + "...\n")


def main():
    demo_add_blocks()
    demo_reorder_blocks()
    demo_create_from_template()
    demo_create_empty()

    print("=== All demos complete! ===")
    print(f"\nGenerated files in {test_dir}/:")
    print("  - modified_spec.atrb")
    print("  - my_project.atrb")


if __name__ == "__main__":
    main()
