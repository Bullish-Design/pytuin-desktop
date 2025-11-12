
from __future__ import annotations

def test_top_level_imports():
    from pytuin_desktop import (
        AtrbParser, AtrbDocument, BaseBlock, load_atrb_templates, clear_template_cache,
        DocumentEditor, BlockBuilder, get_logger, AtrbError, AtrbParseError, AtrbSchemaError,
        AtrbValidationError, TemplateDiscoveryError, TextAlignment, ColorToken, AtrbValidator,
        DocumentRepository, InMemoryDocumentRepository, __version__,
    )
    assert isinstance(__version__, str)
