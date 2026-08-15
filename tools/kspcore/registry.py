"""The skill registry: sixteen analyses declared, two implemented.

Fourteen skills must fail loudly. An unimplemented skill that quietly answers
with a different analysis is the failure mode this whole system is designed
against (PRD 0), so the refusal text is rendered from the registry rather than
improvised - the wording cannot drift, and every refusal names the blocker.

Naming a blocker turns each refusal into a signal about what to build next.
Demand becomes observable instead of guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .store import read_csv, repo_root, split_multi

# The four outcomes. They must be visibly, unmistakably different in output -
# never collapsed into silence or into each other (PRD 6.1).
RESULT = "RESULT"
NO_DATA = "NO DATA"
NOT_IMPLEMENTED = "NOT IMPLEMENTED"
OUT_OF_SCOPE = "OUT OF SCOPE"

IMPLEMENTED = "IMPLEMENTED"


@dataclass
class Skill:
    number: int
    name: str
    summary: str
    status: str
    blocker_type: str  # none | field | deferred | data | time
    missing_field: str
    note: str
    caveat: str
    relevant_implemented: list[int]

    @property
    def implemented(self) -> bool:
        return self.status == IMPLEMENTED

    @property
    def deferred(self) -> bool:
        """Buildable with today's fields, not built by choice (skills 2 and 10)."""
        return self.blocker_type == "deferred"


class Registry:
    def __init__(self, skills: list[Skill]):
        self.skills = skills
        self._by_number = {s.number: s for s in skills}

    @classmethod
    def load(cls, path: Path | str | None = None) -> "Registry":
        target = Path(path) if path else repo_root() / "ksp" / "registry" / "skills.csv"
        skills = [
            Skill(
                number=int(row["number"]),
                name=row["name"],
                summary=row["summary"],
                status=row["status"],
                blocker_type=row["blocker_type"],
                missing_field=row["missing_field"],
                note=row["note"],
                caveat=row["caveat"],
                relevant_implemented=[int(n) for n in split_multi(row["relevant_implemented"])],
            )
            for row in read_csv(target)
        ]
        return cls(sorted(skills, key=lambda s: s.number))

    def get(self, number: int) -> Skill:
        if number not in self._by_number:
            raise KeyError(f"No skill #{number} in the registry")
        return self._by_number[number]

    def implemented(self) -> list[Skill]:
        return [s for s in self.skills if s.implemented]

    def label(self, number: int) -> str:
        skill = self.get(number)
        return f"{skill.name} (#{skill.number})"

    # -- rendering ---------------------------------------------------------

    def render_list(self) -> str:
        lines = [
            "SKILL REGISTRY — 16 declared, 2 implemented",
            "",
            f"{'#':>3}  {'Status':<16} {'Skill':<32} Blocker",
            f"{'—' * 3}  {'—' * 16} {'—' * 32} {'—' * 40}",
        ]
        for skill in self.skills:
            if skill.implemented:
                blocker = "—"
            elif skill.deferred:
                blocker = "buildable, not yet built"
            else:
                blocker = skill.missing_field
            lines.append(f"{skill.number:>3}  {skill.status:<16} {skill.name:<32} {blocker}")
        return "\n".join(lines)

    def render_markdown(self) -> str:
        """The reference table in references/registry.md.

        Generated rather than hand-written so it cannot drift from skills.csv,
        which is the thing the refusals are actually rendered from. A test
        fails if the committed file falls out of step.
        """
        lines = [
            "# Skill registry",
            "",
            "**Sixteen analyses declared. Two implemented. Fourteen refuse by name.**",
            "",
            "Numbering matches `docs/KSP_Analysis_Catalogue.md`.",
            "",
            "<!-- Generated from ksp/registry/skills.csv - do not edit by hand. -->",
            "<!-- Regenerate: python3 tools/render_registry_doc.py -->",
            "",
            "| # | Skill | Status | Blocker |",
            "|---|---|---|---|",
        ]
        for skill in self.skills:
            if skill.implemented:
                blocker = "—"
                name = f"**{skill.name}**"
                status = "**IMPLEMENTED**"
            else:
                name = skill.name
                status = skill.status
                blocker = "*buildable, not yet built*" if skill.deferred else skill.missing_field
            lines.append(f"| {skill.number} | {name} | {status} | {blocker} |")

        lines += [
            "",
            "## Why the fourteen refuse",
            "",
            "Each refusal names the field that would unlock it. That turns user demand",
            "into a build roadmap: what people keep asking for is what to build next.",
            "",
            "**Skills 2 and 10 need no new field.** They are deferred by choice, not",
            "blocked, and their refusal says so rather than naming a field.",
            "",
            "## What each one would mislead about, if built",
            "",
            "From the catalogue's *caveat for decision makers*. These inform future work;",
            "they are not built now.",
            "",
        ]
        for skill in self.skills:
            if skill.caveat:
                lines.append(f"- **#{skill.number} {skill.name}** — {skill.caveat}")
        return "\n".join(lines) + "\n"

    def render_refusal(self, number: int) -> str:
        """The NOT IMPLEMENTED block. Must never read like a finding."""
        skill = self.get(number)
        if skill.implemented:
            raise ValueError(
                f"Skill #{number} ({skill.name}) is implemented - run it, do not refuse it"
            )

        lines = [f"{NOT_IMPLEMENTED} — {skill.name} (#{skill.number})", ""]
        lines.append(skill.summary)
        lines.append("")

        if skill.deferred:
            # No field would unlock these (skills 2 and 10). Saying so is the
            # point: it distinguishes "not built" from "cannot be built".
            lines.append(
                "It needs no new field. This one is buildable, not blocked — "
                "it is deferred by choice and simply not built yet."
            )
        else:
            lines.append(f"It needs: {skill.missing_field}.")
            if skill.note:
                lines.append(skill.note)

        if skill.caveat:
            lines.extend(["", f"Caveat if it is built: {skill.caveat}"])

        if skill.relevant_implemented:
            names = ", ".join(self.label(n) for n in skill.relevant_implemented)
            lines.extend(["", f"Implemented skills that may be relevant: {names}."])

        return "\n".join(lines)


def render_out_of_scope(question: str, themes: list[str]) -> str:
    """Refusal for a question outside the in-scope themes (PRD 6.5 rule 7).

    Kept distinct from NOT IMPLEMENTED on purpose: no field would unlock this,
    so naming one would misdirect the reader about what to build.
    """
    listed = " and ".join(themes) if themes else "(none configured)"
    return "\n".join(
        [
            f"{OUT_OF_SCOPE} — no skill was run",
            "",
            f'The question asked about something outside the themes this POC covers: "{question.strip()}"',
            "",
            f"Themes in scope: {listed}.",
            "",
            "This is not a missing field and no analysis would unlock it. The stores hold "
            "nothing on this subject because it was never in scope to collect.",
        ]
    )
