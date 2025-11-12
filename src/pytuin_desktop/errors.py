# path: pytuin_desktop/errors.py
"""Exception hierarchy for Pytuin-Desktop (v4 Phase 1)."""
from __future__ import annotations

class AtrbError(Exception):
    def __init__(self, message: str, *, suggestion: str | None = None, context: dict | None = None):
        self.message = message
        self.suggestion = suggestion
        self.context = context or {}
        full = message
        if suggestion:
            full = f"{full}\n\nSuggestion: {suggestion}"
        if self.context:
            ctx = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            full = f"{full}\n\nContext: {ctx}"
        super().__init__(full)

class AtrbParseError(AtrbError): ...
class AtrbSchemaError(AtrbError): ...
class AtrbValidationError(AtrbError): ...
class TemplateDiscoveryError(AtrbError): ...
