# tests/test_integration_v1.py
"""Integration tests for complete Pytuin Desktop workflows (Step 13)."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from pytuin_desktop import (
    DocumentEditor,
    BlockBuilder,
    load_atrb_templates,
    AtrbParser,
)

TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_full_workflow_simple():
    """Create a small doc via builders → save → parse."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    editor = (
        DocumentEditor.create("Simple Workflow Test")
        .add_block(BlockBuilder.heading("Title"))
        .add_block(BlockBuilder.paragraph("Content"))
    )

    out = TEST_OUTPUT_DIR / "40_simple_workflow.atrb"
    editor.save(out)

    doc = AtrbParser.parse_file(out)
    assert doc.name == "Simple Workflow Test"
    assert len(doc.content) == 2
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"


def test_full_workflow_complex():
    """Mix builders with hand-crafted templates in one document."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    templates = load_atrb_templates()
    editor = DocumentEditor.create("Complex Workflow Test")

    # Builder-made heading
    editor.add_block(BlockBuilder.heading("Deployment Guide", level=1))

    # Custom paragraph composed directly from templates
    bold = templates.TextContentTemplate(
        text="Important: ",
        styles=templates.TextStylesTemplate(bold=True),
    )
    normal = templates.TextContentTemplate(
        text="Read all steps carefully.",
        styles=templates.TextStylesTemplate(),
    )
    custom_para = templates.ParagraphBlockTemplate(
        block_id=str(uuid4()),  # keep parser happy (UUID)
        content=[bold, normal],
    )
    editor.add_block(custom_para)

    # More blocks
    editor.add_block(BlockBuilder.horizontal_rule())
    editor.add_block(BlockBuilder.heading("Steps", level=2))
    editor.add_block(
        BlockBuilder.script(
            name="deploy",
            code="kubectl apply -f deployment.yaml",
            interpreter="bash",
        )
    )

    out = TEST_OUTPUT_DIR / "41_complex_workflow.atrb"
    editor.save(out)

    doc = AtrbParser.parse_file(out)
    assert doc.name == "Complex Workflow Test"
    assert len(doc.content) == 5
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"
    assert doc.content[2].type == "horizontal_rule"
    assert doc.content[3].type == "heading"
    assert doc.content[4].type == "script"


def test_template_discovery_and_direct_usage():
    """Build a doc using discovered templates only."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    T = load_atrb_templates()
    title = T.HeadingBlockTemplate(
        block_id=str(uuid4()),
        level=1,
        content=[
            T.TextContentTemplate(
                text="Direct Template Usage",
                styles=T.TextStylesTemplate(),
            )
        ],
    )

    doc_tpl = T.DocumentTemplate(
        document_id=str(uuid4()),
        name="Template Direct Usage Test",
        version=1,
        blocks=[title],
    )

    out = TEST_OUTPUT_DIR / "42_template_direct.atrb"
    doc_tpl.write_to(out)

    parsed = AtrbParser.parse_file(out)
    assert parsed.name == "Template Direct Usage Test"
    assert len(parsed.content) == 1
    assert parsed.content[0].type == "heading"
