"""The registry, and the refusals that are the point of it.

All sixteen analyses are declared. Two are implemented, two are POC
placeholders, twelve must fail loudly. An unimplemented skill that quietly
answers with a different analysis is the failure mode the whole system is
designed against (PRD 0).
"""

from __future__ import annotations

import pytest

from kspcore.registry import (
    IMPLEMENTED,
    POC,
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
    7: "Actor type populated in LEAD",
    8: "Source type field plus 12+ months of collection",
    11: "12+ months of continuous collection",
    13: "Outcome data (does not exist anywhere)",
    14: "Transaction records + historical time series",
    15: "Failure capture against LEAD actors",
    16: "Actor type populated in LEAD",
}

DEFERRED = {2, 10}
POC_SKILLS = {6, 9}
IMPLEMENTED_SKILLS = {1, 12}
AVAILABLE = POC_SKILLS | IMPLEMENTED_SKILLS


@pytest.fixture
def registry() -> Registry:
    return Registry.load()


def test_sixteen_skills_declared(registry):
    assert [s.number for s in registry.skills] == list(range(1, 17))


def test_numbering_and_names_match_the_catalogue(registry):
    assert {s.number: s.name for s in registry.skills} == CATALOGUE_NAMES


def test_exactly_two_are_implemented(registry):
    assert [s.number for s in registry.implemented()] == sorted(IMPLEMENTED_SKILLS)


def test_exactly_two_are_poc(registry):
    assert {s.number for s in registry.skills if s.is_poc} == POC_SKILLS


def test_poc_is_not_counted_as_implemented(registry):
    """A POC skill is runnable but improvised. Conflating the two would erase
    the distinction between a computed answer and a guessed one."""
    for number in POC_SKILLS:
        skill = registry.get(number)
        assert skill.available
        assert not skill.implemented


def test_every_other_skill_is_declared_not_implemented(registry):
    for skill in registry.skills:
        if skill.number not in AVAILABLE:
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


@pytest.mark.parametrize("number", sorted(IMPLEMENTED_SKILLS))
def test_implemented_skills_cannot_be_refused(registry, number):
    with pytest.raises(ValueError, match="is implemented"):
        registry.render_refusal(number)


@pytest.mark.parametrize("number", sorted(POC_SKILLS))
def test_poc_skills_cannot_be_refused(registry, number):
    with pytest.raises(ValueError, match="POC"):
        registry.render_refusal(number)


@pytest.mark.parametrize("number", sorted(POC_SKILLS))
def test_poc_skills_have_their_prompt_file(registry, number):
    """A POC skill is its prompt file. Without it there is nothing to run."""
    from pathlib import Path

    skill = registry.get(number)
    target = (
        Path(__file__).resolve().parents[1]
        / ".claude" / "skills" / "ksp" / "analyses" / skill.prompt_filename
    )
    assert target.is_file(), f"#{number} is POC but {skill.prompt_filename} is missing"


@pytest.mark.parametrize("number", sorted(POC_SKILLS))
def test_poc_skills_still_name_the_field_they_lack(registry, number):
    """It is what the evidence base discloses, so it must survive the flip."""
    assert registry.get(number).missing_field


def test_every_refusal_points_at_the_implemented_alternatives(registry):
    for skill in registry.skills:
        if skill.available:
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
    assert text.count(IMPLEMENTED) == 14  # 2 bare + 12 inside "NOT IMPLEMENTED"
    assert text.count(f"\n{POC:<16}".strip()) >= 2


def test_reference_doc_matches_the_registry(registry):
    """references/registry.md is generated. If skills.csv changed, regenerate:
    python3 tools/render_registry_doc.py"""
    from pathlib import Path

    target = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "ksp" / "references" / "registry.md"
    assert target.read_text(encoding="utf-8") == registry.render_markdown()
