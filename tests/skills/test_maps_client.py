"""Tests for maps_client OSRM routing URL construction.

The maps skill routes through the FOSSGIS OSRM servers
(routing.openstreetmap.de), which serve separate car, foot and bike
graphs via the routed-<mode> path prefix. router.project-osrm.org, the
previous host, only serves the car graph and ignored the foot/bike
profile segment (#158494).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO / "skills" / "productivity" / "maps" / "scripts"

EXPECTED_PREFIX = {
    "driving": "https://routing.openstreetmap.de/routed-car/route/v1/driving/",
    "walking": "https://routing.openstreetmap.de/routed-foot/route/v1/driving/",
    "cycling": "https://routing.openstreetmap.de/routed-bike/route/v1/driving/",
}


def _load_maps_client():
    spec = importlib.util.spec_from_file_location(
        "maps_client", SCRIPTS / "maps_client.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["maps_client"] = module
    spec.loader.exec_module(module)
    return module


def _capture_url(monkeypatch, mc, mode):
    """Run one maps_client command with stubbed geocode/HTTP and return the OSRM URL it requests."""
    urls = []
    monkeypatch.setattr(mc, "geocode_single", lambda q: (13.7515, 100.5423, q))
    monkeypatch.setattr(
        mc,
        "http_get",
        lambda u: (
            urls.append(u),
            dict(code="Ok", routes=[dict(distance=1000, duration=600, legs=[])]),
        )[1],
    )
    monkeypatch.setattr(mc, "print_json", lambda d: None)
    mc.cmd_distance(SimpleNamespace(origin=["A"], to=["B"], mode=mode))
    assert len(urls) == 1, urls
    return urls[0]


def test_distance_url_matches_mode(monkeypatch):
    mc = _load_maps_client()
    for mode, prefix in EXPECTED_PREFIX.items():
        url = _capture_url(monkeypatch, mc, mode)
        assert url.startswith(prefix), (mode, url)


def test_directions_url_matches_mode(monkeypatch):
    mc = _load_maps_client()
    for mode, prefix in EXPECTED_PREFIX.items():
        url = _capture_url(monkeypatch, mc, mode)
        assert url.startswith(prefix), (mode, url)


def test_mode_choices_unchanged(monkeypatch):
    mc = _load_maps_client()
    assert list(mc.OSRM_PROFILES.keys()) == ["driving", "walking", "cycling"]
