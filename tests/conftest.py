"""Shared fixtures.

Tests run against ``tests/fixtures``, never against ``ksp/`` - the real store
ships empty and stays that way.
"""

from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kspcore.store import Store  # noqa: E402
from kspcore.vocab import Vocab  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
DEMO = FIXTURES / "demo_store"
EMPTY = FIXTURES / "empty_store"


@pytest.fixture
def vocab() -> Vocab:
    return Vocab.load(ROOT / "ksp" / "vocab")


@pytest.fixture
def demo() -> Store:
    return Store.load(DEMO)


@pytest.fixture
def empty() -> Store:
    return Store.load(EMPTY)


@pytest.fixture
def scratch(tmp_path) -> Path:
    """A writable copy of the demo store, for breaking on purpose."""
    target = tmp_path / "store"
    shutil.copytree(DEMO, target)
    return target


def write_rows(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


ACTOR_HEADER = [
    "id", "name", "form", "actor_type", "affiliation_id", "source_files",
    "pillar", "p1_cluster", "p2_focus_area", "geography", "origin", "basis",
    "date_added",
]
SOURCE_HEADER = [
    "name", "file", "record_type", "description", "quick_insights", "pillar",
    "p1_cluster", "p2_focus_area", "geography", "source_type", "publisher",
    "source_url", "year_published", "total_author_count", "date_added",
]
