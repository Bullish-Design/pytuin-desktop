# path: tests/test_public_api_v4.py
def test_top_level_exports_v4():
    from pytuin_desktop import (
        __version__,
        # parsing
        AtrbParser, AtrbValidator,
        # models
        AtrbDocument, BaseBlock,
        HeadingBlock, ParagraphBlock, ScriptBlock, EditorBlock, TerminalBlock,
        EnvironmentBlock, VariableBlock, DirectoryBlock, HorizontalRuleBlock,
        # props
        HeadingProps, ParagraphProps, ScriptProps, EditorProps, TerminalProps,
        EnvironmentProps, VariableProps, DirectoryProps, HorizontalRuleProps,
        # enums
        TextAlignment, ColorToken,
        # utils
        load_atrb_templates, clear_template_cache, DocumentEditor, BlockBuilder, get_logger,
        # repo + errors
        DocumentRepository, InMemoryDocumentRepository,
        AtrbError, AtrbParseError, AtrbSchemaError, AtrbValidationError, TemplateDiscoveryError
    )
    assert isinstance(__version__, str)
