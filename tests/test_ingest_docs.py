"""The handover documents must not disagree with what the validator enforces.

INGEST_SPEC.md and CONTROLLED_VALUES.md leave this repo and get handed to
whoever is populating the stores. If either drifts from the real schema or the
real vocabularies, work gets done against a spec that was quietly wrong - and
the mistake only surfaces after a crawl has already run.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from kspcore.store import read_csv, repo_root  # noqa: E402

DOCS = repo_root() / "docs"
SPEC = DOCS / "INGEST_SPEC.md"
VALUES = DOCS / "CONTROLLED_VALUES.md"


@pytest.fixture
def spec() -> str:
    return SPEC.read_text(encoding="utf-8")


@pytest.fixture
def values() -> str:
    return VALUES.read_text(encoding="utf-8")


def header_of(path: Path) -> str:
    return path.read_text(encoding="utf-8").splitlines()[0]


# -- the spec quotes the real headers --------------------------------------


@pytest.mark.parametrize(
    "relative",
    ["lab/sources.csv", "lead/actors.csv", "lead/authorship.csv"],
)
def test_spec_quotes_the_real_header(spec, relative):
    header = header_of(repo_root() / "ksp" / relative)
    assert header in spec, f"{relative} header in the spec does not match the file"


@pytest.mark.parametrize(
    "relative",
    ["lab/sources.csv", "lead/actors.csv", "lead/authorship.csv"],
)
def test_every_column_is_documented(spec, relative):
    for column in header_of(repo_root() / "ksp" / relative).split(","):
        assert f"`{column}`" in spec, f"{relative}: column '{column}' is undocumented"


def test_the_stores_ship_empty(spec):
    """The spec tells an external agent to fill these. They must start empty."""
    for relative in ("lab/sources.csv", "lead/actors.csv", "lead/authorship.csv"):
        lines = (repo_root() / "ksp" / relative).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1, f"{relative} has data in it; the real store ships empty"


# -- the values document matches the vocabularies --------------------------


def test_controlled_values_doc_is_up_to_date():
    """Regenerate with: python3 tools/render_vocab_doc.py"""
    sys.path.insert(0, str(repo_root() / "tools"))
    import render_vocab_doc  # noqa: PLC0415

    assert VALUES.read_text(encoding="utf-8") == render_vocab_doc.render()


@pytest.mark.parametrize(
    "filename",
    ["pillar.csv", "source_type.csv", "record_type.csv", "actor_form.csv",
     "actor_type.csv", "origin.csv"],
)
def test_every_simple_vocabulary_value_appears(values, filename):
    for row in read_csv(repo_root() / "ksp" / "vocab" / filename):
        assert row["value"] in values, f"{filename}: '{row['value']}' is missing"


def test_all_36_focus_areas_appear(values):
    sub = read_csv(repo_root() / "ksp" / "vocab" / "sub_pillar.csv")
    focus = [r["value"] for r in sub if r["level"] == "P-2"]
    assert len(focus) == 36
    for value in focus:
        assert value in values, f"focus area '{value}' is missing"


def test_all_geography_values_appear(values):
    for row in read_csv(repo_root() / "ksp" / "vocab" / "geography.csv"):
        assert row["value"] in values, f"geography '{row['value']}' is missing"


# -- the rules the crawler must not get wrong ------------------------------


def test_spec_forbids_not_found(spec):
    assert "Not Found" in spec
    assert "`Internal`" in spec and "`Unknown`" in spec


def test_spec_states_the_actor_row_creation_rule(spec):
    text = " ".join(spec.split())
    assert "either a `source_files` entry or a `basis`" in text
    assert "only a name looks like knowledge and is not" in text


def test_spec_forbids_a_role_column(spec):
    assert "Do not add a `role` column" in spec
    assert "role" not in header_of(repo_root() / "ksp" / "lead" / "authorship.csv")


def test_spec_warns_that_filenames_are_the_key(spec):
    text = " ".join(spec.split())
    assert "by filename and nothing else" in text
    assert "Nothing may be renamed after filing" in text


def test_spec_states_both_levels_of_each_hierarchy(spec):
    assert "Indonesia;Southeast Asia" in spec
    assert "Pollution;Urban Liveability" in spec


def test_spec_names_the_two_in_scope_themes(spec):
    for row in read_csv(repo_root() / "ksp" / "vocab" / "theme.csv"):
        assert row["theme"] in spec
    # Urban Heat is the sibling that is deliberately out of scope.
    assert "Urban Heat" in spec
