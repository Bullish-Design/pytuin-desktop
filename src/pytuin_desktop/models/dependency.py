# src/pytuin_desktop/models/dependency.py
from __future__ import annotations

from pydantic import BaseModel, Field


class DependencySpec(BaseModel):
    """Dependency specification for blocks that require execution ordering."""

    model_config = {"populate_by_name": True}

    blocks: list[str] = Field(default_factory=list, description="List of block IDs this block depends on")
    variables: list[str] = Field(
        default_factory=list, description="List of variable names this block requires"
    )

    @classmethod
    def from_json_string(cls, json_str: str) -> DependencySpec:
        """Parse dependency spec from JSON string."""
        import json

        if not json_str or json_str == "{}":
            return cls()
        data = json.loads(json_str)
        return cls(**data)

    def to_json_string(self) -> str:
        """Convert to JSON string for storage."""
        import json

        return json.dumps(self.model_dump(exclude_defaults=True))

    def is_empty(self) -> bool:
        """Check if this dependency spec has any dependencies."""
        return not self.blocks and not self.variables

    def add_block_dependency(self, block_id: str) -> None:
        """Add a block dependency."""
        if block_id not in self.blocks:
            self.blocks.append(block_id)

    def remove_block_dependency(self, block_id: str) -> None:
        """Remove a block dependency."""
        if block_id in self.blocks:
            self.blocks.remove(block_id)

    def add_variable_dependency(self, variable_name: str) -> None:
        """Add a variable dependency."""
        if variable_name not in self.variables:
            self.variables.append(variable_name)

    def remove_variable_dependency(self, variable_name: str) -> None:
        """Remove a variable dependency."""
        if variable_name in self.variables:
            self.variables.remove(variable_name)
