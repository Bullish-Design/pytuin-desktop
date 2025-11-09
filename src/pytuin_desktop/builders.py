# src/pytuin_desktop/builders.py
from __future__ import annotations

from uuid import uuid4
from typing import Literal

from pytuin_desktop.models.blocks import (
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
    AnyBlock,
)
from pytuin_desktop.models.content import (
    TextContent,
    TextStyles,
    RunbookLinkContent,
    RunbookLinkProps,
)
from pytuin_desktop.models.dependency import DependencySpec
from pytuin_desktop.models.props import (
    TextProps,
    HeadingProps,
    EditorProps,
    ScriptProps,
    RunProps,
    CheckListProps,
    CodeBlockProps,
    EnvProps,
    VarProps,
    LocalVarProps,
    VarDisplayProps,
    DirectoryProps,
    DropdownProps,
    SQLiteProps,
    PostgresProps,
    HttpProps,
    MediaProps,
    FileProps,
)


class BlockBuilder:
    """Factory methods for creating common block types."""

    @staticmethod
    def paragraph(
        text: str = "",
        bold: bool = False,
        italic: bool = False,
        text_color: str = "default",
        background_color: str = "default",
    ) -> ParagraphBlock:
        """Create a paragraph block with optional text and styling."""
        content = []
        if text:
            content = [
                TextContent(
                    text=text,
                    styles=TextStyles(bold=bold, italic=italic),
                )
            ]

        return ParagraphBlock(
            id=uuid4(),
            props=TextProps(
                textColor=text_color,
                backgroundColor=background_color,
            ),
            content=content,
        )

    @staticmethod
    def heading(
        text: str,
        level: Literal[1, 2, 3, 4, 5, 6] = 1,
        is_toggleable: bool = False,
    ) -> HeadingBlock:
        """Create a heading block."""
        return HeadingBlock(
            id=uuid4(),
            props=HeadingProps(level=level, isToggleable=is_toggleable),
            content=[TextContent(text=text)],
        )

    @staticmethod
    def horizontal_rule() -> HorizontalRuleBlock:
        """Create a horizontal rule divider."""
        return HorizontalRuleBlock(id=uuid4())

    @staticmethod
    def editor(
        name: str,
        code: str = "",
        language: str = "python",
        variable_name: str = "variable",
        sync_variable: bool = False,
    ) -> EditorBlock:
        """Create a code editor block."""
        return EditorBlock(
            id=uuid4(),
            props=EditorProps(
                name=name,
                code=code,
                language=language,
                variableName=variable_name,
                syncVariable=sync_variable,
            ),
        )

    @staticmethod
    def script(
        name: str,
        code: str = "",
        interpreter: str = "/bin/bash",
        output_variable: str = "",
        output_visible: bool = True,
        dependency: str | DependencySpec | None = None,
    ) -> ScriptBlock:
        """Create a script execution block."""
        # Convert dependency to string format for storage
        if dependency is None:
            dep_value = "{}"
        elif isinstance(dependency, str):
            dep_value = dependency
        else:
            dep_value = dependency.to_json_string()

        return ScriptBlock(
            id=uuid4(),
            props=ScriptProps(
                name=name,
                code=code,
                interpreter=interpreter,
                outputVariable=output_variable,
                outputVisible=output_visible,
                dependency=dep_value,
            ),
        )

    @staticmethod
    def run(
        name: str,
        code: str = "",
        run_type: str = "bash",
        output_visible: bool = True,
        is_global: bool = False,
        dependency: str | DependencySpec | None = None,
    ) -> RunBlock:
        """Create a terminal/run block."""
        # Convert dependency to string format for storage
        if dependency is None:
            dep_value = "{}"
        elif isinstance(dependency, str):
            dep_value = dependency
        else:
            dep_value = dependency.to_json_string()

        return RunBlock(
            id=uuid4(),
            props=RunProps(
                name=name,
                code=code,
                type=run_type,
                pty="",
                outputVisible=output_visible,
                dependency=dep_value,
            ),
        )

    @staticmethod
    def quote(text: str) -> QuoteBlock:
        """Create a quote block."""
        return QuoteBlock(
            id=uuid4(),
            props=TextProps(),
            content=[TextContent(text=text)],
        )

    @staticmethod
    def bullet_list_item(text: str) -> BulletListItemBlock:
        """Create a bullet list item."""
        return BulletListItemBlock(
            id=uuid4(),
            props=TextProps(),
            content=[TextContent(text=text)],
        )

    @staticmethod
    def numbered_list_item(text: str) -> NumberedListItemBlock:
        """Create a numbered list item."""
        return NumberedListItemBlock(
            id=uuid4(),
            props=TextProps(),
            content=[TextContent(text=text)],
        )

    @staticmethod
    def checklist_item(text: str, checked: bool = False) -> CheckListItemBlock:
        """Create a checklist item."""
        return CheckListItemBlock(
            id=uuid4(),
            props=CheckListProps(checked=checked),
            content=[TextContent(text=text)],
        )

    @staticmethod
    def toggle_item(
        text: str, children: list[AnyBlock] | None = None
    ) -> ToggleListItemBlock:
        """Create a toggle list item with optional children."""
        return ToggleListItemBlock(
            id=uuid4(),
            props=TextProps(),
            content=[TextContent(text=text)],
            children=children or [],
        )

    @staticmethod
    def code_block(code: str, language: str = "python") -> CodeBlockBlock:
        """Create a code block with syntax highlighting."""
        return CodeBlockBlock(
            id=uuid4(),
            props=CodeBlockProps(language=language),
            content=[TextContent(text=code)],
        )

    @staticmethod
    def env_var(name: str, value: str) -> EnvBlock:
        """Create an environment variable block."""
        return EnvBlock(id=uuid4(), props=EnvProps(name=name, value=value))

    @staticmethod
    def var(name: str, value: str) -> VarBlock:
        """Create a variable block."""
        return VarBlock(id=uuid4(), props=VarProps(name=name, value=value))

    @staticmethod
    def local_var(name: str) -> LocalVarBlock:
        """Create a local variable block."""
        return LocalVarBlock(id=uuid4(), props=LocalVarProps(name=name))

    @staticmethod
    def var_display(name: str) -> VarDisplayBlock:
        """Create a variable display block."""
        return VarDisplayBlock(id=uuid4(), props=VarDisplayProps(name=name))

    @staticmethod
    def directory(path: str) -> DirectoryBlock:
        """Create a directory block."""
        return DirectoryBlock(id=uuid4(), props=DirectoryProps(path=path))

    @staticmethod
    def local_directory() -> LocalDirectoryBlock:
        """Create a local directory block."""
        return LocalDirectoryBlock(id=uuid4(), props=DirectoryProps(path=""))

    @staticmethod
    def dropdown(
        name: str,
        options: str = "",
        fixed_options: str = "",
        variable_options: str = "",
        command_options: str = "",
        value: str = "",
        options_type: Literal["fixed", "variable", "command"] = "fixed",
        interpreter: str = "/bin/bash",
    ) -> DropdownBlock:
        """Create a dropdown block."""
        return DropdownBlock(
            id=uuid4(),
            props=DropdownProps(
                name=name,
                options=options,
                fixedOptions=fixed_options,
                variableOptions=variable_options,
                commandOptions=command_options,
                value=value,
                optionsType=options_type,
                interpreter=interpreter,
            ),
        )

    @staticmethod
    def sqlite(
        name: str,
        query: str,
        uri: str,
        auto_refresh: int = 0,
        dependency: str | DependencySpec | None = None,
    ) -> SQLiteBlock:
        """Create a SQLite query block."""
        # Convert dependency to string format for storage
        if dependency is None:
            dep_value = "{}"
        elif isinstance(dependency, str):
            dep_value = dependency
        else:
            dep_value = dependency.to_json_string()

        return SQLiteBlock(
            id=uuid4(),
            props=SQLiteProps(
                name=name,
                query=query,
                uri=uri,
                autoRefresh=auto_refresh,
                dependency=dep_value,
            ),
        )

    @staticmethod
    def postgres(
        name: str,
        query: str,
        uri: str,
        auto_refresh: int = 0,
        dependency: str | DependencySpec | None = None,
    ) -> PostgresBlock:
        """Create a PostgreSQL query block."""
        # Convert dependency to string format for storage
        if dependency is None:
            dep_value = "{}"
        elif isinstance(dependency, str):
            dep_value = dependency
        else:
            dep_value = dependency.to_json_string()

        return PostgresBlock(
            id=uuid4(),
            props=PostgresProps(
                name=name,
                query=query,
                uri=uri,
                autoRefresh=auto_refresh,
                dependency=dep_value,
            ),
        )

    @staticmethod
    def http(
        name: str,
        url: str,
        verb: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET",
        body: str = "",
        headers: str = "",
        dependency: str | DependencySpec | None = None,
    ) -> HttpBlock:
        """Create an HTTP request block."""
        # Convert dependency to string format for storage
        if dependency is None:
            dep_value = "{}"
        elif isinstance(dependency, str):
            dep_value = dependency
        else:
            dep_value = dependency.to_json_string()

        return HttpBlock(
            id=uuid4(),
            props=HttpProps(
                name=name,
                url=url,
                verb=verb,
                body=body,
                headers=headers,
                dependency=dep_value,
            ),
        )

    @staticmethod
    def image(name: str, url: str, caption: str = "") -> ImageBlock:
        """Create an image block."""
        return ImageBlock(
            id=uuid4(),
            props=MediaProps(name=name, url=url, caption=caption),
        )

    @staticmethod
    def video(url: str, name: str = "", caption: str = "") -> VideoBlock:
        """Create a video block."""
        return VideoBlock(
            id=uuid4(),
            props=MediaProps(name=name, url=url, caption=caption),
        )

    @staticmethod
    def audio(url: str, name: str = "", caption: str = "") -> AudioBlock:
        """Create an audio block."""
        return AudioBlock(
            id=uuid4(),
            props=MediaProps(name=name, url=url, caption=caption),
        )

    @staticmethod
    def file(name: str, url: str, caption: str = "") -> FileBlock:
        """Create a file attachment block."""
        return FileBlock(
            id=uuid4(),
            props=FileProps(name=name, url=url, caption=caption),
        )

    @staticmethod
    def runbook_link(
        runbook_id: str, block_id: str | None = None, text: str = ""
    ) -> RunbookLinkContent:
        """Create a runbook link content element."""
        from uuid import UUID

        return RunbookLinkContent(
            props=RunbookLinkProps(
                runbookId=UUID(runbook_id),
                blockId=UUID(block_id) if block_id else None,
            ),
            text=text,
        )
