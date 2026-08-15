"""Skill #1 (coverage) and skill #12 (gap analysis inputs)."""

from __future__ import annotations

import pytest

from kspcore import coverage, evidence
from kspcore.query import filter_actors, filter_sources, year_range
from kspcore.registry import NO_DATA, RESULT
from kspcore.store import role_for


@pytest.fixture
def pollution(vocab):
    return vocab.theme["Pollution"]


@pytest.fixture
def water(vocab):
    return vocab.theme["Water & Waste"]


# -- filtering -------------------------------------------------------------


def test_folder_rows_never_reach_a_query(demo):
    assert len(demo.sources) == 7
    assert len(demo.documents()) == 6
    assert all(row["record_type"] == "Document" for row in demo.documents())


def test_theme_filters_on_the_focus_area(demo, pollution, water):
    assert len(filter_sources(demo, pollution).documents) == 4
    assert len(filter_sources(demo, water).documents) == 2


def test_sibling_focus_areas_do_not_bleed_together(demo, pollution, water):
    pollution_files = {r["file"] for r in filter_sources(demo, pollution).documents}
    water_files = {r["file"] for r in filter_sources(demo, water).documents}
    assert pollution_files & water_files == set()


def test_geography_narrows_and_global_is_kept_apart(demo, pollution):
    match = filter_sources(demo, pollution, "Indonesia")
    assert {r["file"] for r in match.documents} == {
        "Heat_PM25_Study.pdf", "Jakarta_Air_Quality_Review.pdf",
    }
    assert [r["file"] for r in match.global_documents] == ["Clean_Cooking_Outcome_Bond.pdf"]


def test_region_matches_documents_tagged_with_that_region(demo, pollution):
    match = filter_sources(demo, pollution, "Southeast Asia")
    assert len(match.documents) == 3


def test_year_range_counts_undated_rows(demo, pollution):
    earliest, latest, undated = year_range(filter_sources(demo, pollution).documents)
    assert (earliest, latest, undated) == (2023, 2025, 0)


# -- actors ----------------------------------------------------------------


def test_actors_are_tied_to_a_theme_through_named_documents(demo, pollution):
    match = filter_actors(demo, pollution, "Indonesia")
    names = {actor["name"] for actor, _ in match.by_document}
    assert names == {"Jane Smith", "Wei Chen", "Institute of Environmental Health"}
    for _, via in match.by_document:
        assert via, "every actor match must cite the document behind it"


def test_actor_reached_only_through_a_global_document_is_kept_apart(demo, pollution):
    match = filter_actors(demo, pollution, "Indonesia")
    assert [a["name"] for a, _ in match.via_global_only] == ["World Bank"]
    assert "World Bank" not in {a["name"] for a, _ in match.by_document}


def test_manual_actor_without_a_document_is_not_counted_as_theme_evidence(demo, pollution):
    match = filter_actors(demo, pollution, "Southeast Asia")
    assert "Clean Air Fund" in {a["name"] for a in match.geography_only}
    assert "Clean Air Fund" not in {a["name"] for a, _ in match.by_document}


def test_authorship_role_is_derived_from_position(demo):
    authors = demo.authors_of("Heat_PM25_Study.pdf")
    assert [(a["actor_name"], a["role"]) for a in authors] == [
        ("Jane Smith", "Primary"), ("Wei Chen", "Co"),
    ]


def test_role_is_never_stored_on_disk(demo):
    assert "role" not in demo.authorship[0], "position is stored, role is derived"


@pytest.mark.parametrize("position,expected", [("1", "Primary"), ("2", "Co"), ("7", "Co"), ("", "Co")])
def test_role_rule(position, expected):
    assert role_for(position) == expected


# -- skill #1 --------------------------------------------------------------


def test_coverage_reports_a_result_with_counts(demo, vocab, pollution):
    text = coverage.run(demo, vocab, pollution, "Indonesia")
    assert text.startswith(RESULT)
    assert "LAB documents          2" in text
    assert "BY SOURCE TYPE" in text
    assert "BY SUB-PILLAR" in text


def test_coverage_states_what_it_describes(demo, vocab, pollution):
    # Collapsed because the caveat is hard-wrapped across lines.
    text = " ".join(coverage.run(demo, vocab, pollution, "Indonesia").split())
    assert "A well-covered cell means we have read a lot, not that a field is crowded" in text
    assert "A thin cell means we have read little, not that the subject is neglected" in text


def test_coverage_on_an_empty_store_says_no_data_not_nothing(empty, vocab, pollution):
    text = coverage.run(empty, vocab, pollution, "Indonesia")
    assert text.startswith(NO_DATA)
    assert "describes the store, not the world" in text
    assert text.strip(), "silence is never an acceptable answer"


def test_coverage_on_a_theme_with_no_documents(demo, vocab, water):
    text = coverage.run(demo, vocab, water, "Kenya")
    assert text.startswith(NO_DATA)


def test_coverage_runs_without_a_geography(demo, vocab, pollution):
    text = coverage.run(demo, vocab, pollution)
    assert text.startswith(RESULT)
    assert "all geographies" in text


# -- skill #12 -------------------------------------------------------------


def test_evidence_brief_carries_every_section_the_output_needs(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    for heading in (
        "SECTION 1 MATERIAL", "LAB DOCUMENTS", "LEAD ACTORS",
        "SECTION 5 MATERIAL", "MANDATORY DISCLOSURES",
    ):
        assert heading in text


def test_evidence_brief_labels_the_two_stores_separately(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    assert "── LAB DOCUMENTS" in text
    assert "── LEAD ACTORS" in text


def test_evidence_brief_discloses_unstable_classification(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    assert "not stable" in text or "may differ" in text
    assert "lowest-trust" in text


def test_evidence_brief_names_absent_source_types(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    assert "No Policy documents for Indonesia" in text
    assert "No Media documents for Indonesia" in text


def test_absent_type_held_only_globally_is_described_accurately(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    # An Industry document exists but is tagged Global - saying it is simply
    # absent would contradict the document list printed above it.
    assert "No Industry documents for Indonesia — the only one held is tagged Global" in text


def test_evidence_on_empty_store_refuses_to_produce_a_gap(empty, vocab, pollution):
    text = evidence.run(empty, vocab, pollution, "Vietnam")
    assert text.startswith(NO_DATA)
    assert "would be fabrication" in text


def test_evidence_brief_is_not_the_answer(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    assert "raw material, not an answer" in text
    assert "Do not paste this brief" in text


# -- global-only evidence --------------------------------------------------


def test_global_only_match_is_flagged_unmissably(demo, vocab, pollution):
    """Rule 6 forbids withholding thin results, so the disclosure has to be
    impossible to skim past: zero Vietnam documents, one Global one."""
    text = evidence.run(demo, vocab, pollution, "Vietnam")
    assert "⚠ NOTHING SPECIFIC TO VIETNAM" in text
    assert "not the absence of activity in it" in text
    assert not text.startswith(NO_DATA), "a Global document is not nothing"


def test_coverage_flags_a_global_only_match_too(demo, vocab, pollution):
    text = coverage.run(demo, vocab, pollution, "Vietnam")
    assert "⚠ NOTHING SPECIFIC TO VIETNAM" in text


def test_no_warning_when_geography_specific_documents_exist(demo, vocab, pollution):
    text = evidence.run(demo, vocab, pollution, "Indonesia")
    assert "NOTHING SPECIFIC" not in text


def test_no_geography_means_no_such_warning(demo, vocab, pollution):
    assert "NOTHING SPECIFIC" not in evidence.run(demo, vocab, pollution)
