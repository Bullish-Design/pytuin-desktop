
"""Repository protocol and in‑memory implementation (v3 Step 9)."""
from __future__ import annotations

from typing import Protocol, runtime_checkable, Optional, List, Dict
from .models import AtrbDocument


@runtime_checkable
class DocumentRepository(Protocol):
    """Storage seam for AtrbDocument persistence.
    
    Concrete implementations may persist to disk, SQLModel, etc.
    """
    def get(self, doc_id: str) -> Optional[AtrbDocument]: ...
    def save(self, doc: AtrbDocument) -> None: ...
    def list(self, limit: int = 50, offset: int = 0) -> list[AtrbDocument]: ...


class InMemoryDocumentRepository:
    """Simple in‑memory store for tests and examples."""
    def __init__(self) -> None:
        self._store: Dict[str, AtrbDocument] = {}

    def get(self, doc_id: str) -> Optional[AtrbDocument]:
        return self._store.get(doc_id)

    def save(self, doc: AtrbDocument) -> None:
        self._store[str(doc.id)] = doc

    def list(self, limit: int = 50, offset: int = 0) -> list[AtrbDocument]:
        values = list(self._store.values())
        return values[offset: offset + limit]
