"""Exception hierarchy for Pytuin-Desktop (v3 Step 3)."""
from __future__ import annotations

class AtrbError(Exception):
    """Base class for all .atrb-related errors."""

class AtrbParseError(AtrbError):
    """Low-level parsing failure (e.g., invalid YAML)."""

class AtrbSchemaError(AtrbError):
    """The document structure is not conformant (missing/invalid keys)."""

class AtrbValidationError(AtrbError):
    """Semantic/type validation failure when constructing models."""

class TemplateDiscoveryError(AtrbError):
    """Template discovery failed (e.g., directory not found)."""
