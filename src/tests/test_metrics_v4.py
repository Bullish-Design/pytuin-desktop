# path: src/tests/test_metrics_v4.py
import time
from pytuin_desktop.metrics import InMemoryMetricsCollector, TimingContext

def test_inmemory_metrics_collector_and_timing():
    mc = InMemoryMetricsCollector()
    with TimingContext(mc, "sleep10"):
        time.sleep(0.01)
    assert mc.get_average_duration("sleep10") is not None
    mc.increment_counter("docs", 2)
    assert mc.get_counter("docs") == 2
    mc.record_value("size", 123.0)
    assert 123.0 in mc.values["size"]
