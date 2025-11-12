# path: src/tests/test_validation_caching_v4.py
from pytuin_desktop import DocumentEditor, BlockBuilder
from pytuin_desktop.validator import AtrbValidator

def test_validation_cached_once_per_modification(monkeypatch):
    calls = {"n": 0}
    orig = AtrbValidator.validate
    def wrapped(doc):
        calls["n"] += 1
        return orig(doc)
    monkeypatch.setattr(AtrbValidator, "validate", staticmethod(wrapped))

    ed = DocumentEditor.create("CacheTest")
    ed.add_block(BlockBuilder.paragraph("One"))
    # First build triggers validation
    _ = ed.render()  # render does not validate; ensure next write validates
    pyd = ed._build_and_validate_document()
    assert calls["n"] == 1

    # Second call without mutations should use cached validation
    _ = ed._build_and_validate_document()
    assert calls["n"] == 1

    # After a mutation, it validates again
    ed.add_block(BlockBuilder.paragraph("Two"))
    _ = ed._build_and_validate_document()
    assert calls["n"] == 2
