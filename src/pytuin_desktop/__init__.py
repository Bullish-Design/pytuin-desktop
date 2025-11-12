# path: src/pytuin_desktop/__init__.py
"""Pytuin Desktop - .atrb file library (v4 Phase 4/5)."""
from __future__ import annotations

__version__ = "0.4.0-alpha4"

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
from .id_generators import (
    BlockIdGenerator, UUIDv4Generator, UUIDv1Generator, DeterministicGenerator, SequentialGenerator,
    get_default_generator, set_default_generator, reset_default_generator, generate_block_id
)
from .diff import DocumentDiffer, DocumentDiff, BlockChange, ChangeType
from .serializers import YamlSerializer, SafeYamlSerializer, get_default_serializer, set_default_serializer
from .metrics import (
    MetricsCollector, NoOpMetricsCollector, InMemoryMetricsCollector,
    TimingContext, get_default_collector, set_default_collector
)
from .services import DocumentLoader, DocumentSerializer  # re-export services


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
    # ID Generators
    "BlockIdGenerator","UUIDv4Generator","UUIDv1Generator","DeterministicGenerator","SequentialGenerator",
    "get_default_generator","set_default_generator","reset_default_generator","generate_block_id",
    # Diff
    "DocumentDiffer","DocumentDiff","BlockChange","ChangeType",
    # Serializers
    "YamlSerializer","SafeYamlSerializer","get_default_serializer","set_default_serializer",
    # Metrics
    "MetricsCollector","NoOpMetricsCollector","InMemoryMetricsCollector","TimingContext",
    "get_default_collector","set_default_collector",
    # Services
    "DocumentLoader","DocumentSerializer",
]


