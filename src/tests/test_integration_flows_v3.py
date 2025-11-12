
from __future__ import annotations

from io import StringIO
from uuid import uuid4
from templateer import TemplateModel
from pytuin_desktop import AtrbParser, AtrbValidator, DocumentEditor


PARA_TMPL = """
id: "{{ block_id }}"
type: paragraph
props: { }
content:
  - type: text
    text: {{ text|tojson }}
    styles:
      bold: false
      italic: false
      underline: false
      strikethrough: false
      code: false
children: []
"""

HEAD_TMPL = """
id: "{{ block_id }}"
type: heading
props:
  level: {{ level }}
content:
  - type: text
    text: {{ text|tojson }}
    styles: { bold: false, italic: false, underline: false, strikethrough: false, code: false }
children: []
"""


class ParagraphBlockTemplate(TemplateModel):
    __template__ = PARA_TMPL
    block_id: str
    text: str


class HeadingBlockTemplate(TemplateModel):
    __template__ = HEAD_TMPL
    block_id: str
    text: str
    level: int = 1


def _mk_doc(editor_name: str):
    ed = DocumentEditor.create(editor_name)
    ed.add_block(HeadingBlockTemplate(block_id=str(uuid4()), text="Title", level=2))
    ed.add_block(ParagraphBlockTemplate(block_id=str(uuid4()), text="Hello"))
    return ed


def test_flow_create_add_write_parse_validate(tmp_path):
    ed = _mk_doc("Flow1")
    out = tmp_path / "doc1.atrb"
    ed.save(out)

    doc = AtrbParser.parse_file(out)
    AtrbValidator.validate(doc)
    assert doc.name == "Flow1"
    assert len(doc.content) == 2


def test_flow_parse_existing_append_write_reparse(tmp_path):
    ed = _mk_doc("Flow2")
    out = tmp_path / "doc2.atrb"
    ed.save(out)

    ed2 = DocumentEditor.from_file_with_blocks(out)
    ed2.add_block(ParagraphBlockTemplate(block_id=str(uuid4()), text="Appended"))
    ed2.save(out)

    doc = AtrbParser.parse_file(out)
    assert len(doc.content) == 3
    assert doc.content[0].type == "heading"
    assert doc.content[1].type == "paragraph"
    assert doc.content[2].type == "paragraph"


def test_flow_stdin_stdout_streaming_transform():
    ed = _mk_doc("Flow3")
    sio = StringIO()
    ed.write_to_stream(sio)
    text = sio.getvalue()
    assert text.endswith("\n")

    sio2 = StringIO(text)
    doc = AtrbParser.parse_stream(sio2)
    assert doc.name == "Flow3"
    assert len(doc.content) >= 2
