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

OUTPUTS = repo_root() / "outputs"
SPEC = OUTPUTS / "INGEST_SPEC.md"
VALUES = OUTPUTS / "CONTROLLED_VALUES.md"


@pytest.fixture
def spec() -> str:
    return SPEC.read_text(encoding="utf-8")


@pytest.fixture
def values() -> str:
    return VALUES.read_text(encoding="utf-8")


def header_of(path: Path) -> str:
    return path.read_text(encoding="utf-8").splitlines()[0]


# -- where these documents live --------------------------------------------


def test_handoff_documents_live_in_outputs():
    """`docs/` is documentation about this system; these two are a work package
    handed outward. Anything this agent produces goes to `outputs/`."""
    assert SPEC.is_file(), "INGEST_SPEC.md is not in outputs/"
    assert VALUES.is_file(), "CONTROLLED_VALUES.md is not in outputs/"


def test_they_are_not_left_behind_in_docs():
    for stale in ("INGEST_SPEC.md", "CONTROLLED_VALUES.md"):
        path = repo_root() / "docs" / stale
        assert not path.exists(), f"docs/{stale} is back - two copies will drift"


def test_the_generator_writes_to_outputs():
    """If TARGET still pointed at docs/, running the generator would recreate a
    second copy there and the two would diverge silently."""
    sys.path.insert(0, str(repo_root() / "tools"))
    import render_vocab_doc  # noqa: PLC0415

    assert render_vocab_doc.TARGET == VALUES


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


def test_every_store_file_exists_with_its_header(spec):
    """The spec tells an external agent to fill these, so they must exist and
    carry the header it documents - whether or not they hold rows yet."""
    for relative in ("lab/sources.csv", "lead/actors.csv", "lead/authorship.csv"):
        path = repo_root() / "ksp" / relative
        assert path.is_file(), f"{relative} is missing"
        assert path.read_text(encoding="utf-8").splitlines()[0].count(",") > 1


# -- the values document matches the vocabularies --------------------------


def test_controlled_values_doc_is_up_to_date():
    """Regenerate with: python3 tools/render_vocab_doc.py"""
    sys.path.insert(0, str(repo_root() / "tools"))
    import render_vocab_doc  # noqa: PLC0415

    assert VALUES.read_text(encoding="utf-8") == render_vocab_doc.render()


@pytest.mark.parametrize(
    "filename",
    ["source_type.csv", "record_type.csv", "actor_form.csv",
     "actor_type.csv", "origin.csv"],
)
def test_every_simple_vocabulary_value_appears(values, filename):
    for row in read_csv(repo_root() / "ksp" / "vocab" / filename):
        assert row["value"] in values, f"{filename}: '{row['value']}' is missing"


def test_the_whole_taxonomy_appears(values):
    tree = read_csv(repo_root() / "ksp" / "vocab" / "taxonomy.csv")
    by_level = {}
    for row in tree:
        by_level.setdefault(row["level"], []).append(row["value"])
    assert (len(by_level["P"]), len(by_level["P-1"]), len(by_level["P-2"])) == (4, 12, 36)
    for row in tree:
        assert row["value"] in values, f"{row['level']} '{row['value']}' is missing"


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


def test_spec_states_the_three_taxonomy_columns(spec):
    for column in ("`pillar`", "`p1_cluster`", "`p2_focus_area`"):
        assert column in spec
    # The chain rule is the thing a crawler will otherwise get wrong.
    assert "chain must be consistent" in " ".join(spec.split())


def test_spec_states_geography_carries_both_levels(spec):
    assert "Indonesia;Southeast Asia" in spec


def test_spec_requires_the_file_as_well_as_the_url(spec):
    """A URL alone leaves a claim uncheckable once the link rots."""
    text = " ".join(spec.split())
    assert "record it *as well as* the file, never instead" in text
    assert "A URL alone is not enough" in text


def test_spec_names_the_two_in_scope_themes(spec):
    for row in read_csv(repo_root() / "ksp" / "vocab" / "theme.csv"):
        assert row["theme"] in spec
    # Urban Heat is the sibling that is deliberately out of scope.
    assert "Urban Heat" in spec
