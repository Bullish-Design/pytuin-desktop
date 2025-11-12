# path: src/pytuin_desktop/serializers.py
"""Serialization protocols and implementations (v4 Phase 4 - Step 14)."""
from __future__ import annotations

from typing import Any, Protocol, TextIO, runtime_checkable
import yaml


@runtime_checkable
class YamlSerializer(Protocol):
    def dump(self, data: Any, stream: TextIO, **kwargs) -> None: ...
    def dumps(self, data: Any, **kwargs) -> str: ...
    def load(self, stream: TextIO) -> Any: ...
    def loads(self, text: str) -> Any: ...


class SafeYamlSerializer:
    """Default YAML serializer using safe load/dump."""
    def dump(self, data: Any, stream: TextIO, **kwargs) -> None:
        yaml.safe_dump(data, stream, **kwargs)

    def dumps(self, data: Any, **kwargs) -> str:
        return yaml.safe_dump(data, **kwargs)

    def load(self, stream: TextIO) -> Any:
        return yaml.safe_load(stream)

    def loads(self, text: str) -> Any:
        return yaml.safe_load(text)


_default_serializer: YamlSerializer = SafeYamlSerializer()


def get_default_serializer() -> YamlSerializer:
    return _default_serializer


def set_default_serializer(serializer: YamlSerializer) -> None:
    global _default_serializer
    _default_serializer = serializer
