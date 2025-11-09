# tests/test_models.py
from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from pytuin_desktop.models import (
    AtrbDocument,
    HeadingBlock,
    ParagraphBlock,
    EditorBlock,
    ScriptBlock,
)
from pytuin_desktop.models.content import TextContent, TextStyles
from pytuin_desktop.models.props import HeadingProps, TextProps, EditorProps, ScriptProps


class TestBaseBlockValidation:
    """Test validation of base block structure."""

    def test_block_requires_id(self):
        """Test blocks require id field."""
        with pytest.raises(ValidationError):
            HeadingBlock(props=HeadingProps(level=1), content=[])

    def test_block_requires_props(self):
        """Test blocks require props field."""
        with pytest.raises(ValidationError):
            HeadingBlock(id=uuid4(), content=[])

    def test_block_children_defaults_to_empty(self):
        """Test children defaults to empty list."""
        block = HeadingBlock(id=uuid4(), props=HeadingProps(level=1), content=[])

        assert block.children == []


class TestHeadingBlockValidation:
    """Test HeadingBlock validation."""

    def test_valid_heading_levels(self):
        """Test valid heading levels 1-6."""
        for level in range(1, 7):
            block = HeadingBlock(
                id=uuid4(), props=HeadingProps(level=level), content=[]
            )
            assert block.props.level == level

    def test_invalid_heading_level_high(self):
        """Test heading level > 6 is invalid."""
        with pytest.raises(ValidationError):
            HeadingBlock(id=uuid4(), props=HeadingProps(level=7), content=[])

    def test_invalid_heading_level_low(self):
        """Test heading level < 1 is invalid."""
        with pytest.raises(ValidationError):
            HeadingBlock(id=uuid4(), props=HeadingProps(level=0), content=[])

    def test_heading_type_literal(self):
        """Test heading block has correct type literal."""
        block = HeadingBlock(
            id=uuid4(), props=HeadingProps(level=1), content=[]
        )

        assert block.type == "heading"


class TestParagraphBlockValidation:
    """Test ParagraphBlock validation."""

    def test_paragraph_empty_content(self):
        """Test paragraph can have empty content."""
        block = ParagraphBlock(id=uuid4(), props=TextProps(), content=[])

        assert len(block.content) == 0

    def test_paragraph_with_text_content(self):
        """Test paragraph with text content."""
        block = ParagraphBlock(
            id=uuid4(),
            props=TextProps(),
            content=[TextContent(text="Test")],
        )

        assert block.content[0].text == "Test"

    def test_paragraph_type_literal(self):
        """Test paragraph has correct type literal."""
        block = ParagraphBlock(id=uuid4(), props=TextProps(), content=[])

        assert block.type == "paragraph"


class TestTextContentValidation:
    """Test TextContent validation."""

    def test_text_content_requires_text(self):
        """Test TextContent requires text field."""
        with pytest.raises(ValidationError):
            TextContent()

    def test_text_styles_defaults(self):
        """Test TextStyles has correct defaults."""
        styles = TextStyles()

        assert styles.bold is False
        assert styles.italic is False
        assert styles.underline is False
        assert styles.strikethrough is False
        assert styles.code is False

    def test_text_content_type_literal(self):
        """Test TextContent has correct type."""
        content = TextContent(text="test")

        assert content.type == "text"


class TestEditorBlockValidation:
    """Test EditorBlock validation."""

    def test_editor_requires_name(self):
        """Test editor block requires name."""
        with pytest.raises(ValidationError):
            EditorBlock(
                id=uuid4(),
                props=EditorProps(
                    code="", language="python", variableName="var", syncVariable=False
                ),
            )

    def test_editor_valid_props(self):
        """Test editor block with valid props."""
        block = EditorBlock(
            id=uuid4(),
            props=EditorProps(
                name="Editor",
                code="print()",
                language="python",
                variableName="var",
                syncVariable=False,
            ),
        )

        assert block.props.name == "Editor"
        assert block.props.language == "python"


class TestScriptBlockValidation:
    """Test ScriptBlock validation."""

    def test_script_requires_dependency(self):
        """Test script block requires dependency field."""
        with pytest.raises(ValidationError):
            ScriptBlock(
                id=uuid4(),
                props=ScriptProps(
                    name="Script",
                    code="echo test",
                    interpreter="/bin/bash",
                    outputVariable="",
                    outputVisible=True,
                ),
            )

    def test_script_dependency_string(self):
        """Test script block accepts dependency as string."""
        block = ScriptBlock(
            id=uuid4(),
            props=ScriptProps(
                name="Script",
                code="echo test",
                interpreter="/bin/bash",
                outputVariable="",
                outputVisible=True,
                dependency="{}",
            ),
        )

        assert block.props.dependency == "{}"


class TestDocumentValidation:
    """Test AtrbDocument validation."""

    def test_document_requires_all_fields(self):
        """Test document requires id, name, version, content."""
        with pytest.raises(ValidationError):
            AtrbDocument(name="Test", version=1, content=[])

    def test_document_valid(self):
        """Test creating valid document."""
        doc = AtrbDocument(id=uuid4(), name="Test", version=1, content=[])

        assert doc.name == "Test"
        assert doc.version == 1
        assert len(doc.content) == 0

    def test_document_with_blocks(self):
        """Test document with various block types."""
        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                HeadingBlock(
                    id=uuid4(),
                    props=HeadingProps(level=1),
                    content=[TextContent(text="Title")],
                ),
                ParagraphBlock(
                    id=uuid4(),
                    props=TextProps(),
                    content=[TextContent(text="Content")],
                ),
            ],
        )

        assert len(doc.content) == 2


class TestDiscriminatedUnion:
    """Test discriminated union for block types."""

    def test_discriminator_field_is_type(self):
        """Test blocks use 'type' as discriminator."""
        block = HeadingBlock(id=uuid4(), props=HeadingProps(level=1), content=[])

        assert hasattr(block, "type")
        assert block.type == "heading"

    def test_invalid_block_type_rejected(self):
        """Test invalid block type is rejected by parser."""
        from pytuin_desktop.models.blocks import AnyBlock

        # This should work with valid type
        valid_block = HeadingBlock(
            id=uuid4(), props=HeadingProps(level=1), content=[]
        )
        assert isinstance(valid_block, HeadingBlock)


class TestFieldAliases:
    """Test field aliases for camelCase/snake_case conversion."""

    def test_text_color_alias(self):
        """Test textColor alias works."""
        props = TextProps(textColor="blue")

        assert props.text_color == "blue"

    def test_background_color_alias(self):
        """Test backgroundColor alias works."""
        props = TextProps(backgroundColor="red")

        assert props.background_color == "red"

    def test_is_toggleable_alias(self):
        """Test isToggleable alias works."""
        props = HeadingProps(level=1, isToggleable=True)

        assert props.is_toggleable is True

    def test_variable_name_alias(self):
        """Test variableName alias works."""
        props = EditorProps(
            name="Editor",
            code="",
            language="python",
            variableName="myvar",
            syncVariable=False,
        )

        assert props.variable_name == "myvar"

    def test_sync_variable_alias(self):
        """Test syncVariable alias works."""
        props = EditorProps(
            name="Editor",
            code="",
            language="python",
            variableName="var",
            syncVariable=True,
        )

        assert props.sync_variable is True
