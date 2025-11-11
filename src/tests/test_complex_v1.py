# tests/test_v1_complex.py
"""Test v1: Complex multi-block documents (Step 9)."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml

from templateer import discover_templates
from pytuin_desktop import AtrbParser


TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"
templates = discover_templates(TEMPLATES_DIR)

DocumentTemplate = templates.DocumentTemplate
HeadingBlockTemplate = templates.HeadingBlockTemplate
ParagraphBlockTemplate = templates.ParagraphBlockTemplate
HorizontalRuleTemplate = templates.HorizontalRuleTemplate
ScriptBlockTemplate = templates.ScriptBlockTemplate
TextContentTemplate = templates.TextContentTemplate
TextStylesTemplate = templates.TextStylesTemplate

TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def test_generate_complete_runbook():
    """Generate a complete multi-block runbook with 10 blocks."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    # Title
    title_text = TextContentTemplate(text="Server Setup Runbook", styles=TextStylesTemplate())
    title = HeadingBlockTemplate(block_id=str(uuid4()), level=1, content=[title_text])

    # Introduction
    intro_text = TextContentTemplate(
        text="This runbook guides you through server setup and configuration.",
        styles=TextStylesTemplate(),
    )
    intro = ParagraphBlockTemplate(block_id=str(uuid4()), content=[intro_text])

    # Divider
    divider = HorizontalRuleTemplate(block_id=str(uuid4()))

    # Prerequisites heading
    prereq_text = TextContentTemplate(text="Prerequisites", styles=TextStylesTemplate(bold=True))
    prereq_heading = HeadingBlockTemplate(block_id=str(uuid4()), level=2, content=[prereq_text])

    # Prerequisites paragraph
    prereq_para_text = TextContentTemplate(
        text="Before starting, ensure you have root access and network connectivity.",
        styles=TextStylesTemplate(),
    )
    prereq_para = ParagraphBlockTemplate(block_id=str(uuid4()), content=[prereq_para_text])

    # Installation heading
    install_heading_text = TextContentTemplate(text="Installation", styles=TextStylesTemplate())
    install_heading = HeadingBlockTemplate(block_id=str(uuid4()), level=2, content=[install_heading_text])

    # Update script
    update_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="update_system",
        code="apt-get update && apt-get upgrade -y",
        interpreter="bash",
    )

    # Install Docker script
    docker_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="install_docker",
        code="curl -fsSL https://get.docker.com | sh\nsystemctl enable docker\nsystemctl start docker",
        interpreter="bash",
    )

    # Verification heading
    verify_heading_text = TextContentTemplate(text="Verification", styles=TextStylesTemplate())
    verify_heading = HeadingBlockTemplate(block_id=str(uuid4()), level=2, content=[verify_heading_text])

    # Verify script
    verify_script = ScriptBlockTemplate(
        block_id=str(uuid4()),
        name="verify_installation",
        code="docker --version\nsystemctl status docker",
        interpreter="bash",
    )

    # Build document
    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Complete Server Setup Runbook",
        version=1,
        blocks=[
            title,
            intro,
            divider,
            prereq_heading,
            prereq_para,
            install_heading,
            update_script,
            docker_script,
            verify_heading,
            verify_script,
        ],
    )

    # Write and validate
    output_path = TEST_OUTPUT_DIR / "10_complete_runbook.atrb"
    doc.write_to(output_path)

    # Parse to validate
    parsed_doc = AtrbParser.parse_file(output_path)

    assert len(parsed_doc.content) == 10
    assert parsed_doc.content[0].type == "heading"
    assert parsed_doc.content[1].type == "paragraph"
    assert parsed_doc.content[2].type == "horizontal_rule"
    assert parsed_doc.content[6].type == "script"
    assert parsed_doc.content[9].type == "script"


def test_document_with_mixed_styles():
    """Generate document with various inline text styles in a single paragraph."""
    TEST_OUTPUT_DIR.mkdir(exist_ok=True)

    # Paragraph with mixed inline styles
    bold = TextContentTemplate(text="Bold text ", styles=TextStylesTemplate(bold=True))
    italic = TextContentTemplate(text="italic text ", styles=TextStylesTemplate(italic=True))
    code = TextContentTemplate(text="inline code ", styles=TextStylesTemplate(code=True))
    normal = TextContentTemplate(text="normal text", styles=TextStylesTemplate())

    mixed_para = ParagraphBlockTemplate(block_id=str(uuid4()), content=[bold, italic, code, normal])

    doc = DocumentTemplate(
        document_id=str(uuid4()),
        name="Mixed Styles Test",
        version=1,
        blocks=[mixed_para],
    )

    output_path = TEST_OUTPUT_DIR / "11_mixed_styles.atrb"
    doc.write_to(output_path)

    # Validate via parser
    parsed = AtrbParser.parse_file(output_path)
    assert len(parsed.content) == 1
    # Parser should preserve content array (not validating inner style schema here)
    assert isinstance(parsed.content[0].content, list)
    assert len(parsed.content[0].content) == 4
