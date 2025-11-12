"""Template discovery for .atrb templates (v3 Step 1 & Step 2: logging)."""
from __future__ import annotations

import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Union, Optional
from logging import Logger

from templateer import discover_templates as _discover_templates
from .logger import get_logger, logger as _default_logger
from .errors import TemplateDiscoveryError

# Internal cache keyed by absolute directory path string
_TEMPLATE_CACHE: dict[str, SimpleNamespace] = {}

def _resolve_template_dir(template_dir: Optional[Union[str, Path]]) -> Path:
    """Resolve the directory to search in precedence:
    explicit arg > env PYTUIN_TEMPLATE_DIR > default '.templateer'.
    """
    if template_dir is not None:
        return Path(template_dir).absolute()
    env = os.getenv("PYTUIN_TEMPLATE_DIR")
    if env:
        return Path(env).absolute()
    return Path(".templateer").absolute()

def clear_template_cache() -> None:
    """Clear the in-process template discovery cache."""
    _TEMPLATE_CACHE.clear()

def load_atrb_templates(
    template_dir: Union[str, Path, None] = None,
    *, cache: bool = True, logger: Logger | None = None
) -> SimpleNamespace:
    """Load .atrb Templateer templates from a directory.

    Args:
        template_dir: Directory containing .py template files.
                      Precedence: explicit arg > env PYTUIN_TEMPLATE_DIR > '.templateer'
        cache: If True, memoize results per absolute directory path.
        logger: Optional logger to receive discovery messages.

    Returns:
        SimpleNamespace where attributes are discovered TemplateModel subclasses.
    """
    lg = logger or _default_logger
    resolved = _resolve_template_dir(template_dir)
    key = str(resolved)

    if not resolved.exists():
        lg.error("discovery.missing_dir", extra={"dir": key})
        raise TemplateDiscoveryError(f"Template directory not found: {resolved}")

    t0 = time.perf_counter()
    if cache and key in _TEMPLATE_CACHE:
        ns = _TEMPLATE_CACHE[key]
        lg.debug("discovery.cache_hit", extra={"dir": key, "count": len(vars(ns)), "cache": True})
        return ns

    ns = _discover_templates(resolved)
    if cache:
        _TEMPLATE_CACHE[key] = ns
    duration = time.perf_counter() - t0
    try:
        count = len(vars(ns))
    except Exception:
        count = 0
    lg.info("discovery.loaded", extra={"dir": key, "count": count, "cache": cache, "duration_ms": int(duration * 1000)})
    return ns
