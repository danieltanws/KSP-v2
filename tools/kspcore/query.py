"""Filtering the stores by theme and geography.

Shared by skill #1 (coverage) and skill #12 (gap analysis) so both count the
same rows the same way.

**Theme matches the ``p2_focus_area`` column.** In the Temasek Trust taxonomy
the two in-scope themes are siblings inside one P-1 cluster:

    PLANET → Urban Liveability → { Urban Heat, Water & Waste, Pollution }

Matching the cluster instead would sweep in Urban Heat. Since P-2 has its own
column, that mistake is now unavailable rather than merely forbidden.

**Geography matches exactly** on the stored multi-select. A document about
Indonesia carries both ``Indonesia`` and ``Southeast Asia`` (PRD 3), and the
validator warns when a country is tagged without its region, so the convention
is what makes exact matching sufficient. Documents tagged ``Global`` are
counted separately rather than folded in - a global report does cover
Indonesia, but silently inflating a country count would misrepresent what was
actually read about that country.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .store import Store, split_multi
from .vocab import Vocab

GLOBAL = "Global"


@dataclass
class SourceMatch:
    documents: list[dict] = field(default_factory=list)
    global_documents: list[dict] = field(default_factory=list)

    @property
    def all_documents(self) -> list[dict]:
        return self.documents + self.global_documents

    def __len__(self) -> int:
        return len(self.documents)


@dataclass
class ActorMatch:
    """Four buckets, four strengths of evidence. Never merge them.

    LEAD exists largely to hold the implementers and funders who never publish,
    so an actor must be able to reach a theme without a document. But a
    hand-typed tag is weaker evidence than a named document, and reporting the
    two together would overstate the response side.
    """

    #: Actors linked by a document specific to the queried geography. Traceable.
    by_document: list[tuple[dict, list[str]]] = field(default_factory=list)
    #: Actors reached only through a Global document. Counted apart for the same
    #: reason global documents are: they do not evidence presence *here*.
    via_global_only: list[tuple[dict, list[str]]] = field(default_factory=list)
    #: Actors whose own p2_focus_area matches, with no matching document. Their
    #: claim cites their `basis`, which the row-creation rule guarantees exists.
    by_tag: list[dict] = field(default_factory=list)
    #: Actors matching the geography with no document and no matching tag.
    geography_only: list[dict] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.by_document)


def matches_theme(row: dict, theme: dict) -> bool:
    """True when a row - source or actor - carries the theme's focus area."""
    return theme["p2_focus_area"] in split_multi(row.get("p2_focus_area"))


def matches_geography(row: dict, geography: str | None) -> bool:
    if not geography:
        return True
    return geography in split_multi(row.get("geography"))


def is_global(row: dict) -> bool:
    return GLOBAL in split_multi(row.get("geography"))


def filter_sources(store: Store, theme: dict | None, geography: str | None = None) -> SourceMatch:
    """LAB documents for a theme and geography. Folder rows never appear."""
    result = SourceMatch()
    for row in store.documents():
        if theme and not matches_theme(row, theme):
            continue
        if matches_geography(row, geography):
            result.documents.append(row)
        elif geography and is_global(row):
            result.global_documents.append(row)
    return result


def linked_sources(store: Store, actor: dict) -> set[str]:
    """Every LAB file an actor is tied to - by direct link or by authorship."""
    files = set(split_multi(actor.get("source_files")))
    actor_id = actor.get("id", "")
    files.update(
        row.get("source_file", "")
        for row in store.authorship
        if row.get("actor_id") == actor_id and row.get("source_file")
    )
    return files


def filter_actors(
    store: Store, theme: dict | None, geography: str | None = None, sources: SourceMatch | None = None
) -> ActorMatch:
    """LEAD actors for a theme and geography.

    An actor has no theme field. The tie to a theme runs through the documents
    they are linked to, which is what makes the connection citable - the
    evidence for "this actor works on this" is a named document.

    An actor with no linked document can still carry the theme's focus area in
    their own ``p2_focus_area`` - that is how a manually-added implementer or
    funder reaches a theme at all. Those land in ``by_tag``, cited by their
    ``basis``, and are never merged into the document-backed count.
    """
    match = ActorMatch()
    if sources is None:
        sources = filter_sources(store, theme, geography)
    specific_files = {row.get("file", "") for row in sources.documents}
    global_files = {row.get("file", "") for row in sources.global_documents}
    theme_files = specific_files | global_files

    for actor in store.actors:
        linked = linked_sources(store, actor)
        overlap = sorted(f for f in linked & theme_files if f)
        if overlap:
            if set(overlap) <= global_files and global_files:
                match.via_global_only.append((actor, overlap))
            else:
                match.by_document.append((actor, overlap))
        elif theme and matches_theme(actor, theme) and matches_geography(actor, geography):
            match.by_tag.append(actor)
        elif geography and matches_geography(actor, geography):
            match.geography_only.append(actor)
        elif not geography and not linked and theme is None:
            match.geography_only.append(actor)
    return match


def year_range(documents: list[dict]) -> tuple[int | None, int | None, int]:
    """(earliest, latest, how many rows carried no year)."""
    years, undated = [], 0
    for row in documents:
        value = row.get("year_published", "")
        if value.isdigit():
            years.append(int(value))
        else:
            undated += 1
    if not years:
        return None, None, undated
    return min(years), max(years), undated


def tally(documents: list[dict], field_name: str, multi: bool = False) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in documents:
        values = split_multi(row.get(field_name)) if multi else [row.get(field_name, "")]
        for value in values:
            if value:
                counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
