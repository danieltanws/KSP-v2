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


def test_demo_store_is_clean(demo, vocab):
    assert validate(demo, vocab) == []


def test_empty_store_is_clean(empty, vocab):
    assert validate(empty, vocab) == []


# -- the taxonomy ----------------------------------------------------------


def test_all_36_focus_areas_and_12_clusters_are_present(vocab):
    p1 = [v for v, r in vocab.sub_pillar.items() if r["level"] == "P-1"]
    p2 = [v for v, r in vocab.sub_pillar.items() if r["level"] == "P-2"]
    assert len(p1) == 12
    assert len(p2) == 36
    assert len(vocab.pillar) == 4


def test_both_in_scope_themes_sit_under_urban_liveability(vocab):
    for theme in ("Pollution", "Water & Waste"):
        row = vocab.sub_pillar[theme]
        assert row["level"] == "P-2"
        assert row["parent_p1"] == "Urban Liveability"
        assert row["pillar"] == "PLANET"


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
        [["A doc", "Heat_PM25_Study.pdf", "Document", "d", "", "PLANET",
          "Pollution;Urban Liveability", "Indonesia;Southeast Asia", "Research",
          "Not Found", "2024", "", "2026-08-14"]],
    )
    problems = validate(Store.load(scratch), vocab)
    assert "Internal" in messages(errors(problems))
    assert "Unknown" in messages(errors(problems))


def test_unknown_vocabulary_value_is_rejected(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["A doc", "Heat_PM25_Study.pdf", "Document", "d", "", "PLANET",
          "Pollution;Urban Liveability", "ASEAN", "Research", "Someone",
          "2024", "", "2026-08-14"]],
    )
    assert "'ASEAN' is not in the controlled list" in messages(errors(validate(Store.load(scratch), vocab)))


def test_country_without_its_region_warns_but_does_not_block(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["A doc", "Heat_PM25_Study.pdf", "Document", "d", "", "PLANET",
          "Pollution;Urban Liveability", "Indonesia", "Research", "Someone",
          "2024", "", "2026-08-14"]],
    )
    problems = in_file(validate(Store.load(scratch), vocab), "sources.csv")
    assert errors(problems) == []
    assert "without its region 'Southeast Asia'" in messages(warnings(problems))


def test_focus_area_without_its_cluster_warns(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["A doc", "Heat_PM25_Study.pdf", "Document", "d", "", "PLANET",
          "Pollution", "Indonesia;Southeast Asia", "Research", "Someone",
          "2024", "", "2026-08-14"]],
    )
    problems = in_file(validate(Store.load(scratch), vocab), "sources.csv")
    assert errors(problems) == []
    assert "without its P-1 cluster 'Urban Liveability'" in messages(warnings(problems))


def test_folder_row_needs_no_other_fields(scratch, vocab):
    write_rows(
        scratch / "lab" / "sources.csv",
        SOURCE_HEADER,
        [["Some folder", "", "Folder", "", "", "", "", "", "", "", "", "", ""]],
    )
    assert errors(in_file(validate(Store.load(scratch), vocab), "sources.csv")) == []


def test_two_rows_cannot_claim_the_same_file(scratch, vocab):
    row = ["A doc", "Heat_PM25_Study.pdf", "Document", "d", "", "PLANET",
           "Pollution;Urban Liveability", "Indonesia;Southeast Asia", "Research",
           "Someone", "2024", "", "2026-08-14"]
    write_rows(scratch / "lab" / "sources.csv", SOURCE_HEADER, [row, [*row[:1], *row[1:]]])
    assert "already used by" in messages(errors(validate(Store.load(scratch), vocab)))


# -- LEAD rules ------------------------------------------------------------


def test_actor_with_only_a_name_is_rejected(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "Someone", "Person", "", "", "", "", "Manual", "", "2026-08-14"]],
    )
    problems = errors(validate(Store.load(scratch), vocab))
    assert "a name alone is not a record" in messages(problems)


def test_actor_needs_a_valid_form(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "Someone", "Charity", "", "", "", "", "Manual", "basis", "2026-08-14"]],
    )
    assert "is not Person or Organisation" in messages(errors(validate(Store.load(scratch), vocab)))


def test_duplicate_actor_ids_are_rejected(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "", "", "", "Manual", "b", "2026-08-14"],
         ["1", "B", "Person", "", "", "", "", "Manual", "b", "2026-08-14"]],
    )
    assert "used more than once" in messages(errors(validate(Store.load(scratch), vocab)))


def test_affiliation_must_point_at_a_real_actor(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "99", "", "", "Manual", "b", "2026-08-14"]],
    )
    assert "does not match any actor id" in messages(errors(validate(Store.load(scratch), vocab)))


def test_affiliation_is_for_people_only(scratch, vocab):
    write_rows(
        scratch / "lead" / "actors.csv",
        ACTOR_HEADER,
        [["1", "A", "Person", "", "", "", "", "Manual", "b", "2026-08-14"],
         ["2", "Org", "Organisation", "", "1", "", "", "Manual", "b", "2026-08-14"]],
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
