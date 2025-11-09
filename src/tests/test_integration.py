# tests/test_integration.py
from __future__ import annotations

import pytest

from pytuin_desktop import AtrbParser, AtrbWriter, DocumentEditor, BlockBuilder


class TestRoundTrip:
    """Test round-trip operations: parse -> edit -> write -> parse."""

    def test_parse_write_parse_preserves_data(self, sample_atrb_file, temp_dir):
        """Test parsing, writing, and re-parsing preserves all data."""
        # Parse original
        original = AtrbParser.parse_file(sample_atrb_file)

        # Write to new file
        output = temp_dir / "roundtrip.atrb"
        AtrbWriter.write_file(original, output)

        # Re-parse
        reloaded = AtrbParser.parse_file(output)

        # Verify
        assert reloaded.name == original.name
        assert reloaded.version == original.version
        assert len(reloaded.content) == len(original.content)

        # Check first few blocks match
        for i in range(min(5, len(original.content))):
            assert reloaded.content[i].type == original.content[i].type
            assert str(reloaded.content[i].id) == str(original.content[i].id)

    def test_edit_write_parse_roundtrip(self, sample_atrb_file, temp_dir):
        """Test editing, writing, and re-parsing works correctly."""
        # Load and edit
        editor = DocumentEditor.from_file(sample_atrb_file)
        original_count = len(editor)

        editor.add_block(BlockBuilder.heading("Added Section", level=2))
        editor.add_block(BlockBuilder.paragraph("Added paragraph"))

        # Save
        output = temp_dir / "edited.atrb"
        editor.save(output)

        # Reload and verify
        reloaded = AtrbParser.parse_file(output)
        assert len(reloaded.content) == original_count + 2
        assert reloaded.content[-2].type == "heading"
        assert reloaded.content[-1].type == "paragraph"

    def test_create_write_parse_roundtrip(self, temp_dir):
        """Test creating, writing, and parsing new document."""
        # Create new document
        editor = DocumentEditor.create("Test Doc")
        editor.add_block(BlockBuilder.heading("Title", level=1))
        editor.add_block(BlockBuilder.paragraph("Introduction"))
        editor.add_block(BlockBuilder.bullet_list_item("Point 1"))
        editor.add_block(BlockBuilder.bullet_list_item("Point 2"))

        # Save
        output = temp_dir / "new.atrb"
        editor.save(output)

        # Reload
        reloaded = AtrbParser.parse_file(output)

        assert reloaded.name == "Test Doc"
        assert len(reloaded.content) == 4
        assert reloaded.content[0].type == "heading"
        assert reloaded.content[2].type == "bulletListItem"


class TestWorkflows:
    """Test complete workflows using the library."""

    def test_create_simple_document_workflow(self, temp_dir):
        """Test workflow for creating a simple document."""
        # Create document
        editor = DocumentEditor.create("Project README")

        # Add structure
        editor.add_block(BlockBuilder.heading("Project Name", level=1))
        editor.add_block(BlockBuilder.paragraph("A brief description."))
        editor.add_block(BlockBuilder.horizontal_rule())
        editor.add_block(BlockBuilder.heading("Installation", level=2))
        editor.add_block(BlockBuilder.code_block("pip install package", language="bash"))

        # Save
        output = temp_dir / "README.atrb"
        editor.save(output)

        # Verify
        assert output.exists()
        doc = AtrbParser.parse_file(output)
        assert doc.name == "Project README"
        assert len(doc.content) == 5

    def test_modify_existing_document_workflow(self, sample_atrb_file, temp_dir):
        """Test workflow for modifying existing document."""
        # Load
        editor = DocumentEditor.from_file(sample_atrb_file)

        # Insert new section at beginning
        editor.add_block(BlockBuilder.heading("Overview", level=1), index=0)
        editor.add_block(BlockBuilder.paragraph("This is an overview."), index=1)

        # Reorder blocks
        editor.move_block(from_index=10, to_index=5)

        # Save
        output = temp_dir / "modified.atrb"
        editor.save(output)

        # Verify
        doc = AtrbParser.parse_file(output)
        assert doc.content[0].type == "heading"
        assert doc.content[1].type == "paragraph"

    def test_template_based_workflow(self, sample_atrb_file, temp_dir):
        """Test workflow using template."""
        # Create from template
        editor = DocumentEditor.from_template(sample_atrb_file, "My Project")

        # Clear most content
        while len(editor) > 5:
            editor.remove_block_at(-1)

        # Add custom content
        editor.add_block(BlockBuilder.heading("Custom Section", level=2))
        editor.add_block(BlockBuilder.paragraph("Custom content here."))

        # Save
        output = temp_dir / "project.atrb"
        editor.save(output)

        # Verify
        doc = AtrbParser.parse_file(output)
        assert doc.name == "My Project"
        assert doc.content[-2].type == "heading"

    def test_complex_nested_structure_workflow(self, temp_dir):
        """Test creating complex nested structures."""
        editor = DocumentEditor.create("Complex Doc")

        # Create nested toggle structure
        toggle = BlockBuilder.toggle_item(
            "Main Section",
            children=[
                BlockBuilder.paragraph("Section intro"),
                BlockBuilder.heading("Subsection", level=3),
                BlockBuilder.bullet_list_item("Point A"),
                BlockBuilder.bullet_list_item("Point B"),
            ],
        )

        editor.add_block(toggle)

        # Save and reload
        output = temp_dir / "complex.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert len(doc.content[0].children) == 4

    def test_multiple_edits_workflow(self, temp_dir):
        """Test multiple sequential edits."""
        editor = DocumentEditor.create("Multi Edit")

        # First edit: add content
        editor.add_block(BlockBuilder.heading("Title", level=1))
        editor.add_block(BlockBuilder.paragraph("Para 1"))

        # Second edit: insert in middle
        editor.add_block(BlockBuilder.paragraph("Para 0.5"), index=1)

        # Third edit: reorder
        editor.swap_blocks(0, 2)

        # Fourth edit: remove
        editor.remove_block_at(1)

        # Save
        output = temp_dir / "multi.atrb"
        editor.save(output)

        # Verify final state
        doc = AtrbParser.parse_file(output)
        assert len(doc.content) == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_document_roundtrip(self, temp_dir):
        """Test empty document can be written and read."""
        editor = DocumentEditor.create("Empty")
        output = temp_dir / "empty.atrb"

        editor.save(output)
        doc = AtrbParser.parse_file(output)

        assert doc.name == "Empty"
        assert len(doc.content) == 0

    def test_document_with_only_empty_blocks(self, temp_dir):
        """Test document with empty paragraphs."""
        editor = DocumentEditor.create("Empty Blocks")
        editor.add_block(BlockBuilder.paragraph())
        editor.add_block(BlockBuilder.paragraph())

        output = temp_dir / "empty_blocks.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert len(doc.content) == 2
        assert all(len(b.content) == 0 for b in doc.content)

    def test_unicode_content_preserved(self, temp_dir):
        """Test unicode characters are preserved."""
        editor = DocumentEditor.create("Unicode")
        editor.add_block(BlockBuilder.paragraph("Hello 世界 🌍"))
        editor.add_block(BlockBuilder.heading("Émojis: 😀🎉", level=1))

        output = temp_dir / "unicode.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert "世界" in doc.content[0].content[0].text
        assert "😀" in doc.content[1].content[0].text

    def test_large_document_roundtrip(self, temp_dir):
        """Test handling large documents."""
        editor = DocumentEditor.create("Large Doc")

        # Add many blocks
        for i in range(100):
            editor.add_block(BlockBuilder.paragraph(f"Paragraph {i}"))

        output = temp_dir / "large.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert len(doc.content) == 100

    def test_deeply_nested_toggles(self, temp_dir):
        """Test deeply nested toggle structures."""
        level3 = BlockBuilder.toggle_item(
            "Level 3", children=[BlockBuilder.paragraph("Deep content")]
        )
        level2 = BlockBuilder.toggle_item("Level 2", children=[level3])
        level1 = BlockBuilder.toggle_item("Level 1", children=[level2])

        editor = DocumentEditor.create("Nested")
        editor.add_block(level1)

        output = temp_dir / "nested.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert len(doc.content[0].children) == 1
        assert len(doc.content[0].children[0].children) == 1

    def test_special_characters_in_code(self, temp_dir):
        """Test special characters in code blocks."""
        code = '''def test():
    return "<>&\'"'''

        editor = DocumentEditor.create("Code")
        editor.add_block(BlockBuilder.code_block(code, language="python"))

        output = temp_dir / "code.atrb"
        editor.save(output)

        doc = AtrbParser.parse_file(output)
        assert "<>&" in doc.content[0].content[0].text
