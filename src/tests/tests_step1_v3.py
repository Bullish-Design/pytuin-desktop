"""v3 Step 1: discovery parameter + cache tests."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
import pytest

from pytuin_desktop import load_atrb_templates, clear_template_cache, DocumentEditor, BlockBuilder

TEMPLATES_DIR = Path(__file__).parent.parent.parent / ".templateer"


def test_discovery_with_explicit_dir_finds_expected_templates():
    clear_template_cache()
    templates = load_atrb_templates(TEMPLATES_DIR)
    assert hasattr(templates, "DocumentTemplate")
    assert hasattr(templates, "ParagraphBlockTemplate")
    assert hasattr(templates, "TextStylesTemplate")


def test_env_fallback_when_arg_none(monkeypatch):
    clear_template_cache()
    monkeypatch.setenv("PYTUIN_TEMPLATE_DIR", str(TEMPLATES_DIR))
    templates = load_atrb_templates(None)
    assert hasattr(templates, "HeadingBlockTemplate")


def test_cache_hit_and_clear(monkeypatch):
    clear_template_cache()
    monkeypatch.delenv("PYTUIN_TEMPLATE_DIR", raising=False)

    t1 = load_atrb_templates(TEMPLATES_DIR)   # populate cache
    t2 = load_atrb_templates(TEMPLATES_DIR)   # should be same object if cached
    assert t1 is t2

    clear_template_cache()
    t3 = load_atrb_templates(TEMPLATES_DIR)   # new object after clear
    assert t1 is not t3


def test_thread_template_dir_through_editor_and_builders(tmp_path):
    clear_template_cache()
    editor = DocumentEditor.create("Step1 Test", template_dir=TEMPLATES_DIR)
    # use builders with explicit template_dir
    heading = BlockBuilder.heading("Title", level=1, template_dir=TEMPLATES_DIR)
    para = BlockBuilder.paragraph("hello", template_dir=TEMPLATES_DIR)

    editor.add_block(heading).add_block(para)

    out = tmp_path / "step1.atrb"
    editor.save(out)

    data = yaml.safe_load(out.read_text())
    assert data["name"] == "Step1 Test"
    assert len(data["content"]) == 2
    assert data["content"][0]["type"] == "heading"
    assert data["content"][1]["type"] == "paragraph"
