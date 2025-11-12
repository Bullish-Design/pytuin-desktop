# path: src/pytuin_desktop/id_generators.py
"""ID generation strategies for blocks (v4 Phase 3)."""
from __future__ import annotations
import random
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4, uuid1

@runtime_checkable
class BlockIdGenerator(Protocol):
    def generate(self) -> UUID: ...

class UUIDv4Generator:
    def generate(self) -> UUID: return uuid4()

class UUIDv1Generator:
    def generate(self) -> UUID: return uuid1()

class DeterministicGenerator:
    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)
    def generate(self) -> UUID:
        return UUID(int=self._rng.getrandbits(128))

class SequentialGenerator:
    def __init__(self, start: int = 0) -> None:
        self._n = start
    def generate(self) -> UUID:
        self._n += 1
        return UUID(int=self._n)

_default: BlockIdGenerator = UUIDv4Generator()
def get_default_generator() -> BlockIdGenerator: return _default
def set_default_generator(gen: BlockIdGenerator) -> None:
    global _default; _default = gen
def reset_default_generator() -> None:
    global _default; _default = UUIDv4Generator()
def generate_block_id() -> UUID: return _default.generate()
