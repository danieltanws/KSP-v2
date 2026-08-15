"""Controlled vocabularies, and validation of the stores against them.

Every filter and comparison depends on exact matching (PRD 3). Free text
forces the agent to re-interpret values at query time, differently each run,
so the lists below are the only permitted values.

Two of the lists are hierarchical and work the same way: a row carries values
from both levels in one multi-select cell.

    geography    Indonesia;Southeast Asia      country + its region
    sub_pillar   Pollution;Urban Liveability   P-2 focus area + its P-1 cluster
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .store import Store, read_csv, repo_root, split_multi

ERROR = "error"
WARNING = "warning"

#: Publisher must never carry this - it makes "there isn't one" look
#: identical to "we didn't look" (PRD 3).
FORBIDDEN_PUBLISHER = "Not Found"


@dataclass
class Problem:
    level: str
    where: str
    message: str

    def __str__(self) -> str:
        mark = "✗" if self.level == ERROR else "⚠"
        return f"  {mark} {self.where}: {self.message}"


@dataclass
class Vocab:
    root: Path
    pillar: set[str] = field(default_factory=set)
    sub_pillar: dict[str, dict] = field(default_factory=dict)
    geography: dict[str, dict] = field(default_factory=dict)
    theme: dict[str, dict] = field(default_factory=dict)
    source_type: set[str] = field(default_factory=set)
    publisher_status: set[str] = field(default_factory=set)
    actor_form: set[str] = field(default_factory=set)
    actor_type: set[str] = field(default_factory=set)
    record_type: set[str] = field(default_factory=set)
    origin: set[str] = field(default_factory=set)

    @classmethod
    def load(cls, root: Path | str | None = None) -> "Vocab":
        base = Path(root) if root else repo_root() / "ksp" / "vocab"
        simple = lambda fn: {r["value"] for r in read_csv(base / fn)}
        return cls(
            root=base,
            pillar=simple("pillar.csv"),
            sub_pillar={r["value"]: r for r in read_csv(base / "sub_pillar.csv")},
            geography={r["value"]: r for r in read_csv(base / "geography.csv")},
            theme={r["theme"]: r for r in read_csv(base / "theme.csv")},
            source_type=simple("source_type.csv"),
            publisher_status=simple("publisher_status.csv"),
            actor_form=simple("actor_form.csv"),
            actor_type=simple("actor_type.csv"),
            record_type=simple("record_type.csv"),
            origin=simple("origin.csv"),
        )

    # -- themes ------------------------------------------------------------

    def resolve_theme(self, text: str) -> dict | None:
        """Match free-language text to an in-scope theme, or None.

        None means out of scope. PRD 6.5 rule 7 restricts the agent to the
        themes in theme.csv, so this is the check behind that refusal.

        Aliases match on word boundaries, not substrings: 'wash' must not fire
        on "Washington". Where text mentions more than one theme, the first in
        theme.csv wins - deterministic, and the agent states which it chose.
        """
        if not text:
            return None
        needle = text.strip().lower()
        for name, row in self.theme.items():
            if needle in (name.lower(), row["p2_focus_area"].lower()):
                return row
        for row in self.theme.values():
            for alias in split_multi(row.get("aliases", "")):
                if re.search(rf"\b{re.escape(alias.lower())}\b", needle):
                    return row
        return None

    def theme_names(self) -> list[str]:
        return list(self.theme)

    # -- geography ---------------------------------------------------------

    def countries_in(self, region: str) -> list[str]:
        return [
            v for v, r in self.geography.items() if r.get("parent_region") == region
        ]

    def is_region(self, value: str) -> bool:
        return self.geography.get(value, {}).get("level") == "Region"


def _check_values(values, allowed, where, label, problems, level=ERROR):
    for value in values:
        if value not in allowed:
            problems.append(
                Problem(level, where, f"{label} '{value}' is not in the controlled list")
            )


def validate(store: Store, vocab: Vocab) -> list[Problem]:
    """Check every row against the vocabularies and the row-creation rules."""
    problems: list[Problem] = []

    # -- LAB sources -------------------------------------------------------
    seen_files: dict[str, str] = {}
    for row in store.sources:
        name = row.get("name") or "(unnamed row)"
        where = f"sources.csv [{name}]"

        record_type = row.get("record_type", "")
        if record_type not in vocab.record_type:
            problems.append(
                Problem(ERROR, where, f"record_type '{record_type}' is not Document or Folder")
            )
        if record_type == "Folder":
            # Folder rows are excluded from queries; they need no other fields.
            continue

        for required in ("name", "file", "description", "pillar", "geography", "source_type", "publisher"):
            if not row.get(required):
                problems.append(Problem(ERROR, where, f"required field '{required}' is empty"))

        filename = row.get("file", "")
        if filename:
            if filename in seen_files:
                problems.append(
                    Problem(ERROR, where, f"file '{filename}' is already used by '{seen_files[filename]}'")
                )
            seen_files[filename] = name

        publisher = row.get("publisher", "")
        if publisher == FORBIDDEN_PUBLISHER:
            problems.append(
                Problem(
                    ERROR,
                    where,
                    "publisher is 'Not Found' - use 'Internal' (no external publisher) "
                    "or 'Unknown' (looked, could not establish)",
                )
            )

        _check_values(split_multi(row.get("pillar")), vocab.pillar, where, "pillar", problems)
        _check_values(split_multi(row.get("sub_pillar")), set(vocab.sub_pillar), where, "sub_pillar", problems)
        _check_values(split_multi(row.get("geography")), set(vocab.geography), where, "geography", problems)
        if row.get("source_type") and row["source_type"] not in vocab.source_type:
            problems.append(
                Problem(ERROR, where, f"source_type '{row['source_type']}' is not in the controlled list")
            )

        problems.extend(_hierarchy_warnings(row, vocab, where))

        for numeric in ("year_published", "total_author_count"):
            value = row.get(numeric)
            if value and not value.isdigit():
                problems.append(Problem(ERROR, where, f"{numeric} '{value}' is not a number"))

    # -- LEAD actors -------------------------------------------------------
    seen_ids: set[str] = set()
    for row in store.actors:
        name = row.get("name") or "(unnamed row)"
        where = f"actors.csv [{name}]"

        actor_id = row.get("id", "")
        if not actor_id:
            problems.append(Problem(ERROR, where, "id is empty - it is mandatory, affiliation links point at it"))
        elif actor_id in seen_ids:
            problems.append(Problem(ERROR, where, f"id '{actor_id}' is used more than once"))
        else:
            seen_ids.add(actor_id)

        if not row.get("name"):
            problems.append(Problem(ERROR, where, "name is empty"))

        form = row.get("form", "")
        if form not in vocab.actor_form:
            problems.append(Problem(ERROR, where, f"form '{form}' is not Person or Organisation"))

        # Row-creation rule (PRD 5.2): a row that is only a name looks like
        # knowledge and is not.
        if not row.get("source_files") and not row.get("basis"):
            problems.append(
                Problem(ERROR, where, "needs either a source link or a basis - a name alone is not a record")
            )

        if row.get("actor_type") and row["actor_type"] not in vocab.actor_type:
            problems.append(Problem(ERROR, where, f"actor_type '{row['actor_type']}' is not in the controlled list"))
        if row.get("origin") and row["origin"] not in vocab.origin:
            problems.append(Problem(ERROR, where, f"origin '{row['origin']}' is not Manual or From LAB"))

        _check_values(split_multi(row.get("geography")), set(vocab.geography), where, "geography", problems)
        problems.extend(_hierarchy_warnings(row, vocab, where, sub_pillar=False))

        for filename in split_multi(row.get("source_files")):
            if not store.source_by_file(filename):
                problems.append(Problem(ERROR, where, f"source_files references '{filename}', which is not a LAB row"))

    for row in store.actors:
        affiliation = row.get("affiliation_id", "")
        if not affiliation:
            continue
        where = f"actors.csv [{row.get('name') or '(unnamed row)'}]"
        if not store.actor_by_id(affiliation):
            problems.append(Problem(ERROR, where, f"affiliation_id '{affiliation}' does not match any actor id"))
        elif row.get("form") != "Person":
            problems.append(Problem(ERROR, where, "affiliation_id is set on an Organisation - it is for people only"))

    # -- LEAD authorship ---------------------------------------------------
    seen_pairs: set[tuple[str, str]] = set()
    for row in store.authorship:
        actor_id = row.get("actor_id", "")
        filename = row.get("source_file", "")
        where = f"authorship.csv [actor {actor_id or '?'} / {filename or '?'}]"

        if not store.actor_by_id(actor_id):
            problems.append(Problem(ERROR, where, f"actor_id '{actor_id}' does not match any actor id"))
        if not store.source_by_file(filename):
            problems.append(Problem(ERROR, where, f"source_file '{filename}' is not a LAB document row"))

        position = row.get("position", "")
        if not position.isdigit() or int(position) < 1:
            problems.append(Problem(ERROR, where, f"position '{position}' must be a whole number of 1 or more"))

        pair = (actor_id, filename)
        if pair in seen_pairs:
            problems.append(Problem(ERROR, where, "duplicate - one row per person per document"))
        seen_pairs.add(pair)

    return problems


def _hierarchy_warnings(row, vocab, where, sub_pillar=True) -> list[Problem]:
    """Warn when a child value is tagged without its parent.

    A warning, never a rewrite: the convention is enforced but the user's data
    is not silently edited underneath them.
    """
    problems = []
    geography = split_multi(row.get("geography"))
    for value in geography:
        parent = vocab.geography.get(value, {}).get("parent_region")
        if parent and parent not in geography:
            problems.append(
                Problem(WARNING, where, f"geography has '{value}' without its region '{parent}'")
            )
    if sub_pillar:
        values = split_multi(row.get("sub_pillar"))
        for value in values:
            parent = vocab.sub_pillar.get(value, {}).get("parent_p1")
            if parent and parent not in values:
                problems.append(
                    Problem(WARNING, where, f"sub_pillar has '{value}' without its P-1 cluster '{parent}'")
                )
    return problems
