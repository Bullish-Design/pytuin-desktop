# path: src/pytuin_desktop/services.py
"""Service classes for document operations (v4 Phase 6).
- DocumentLoader: streaming load helpers with metrics.
- DocumentSerializer: YAML-safe serialization helpers shared by writer/editor.
"""
from __future__ import annotations

from typing import Any, TextIO, Optional
from pathlib import Path
from logging import Logger

from .parser import AtrbParser
from .serializers import YamlSerializer, get_default_serializer
from .logger import logger as _default_logger
from .metrics import MetricsCollector, get_default_collector, TimingContext


class DocumentLoader:
    """Service for loading Atrb documents."""
    def __init__(
        self,
        *,
        logger: Logger | None = None,
        metrics: MetricsCollector | None = None,
    ) -> None:
        self._logger = logger or _default_logger
        self._metrics = metrics or get_default_collector()

    def load_from_file(self, filepath: str | Path, *, validate: bool = True) -> "AtrbDocument":
        """Load an Atrb document from disk using the parser."""
        p = Path(filepath)
        self._logger.info("services.load_from_file", extra={"path": str(p.absolute())})
        with TimingContext(self._metrics, "services.load_from_file"):
            doc = AtrbParser.parse_file(p, logger=self._logger, validate=validate, metrics=self._metrics)
        self._metrics.increment_counter("documents_loaded")
        return doc

    def load_from_stream(self, stream: TextIO, *, validate: bool = True) -> "AtrbDocument":
        """Load an Atrb document from an open stream."""
        with TimingContext(self._metrics, "services.load_from_stream"):
            doc = AtrbParser.parse_stream(stream, logger=self._logger, validate=validate, metrics=self._metrics)
        self._metrics.increment_counter("documents_loaded")
        return doc


class DocumentSerializer:
    """Service for serializing documents and portable structures."""
    def __init__(
        self,
        *,
        serializer: Optional[YamlSerializer] = None,
        logger: Logger | None = None,
        metrics: MetricsCollector | None = None,
    ) -> None:
        self._serializer: YamlSerializer = serializer or get_default_serializer()
        self._logger = logger or _default_logger
        self._metrics = metrics or get_default_collector()

    # --- utility helpers ---
    def ensure_single_trailing_newline(self, text: str) -> str:
        """Ensure the given text ends with exactly one trailing newline."""
        if not text:
            return "\n"
        return text.rstrip("\n") + "\n"

    def to_jsonable(self, obj: Any) -> Any:
        """Convert nested objects into JSON/YAML-serializable primitives."""
        from uuid import UUID
        from enum import Enum
        if isinstance(obj, dict):
            return {k: self.to_jsonable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self.to_jsonable(v) for v in obj]
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, "model_dump"):
            try:
                return self.to_jsonable(obj.model_dump(mode="python"))
            except Exception:
                pass
        if isinstance(obj, UUID):
            return str(obj)
        return obj

    # --- YAML IO convenience ---
    def dumps_yaml(self, data: Any, **kwargs) -> str:
        """Dump to YAML string using the configured serializer."""
        with TimingContext(self._metrics, "services.dumps_yaml"):
            return self._serializer.dumps(data, **kwargs)

    def dump_yaml(self, data: Any, stream: TextIO, **kwargs) -> None:
        """Dump to YAML stream using the configured serializer."""
        with TimingContext(self._metrics, "services.dump_yaml"):
            self._serializer.dump(data, stream, **kwargs)
