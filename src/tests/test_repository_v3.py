
from __future__ import annotations

from templateer import TemplateModel
from pytuin_desktop import DocumentEditor
from pytuin_desktop import InMemoryDocumentRepository


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


class ParagraphBlockTemplate(TemplateModel):
    __template__ = PARA_TMPL
    block_id: str
    text: str


def test_repo_save_list_get(tmp_path):
    repo = InMemoryDocumentRepository()
    ed = DocumentEditor.create("Repo Doc", repository=repo)
    ed.add_block(ParagraphBlockTemplate(block_id="00000000-0000-0000-0000-000000000001", text="hi"))

    out = tmp_path / "doc.atrb"
    ed.save(out)

    items = repo.list()
    assert len(items) == 1
    doc = repo.get(str(items[0].id))
    assert doc is not None
    assert doc.name == "Repo Doc"
    assert len(doc.content) == 1
