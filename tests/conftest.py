"""Shared fixtures.

**Test stores are built here, in code, into a temp directory.** There is no
checked-in store of fabricated documents.

That is deliberate. An earlier version kept a `demo_store/` folder of
plausible-looking PDFs on disk, and it was mistaken twice for real data -
including once when a skill produced a confident-looking analysis whose every
fact came from those invented files. A store that looks real is a liability in
a system whose whole premise is that claims trace to sources someone can open.

Built here, the same rows are unmistakably scaffolding: they exist for the
length of one test and nowhere else. The real store at `ksp/` ships empty and
stays that way.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kspcore.store import Store  # noqa: E402
from kspcore.vocab import Vocab  # noqa: E402

SOURCE_HEADER = [
    "name", "file", "record_type", "description", "quick_insights", "pillar",
    "p1_cluster", "p2_focus_area", "geography", "source_type", "publisher",
    "source_url", "year_published", "total_author_count", "date_added",
]
ACTOR_HEADER = [
    "id", "name", "form", "actor_type", "affiliation_id", "source_files",
    "pillar", "p1_cluster", "p2_focus_area", "geography", "origin", "basis",
    "date_added",
]
AUTHORSHIP_HEADER = ["actor_id", "source_file", "position"]

UL = "Urban Liveability"


def source(name, file, **over):
    """One LAB row. Every field defaults to something valid."""
    row = {
        "name": name, "file": file, "record_type": "Document",
        "description": f"Synthetic description for {name}.", "quick_insights": "",
        "pillar": "PLANET", "p1_cluster": UL, "p2_focus_area": "Pollution",
        "geography": "Indonesia;Southeast Asia", "source_type": "Research",
        "publisher": "Synthetic Publisher", "source_url": "",
        "year_published": "2024", "total_author_count": "", "date_added": "2026-08-16",
    }
    row.update(over)
    return row


def actor(actor_id, name, **over):
    row = {
        "id": str(actor_id), "name": name, "form": "Person", "actor_type": "",
        "affiliation_id": "", "source_files": "", "pillar": "", "p1_cluster": "",
        "p2_focus_area": "", "geography": "", "origin": "From LAB", "basis": "",
        "date_added": "2026-08-16",
    }
    row.update(over)
    return row


# -- the standard test store ------------------------------------------------
#
# Shaped to exercise the behaviours that are easy to break, not to look like a
# real corpus. Each row below earns its place; see tests for what each proves.

DEMO_SOURCES = [
    source("Heat and PM2.5 compound exposure study", "Heat_PM25_Study.pdf",
           quick_insights="PM2.5 concentrations measurably higher on heatwave days.",
           source_url="https://example.org/synthetic/heat-pm25", total_author_count="2"),
    source("Air pollution convenings learning note", "Air_Pollution_Convenings.pdf",
           geography="Southeast Asia", source_type="Internal", publisher="Internal",
           year_published="2025"),
    # Global: proves global documents and the actors reached only through them
    # are counted apart from a country.
    source("Clean cooking outcome bond brief", "Clean_Cooking_Outcome_Bond.pdf",
           geography="Global", source_type="Industry", publisher="Synthetic Issuer",
           year_published="2023"),
    source("Jakarta air quality review", "Jakarta_Air_Quality_Review.pdf",
           year_published="2025", total_author_count="1"),
    # -- Water & Waste --
    source("Mekong water security assessment", "Mekong_Water_Security.pdf",
           p2_focus_area="Water & Waste", geography="Vietnam;Southeast Asia",
           total_author_count="1"),
    # Policy under Water & Waste only, so Pollution queries have a real
    # source-type absence to report.
    source("Urban waste management policy brief", "Urban_Waste_Management_Brief.pdf",
           p2_focus_area="Water & Waste", source_type="Policy", year_published="2026"),
    source("Community water kiosk programme", "Vietnam_Water_Kiosk.pdf",
           p2_focus_area="Water & Waste", geography="Vietnam;Southeast Asia",
           quick_insights="Twelve kiosks operating after five years; 78% still "
                          "financially self-sustaining at year three.",
           source_url="https://example.org/synthetic/water-kiosks", total_author_count="2"),
    source("Rural water access baseline", "Indonesia_Water_Access_Baseline.pdf",
           p2_focus_area="Water & Waste", year_published="2025", total_author_count="3"),
    source("Water utility financing note", "SEA_Water_Utility_Financing.pdf",
           p2_focus_area="Water & Waste", geography="Southeast Asia",
           source_type="Industry", publisher="Unknown", year_published="2023"),
    # A folder row: every field blank, to prove folders never reach a query.
    {**{k: "" for k in SOURCE_HEADER}, "name": "A folder", "record_type": "Folder"},
]

DEMO_ACTORS = [
    actor(1, "Jane Smith", actor_type="Researcher", affiliation_id="3",
          source_files="Heat_PM25_Study.pdf", geography="Indonesia;Southeast Asia"),
    actor(2, "Wei Chen", actor_type="Researcher", affiliation_id="3",
          source_files="Heat_PM25_Study.pdf", geography="Indonesia;Southeast Asia"),
    actor(3, "Institute of Environmental Health", form="Organisation",
          actor_type="Researcher",
          source_files="Jakarta_Air_Quality_Review.pdf;Indonesia_Water_Access_Baseline.pdf",
          geography="Indonesia;Southeast Asia"),
    # Reached only through the Global document.
    actor(4, "A Global Funder", form="Organisation", actor_type="Funder",
          source_files="Clean_Cooking_Outcome_Bond.pdf", geography="Global"),
    # Manual, no document, NO topic tag: stays a geography match only.
    actor(5, "An Untagged Fund", form="Organisation", geography="Southeast Asia",
          origin="Manual", basis="Named by a colleague, checked 14 Aug"),
    actor(6, "A River Commission", form="Organisation", actor_type="Government",
          source_files="Mekong_Water_Security.pdf", geography="Vietnam;Southeast Asia"),
    actor(7, "A Cooperative Union", form="Organisation", actor_type="Implementer",
          source_files="Vietnam_Water_Kiosk.pdf", geography="Vietnam;Southeast Asia"),
    # Manual, no document, WITH a topic tag: the case the tag column exists for.
    actor(8, "A Tagged Advocate", actor_type="Advocate", pillar="PLANET",
          p1_cluster=UL, p2_focus_area="Water & Waste",
          geography="Indonesia;Southeast Asia", origin="Manual",
          basis="Organisation staff page, checked 29 Jul"),
]

DEMO_AUTHORSHIP = [
    {"actor_id": "1", "source_file": "Heat_PM25_Study.pdf", "position": "1"},
    {"actor_id": "2", "source_file": "Heat_PM25_Study.pdf", "position": "2"},
    {"actor_id": "3", "source_file": "Jakarta_Air_Quality_Review.pdf", "position": "1"},
    {"actor_id": "4", "source_file": "Clean_Cooking_Outcome_Bond.pdf", "position": "1"},
    {"actor_id": "6", "source_file": "Mekong_Water_Security.pdf", "position": "1"},
    {"actor_id": "7", "source_file": "Vietnam_Water_Kiosk.pdf", "position": "2"},
    {"actor_id": "3", "source_file": "Indonesia_Water_Access_Baseline.pdf", "position": "1"},
]


def _write(path: Path, header: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_store(root: Path, sources=(), actors=(), authorship=()) -> Path:
    """Write a store at `root`, creating a placeholder file for every LAB row.

    The placeholder exists because the integrity check verifies presence, not
    content - so a one-line file is all a test ever needs.
    """
    _write(root / "lab" / "sources.csv", SOURCE_HEADER, list(sources))
    _write(root / "lead" / "actors.csv", ACTOR_HEADER, list(actors))
    _write(root / "lead" / "authorship.csv", AUTHORSHIP_HEADER, list(authorship))

    documents = root / "lab" / "documents"
    documents.mkdir(parents=True, exist_ok=True)
    for row in sources:
        if row.get("file"):
            (documents / row["file"]).write_text(
                "Placeholder for a test. Not a document.\n", encoding="utf-8"
            )
    return root


@pytest.fixture
def vocab() -> Vocab:
    return Vocab.load(ROOT / "ksp" / "vocab")


@pytest.fixture
def scratch(tmp_path) -> Path:
    """The standard store, on disk and writable. For breaking on purpose."""
    return build_store(tmp_path / "store", DEMO_SOURCES, DEMO_ACTORS, DEMO_AUTHORSHIP)


@pytest.fixture
def demo(scratch) -> Store:
    return Store.load(scratch)


@pytest.fixture
def empty_path(tmp_path) -> Path:
    """Headers and nothing else - the state the real store ships in."""
    return build_store(tmp_path / "empty")


@pytest.fixture
def empty(empty_path) -> Store:
    return Store.load(empty_path)


def write_rows(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
