# path: src/tests/test_builders_return_enums.py
import yaml
from pytuin_desktop.builders import BlockBuilder
from pytuin_desktop.enums import TextAlignment, ColorToken

def test_heading_builder_with_enum_instances():
    heading = BlockBuilder.heading(text="Title", text_alignment=TextAlignment.right, text_color=ColorToken.accent)
    rendered = str(heading)
    assert "right" in rendered
    assert "accent" in rendered
