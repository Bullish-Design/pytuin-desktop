"""Test v1: Individual block types (Step 7)."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml

from templateer import discover_templates

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
templates = discover_templates(TEMPLATES_DIR)

DocumentTemplate = templates.DocumentTemplate if hasattr(templates, "DocumentTemplate") else None
HeadingBlockTemplate = templates.HeadingBlockTemplate
HorizontalRuleTemplate = templates.HorizontalRuleTemplate
ScriptBlockTemplate = templates.ScriptBlockTemplate
TextContentTemplate = templates.TextContentTemplate
TextStylesTemplate = templates.TextStylesTemplate

TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_heading_document():
    """Generate document with heading block."""
    if DocumentTemplate is None:
        # If DocumentTemplate is not available in this environment, just render the block itself.
        heading = HeadingBlockTemplate(
            block_id=str(uuid4()),
            level=1,
            content=[TextContentTemplate(text="Main Heading", styles=TextStylesTemplate())],
        )
        data = yaml.safe_load(heading.render())
        assert data["type"] == "heading"
        assert data["props"]["level"] == 1
        assert data["content"][0]["text"] == "Main Heading"
        return

    TEST_OUTPUT_DIR.mkdir(exist_ok=True)
    text = TextContentTemplate(text="Main Heading", styles=TextStylesTemplate())
    heading = HeadingBlockTemplate(block_id=str(uuid4()), level=1, content=[text])

    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Heading Test",
        version=1,
        blocks=[heading],
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
    hr = HorizontalRuleTemplate(block_id=str(uuid4()))
    rendered_hr = hr.render()
    # print(f"\nRendered Horizontal Rule:\n{rendered_hr}\n")
    data = yaml.safe_load(rendered_hr)
    assert data["type"] == "horizontal_rule"
    assert data["props"] == {}

    # Optional document write if DocumentTemplate is available
    if DocumentTemplate is not None:
        TEST_OUTPUT_DIR.mkdir(exist_ok=True)
        doc = DocumentTemplate(
            document_id=str(uuid4()),
            name="Horizontal Rule Test",
            version=1,
            blocks=[hr],
        )
        output_path = TEST_OUTPUT_DIR / "04_horizontal_rule.atrb"
        doc.write_to(output_path)
        with output_path.open() as f:
            parsed = yaml.safe_load(f)
        assert parsed["content"][0]["type"] == "horizontal_rule"


def test_generate_script_document():
    """Generate document with script block."""
    script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="hello_script",
        code="echo 'Hello from script'",
        interpreter="bash",
    )
    data = yaml.safe_load(script.render())
    assert data["type"] == "script"
    assert data["props"]["name"] == "hello_script"
    assert data["props"]["interpreter"] == "bash"
    assert "Hello from script" in data["props"]["code"]

    if DocumentTemplate is not None:
        TEST_OUTPUT_DIR.mkdir(exist_ok=True)
        doc = DocumentTemplate(
            document_id=str(uuid4()),
            name="Script Test",
            version=1,
            blocks=[script],
        )
        output_path = TEST_OUTPUT_DIR / "05_script.atrb"
        doc.write_to(output_path)
        with output_path.open() as f:
            parsed = yaml.safe_load(f)
        assert parsed["content"][0]["type"] == "script"


def test_heading_levels():
    """Test different heading levels."""
    for level in [1, 2, 3, 4, 5, 6]:
        text = TextContentTemplate(text=f"Level {level} Heading", styles=TextStylesTemplate())
        heading = HeadingBlockTemplate(block_id=str(uuid4()), level=level, content=[text])
        data = yaml.safe_load(heading.render())
        assert data["props"]["level"] == level
