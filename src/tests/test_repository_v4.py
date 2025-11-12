# path: tests/test_repository_v4.py
from uuid import uuid4
from pytuin_desktop import InMemoryDocumentRepository, DocumentEditor
from templateer import TemplateModel

PARA = 'id: {{ block_id }}\ntype: paragraph\nprops: {}\ncontent: []\nchildren: []\n'

class Para(TemplateModel):
    __template__ = PARA
    block_id: str

def test_repo_lifecycle(tmp_path):
    repo = InMemoryDocumentRepository()
    ed = DocumentEditor.create("RepoDoc", repository=repo)
    ed.add_block(Para(block_id=str(uuid4())))
    fp = tmp_path / "r.atrb"
    ed.save(fp)
    items = repo.list()
    assert len(items) == 1
    back = repo.get(str(items[0].id))
    assert back and back.name == "RepoDoc"
