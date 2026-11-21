"""ManagedWorker.interrupt conforms to the legacy interrupt ABI request_hard_interrupt drives."""

from __future__ import annotations

from agent.interrupt_compat import request_hard_interrupt
from gateway.session_managed_worker import ManagedWorker


def test_request_hard_interrupt_drives_managed_worker_without_type_error() -> None:
    worker = ManagedWorker.__new__(ManagedWorker)
    sent: list[dict] = []
    worker.control = sent.append  # type: ignore[method-assign]

    assert request_hard_interrupt(worker, "[Gateway shutting down]") is True
    assert request_hard_interrupt(worker) is True

    assert sent == [{"type": "stop"}, {"type": "stop"}]
