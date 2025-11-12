# path: pytuin_desktop/discovery.py
"""Template discovery for .atrb templates."""
from __future__ import annotations
import os, time
from pathlib import Path
from types import SimpleNamespace
from typing import Union, Optional
from logging import Logger
from templateer import discover_templates as _discover_templates
from .logger import logger as _default_logger
from .errors import TemplateDiscoveryError

_TEMPLATE_CACHE: dict[str, SimpleNamespace] = {}

def _resolve_template_dir(template_dir: Optional[Union[str, Path]]) -> Path:
    if template_dir is not None:
        return Path(template_dir).absolute()
    env = os.getenv("PYTUIN_TEMPLATE_DIR")
    if env:
        return Path(env).absolute()
    return Path(".templateer").absolute()

def clear_template_cache() -> None:
    _TEMPLATE_CACHE.clear()

def load_atrb_templates(template_dir: Union[str, Path, None] = None, *, cache: bool = True, logger: Logger | None = None) -> SimpleNamespace:
    lg = logger or _default_logger
    resolved = _resolve_template_dir(template_dir)
    key = str(resolved)
    if not resolved.exists():
        lg.error("discovery.missing_dir", extra={"dir": key})
        raise TemplateDiscoveryError(f"Template directory not found: {resolved}")
    if cache and key in _TEMPLATE_CACHE:
        ns = _TEMPLATE_CACHE[key]
        lg.debug("discovery.cache_hit", extra={"dir": key, "count": len(vars(ns)), "cache": True})
        return ns
    t0 = time.perf_counter()
    ns = _discover_templates(resolved)
    if cache:
        _TEMPLATE_CACHE[key] = ns
    lg.info("discovery.loaded", extra={"dir": key, "count": len(vars(ns)), "cache": cache, "duration_ms": int((time.perf_counter()-t0)*1000)})
    return ns
