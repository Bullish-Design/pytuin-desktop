import logging
from pathlib import Path
from types import SimpleNamespace

import pytuin_desktop as pd


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    def emit(self, record):
        self.records.append(record)


def test_get_logger_is_silent_and_idempotent(monkeypatch):
    monkeypatch.delenv("PYTUIN_LOG_LEVEL", raising=False)
    lg1 = pd.get_logger("pytuin.desktop.test")
    lg2 = pd.get_logger("pytuin.desktop.test")
    # one NullHandler only
    nulls = [h for h in lg1.handlers if isinstance(h, logging.NullHandler)]
    assert len(nulls) == 1
    assert lg1 is lg2
    assert lg1.propagate is False


def test_get_logger_env_level(monkeypatch):
    monkeypatch.setenv("PYTUIN_LOG_LEVEL", "INFO")
    lg = pd.get_logger("pytuin.desktop.level")
    assert lg.level == logging.INFO


def test_discovery_logs_loaded_and_cache_hit(monkeypatch, tmp_path):
    # stub template discovery to avoid filesystem dependency
    from pytuin_desktop import discovery as disc
    calls = {"n": 0}
    def fake_discover(_p):
        calls["n"] += 1
        return SimpleNamespace(DocumentTemplate=object)
    monkeypatch.setattr(disc, "_discover_templates", fake_discover)

    h = ListHandler()
    lg = pd.get_logger("pytuin.desktop.test.discovery")
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)  # ensure INFO logs are recorded

    disc.clear_template_cache()
    disc.load_atrb_templates(template_dir=tmp_path, cache=True, logger=lg)
    disc.load_atrb_templates(template_dir=tmp_path, cache=True, logger=lg)

    assert calls["n"] == 1
    msgs = [r.msg for r in h.records]
    assert "discovery.loaded" in msgs
    assert "discovery.cache_hit" in msgs


def test_parser_logs_parse_events(tmp_path):
    content = """id: 00000000-0000-0000-0000-000000000000
name: Demo
version: 1
content: []
"""
    f = tmp_path / "demo.atrb"
    f.write_text(content)

    h = ListHandler()
    lg = pd.get_logger("pytuin.desktop.test.parser")
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)  # capture info/debug

    doc = pd.AtrbParser.parse_file(f, logger=lg)
    assert doc.name == "Demo"
    msgs = [r.msg for r in h.records]
    assert "parser.parse_file" in msgs and "parser.parse_ok" in msgs


def test_editor_logs_basic_flow(monkeypatch, tmp_path):
    h = ListHandler()
    lg = pd.get_logger("pytuin.desktop.test.editor")
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)

    # Patch the symbol used within the editor module namespace
    from pytuin_desktop import editor as edmod
    class DummyDoc:
        def __init__(self, **kwargs): self.kw = kwargs
        def render(self): return "ok"
    monkeypatch.setattr(edmod, "load_atrb_templates", lambda *a, **k: SimpleNamespace(DocumentTemplate=DummyDoc))

    ed = pd.DocumentEditor.create("Demo", logger=lg)
    text = ed.render()
    assert text == "ok"
    out = tmp_path / "out.atrb"
    ed.save(out)
    msgs = {r.msg for r in h.records}
    assert {"editor.create","editor.render_start","editor.render_done","editor.save"} <= msgs
