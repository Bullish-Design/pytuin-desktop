"""Template discovery for .atrb templates (v3 Step 1)."""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Union, Optional

from templateer import discover_templates as _discover_templates

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
    *, cache: bool = True
) -> SimpleNamespace:
    """Load .atrb Templateer templates from a directory.

    Args:
        template_dir: Directory containing .py template files.
                      Precedence: explicit arg > env PYTUIN_TEMPLATE_DIR > '.templateer'
        cache: If True, memoize results per absolute directory path.

    Returns:
        SimpleNamespace where attributes are discovered TemplateModel subclasses.
    """
    resolved = _resolve_template_dir(template_dir)
    key = str(resolved)

    if cache and key in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[key]

    ns = _discover_templates(resolved)
    if cache:
        _TEMPLATE_CACHE[key] = ns
    return ns
