# path: src/tests/test_document_diff_v4.py
from uuid import uuid4
from pytuin_desktop.models import AtrbDocument, BaseBlock
from pytuin_desktop.diff import DocumentDiffer, ChangeType

def test_diff_added_removed_modified_and_moved():
    a1 = BaseBlock(id=uuid4(), type="heading", props={"level": 1})
    a2 = BaseBlock(id=uuid4(), type="paragraph", props={"text_color": "default"})
    a3 = BaseBlock(id=uuid4(), type="paragraph", props={"text_color": "muted"})
    doc1 = AtrbDocument(id=uuid4(), name="Doc", version=1, content=[a1, a2, a3])

    # Modify a2, remove a1, add b4, move a3 to index 0
    b2 = BaseBlock(id=a2.id, type="paragraph", props={"text_color": "primary"})
    b3 = BaseBlock(id=a3.id, type="paragraph", props={"text_color": "muted"})
    b4 = BaseBlock(id=uuid4(), type="horizontal_rule", props={})
    doc2 = AtrbDocument(id=uuid4(), name="Doc", version=1, content=[b3, b2, b4])

    diff = DocumentDiffer.diff(doc1, doc2)
    kinds = [c.change_type for c in diff.changes]
    assert ChangeType.REMOVED in kinds
    assert ChangeType.ADDED in kinds
    assert ChangeType.MODIFIED in kinds
    assert ChangeType.MOVED in kinds
