"""Skill #1 - Coverage check. What the store holds.

Counting and grouping only. No inference over content.

This is the only output that is certainly true, because it describes the store
rather than the world. Everything else is uninterpretable without it: a weak
result is otherwise discovered *after* it has already convinced someone.

It runs on its own, not only as part of skill #12 (PRD 6.3) - the point is to
check coverage *before* asking a question that depends on it.
"""

from __future__ import annotations

from .query import filter_actors, filter_sources, tally, year_range
from .registry import NO_DATA, RESULT
from .store import Store
from .vocab import Vocab


def run(store: Store, vocab: Vocab, theme: dict | None, geography: str | None = None) -> str:
    sources = filter_sources(store, theme, geography)
    actors = filter_actors(store, theme, geography, sources)

    scope = _scope_line(theme, geography)
    docs = sources.documents

    if not docs and not sources.global_documents:
        return "\n".join(
            [
                f"{NO_DATA} — Coverage check (#1)",
                "",
                f"Scope: {scope}",
                "",
                "The store holds no documents matching this scope.",
                "",
                "This describes the store, not the world. Nothing here says the subject is "
                "unstudied — only that nothing on it has been filed yet.",
                _store_size(store),
            ]
        )

    earliest, latest, undated = year_range(docs)
    lines = [
        f"{RESULT} — Coverage check (#1)",
        "",
        f"Scope: {scope}",
        "",
        "EVIDENCE BASE",
        f"  LAB documents          {len(docs)}",
        f"  LEAD actors            {len(actors)} linked by a matching document",
    ]
    if actors.via_global_only:
        lines.append(
            f"  LEAD actors           +{len(actors.via_global_only)} reached only via a Global "
            "document — not evidence of presence in this geography"
        )
    if actors.by_tag:
        lines.append(
            f"  LEAD actors           +{len(actors.by_tag)} tagged with this focus area but "
            "backed by no document — cited by their basis"
        )
    if actors.geography_only:
        lines.append(
            f"  LEAD actors           +{len(actors.geography_only)} matching geography only, "
            "with no document or tag tying them to this theme"
        )
    if sources.global_documents:
        lines.append(
            f"  Global documents      +{len(sources.global_documents)} tagged Global "
            "(cover this geography but are not specific to it; counted separately)"
        )
    if earliest is None:
        lines.append("  Date range             no years recorded")
    else:
        span = str(earliest) if earliest == latest else f"{earliest}–{latest}"
        lines.append(f"  Date range             {span}")
    if undated:
        lines.append(f"  Undated                {undated} document(s) carry no year")

    lines.extend(_breakdown("BY SOURCE TYPE", tally(docs, "source_type")))
    lines.extend(_breakdown("BY FOCUS AREA", tally(docs, "p2_focus_area", multi=True)))
    lines.extend(_breakdown("BY GEOGRAPHY", tally(docs, "geography", multi=True)))
    lines.extend(_breakdown("BY PUBLISHER", tally(docs, "publisher")))

    if not docs and geography:
        lines.extend(
            [
                "",
                f"  ⚠ NOTHING SPECIFIC TO {geography.upper()}",
                f"    No document names {geography}. The count above is Global material only.",
            ]
        )

    lines.extend(
        [
            "",
            "READ THIS AS: what has been collected. A well-covered cell means we have read",
            "a lot, not that a field is crowded. A thin cell means we have read little, not",
            "that the subject is neglected.",
        ]
    )
    return "\n".join(lines)


def _breakdown(title: str, counts: dict[str, int]) -> list[str]:
    lines = ["", title]
    if not counts:
        lines.append("  (nothing recorded)")
        return lines
    width = max(len(k) for k in counts)
    for key, count in counts.items():
        lines.append(f"  {key.ljust(width)}   {count}")
    return lines


def _scope_line(theme: dict | None, geography: str | None) -> str:
    parts = [f"theme {theme['theme']}" if theme else "all themes"]
    parts.append(f"geography {geography}" if geography else "all geographies")
    return ", ".join(parts)


def _store_size(store: Store) -> str:
    return (
        f"\nWhole store: {len(store.documents())} document(s), "
        f"{len(store.actors)} actor(s)."
    )
