# path: pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library (v4 Phase 2)."""
__version__ = "0.4.0-alpha2"

from .parser import AtrbParser
from .models import (
    AtrbDocument, BaseBlock,
    HeadingBlock, ParagraphBlock, ScriptBlock, EditorBlock, TerminalBlock,
    EnvironmentBlock, VariableBlock, DirectoryBlock, HorizontalRuleBlock
)
from .discovery import load_atrb_templates, clear_template_cache
from .editor import DocumentEditor
from .builders import BlockBuilder
from .logger import get_logger
from .enums import TextAlignment, ColorToken
from .validator import AtrbValidator
from .repository import DocumentRepository, InMemoryDocumentRepository
from .block_props import (
    HeadingProps, ParagraphProps, ScriptProps, EditorProps, TerminalProps,
    EnvironmentProps, VariableProps, DirectoryProps, HorizontalRuleProps
)
from .errors import (
    AtrbError, AtrbParseError, AtrbSchemaError, AtrbValidationError, TemplateDiscoveryError,
)

__all__ = [
    # Repositories
    "DocumentRepository","InMemoryDocumentRepository",
    # Parsing
    "AtrbParser",
    # Models
    "AtrbDocument","BaseBlock",
    "HeadingBlock","ParagraphBlock","ScriptBlock","EditorBlock","TerminalBlock",
    "EnvironmentBlock","VariableBlock","DirectoryBlock","HorizontalRuleBlock",
    # Props
    "HeadingProps","ParagraphProps","ScriptProps","EditorProps","TerminalProps",
    "EnvironmentProps","VariableProps","DirectoryProps","HorizontalRuleProps",
    # Templates & builders
    "load_atrb_templates","clear_template_cache","DocumentEditor","BlockBuilder",
    # Logging
    "get_logger",
    # Errors
    "AtrbError","AtrbParseError","AtrbSchemaError","AtrbValidationError","TemplateDiscoveryError",
    # Enums & Validation
    "TextAlignment","ColorToken","AtrbValidator","__version__",
]
