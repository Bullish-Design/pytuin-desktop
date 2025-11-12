
import io
import uuid
import yaml
from pathlib import Path
from textwrap import dedent

import pytest

# Prefer the installed package name, but fall back to local modules if needed.
try:
    from pytuin_desktop.editor import DocumentEditor
    from pytuin_desktop.parser import AtrbParser
except Exception:  # pragma: no cover
    from editor import DocumentEditor  # type: ignore
    from parser import AtrbParser  # type: ignore

try:
    from templateer import TemplateModel
except Exception:  # pragma: no cover
    TemplateModel = object  # fallback to avoid NameError in collection


class DummyBlock(TemplateModel):
    """Minimal Templateer block that renders to a YAML mapping."""
    __template__ = "id: {{ id }}\ntype: {{ type }}\nprops: {{} }\ncontent: []\nchildren: []\n"
    id: str
    type: str = "paragraph"


def test_parser_parse_stream_roundtrip():
    doc_id = str(uuid.uuid4())
    yaml_text = f"""
    id: {doc_id}
    name: Example
    version: 3
    content:
      - id: {uuid.uuid4()}
        type: paragraph
        props: {{}}
        content: []
        children: []
    """
    stream = io.StringIO(yaml_text)
    doc = AtrbParser.parse_stream(stream)
    assert str(doc.id) == doc_id
    assert doc.name == "Example"
    assert doc.version == 3
    assert len(doc.content) == 1


def test_editor_write_to_stream_trailing_newline():
    ed = DocumentEditor.create(name="Streamy", version=3)
    out = io.StringIO()
    ed.write_to_stream(out)  # default ensure_trailing_newline=True
    text = out.getvalue()
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_editor_write_to_stream_preserves_existing_and_appends_new(tmp_path: Path):
    # Create an existing .atrb file with one block.
    doc_id = str(uuid.uuid4())
    existing_yaml = f"""
    id: {doc_id}
    name: Base
    version: 3
    content:
      - id: {uuid.uuid4()}
        type: heading
        props: {{ level: 1, text: "Hello" }}
        content: []
        children: []
    """
    src = tmp_path / "base.atrb"
    src.write_text(dedent(existing_yaml).strip() + "\n", encoding="utf-8")

    # Load with preservation of parsed blocks.
    ed = DocumentEditor.from_file_with_blocks(src)

    # Append a new block via a minimal TemplateModel implementation.
    new_block = DummyBlock(id=str(uuid.uuid4()), type="paragraph")
    ed.add_block(new_block)

    # Write to a stream and inspect merged result.
    out = io.StringIO()
    ed.write_to_stream(out)
    merged = yaml.safe_load(out.getvalue())

    assert merged["id"] == doc_id
    assert merged["name"] == "Base"
    assert merged["version"] == 3
    assert isinstance(merged.get("content"), list)
    # Should have original 1 + appended 1
    assert len(merged["content"]) == 2

    # First block is the original heading, second is the appended paragraph
    assert merged["content"][0]["type"] == "heading"
    assert merged["content"][1]["type"] == "paragraph"
