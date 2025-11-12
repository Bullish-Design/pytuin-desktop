# path: pytuin_desktop/repository.py
"""Repository protocol and in-memory implementation."""
from __future__ import annotations
from typing import Protocol, runtime_checkable, Optional, Dict
from .models import AtrbDocument

@runtime_checkable
class DocumentRepository(Protocol):
    def get(self, doc_id: str) -> Optional[AtrbDocument]: ...
    def save(self, doc: AtrbDocument) -> None: ...
    def list(self, limit: int = 50, offset: int = 0) -> list[AtrbDocument]: ...

class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._store: Dict[str, AtrbDocument] = {}
    def get(self, doc_id: str) -> Optional[AtrbDocument]:
        return self._store.get(doc_id)
    def save(self, doc: AtrbDocument) -> None:
        self._store[str(doc.id)] = doc
    def list(self, limit: int = 50, offset: int = 0) -> list[AtrbDocument]:
        vals = list(self._store.values())
        return vals[offset: offset + limit]
