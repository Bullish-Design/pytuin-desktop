# path: tests/test_discovery_v4.py
from types import SimpleNamespace
from pathlib import Path
from uuid import uuid4
import yaml
import pytest

from pytuin_desktop import load_atrb_templates, clear_template_cache

def test_load_discovers_core_templates(monkeypatch, tmp_path):
    clear_template_cache()
    from types import SimpleNamespace
    from pytuin_desktop import discovery as disc
    monkeypatch.setattr(disc, "_discover_templates", lambda p: SimpleNamespace(
        DocumentTemplate=object,
        ParagraphBlockTemplate=object,
        TextContentTemplate=object,
        TextStylesTemplate=object,
    ))
    T = load_atrb_templates(template_dir=tmp_path)
    assert hasattr(T, "DocumentTemplate")
    assert hasattr(T, "ParagraphBlockTemplate")
    assert hasattr(T, "TextContentTemplate")
    assert hasattr(T, "TextStylesTemplate")

def test_cache_hit(monkeypatch, tmp_path):
    from pytuin_desktop import discovery as disc
    calls = {"n": 0}
    def fake(_p): calls["n"] += 1; return SimpleNamespace(DocumentTemplate=object)
    monkeypatch.setattr(disc, "_discover_templates", fake)
    clear_template_cache()
    disc.load_atrb_templates(template_dir=tmp_path, cache=True)
    disc.load_atrb_templates(template_dir=tmp_path, cache=True)
    assert calls["n"] == 1
