"""Hard rules that apply to every rendered output (PRD 6.5).

These are checked mechanically because they are easy to violate by accident
and expensive to violate in front of a stakeholder.
"""

from __future__ import annotations

import pytest

from kspcore import coverage, evidence, integrity
from kspcore.registry import Registry, render_out_of_scope


@pytest.fixture
def rendered(demo, empty, vocab) -> list[tuple[str, str]]:
    """Every string this system can print, labelled by where it came from."""
    registry = Registry.load()
    pollution = vocab.theme["Pollution"]
    water = vocab.theme["Water & Waste"]

    outputs = [
        ("integrity/demo", integrity.check(demo).render()),
        ("integrity/empty", integrity.check(empty).render()),
        ("registry", registry.render_list()),
        ("out-of-scope", render_out_of_scope("semiconductors", ["Pollution", "Water & Waste"])),
        ("coverage/demo", coverage.run(demo, vocab, pollution, "Indonesia")),
        ("coverage/all", coverage.run(demo, vocab, pollution)),
        ("coverage/water", coverage.run(demo, vocab, water, "Vietnam")),
        ("coverage/empty", coverage.run(empty, vocab, pollution, "Indonesia")),
        ("evidence/demo", evidence.run(demo, vocab, pollution, "Indonesia")),
        ("evidence/water", evidence.run(demo, vocab, water, "Indonesia")),
        ("evidence/empty", evidence.run(empty, vocab, pollution, "Indonesia")),
    ]
    outputs += [
        (f"refusal/{s.number}", registry.render_refusal(s.number))
        for s in registry.skills
        if not s.implemented
    ]
    return outputs


def test_the_word_opportunity_never_appears(rendered):
    """PRD 6.5 rule 5. In a deck it reads as a fundable thing, and the meeting
    goes on that instead of the work. Use gap or candidate."""
    for where, text in rendered:
        assert "opportunit" not in text.lower(), f"{where} used a banned word"


def test_nothing_recommends_a_course_of_action(rendered):
    """PRD 6.5 rule 4. Output states a mismatch; it does not say what to do."""
    banned = ("we recommend", "you should fund", "the trust should", "worth funding")
    for where, text in rendered:
        lowered = text.lower()
        for phrase in banned:
            assert phrase not in lowered, f"{where} recommended: {phrase}"


def test_no_output_is_ever_empty(rendered):
    """PRD 6.5 rule 8. Silence is the specific thing this system must not produce."""
    for where, text in rendered:
        assert text.strip(), f"{where} produced silence"


def test_every_outcome_is_labelled(rendered):
    """A reader must be able to tell a refusal from a finding at a glance."""
    labelled = ("RESULT", "NO DATA", "NOT IMPLEMENTED", "OUT OF SCOPE",
                "INTEGRITY CHECK", "SKILL REGISTRY", "EVIDENCE BRIEF")
    for where, text in rendered:
        assert text.split("\n", 1)[0].startswith(labelled), f"{where} has no outcome label"


def test_absence_is_never_stated_as_fact_about_the_world(rendered):
    """PRD 6.5 rule 3. 'Nothing in the store' and 'nothing in the world' are
    different claims."""
    banned = ("nobody is working on", "no one is working on", "there are no actors working")
    for where, text in rendered:
        lowered = text.lower()
        for phrase in banned:
            assert phrase not in lowered, f"{where} asserted absence in the world: {phrase}"


def test_thin_evidence_is_disclosed_rather_than_withheld(demo, vocab):
    """PRD 6.5 rule 6. No coverage threshold - produce the result and disclose."""
    text = coverage.run(demo, vocab, vocab.theme["Water & Waste"], "Vietnam")
    assert "NO DATA" not in text, "one document is thin, but it is not no data"
    assert "LAB documents          1" in text
