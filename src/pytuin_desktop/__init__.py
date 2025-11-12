"""Pytuin Desktop - .atrb file library built on Templateer (v3 Step 2)."""

from .parser import AtrbParser
from .models import AtrbDocument, BaseBlock
from .discovery import load_atrb_templates, clear_template_cache
from .editor import DocumentEditor
from .builders import BlockBuilder
from .logger import get_logger
from .errors import (
    AtrbError,
    AtrbParseError,
    AtrbSchemaError,
    AtrbValidationError,
    TemplateDiscoveryError,
)

__version__ = "0.3.0-dev5"

__all__ = [
    "AtrbParser",
    "AtrbDocument",
    "BaseBlock",
    "load_atrb_templates",
    "clear_template_cache",
    "DocumentEditor",
    "BlockBuilder",
    "get_logger",
    "AtrbError",
    "AtrbParseError",
    "AtrbSchemaError",
    "AtrbValidationError",
    "TemplateDiscoveryError",
]
