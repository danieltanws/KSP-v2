"""Controlled vocabularies, and validation of the stores against them.

Every filter and comparison depends on exact matching (PRD 3). Free text
forces the agent to re-interpret values at query time, differently each run,
so the lists below are the only permitted values.

The 4P taxonomy is three explicit levels, one column each, matching the
Trust's own structure:

    pillar         PLANET
    p1_cluster     Urban Liveability
    p2_focus_area  Pollution

Each P-2 has exactly one parent P-1, and each P-1 exactly one pillar, so the
chain a row writes is checkable: a mismatched chain is an error, not a style
lapse. Keeping P-2 in its own column also makes a whole class of mistake
unavailable - filtering on the cluster can no longer sweep in its siblings.

Geography stays a single multi-select carrying both levels
(``Indonesia;Southeast Asia``). Its values are not a strict tree - a document
can be about Indonesia and Kenya at once - so the same treatment would not fit.
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
    #: The whole 4P tree, keyed by value. Rows carry level, pillar, parent_p1.
    taxonomy: dict[str, dict] = field(default_factory=dict)
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
            taxonomy={r["value"]: r for r in read_csv(base / "taxonomy.csv")},
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

    # -- the 4P taxonomy -----------------------------------------------------

    def at_level(self, level: str) -> dict[str, dict]:
        return {v: r for v, r in self.taxonomy.items() if r["level"] == level}

    @property
    def pillar(self) -> set[str]:
        return set(self.at_level("P"))

    @property
    def p1_cluster(self) -> set[str]:
        return set(self.at_level("P-1"))

    @property
    def p2_focus_area(self) -> set[str]:
        return set(self.at_level("P-2"))

    def parents_of(self, value: str) -> tuple[str, str]:
        """(pillar, p1_cluster) for any taxonomy value. Blank where not applicable."""
        row = self.taxonomy.get(value, {})
        return row.get("pillar", ""), row.get("parent_p1", "")

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

        _check_values(split_multi(row.get("geography")), set(vocab.geography), where, "geography", problems)
        if row.get("source_type") and row["source_type"] not in vocab.source_type:
            problems.append(
                Problem(ERROR, where, f"source_type '{row['source_type']}' is not in the controlled list")
            )

        url = row.get("source_url", "")
        if url and not url.startswith(("http://", "https://")):
            problems.append(
                Problem(ERROR, where, f"source_url '{url}' must start with http:// or https://")
            )

        problems.extend(_taxonomy_problems(row, vocab, where))
        problems.extend(_geography_warnings(row, vocab, where))

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
        problems.extend(_taxonomy_problems(row, vocab, where, required=False))
        problems.extend(_geography_warnings(row, vocab, where))

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


def _taxonomy_problems(row, vocab, where, required=True) -> list[Problem]:
    """Check the P / P-1 / P-2 chain a row writes.

    Each P-2 has exactly one parent P-1 and each P-1 one pillar, so a written
    chain is verifiable rather than merely conventional. A wrong chain is an
    error: it asserts a relationship the taxonomy does not contain.
    """
    problems: list[Problem] = []
    pillars = split_multi(row.get("pillar"))
    clusters = split_multi(row.get("p1_cluster"))
    focus_areas = split_multi(row.get("p2_focus_area"))

    _check_values(pillars, vocab.pillar, where, "pillar", problems)
    _check_values(clusters, vocab.p1_cluster, where, "p1_cluster", problems)
    _check_values(focus_areas, vocab.p2_focus_area, where, "p2_focus_area", problems)

    if required and not pillars:
        problems.append(Problem(ERROR, where, "required field 'pillar' is empty"))

    for focus in focus_areas:
        pillar, cluster = vocab.parents_of(focus)
        if not pillar:
            continue  # unknown value, already reported above
        if clusters and cluster not in clusters:
            problems.append(
                Problem(
                    ERROR,
                    where,
                    f"p2_focus_area '{focus}' belongs to p1_cluster '{cluster}', "
                    f"but the row says {clusters}",
                )
            )
        if pillars and pillar not in pillars:
            problems.append(
                Problem(
                    ERROR, where,
                    f"p2_focus_area '{focus}' belongs to pillar '{pillar}', but the row says {pillars}",
                )
            )

    for cluster in clusters:
        pillar, _ = vocab.parents_of(cluster)
        if pillar and pillars and pillar not in pillars:
            problems.append(
                Problem(
                    ERROR, where,
                    f"p1_cluster '{cluster}' belongs to pillar '{pillar}', but the row says {pillars}",
                )
            )
    return problems


def _geography_warnings(row, vocab, where) -> list[Problem]:
    """Warn when a country is tagged without its region.

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
    return problems
