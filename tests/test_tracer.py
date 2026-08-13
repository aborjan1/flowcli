from __future__ import annotations

import sys
from pathlib import Path

import pytest

from flowcli.tracer import SAMPLE_LIMIT, capture

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = FIXTURES / "traceproj"


@pytest.fixture(scope="module")
def work():
    sys.path.insert(0, str(FIXTURES))
    try:
        import traceproj.work as work_mod

        yield work_mod
    finally:
        sys.path.remove(str(FIXTURES))


def test_capture_types_and_node_id_keying(work) -> None:
    with capture(ROOT) as cap:
        work.add(1, 2)
        repo = work.Repo()
        repo.bump(3)
        work.outer()
    add = cap.functions["traceproj.work:add"]
    assert add["args"] == {"a": ["int"], "b": ["int"]}
    assert add["returns"] == ["int"]
    assert "traceproj.work:Repo.__init__" in cap.functions
    bump = cap.functions["traceproj.work:Repo.bump"]
    assert bump["args"]["self"] == ["traceproj.work.Repo"]
    assert "traceproj.work:outer.inner" in cap.functions  # <locals> stripped
    assert list(cap.functions) == sorted(cap.functions)


def test_sampling_caps_and_pairs_returns(work) -> None:
    with capture(ROOT) as cap:
        for i in range(10):
            work.many(i)
    rec = cap.functions["traceproj.work:many"]
    assert rec["ncalls"] == 10
    assert len(rec["samples"]) == SAMPLE_LIMIT
    assert rec["samples"][0] == {"args": {"x": "0"}, "ret": "0"}


def test_no_samples_mode(work) -> None:
    with capture(ROOT, samples=False) as cap:
        work.many(1)
    assert cap.functions["traceproj.work:many"]["samples"] == []


def test_foreign_frames_filtered(work) -> None:
    import json as json_mod

    with capture(ROOT) as cap:
        work.add(1, 2)
        json_mod.dumps({"a": 1})
    assert all(key.startswith("traceproj.") for key in cap.functions)


def test_events_recorded(work) -> None:
    with capture(ROOT) as cap:
        work.main()
    assert ["traceproj.work:main", "traceproj.work:add"] in cap.events
    assert ["traceproj.work:chain", "traceproj.work:helper"] in cap.events
    assert ["traceproj.work:fact", "traceproj.work:fact"] in cap.events  # recursion
    assert cap.calls_total >= 15


def test_lambda_frames_skipped(work) -> None:
    with capture(ROOT) as cap:
        work.uses_lambda()
    assert not any("<lambda>" in key for key in cap.functions)
    assert "traceproj.work:uses_lambda" in cap.functions


def test_profile_hook_restored(work) -> None:
    prev = sys.getprofile()
    with capture(ROOT) as cap:
        work.add(1, 2)
    assert sys.getprofile() is prev
    assert cap.functions  # and we still captured
