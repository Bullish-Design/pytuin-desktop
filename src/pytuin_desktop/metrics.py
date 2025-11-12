# path: src/pytuin_desktop/metrics.py
"""Metrics collection protocol and helpers (v4 Phase 4 - Step 15)."""
from __future__ import annotations

from typing import Protocol, runtime_checkable
from collections import defaultdict
import time


@runtime_checkable
class MetricsCollector(Protocol):
    def record_duration(self, operation: str, duration_ms: float) -> None: ...
    def increment_counter(self, metric: str, value: int = 1) -> None: ...
    def record_value(self, metric: str, value: float) -> None: ...


class NoOpMetricsCollector:
    def record_duration(self, operation: str, duration_ms: float) -> None: ...
    def increment_counter(self, metric: str, value: int = 1) -> None: ...
    def record_value(self, metric: str, value: float) -> None: ...


class InMemoryMetricsCollector:
    def __init__(self) -> None:
        self.durations: dict[str, list[float]] = defaultdict(list)
        self.counters: dict[str, int] = defaultdict(int)
        self.values: dict[str, list[float]] = defaultdict(list)

    def record_duration(self, operation: str, duration_ms: float) -> None:
        self.durations[operation].append(duration_ms)

    def increment_counter(self, metric: str, value: int = 1) -> None:
        self.counters[metric] += value

    def record_value(self, metric: str, value: float) -> None:
        self.values[metric].append(value)

    def get_average_duration(self, operation: str) -> float | None:
        vals = self.durations.get(operation) or []
        return (sum(vals) / len(vals)) if vals else None

    def get_counter(self, metric: str) -> int:
        return self.counters.get(metric, 0)

    def reset(self) -> None:
        self.durations.clear(); self.counters.clear(); self.values.clear()


class TimingContext:
    def __init__(self, metrics: MetricsCollector, operation: str):
        self.metrics = metrics
        self.operation = operation
        self._t0: float | None = None

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self._t0 is not None:
            dt = (time.perf_counter() - self._t0) * 1000.0
            self.metrics.record_duration(self.operation, dt)


_default_collector: MetricsCollector = NoOpMetricsCollector()


def get_default_collector() -> MetricsCollector:
    return _default_collector


def set_default_collector(collector: MetricsCollector) -> None:
    global _default_collector
    _default_collector = collector
