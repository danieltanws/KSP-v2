"""The registry, and the refusals that are the point of it.

PRD 0: all sixteen analyses are declared, two are implemented, fourteen must
fail loudly. An unimplemented skill that quietly answers with a different
analysis is the failure mode the whole system is designed against.
"""

from __future__ import annotations

import pytest

from kspcore.registry import (
    IMPLEMENTED,
    NO_DATA,
    NOT_IMPLEMENTED,
    OUT_OF_SCOPE,
    RESULT,
    Registry,
    render_out_of_scope,
)

CATALOGUE_NAMES = {
    1: "Coverage check", 2: "Adjacent actors", 3: "Network position",
    4: "Policy-implementation gap", 5: "Scale mismatch", 6: "Proven but unscaled",
    7: "Actor mix", 8: "Venue shift", 9: "Transferability",
    10: "Sub-pillar co-occurrence", 11: "Problem rising, response static",
    12: "Gap analysis", 13: "Well resourced, not working", 14: "Fund flows",
    15: "Failure mapping", 16: "Crowded field",
}

# PRD 6.2 - the field each refusal must name.
MISSING_FIELDS = {
    3: "Code execution + author-count weighting",
    4: "Commitment identification on LAB",
    5: "Stated quantity field on LAB",
    6: "Solution maturity field on LAB",
    7: "Actor type populated in LEAD",
    8: "Source type field plus 12+ months of collection",
    9: "Enabling conditions list per case study",
    11: "12+ months of continuous collection",
    13: "Outcome data (does not exist anywhere)",
    14: "Transaction records + historical time series",
    15: "Failure capture against LEAD actors",
    16: "Actor type populated in LEAD",
}

DEFERRED = {2, 10}


@pytest.fixture
def registry() -> Registry:
    return Registry.load()


def test_sixteen_skills_declared(registry):
    assert [s.number for s in registry.skills] == list(range(1, 17))


def test_numbering_and_names_match_the_catalogue(registry):
    assert {s.number: s.name for s in registry.skills} == CATALOGUE_NAMES


def test_exactly_two_are_implemented(registry):
    assert [s.number for s in registry.implemented()] == [1, 12]


def test_every_other_skill_is_declared_not_implemented(registry):
    for skill in registry.skills:
        if skill.number not in (1, 12):
            assert skill.status == "NOT IMPLEMENTED", f"#{skill.number}"


@pytest.mark.parametrize("number", sorted(MISSING_FIELDS))
def test_blocked_skills_refuse_and_name_their_field(registry, number):
    text = registry.render_refusal(number)
    assert text.startswith(f"{NOT_IMPLEMENTED} — ")
    assert f"(#{number})" in text
    assert MISSING_FIELDS[number] in text, f"#{number} must name its blocker"


@pytest.mark.parametrize("number", sorted(DEFERRED))
def test_deferred_skills_say_buildable_and_name_no_field(registry, number):
    text = registry.render_refusal(number)
    assert text.startswith(NOT_IMPLEMENTED)
    assert "buildable, not blocked" in text
    assert "It needs:" not in text, "#%d is not blocked by a field" % number


@pytest.mark.parametrize("number", [1, 12])
def test_implemented_skills_cannot_be_refused(registry, number):
    with pytest.raises(ValueError, match="is implemented"):
        registry.render_refusal(number)


def test_every_refusal_points_at_the_implemented_alternatives(registry):
    for skill in registry.skills:
        if skill.implemented:
            continue
        text = registry.render_refusal(skill.number)
        assert "Implemented skills that may be relevant:" in text
        for number in skill.relevant_implemented:
            assert registry.get(number).implemented, "only implemented skills may be offered"


def test_no_refusal_ever_offers_an_unimplemented_skill(registry):
    for skill in registry.skills:
        assert set(skill.relevant_implemented) <= {1, 12}


def test_the_four_outcomes_are_distinct(registry):
    labels = {RESULT, NO_DATA, NOT_IMPLEMENTED, OUT_OF_SCOPE}
    assert len(labels) == 4
    # None may be a prefix of another, or a reader skimming could conflate them.
    for a in labels:
        for b in labels - {a}:
            assert not a.startswith(b)


def test_out_of_scope_is_not_dressed_up_as_a_missing_field():
    text = render_out_of_scope("semiconductor supply chains", ["Pollution", "Water & Waste"])
    assert text.startswith(OUT_OF_SCOPE)
    assert NOT_IMPLEMENTED not in text
    assert "no analysis would unlock it" in text
    assert "Pollution" in text and "Water & Waste" in text


def test_registry_listing_shows_all_sixteen(registry):
    text = registry.render_list()
    for number in range(1, 17):
        assert f"\n{number:>3}  " in text
    assert text.count(IMPLEMENTED) == 16  # 2 bare + 14 inside "NOT IMPLEMENTED"


def test_reference_doc_matches_the_registry(registry):
    """references/registry.md is generated. If skills.csv changed, regenerate:
    python3 tools/render_registry_doc.py"""
    from pathlib import Path

    target = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "ksp" / "references" / "registry.md"
    assert target.read_text(encoding="utf-8") == registry.render_markdown()
