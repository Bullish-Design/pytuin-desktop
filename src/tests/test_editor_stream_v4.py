# path: tests/test_editor_stream_v4.py
import io, yaml
from uuid import uuid4
from types import SimpleNamespace
from pathlib import Path
from pytuin_desktop import DocumentEditor, load_atrb_templates, AtrbParser

def test_create_and_render(monkeypatch):
    # Use a tiny dummy DocumentTemplate to avoid FS dependencies
    class Dummy:
        def __init__(self, **kw): self.kw = kw
        def render(self): return "name: %s\nversion: %s\ncontent: []\nid: %s\n" % (self.kw["name"], self.kw.get("version",1), self.kw.get("document_id","0000"))
    monkeypatch.setattr("pytuin_desktop.editor.load_atrb_templates", lambda *a, **k: SimpleNamespace(DocumentTemplate=Dummy))
    ed = DocumentEditor.create("Demo")
    text = ed.render()
    assert "Demo" in text

def test_write_to_stream_roundtrip(tmp_path: Path):
    ed = DocumentEditor.create("Stream Test")
    out = io.StringIO()
    ed.write_to_stream(out)
    text = out.getvalue()
    assert text.endswith("\n")
    # Parse back
    doc = AtrbParser.parse_stream(io.StringIO(text))
    assert doc.name == "Stream Test"
