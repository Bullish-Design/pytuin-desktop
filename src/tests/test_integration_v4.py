# path: tests/test_integration_v4.py
from uuid import uuid4
from templateer import TemplateModel
from pytuin_desktop import DocumentEditor, AtrbParser, AtrbValidator

PARA = '''
id: "{{ block_id }}"
type: paragraph
props: { }
content:
  - type: text
    text: {{ text|tojson }}
    styles: { bold: false, italic: false, underline: false, strikethrough: false, code: false }
children: []
'''

HEAD = '''
id: "{{ block_id }}"
type: heading
props: { level: {{ level }} }
content:
  - type: text
    text: {{ text|tojson }}
    styles: { bold: false, italic: false, underline: false, strikethrough: false, code: false }
children: []
'''

class P(TemplateModel):
    __template__ = PARA
    block_id: str
    text: str

class H(TemplateModel):
    __template__ = HEAD
    block_id: str
    text: str
    level: int = 1

def test_e2e_build_save_parse_validate(tmp_path):
    ed = DocumentEditor.create("E2E")
    ed.add_block(H(block_id=str(uuid4()), text="Title", level=2))
    ed.add_block(P(block_id=str(uuid4()), text="Hello"))
    fp = tmp_path / "e2e.atrb"
    ed.save(fp)
    doc = AtrbParser.parse_file(fp)
    AtrbValidator.validate(doc)
    assert doc.name == "E2E" and len(doc.content) == 2
