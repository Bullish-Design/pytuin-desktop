# path: tests/test_logger_v4.py
import logging
from types import SimpleNamespace
from pytuin_desktop import get_logger
from pytuin_desktop import discovery as disc

class Collect(logging.Handler):
    def __init__(self): super().__init__(); self.msgs=[] 
    def emit(self, r): self.msgs.append(r.msg)

def test_logger_idempotent_and_env(monkeypatch, tmp_path):
    monkeypatch.delenv("PYTUIN_LOG_LEVEL", raising=False)
    lg1 = get_logger("x.y")
    lg2 = get_logger("x.y")
    assert lg1 is lg2 and lg1.propagate is False
    monkeypatch.setenv("PYTUIN_LOG_LEVEL", "INFO")
    lg3 = get_logger("x.z")
    assert lg3.level == logging.INFO

def test_discovery_logs(monkeypatch, tmp_path):
    calls = {"n":0}
    def fake(p):
        calls["n"] += 1
        return SimpleNamespace(DocumentTemplate=object)
    monkeypatch.setattr(disc, "_discover_templates", fake)
    lg = get_logger("disc.test")
    h = Collect()
    lg.addHandler(h); lg.setLevel(logging.DEBUG)
    disc.clear_template_cache()
    disc.load_atrb_templates(tmp_path, cache=True, logger=lg)
    disc.load_atrb_templates(tmp_path, cache=True, logger=lg)
    assert calls["n"] == 1
    assert "discovery.loaded" in h.msgs and "discovery.cache_hit" in h.msgs
