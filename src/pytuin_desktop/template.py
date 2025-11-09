# src/pytuin_desktop/template.py
from __future__ import annotations

import re
from typing import Any
from abc import ABC, abstractmethod
from pytuin_desktop.models.blocks import AnyBlock
from pytuin_desktop.models.document import AtrbDocument


class TemplateVariable(ABC):
    """Base class for template variables that can be resolved."""

    @abstractmethod
    def get_pattern(self) -> str:
        """Return regex pattern to match this variable type."""
        pass

    @abstractmethod
    def extract_references(self, text: str) -> set[str]:
        """Extract all references of this variable type from text."""
        pass

    @abstractmethod
    def resolve(self, reference: str, context: dict[str, Any]) -> str | None:
        """Resolve a variable reference using the provided context."""
        pass


class VarTemplateVariable(TemplateVariable):
    """Handler for {{ var.variable_name }} template variables."""

    def get_pattern(self) -> str:
        return r'{{\s*var\.(\w+)(?:\s*\|\s*[^}]+)?\s*}}'

    def extract_references(self, text: str) -> set[str]:
        """Extract all {{ var.* }} references from text."""
        pattern = self.get_pattern()
        matches = re.finditer(pattern, text)
        return {match.group(1) for match in matches}

    def resolve(self, reference: str, context: dict[str, Any]) -> str | None:
        """Resolve var reference from context."""
        variables = context.get("variables", {})
        return variables.get(reference)


class DocTemplateVariable(TemplateVariable):
    """Handler for {{ doc.* }} template variables."""

    def get_pattern(self) -> str:
        # Matches doc.first, doc.last, doc.content[0], doc.named.name, doc.previous, etc
        return r'{{\s*doc\.([a-zA-Z0-9_.[\]]+)(?:\s*\|\s*[^}]+)?\s*}}'

    def extract_references(self, text: str) -> set[str]:
        """Extract all {{ doc.* }} references from text."""
        pattern = self.get_pattern()
        matches = re.finditer(pattern, text)
        return {match.group(1) for match in matches}

    def resolve(self, reference: str, context: dict[str, Any]) -> str | None:
        """Resolve doc reference from context."""
        document = context.get("document")
        if not document:
            return None

        parts = reference.split(".")
        if not parts:
            return None

        # Handle doc.first, doc.last
        if parts[0] == "first" and document.content:
            return self._extract_block_content(document.content[0])
        elif parts[0] == "last" and document.content:
            return self._extract_block_content(document.content[-1])

        # Handle doc.named.block_name
        elif parts[0] == "named" and len(parts) > 1:
            block_name = parts[1]
            for block in document.content:
                if hasattr(block.props, "name") and block.props.name == block_name:
                    if len(parts) > 2 and parts[2] == "content":
                        return self._extract_block_content(block)
                    return str(block.id)
            return None

        # Handle doc.content[index]
        elif parts[0].startswith("content[") and parts[0].endswith("]"):
            try:
                index_str = parts[0][8:-1]
                index = int(index_str)
                if 0 <= index < len(document.content):
                    return self._extract_block_content(document.content[index])
            except (ValueError, IndexError):
                return None

        return None

    def _extract_block_content(self, block: AnyBlock) -> str:
        """Extract text content from a block."""
        if hasattr(block, "content") and block.content:
            text_parts = []
            for item in block.content:
                if hasattr(item, "text"):
                    text_parts.append(item.text)
            return " ".join(text_parts)
        return ""


class WorkspaceTemplateVariable(TemplateVariable):
    """Handler for {{ workspace.* }} template variables."""

    def get_pattern(self) -> str:
        return r'{{\s*workspace\.(\w+)(?:\s*\|\s*[^}]+)?\s*}}'

    def extract_references(self, text: str) -> set[str]:
        """Extract all {{ workspace.* }} references from text."""
        pattern = self.get_pattern()
        matches = re.finditer(pattern, text)
        return {match.group(1) for match in matches}

    def resolve(self, reference: str, context: dict[str, Any]) -> str | None:
        """Resolve workspace reference from context."""
        workspace = context.get("workspace", {})
        return workspace.get(reference)


class TemplateResolver:
    """Main class for extracting and resolving template variables."""

    def __init__(self):
        self.handlers: dict[str, TemplateVariable] = {
            "var": VarTemplateVariable(),
            "doc": DocTemplateVariable(),
            "workspace": WorkspaceTemplateVariable(),
        }

    def extract_all_variables(self, text: str) -> dict[str, set[str]]:
        """Extract all template variables from text, grouped by type."""
        result = {}
        for var_type, handler in self.handlers.items():
            refs = handler.extract_references(text)
            if refs:
                result[var_type] = refs
        return result

    def find_document_variables(self, document: AtrbDocument) -> dict[str, set[str]]:
        """Find all template variables used in a document."""
        all_variables = {}

        def extract_from_block(block: AnyBlock) -> None:
            # Check content
            if hasattr(block, "content") and block.content:
                for item in block.content:
                    if hasattr(item, "text"):
                        vars_found = self.extract_all_variables(item.text)
                        for var_type, refs in vars_found.items():
                            if var_type not in all_variables:
                                all_variables[var_type] = set()
                            all_variables[var_type].update(refs)

            # Check props
            if hasattr(block, "props"):
                for key, value in block.props.model_dump().items():
                    if isinstance(value, str):
                        vars_found = self.extract_all_variables(value)
                        for var_type, refs in vars_found.items():
                            if var_type not in all_variables:
                                all_variables[var_type] = set()
                            all_variables[var_type].update(refs)

            # Check children recursively
            if hasattr(block, "children") and block.children:
                for child in block.children:
                    extract_from_block(child)

        for block in document.content:
            extract_from_block(block)

        return all_variables

    def resolve_template(self, text: str, context: dict[str, Any]) -> str:
        """Resolve all template variables in text using the provided context."""
        result = text

        # Process each handler type
        for var_type, handler in self.handlers.items():
            pattern = handler.get_pattern()
            matches = list(re.finditer(pattern, result))

            # Process matches in reverse order to maintain string positions
            for match in reversed(matches):
                reference = match.group(1)
                resolved = handler.resolve(reference, context)

                if resolved is not None:
                    # Replace the entire {{ }} expression with the resolved value
                    result = result[: match.start()] + resolved + result[match.end() :]

        return result
