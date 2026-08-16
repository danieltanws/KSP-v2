"""Controlled vocabularies and the row-creation rules."""

from __future__ import annotations

import pytest

from conftest import ACTOR_HEADER, SOURCE_HEADER, write_rows
from kspcore.store import Store
from kspcore.vocab import ERROR, WARNING, validate


def errors(problems):
    return [p for p in problems if p.level == ERROR]


def in_file(problems, filename):
    """Scope problems to one table.

    Replacing sources.csv legitimately orphans the LEAD rows that pointed at
    it, so a test about LAB rules asserts only on LAB problems.
    """
    return [p for p in problems if p.where.startswith(filename)]


def warnings(problems):
    return [p for p in problems if p.level == WARNING]


def messages(problems):
    return " | ".join(p.message for p in problems)


def test_the_built_test_store_is_clean(demo, vocab):
    assert validate(demo, vocab) == []


def test_empty_store_is_clean(empty, vocab):
    assert validate(empty, vocab) == []


# -- the taxonomy ----------------------------------------------------------


def test_all_36_focus_areas_and_12_clusters_are_present(vocab):
    assert len(vocab.pillar) == 4
    assert len(vocab.p1_cluster) == 12
    assert len(vocab.p2_focus_area) == 36
    assert len(vocab.taxonomy) == 52


def test_both_in_scope_themes_sit_under_urban_liveability(vocab):
    for theme in ("Pollution", "Water & Waste"):
        assert vocab.parents_of(theme) == ("PLANET", "Urban Liveability")


def test_theme_resolution(vocab):
    assert vocab.resolve_theme("pollution")["theme"] == "Pollution"
    assert vocab.resolve_theme("air quality in Jakarta")["theme"] == "Pollution"
    assert vocab.resolve_theme("PM2.5")["theme"] == "Pollution"
    assert vocab.resolve_theme("clean water")["theme"] == "Water & Waste"
    assert vocab.resolve_theme("solid waste")["theme"] == "Water & Waste"


def test_out_of_scope_themes_resolve_to_none(vocab):
    for text in ("semiconductor supply chains", "mental health", "carbon markets", ""):
        assert vocab.resolve_theme(text) is None


def test_a_p1_cluster_is_not_a_theme(vocab):
    # Filtering on Urban Liveability would sweep in Urban Heat.
    assert vocab.resolve_theme("Urban Liveability") is None


def test_short_alias_does_not_match_inside_a_longer_word(vocab):
    assert vocab.resolve_theme("Washington monitoring programme") is None


# -- LAB rules -------------------------------------------------------------


def test_publisher_not_found_is_rejected(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [_source_row(publisher="Not Found")],
    )
    problems = validate(Store.load(scratch), vocab)
    assert "Internal" in messages(errors(problems))
    assert "Unknown" in messages(errors(problems))


def test_unknown_vocabulary_value_is_rejected(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [_source_row(geography="ASEAN")],
    )
    assert "'ASEAN' is not in the controlled list" in messages(errors(validate(Store.load(scratch), vocab)))


def test_country_without_its_region_warns_but_does_not_block(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv", SOURCE_HEADER, [_source_row(geography="Indonesia")],
    )
    problems = in_file(validate(Store.load(scratch), vocab), "sources.csv")
    assert errors(problems) == []
    assert "without its region 'Southeast Asia'" in messages(warnings(problems))


def _source_row(**over):
    row = {
        "name": "A doc", "file": "Heat_PM25_Study.pdf", "record_type": "Document",
        "description": "d", "quick_insights": "", "pillar": "PLANET",
        "p1_cluster": "Urban Liveability", "p2_focus_area": "Pollution",
        "geography": "Indonesia;Southeast Asia", "source_type": "Research",
        "publisher": "Someone", "source_url": "", "year_published": "2024",
        "total_author_count": "", "date_added": "2026-08-14",
    }
    row.update(over)
    return [row[k] for k in SOURCE_HEADER]


def test_a_correct_chain_validates(scratch, vocab):
    write_rows(scratch / "lab" / "sources.csv", SOURCE_HEADER, [_source_row()])
    assert errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")) == []


def test_focus_area_under_the_wrong_cluster_is_an_error(scratch, vocab):
    """The chain is checkable, so a wrong one is a mistake, not a style lapse."""
    write_rows(
        scratch / "lab" / "sources.csv", SOURCE_HEADER,
        [_source_row(p1_cluster="Global Health", pillar="PEOPLE")],
    )
    text = messages(errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")))
    assert "belongs to p1_cluster 'Urban Liveability'" in text
    assert "Pollution" in text


def test_focus_area_under_the_wrong_pillar_is_an_error(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv", SOURCE_HEADER, [_source_row(pillar="PEOPLE")],
    )
    text = messages(errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")))
    assert "belongs to pillar 'PLANET'" in text


def test_cluster_under_the_wrong_pillar_is_an_error(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv", SOURCE_HEADER,
        [_source_row(pillar="PEACE", p2_focus_area="")],
    )
    text = messages(errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")))
    assert "p1_cluster 'Urban Liveability' belongs to pillar 'PLANET'" in text


def test_a_level_value_in_the_wrong_column_is_rejected(scratch, vocab):
    """'Urban Liveability' is a cluster; it is not a focus area."""
    write_rows(
        scratch / "lab" / "sources.csv", SOURCE_HEADER,
        [_source_row(p2_focus_area="Urban Liveability")],
    )
    text = messages(errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")))
    assert "p2_focus_area 'Urban Liveability' is not in the controlled list" in text


@pytest.mark.parametrize("url,ok", [
    ("https://example.org/a", True), ("http://example.org/a", True),
    ("example.org/a", False), ("www.example.org", False),
])
def test_source_url_shape(scratch, vocab, url, ok):
    write_rows(scratch / "lab" / "sources.csv", SOURCE_HEADER, [_source_row(source_url=url)])
    text = messages(errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")))
    assert ("must start with http:// or https://" in text) is not ok


def test_folder_row_needs_no_other_fields(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["Some folder", "", "Folder"] + [""] * (len(SOURCE_HEADER) - 3)],
    )
    assert errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")) == []


def test_two_rows_cannot_claim_the_same_file(scratch, vocab):
    row = _source_row()
    write_rows(scratch / "lab" / "sources.csv", SOURCE_HEADER, [row, list(row)])
    assert "already used by" in messages(errors(validate(Store.load(scratch), vocab)))


# -- LEAD rules ------------------------------------------------------------


def test_actor_with_only_a_name_is_rejected(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "Someone", "Person", "", "", "", "", "", "", "", "Manual", "", "2026-08-14"]],
    )
    problems = errors(validate(Store.load(scratch), vocab))
    assert "a name alone is not a record" in messages(problems)


def test_actor_needs_a_valid_form(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "Someone", "Charity", "", "", "", "", "", "", "", "Manual", "basis", "2026-08-14"]],
    )
    assert "is not Person or Organisation" in messages(errors(validate(Store.load(scratch), vocab)))


def test_duplicate_actor_ids_are_rejected(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "", "", "", "", "", "", "Manual", "b", "2026-08-14"],
         ["1", "B", "Person", "", "", "", "", "", "", "", "Manual", "b", "2026-08-14"]],
    )
    assert "used more than once" in messages(errors(validate(Store.load(scratch), vocab)))


def test_affiliation_must_point_at_a_real_actor(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "99", "", "", "", "", "", "Manual", "b", "2026-08-14"]],
    )
    assert "does not match any actor id" in messages(errors(validate(Store.load(scratch), vocab)))


def test_affiliation_is_for_people_only(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "", "", "", "", "", "", "Manual", "b", "2026-08-14"],
         ["2", "Org", "Organisation", "", "1", "", "", "", "", "", "Manual", "b", "2026-08-14"]],
    )
    assert "it is for people only" in messages(errors(validate(Store.load(scratch), vocab)))


def test_authorship_must_reference_real_rows(scratch, vocab):
    write_rows(
        scratch / "lead" / "authorship.csv",
        ["actor_id", "source_file", "position"],
        [["99", "Nope.pdf", "1"]],
    )
    text = messages(errors(validate(Store.load(scratch), vocab)))
    assert "actor_id '99' does not match" in text
    assert "is not a LAB document row" in text


def test_one_authorship_row_per_person_per_document(scratch, vocab):
    write_rows(
        scratch / "lead" / "authorship.csv",
        ["actor_id", "source_file", "position"],
        [["1", "Heat_PM25_Study.pdf", "1"], ["1", "Heat_PM25_Study.pdf", "2"]],
    )
    assert "duplicate" in messages(errors(validate(Store.load(scratch), vocab)))
