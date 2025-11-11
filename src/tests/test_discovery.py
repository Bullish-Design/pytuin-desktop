"""Step 10: Test template discovery wrapper."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import yaml

from pytuin_desktop import load_atrb_templates

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"

def test_load_atrb_templates_finds_core_templates():
    templates = load_atrb_templates(TEMPLATES_DIR)

    expected = [
        "EmptyDocumentTemplate",
        "DocumentTemplate",
        "TextStylesTemplate",
        "TextContentTemplate",
        "ParagraphBlockTemplate",
        "HeadingBlockTemplate",
        "HorizontalRuleTemplate",
        "ScriptBlockTemplate",
    ]
    missing = [name for name in expected if not hasattr(templates, name)]
    assert not missing, f"Missing templates: {missing}"

def test_can_instantiate_and_render_via_discovery():
    templates = load_atrb_templates(TEMPLATES_DIR)

    text = templates.TextContentTemplate(text="Discovery OK", styles=templates.TextStylesTemplate())
    para = templates.ParagraphBlockTemplate(block_id=str(uuid4()), content=[text])
    doc = templates.DocumentTemplate(document_id=str(uuid4()), name="Discovery Doc", version=1, blocks=[para])

    rendered = doc.render()
    data = yaml.safe_load(rendered)

    assert data["name"] == "Discovery Doc"
    assert data["content"][0]["type"] == "paragraph"
    assert data["content"][0]["content"][0]["text"] == "Discovery OK"
