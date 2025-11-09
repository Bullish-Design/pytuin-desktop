# tests/test_editor.py
from __future__ import annotations

from uuid import uuid4

import pytest

from pytuin_desktop.editor import DocumentEditor
from pytuin_desktop.builders import BlockBuilder
from pytuin_desktop.models import AtrbDocument, HeadingBlock, ParagraphBlock
from pytuin_desktop.parser import AtrbParser


class TestDocumentEditor:
    """Test suite for DocumentEditor."""

    def test_from_file(self, sample_atrb_file):
        """Test loading document from file."""
        editor = DocumentEditor.from_file(sample_atrb_file)

        assert isinstance(editor.document, AtrbDocument)
        assert editor.document.name == "Block_Spec"
        assert len(editor) > 0

    def test_create_empty(self):
        """Test creating empty document."""
        editor = DocumentEditor.create("New Doc")

        assert editor.document.name == "New Doc"
        assert editor.document.version == 1
        assert len(editor) == 0

    def test_from_template(self, sample_atrb_file):
        """Test creating document from template."""
        editor = DocumentEditor.from_template(sample_atrb_file, "My Copy")

        assert editor.document.name == "My Copy"
        assert len(editor) > 0
        assert editor.document.id != "019a609e-dfe1-7330-8398-81906ac3b0f1"

    def test_add_block_append(self, simple_document):
        """Test adding block to end."""
        editor = DocumentEditor(simple_document)
        original_len = len(editor)

        editor.add_block(BlockBuilder.paragraph("New paragraph"))

        assert len(editor) == original_len + 1
        assert editor.get_block(-1).type == "paragraph"

    def test_add_block_at_index(self, simple_document):
        """Test adding block at specific index."""
        editor = DocumentEditor(simple_document)

        editor.add_block(BlockBuilder.heading("Inserted", level=2), index=1)

        assert isinstance(editor.get_block(1), HeadingBlock)
        assert editor.get_block(1).content[0].text == "Inserted"

    def test_remove_block_by_id(self, simple_document):
        """Test removing block by UUID."""
        editor = DocumentEditor(simple_document)
        original_len = len(editor)
        block_id = str(editor.get_block(0).id)

        editor.remove_block(block_id)

        assert len(editor) == original_len - 1

    def test_remove_block_by_id_not_found(self, simple_document):
        """Test removing non-existent block raises error."""
        editor = DocumentEditor(simple_document)

        with pytest.raises(ValueError, match="not found"):
            editor.remove_block(str(uuid4()))

    def test_remove_block_at_index(self, simple_document):
        """Test removing block by index."""
        editor = DocumentEditor(simple_document)
        original_len = len(editor)

        editor.remove_block_at(0)

        assert len(editor) == original_len - 1

    def test_move_block_forward(self, simple_document):
        """Test moving block forward in document."""
        editor = DocumentEditor(simple_document)
        block = editor.get_block(0)

        editor.move_block(from_index=0, to_index=1)

        assert editor.get_block(1).id == block.id

    def test_move_block_backward(self, simple_document):
        """Test moving block backward in document."""
        editor = DocumentEditor(simple_document)
        block = editor.get_block(1)

        editor.move_block(from_index=1, to_index=0)

        assert editor.get_block(0).id == block.id

    def test_swap_blocks(self, simple_document):
        """Test swapping two blocks."""
        editor = DocumentEditor(simple_document)
        block0 = editor.get_block(0)
        block1 = editor.get_block(1)

        editor.swap_blocks(0, 1)

        assert editor.get_block(0).id == block1.id
        assert editor.get_block(1).id == block0.id

    def test_get_block(self, simple_document):
        """Test getting block by index."""
        editor = DocumentEditor(simple_document)

        block = editor.get_block(0)

        assert isinstance(block, HeadingBlock)

    def test_find_block_found(self, simple_document):
        """Test finding block by ID."""
        editor = DocumentEditor(simple_document)
        block_id = str(editor.get_block(0).id)

        result = editor.find_block(block_id)

        assert result is not None
        assert result[0] == 0
        assert result[1].id == editor.get_block(0).id

    def test_find_block_not_found(self, simple_document):
        """Test finding non-existent block returns None."""
        editor = DocumentEditor(simple_document)

        result = editor.find_block(str(uuid4()))

        assert result is None

    def test_save(self, simple_document, temp_dir):
        """Test saving document to file."""
        editor = DocumentEditor(simple_document)
        output_file = temp_dir / "saved.atrb"

        editor.save(output_file)

        assert output_file.exists()
        reloaded = AtrbParser.parse_file(output_file)
        assert reloaded.name == simple_document.name

    def test_to_string(self, simple_document):
        """Test converting document to YAML string."""
        editor = DocumentEditor(simple_document)

        yaml_str = editor.to_string()

        assert "name: Test Document" in yaml_str
        assert "version: 1" in yaml_str

    def test_len(self, simple_document):
        """Test __len__ returns block count."""
        editor = DocumentEditor(simple_document)

        assert len(editor) == len(simple_document.content)

    def test_iter(self, simple_document):
        """Test __iter__ allows iteration over blocks."""
        editor = DocumentEditor(simple_document)

        blocks = list(editor)

        assert len(blocks) == len(simple_document.content)
        assert all(hasattr(b, "type") for b in blocks)

    def test_chaining_operations(self):
        """Test method chaining."""
        from pytuin_desktop.models import AtrbDocument
        from uuid import uuid4

        doc = AtrbDocument(
            id=uuid4(),
            name="Test",
            version=1,
            content=[
                BlockBuilder.heading("Title", level=1),
                BlockBuilder.paragraph("Content"),
            ],
        )
        editor = DocumentEditor(doc)
        original_len = len(editor)

        editor.add_block(BlockBuilder.paragraph("First")).add_block(
            BlockBuilder.paragraph("Second")
        ).move_block(2, 3)

        assert len(editor) == original_len + 2

    def test_complex_editing_workflow(self, sample_atrb_file, temp_dir):
        """Test complex editing workflow."""
        # Load, edit, save, reload
        editor = DocumentEditor.from_file(sample_atrb_file)
        original_count = len(editor)

        # Add new section
        editor.add_block(BlockBuilder.heading("New Section", level=1))
        editor.add_block(BlockBuilder.paragraph("Description"))
        editor.add_block(BlockBuilder.bullet_list_item("Point 1"))
        editor.add_block(BlockBuilder.bullet_list_item("Point 2"))

        # Reorder
        editor.move_block(0, 5)

        # Save
        output = temp_dir / "edited.atrb"
        editor.save(output)

        # Reload and verify
        reloaded = DocumentEditor.from_file(output)
        assert len(reloaded) == original_count + 4
