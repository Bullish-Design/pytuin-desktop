"""Template discovery for .atrb templates (Step 10)."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Union

from templateer import discover_templates as _discover_templates


def load_atrb_templates(template_dir: Union[str, Path] = ".templateer") -> SimpleNamespace:
    """Load .atrb Templateer templates from a directory.

    Args:
        template_dir: Directory containing .py template files (default: ".templateer").

    Returns:
        SimpleNamespace where attributes are discovered TemplateModel subclasses,
        e.g., ns.DocumentTemplate, ns.ParagraphBlockTemplate, etc.
    """
    return _discover_templates(template_dir)
