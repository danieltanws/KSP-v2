"""The generic gatherer behind POC skills.

A POC answer wears the same RESULT label as a computed one, by decision. The
evidence base is therefore the only place the difference stays visible, which
makes the disclosure line load-bearing rather than decorative.
"""

from __future__ import annotations

import pytest

from kspcore import brief
from kspcore.registry import NO_DATA, RESULT, Registry


@pytest.fixture
def registry() -> Registry:
    return Registry.load()


@pytest.fixture
def water(vocab):
    return vocab.theme["Water & Waste"]


POC_SKILLS = [6, 9]


@pytest.mark.parametrize("number", POC_SKILLS)
def test_brief_leads_with_the_result_label_and_the_skill(demo, vocab, registry, water, number):
    text = brief.run(demo, vocab, registry, number, water)
    assert text.startswith(f"{RESULT} — {registry.get(number).name} (#{number})")


@pytest.mark.parametrize("number", POC_SKILLS)
def test_evidence_base_comes_first(demo, vocab, registry, water, number):
    text = brief.run(demo, vocab, registry, number, water)
    assert text.index("EVIDENCE BASE") < text.index("── LAB DOCUMENTS")


@pytest.mark.parametrize("number", POC_SKILLS)
def test_evidence_base_names_the_field_that_is_not_stored(demo, vocab, registry, water, number):
    """The only signal separating an improvised answer from a computed one."""
    text = brief.run(demo, vocab, registry, number, water)
    assert "Not stored" in text
    assert registry.get(number).missing_field in text
    assert "Improvised, not computed" in text


def test_a_computed_skill_gets_no_not_stored_line(demo, vocab, registry, water):
    """#12 reads real fields, so it must not claim otherwise. Guards against
    the disclosure becoming boilerplate that appears everywhere and means
    nothing."""
    from kspcore import evidence

    assert "Improvised, not computed" not in evidence.run(demo, vocab, water, "Indonesia")


@pytest.mark.parametrize("number", POC_SKILLS)
def test_brief_hands_over_the_documents_to_reason_over(demo, vocab, registry, water, number):
    text = brief.run(demo, vocab, registry, number, water)
    assert "Community water kiosk programme" in text
    assert "Vietnam_Water_Kiosk.pdf" in text
    # Quick insights carry the substance the agent has to work from.
    assert "78% still financially self-sustaining" in text


@pytest.mark.parametrize("number", POC_SKILLS)
def test_brief_points_at_the_prompt_file(demo, vocab, registry, water, number):
    text = brief.run(demo, vocab, registry, number, water)
    assert registry.get(number).prompt_filename in text


@pytest.mark.parametrize("number", POC_SKILLS)
def test_brief_restates_the_binding_rules(demo, vocab, registry, water, number):
    """The method is free; the rules are not."""
    text = " ".join(brief.run(demo, vocab, registry, number, water).split())
    assert "Every claim names its document or actor" in text
    assert "Label LAB and LEAD claims separately" in text
    assert "Absence in the store is never absence in the world" in text
    assert "do not recommend" in text


@pytest.mark.parametrize("number", POC_SKILLS)
def test_brief_labels_the_stores_apart(demo, vocab, registry, water, number):
    text = brief.run(demo, vocab, registry, number, water)
    assert "── LAB DOCUMENTS ──" in text
    assert "── LEAD ACTORS ──" in text


@pytest.mark.parametrize("number", POC_SKILLS)
def test_empty_store_returns_no_data_not_a_guess(empty, vocab, registry, water, number):
    text = brief.run(empty, vocab, registry, number, water)
    assert text.startswith(NO_DATA)
    assert "describes the store, not the world" in text


def test_folder_rows_never_appear(demo, vocab, registry, water):
    assert "(folder)" not in brief.run(demo, vocab, registry, 9, water)


def test_prompt_filename_follows_the_convention(registry):
    """Adding a POC skill is dropping in a file of this name - so the name has
    to be derivable, not configured."""
    assert registry.get(6).prompt_filename == "06-proven-but-unscaled.md"
    assert registry.get(9).prompt_filename == "09-transferability.md"


def test_an_implementer_reaches_the_response_side(demo, vocab, registry, water):
    text = brief.run(demo, vocab, registry, 9, water)
    assert "A Cooperative Union" in text
    assert "Implementer" in text
