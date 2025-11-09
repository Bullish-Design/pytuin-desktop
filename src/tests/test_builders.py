# tests/test_builders.py
from __future__ import annotations

from uuid import UUID

import pytest

from pytuin_desktop.builders import BlockBuilder
from pytuin_desktop.models import (
    ParagraphBlock,
    HeadingBlock,
    HorizontalRuleBlock,
    EditorBlock,
    ScriptBlock,
    RunBlock,
    QuoteBlock,
    BulletListItemBlock,
    NumberedListItemBlock,
    CheckListItemBlock,
    ToggleListItemBlock,
    CodeBlockBlock,
    EnvBlock,
    VarBlock,
    LocalVarBlock,
    VarDisplayBlock,
    DirectoryBlock,
    LocalDirectoryBlock,
    DropdownBlock,
    SQLiteBlock,
    PostgresBlock,
    HttpBlock,
    ImageBlock,
    VideoBlock,
    AudioBlock,
    FileBlock,
)


class TestBlockBuilder:
    """Test suite for BlockBuilder factory methods."""

    def test_paragraph_basic(self):
        """Test creating basic paragraph."""
        block = BlockBuilder.paragraph("Test text")

        assert isinstance(block, ParagraphBlock)
        assert isinstance(block.id, UUID)
        assert len(block.content) == 1
        assert block.content[0].text == "Test text"

    def test_paragraph_empty(self):
        """Test creating empty paragraph."""
        block = BlockBuilder.paragraph()

        assert isinstance(block, ParagraphBlock)
        assert len(block.content) == 0

    def test_paragraph_with_styles(self):
        """Test creating paragraph with text styles."""
        block = BlockBuilder.paragraph("Bold text", bold=True, italic=True)

        assert block.content[0].styles.bold is True
        assert block.content[0].styles.italic is True

    def test_heading_all_levels(self):
        """Test creating headings at all levels."""
        for level in range(1, 7):
            block = BlockBuilder.heading(f"Level {level}", level=level)

            assert isinstance(block, HeadingBlock)
            assert block.props.level == level
            assert block.content[0].text == f"Level {level}"

    def test_heading_toggleable(self):
        """Test creating toggleable heading."""
        block = BlockBuilder.heading("Toggle", is_toggleable=True)

        assert block.props.is_toggleable is True

    def test_horizontal_rule(self):
        """Test creating horizontal rule."""
        block = BlockBuilder.horizontal_rule()

        assert isinstance(block, HorizontalRuleBlock)
        assert isinstance(block.id, UUID)

    def test_editor(self):
        """Test creating editor block."""
        block = BlockBuilder.editor(
            name="Test Editor", code="print('hello')", language="python"
        )

        assert isinstance(block, EditorBlock)
        assert block.props.name == "Test Editor"
        assert block.props.code == "print('hello')"
        assert block.props.language == "python"

    def test_script(self):
        """Test creating script block."""
        block = BlockBuilder.script(
            name="Test Script", code="echo hello", interpreter="/bin/bash"
        )

        assert isinstance(block, ScriptBlock)
        assert block.props.name == "Test Script"
        assert block.props.code == "echo hello"
        assert block.props.dependency == "{}"

    def test_run(self):
        """Test creating run block."""
        block = BlockBuilder.run(name="Test Run", code="ls -la")

        assert isinstance(block, RunBlock)
        assert block.props.name == "Test Run"
        assert block.props.type == "bash"

    def test_quote(self):
        """Test creating quote block."""
        block = BlockBuilder.quote("Famous quote")

        assert isinstance(block, QuoteBlock)
        assert block.content[0].text == "Famous quote"

    def test_bullet_list_item(self):
        """Test creating bullet list item."""
        block = BlockBuilder.bullet_list_item("Bullet point")

        assert isinstance(block, BulletListItemBlock)
        assert block.content[0].text == "Bullet point"

    def test_numbered_list_item(self):
        """Test creating numbered list item."""
        block = BlockBuilder.numbered_list_item("First item")

        assert isinstance(block, NumberedListItemBlock)
        assert block.content[0].text == "First item"

    def test_checklist_unchecked(self):
        """Test creating unchecked checklist item."""
        block = BlockBuilder.checklist_item("Task")

        assert isinstance(block, CheckListItemBlock)
        assert block.props.checked is False

    def test_checklist_checked(self):
        """Test creating checked checklist item."""
        block = BlockBuilder.checklist_item("Completed", checked=True)

        assert block.props.checked is True

    def test_toggle_item_no_children(self):
        """Test creating toggle without children."""
        block = BlockBuilder.toggle_item("Toggle")

        assert isinstance(block, ToggleListItemBlock)
        assert len(block.children) == 0

    def test_toggle_item_with_children(self):
        """Test creating toggle with children."""
        children = [
            BlockBuilder.paragraph("Child 1"),
            BlockBuilder.paragraph("Child 2"),
        ]
        block = BlockBuilder.toggle_item("Toggle", children=children)

        assert len(block.children) == 2
        assert isinstance(block.children[0], ParagraphBlock)

    def test_code_block(self):
        """Test creating code block."""
        block = BlockBuilder.code_block("def hello():\n    pass", language="python")

        assert isinstance(block, CodeBlockBlock)
        assert block.props.language == "python"
        assert "def hello()" in block.content[0].text

    def test_env_var(self):
        """Test creating environment variable block."""
        block = BlockBuilder.env_var("PATH", "/usr/bin")

        assert isinstance(block, EnvBlock)
        assert block.props.name == "PATH"
        assert block.props.value == "/usr/bin"

    def test_var(self):
        """Test creating variable block."""
        block = BlockBuilder.var("myvar", "value")

        assert isinstance(block, VarBlock)
        assert block.props.name == "myvar"

    def test_local_var(self):
        """Test creating local variable block."""
        block = BlockBuilder.local_var("localvar")

        assert isinstance(block, LocalVarBlock)
        assert block.props.name == "localvar"

    def test_var_display(self):
        """Test creating variable display block."""
        block = BlockBuilder.var_display("myvar")

        assert isinstance(block, VarDisplayBlock)
        assert block.props.name == "myvar"

    def test_directory(self):
        """Test creating directory block."""
        block = BlockBuilder.directory("/home/user")

        assert isinstance(block, DirectoryBlock)
        assert block.props.path == "/home/user"

    def test_local_directory(self):
        """Test creating local directory block."""
        block = BlockBuilder.local_directory()

        assert isinstance(block, LocalDirectoryBlock)

    def test_dropdown_fixed_options(self):
        """Test creating dropdown with fixed options."""
        block = BlockBuilder.dropdown(
            name="Select", options="opt1, opt2", options_type="fixed"
        )

        assert isinstance(block, DropdownBlock)
        assert block.props.options_type == "fixed"
        assert block.props.fixed_options == "opt1, opt2"

    def test_dropdown_variable_options(self):
        """Test creating dropdown with variable options."""
        block = BlockBuilder.dropdown(
            name="Select", options="var1, var2", options_type="variable"
        )

        assert block.props.options_type == "variable"
        assert block.props.variable_options == "var1, var2"

    def test_dropdown_command_options(self):
        """Test creating dropdown with command options."""
        block = BlockBuilder.dropdown(
            name="Select", options="ls -la", options_type="command"
        )

        assert block.props.options_type == "command"
        assert block.props.command_options == "ls -la"

    def test_sqlite(self):
        """Test creating SQLite block."""
        block = BlockBuilder.sqlite(name="Query", uri="test.db", query="SELECT * FROM t")

        assert isinstance(block, SQLiteBlock)
        assert block.props.name == "Query"
        assert block.props.uri == "test.db"

    def test_postgres(self):
        """Test creating PostgreSQL block."""
        block = BlockBuilder.postgres(name="Query", uri="postgresql://localhost")

        assert isinstance(block, PostgresBlock)
        assert block.props.uri == "postgresql://localhost"

    def test_http_get(self):
        """Test creating HTTP GET block."""
        block = BlockBuilder.http(name="API", url="https://api.example.com", verb="GET")

        assert isinstance(block, HttpBlock)
        assert block.props.verb == "GET"
        assert block.props.url == "https://api.example.com"

    def test_http_post(self):
        """Test creating HTTP POST block."""
        block = BlockBuilder.http(
            name="API", url="https://api.example.com", verb="POST", body='{"key": "value"}'
        )

        assert block.props.verb == "POST"
        assert block.props.body == '{"key": "value"}'

    def test_image(self):
        """Test creating image block."""
        block = BlockBuilder.image(
            name="Photo", url="https://example.com/pic.jpg", caption="A photo"
        )

        assert isinstance(block, ImageBlock)
        assert block.props.url == "https://example.com/pic.jpg"
        assert block.props.caption == "A photo"

    def test_video(self):
        """Test creating video block."""
        block = BlockBuilder.video(url="https://example.com/video.mp4")

        assert isinstance(block, VideoBlock)
        assert block.props.show_preview is True

    def test_audio(self):
        """Test creating audio block."""
        block = BlockBuilder.audio(url="https://example.com/audio.mp3")

        assert isinstance(block, AudioBlock)

    def test_file(self):
        """Test creating file block."""
        block = BlockBuilder.file(name="Document", url="https://example.com/doc.pdf")

        assert isinstance(block, FileBlock)
        assert block.props.name == "Document"
