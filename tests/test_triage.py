"""Triage suggests; it never decides and never runs anything.

The failure this file exists to catch: a ranked candidate list quietly becoming
a fallback chain, so a blocked analysis gets answered by the next one down.
That is the substitution PRD 6.1 forbids.
"""

from __future__ import annotations

import pytest

from kspcore import triage
from kspcore.registry import Registry


@pytest.fixture
def registry() -> Registry:
    return Registry.load()


def top(registry, question):
    candidates = triage.rank(registry, question)
    assert candidates, f"nothing matched: {question}"
    return candidates[0].skill.number


# -- ranking ---------------------------------------------------------------


@pytest.mark.parametrize(
    "question,expected",
    [
        ("what do we hold on water in Indonesia?", 1),
        ("which water solutions work but haven't spread?", 6),
        ("could the Vietnam kiosk model work in Indonesia?", 9),
        ("is the funding response the right size for clean cooking?", 5),
        ("who should I talk to about air quality in Jakarta?", 2),
        ("where's the gap in air pollution in Vietnam?", 12),
        ("has anyone tried this before and failed?", 15),
        ("is this field already crowded?", 16),
    ],
)
def test_questions_reach_the_right_analysis(registry, question, expected):
    assert top(registry, question) == expected


def test_ranking_is_stable(registry):
    question = "which water solutions work but haven't spread?"
    first = [c.skill.number for c in triage.rank(registry, question)]
    assert first == [c.skill.number for c in triage.rank(registry, question)]


def test_every_candidate_shows_why_it_matched(registry):
    for candidate in triage.rank(registry, "what do we hold on water?"):
        assert candidate.hits, "a candidate with no matched cue is unexplainable"


def test_cues_match_on_word_boundaries(registry):
    # 'gap' must not fire on 'Singapore'.
    assert not any(c.skill.number == 12 for c in triage.rank(registry, "Singapore water"))


# -- the no-fallback rule --------------------------------------------------


def test_blocked_top_match_is_named_with_its_blocker(registry):
    text = triage.run(registry, "is the funding response the right size for clean cooking?")
    assert "#5 Scale mismatch, and it is blocked" in text
    assert "Stated quantity field on LAB" in text


def test_blocked_top_match_offers_no_substitute_command(registry):
    text = triage.run(registry, "is the funding response the right size for clean cooking?")
    assert "To run it:" not in text, "a blocked analysis must not hand over a command"
    assert "substitution, not an answer" in text or "none should be inferred" in text


def test_blocked_top_match_says_the_others_answer_different_questions(registry):
    # Craft a question that hits a blocked skill first and a ready one below it.
    question = "is the funding response the right size, and where is the gap?"
    candidates = triage.rank(registry, question)
    assert not candidates[0].skill.available
    assert any(c.skill.available for c in candidates[1:])

    text = triage.render(registry, question, candidates)
    assert "answer different questions" in text
    assert "substitution, not an answer" in text


def test_triage_never_claims_to_have_run_anything(registry):
    for question in (
        "what do we hold on water?",
        "is the funding response the right size?",
        "tell me about semiconductors",
    ):
        assert "Nothing has been run" in triage.run(registry, question)


def test_no_match_asks_rather_than_defaulting(registry):
    raw = triage.run(registry, "tell me about semiconductor supply chains")
    text = " ".join(raw.split())  # the body is hard-wrapped
    assert "No analysis matched" in text
    assert "Nothing has been run" in text
    assert "defaulting to whichever skill happens to be available" in text


# -- POC presentation ------------------------------------------------------


@pytest.mark.parametrize("question,number", [
    ("which water solutions work but haven't spread?", 6),
    ("could this transfer to Indonesia?", 9),
])
def test_poc_candidates_are_marked_as_poc(registry, question, number):
    text = triage.run(registry, question)
    assert "READY (POC)" in text
    assert f"#{number} is a POC skill" in text
    assert registry.get(number).missing_field in text


def test_poc_candidate_offers_the_brief_command(registry):
    text = triage.run(registry, "which water solutions work but haven't spread?")
    assert "ksp.py brief --skill 6" in text


def test_implemented_candidate_offers_its_own_command(registry):
    assert "ksp.py coverage" in triage.run(registry, "what do we hold on water?")
