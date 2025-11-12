# path: pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library (v4 Phase 1)."""
__version__ = "0.4.0-alpha1"

from .parser import AtrbParser
from .models import AtrbDocument, BaseBlock
from .discovery import load_atrb_templates, clear_template_cache
from .editor import DocumentEditor
from .builders import BlockBuilder
from .logger import get_logger
from .enums import TextAlignment, ColorToken
from .validator import AtrbValidator
from .repository import DocumentRepository, InMemoryDocumentRepository
from .errors import (
    AtrbError, AtrbParseError, AtrbSchemaError, AtrbValidationError, TemplateDiscoveryError,
)

__all__ = [
    "DocumentRepository","InMemoryDocumentRepository","AtrbParser","AtrbDocument","BaseBlock",
    "load_atrb_templates","clear_template_cache","DocumentEditor","BlockBuilder","get_logger",
    "AtrbError","AtrbParseError","AtrbSchemaError","AtrbValidationError","TemplateDiscoveryError",
    "TextAlignment","ColorToken","AtrbValidator","__version__",
]
