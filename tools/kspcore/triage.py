"""Triage: which analyses would answer this question, and is each one ready?

Suggests. Does not decide, and does not run anything.

The shortlist is deterministic so it is reproducible and inspectable; the
choice stays with the agent, which is where PRD 6.1 puts routing.

**The one thing this must never become is a fallback chain.** A ranked list is
one small step from "the analysis you wanted is blocked, so here is the next
one down" - which is the substitution the whole system is built to prevent. So
whenever the closest match is blocked, the output says in as many words that
the ready analyses answer *different questions*, and no command to run them is
offered.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .registry import Registry, Skill

READY = "READY"
BLOCKED = "BLOCKED"


@dataclass
class Candidate:
    skill: Skill
    hits: list[str]

    @property
    def state(self) -> str:
        return READY if self.skill.available else BLOCKED

    @property
    def score(self) -> int:
        return len(self.hits)


def rank(registry: Registry, question: str, limit: int = 4) -> list[Candidate]:
    """Candidates ordered by how many cues the question matched.

    Ties break by skill number, so the same question always ranks the same way.
    """
    needle = (question or "").lower()
    scored = []
    for skill in registry.skills:
        hits = [
            cue
            for cue in skill.question_cues
            if re.search(rf"\b{re.escape(cue.lower())}\b", needle)
        ]
        if hits:
            scored.append(Candidate(skill, hits))
    scored.sort(key=lambda c: (-c.score, c.skill.number))
    return scored[:limit]


def render(registry: Registry, question: str, candidates: list[Candidate]) -> str:
    lines = [f'ROUTING — "{question.strip()}"', ""]

    if not candidates:
        lines += [
            "  No analysis matched this question.",
            "",
            "Nothing has been run. Rather than defaulting to whichever skill happens to be",
            "available, say what you are trying to find out and it can be routed properly.",
            "",
            f"Declared analyses: {len(registry.skills)}. See: ksp.py registry",
        ]
        return "\n".join(lines)

    width = max(len(c.skill.name) for c in candidates)
    for index, candidate in enumerate(candidates):
        skill, marker = candidate.skill, "←" if index == 0 else " "
        state = candidate.state
        if skill.is_poc:
            state = f"{READY} (POC)"
        detail = "" if skill.available else f"   needs: {skill.missing_field}"
        if skill.deferred:
            detail = "   buildable, not yet built"
        lines.append(
            f"  {marker} {skill.name.ljust(width)}  {state:<12}{detail}".rstrip()
        )
        lines.append(f"        matched: {', '.join(candidate.hits)}")

    top = candidates[0]
    lines.append("")
    lines.append("Nothing has been run.")
    lines.append("")

    if top.skill.available:
        lines.append(f"Closest match is {top.skill.name}. To run it:")
        lines.append(f"    {_command(top.skill)}")
        if top.skill.is_poc:
            lines += [
                "",
                f"{top.skill.name} is a POC skill: no stored field backs it, so the method",
                "is improvised from reading the documents. The proper version would need: "
                f"{top.skill.missing_field}.",
            ]
    else:
        # The dangerous branch. Never offer a substitute here.
        lines += [
            f"Closest match is {top.skill.name}, and it is blocked.",
            f"It needs: {top.skill.missing_field}."
            if not top.skill.deferred
            else "It needs no new field — buildable, not yet built.",
            "",
        ]
        others = [c for c in candidates[1:] if c.skill.available]
        if others:
            named = ", ".join(c.skill.name for c in others)
            lines += [
                f"{named} answer different questions. Running one instead would be a",
                "substitution, not an answer, so no command is offered for them.",
            ]
        else:
            lines.append(
                "No substitute is offered, and none should be inferred — a different "
                "analysis would answer a different question."
            )

    return "\n".join(lines)


def _command(skill: Skill) -> str:
    if skill.number == 1:
        return 'ksp.py coverage --theme "<theme>" --geography "<geography>"'
    if skill.number == 12:
        return 'ksp.py evidence --theme "<theme>" --geography "<geography>"'
    return f'ksp.py brief --skill {skill.number} --theme "<theme>" --geography "<geography>"'


def run(registry: Registry, question: str) -> str:
    return render(registry, question, rank(registry, question))
