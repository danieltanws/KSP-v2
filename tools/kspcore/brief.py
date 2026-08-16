"""The generic gatherer behind every POC skill.

A POC skill has no stored field and no analysis code. What it gets is this: a
fixed evidence-base block, then the documents and actors for the theme. The
method is the agent's to invent, guided by the prompt file in
``.claude/skills/ksp/analyses/``.

Generic on purpose. Adding a POC skill needs a prompt file and a status cell -
never a new gatherer.

**What the evidence base is doing here.** A POC answer carries the same
``RESULT`` label as skill #1, which counts, and skill #12, which reads stored
fields. Nothing in the label distinguishes a computed answer from a guessed
one. The evidence base is where that difference stays visible: it names the
field the proper analysis would use and states plainly that it is not stored.
It goes first for the reason it always goes first - a caveat read after the
argument is too late to change how the argument landed.
"""

from __future__ import annotations

from .query import filter_actors, filter_sources, tally, year_range
from .registry import NO_DATA, RESULT, Registry, Skill
from .store import Store
from .vocab import Vocab


def run(
    store: Store, vocab: Vocab, registry: Registry, number: int, theme: dict, geography: str | None = None
) -> str:
    skill = registry.get(number)
    sources = filter_sources(store, theme, geography)
    actors = filter_actors(store, theme, geography, sources)
    docs = sources.documents

    scope = f"theme {theme['theme']}" + (f", geography {geography}" if geography else ", all geographies")

    if not docs and not sources.global_documents:
        return "\n".join(
            [
                f"{NO_DATA} — {skill.name} (#{skill.number})",
                "",
                f"Scope: {scope}",
                "",
                "The store holds no documents matching this scope. There is nothing to read,",
                "so there is nothing to analyse.",
                "",
                "This describes the store, not the world.",
                f"\nWhole store: {len(store.documents())} document(s), {len(store.actors)} actor(s).",
            ]
        )

    earliest, latest, undated = year_range(docs)
    lines = [
        f"{RESULT} — {skill.name} (#{skill.number})",
        "",
        f"Scope: {scope}",
        "",
        "EVIDENCE BASE",
        f"  LAB documents          {len(docs)}",
        f"  LEAD actors            {len(actors)} linked by a matching document",
    ]
    if actors.via_global_only:
        lines.append(f"  LEAD actors           +{len(actors.via_global_only)} via a Global document only")
    if actors.by_tag:
        lines.append(f"  LEAD actors           +{len(actors.by_tag)} tagged with this focus area, no document")
    if actors.geography_only:
        lines.append(f"  LEAD actors           +{len(actors.geography_only)} geography-only, no document or tag")
    if sources.global_documents:
        lines.append(f"  Global documents      +{len(sources.global_documents)} tagged Global, counted separately")
    if earliest is None:
        lines.append("  Date range             no years recorded")
    else:
        span = str(earliest) if earliest == latest else f"{earliest}–{latest}"
        lines.append(f"  Date range             {span}" + (f" ({undated} undated)" if undated else ""))
    lines.append(f"  Source types           {_inline(tally(docs, 'source_type'))}")
    lines.extend(_what_is_not_stored(skill))

    lines.extend(["", "── LAB DOCUMENTS ──"])
    for row in docs:
        lines.extend(_document_block(row))
    for row in sources.global_documents:
        lines.extend(_document_block(row, tag=" [Global — not specific to this geography]"))

    lines.extend(["", "── LEAD ACTORS ──"])
    if actors.by_document:
        for actor, via in actors.by_document:
            actor_type = actor.get("actor_type") or "type not recorded"
            lines.append(f"  • {actor.get('name')} — {actor.get('form')}, {actor_type}")
            lines.append(f"      linked via: {', '.join(via)}")
    else:
        lines.append("  (none linked by a matching document)")
    for actor, via in actors.via_global_only:
        lines.append(f"  • {actor.get('name')} — via a Global document only: {', '.join(via)}")
    for actor in actors.by_tag:
        actor_type = actor.get("actor_type") or "type not recorded"
        lines.append(f"  • {actor.get('name')} — {actor.get('form')}, {actor_type}")
        lines.append(f"      tagged {actor.get('p2_focus_area')}; no document. "
                     f"Cite: {actor.get('basis') or 'no basis recorded'}")
    for actor in actors.geography_only:
        lines.append(f"  • {actor.get('name')} — geography match only, {actor.get('basis') or 'no basis recorded'}")

    lines.extend(
        [
            "",
            "── HOW TO USE THIS ──",
            f"  Method is yours to work out. Read .claude/skills/ksp/analyses/{skill.prompt_filename}",
            "  for what this analysis is trying to find, then reason over the documents above.",
            "",
            "  Binding regardless of method:",
            "    · Every claim names its document or actor. No claim without one.",
            "    · Label LAB and LEAD claims separately.",
            "    · Absence in the store is never absence in the world.",
            "    · State a mismatch; do not recommend.",
            "    · The evidence base above goes first, unedited.",
        ]
    )
    return "\n".join(lines)


def _what_is_not_stored(skill: Skill) -> list[str]:
    """Name the field the proper analysis would use, and say it is absent.

    This is the only place a reader can tell a POC answer from a computed one,
    so it is not optional.
    """
    if not skill.is_poc or not skill.missing_field:
        return []
    return [
        f"  {'Not stored':<22} {skill.missing_field}",
        f"  {'':<22} → identified by reading, not by a field. Improvised, not computed.",
    ]


def _document_block(row: dict, tag: str = "") -> list[str]:
    year = row.get("year_published") or "no year"
    block = [
        "",
        f"  ▸ {row.get('name')}{tag}",
        f"      file: {row.get('file')}  ·  {row.get('source_type')}  ·  "
        f"{row.get('publisher')}  ·  {year}",
        f"      geography: {row.get('geography')}",
        f"      focus area: {row.get('p2_focus_area') or '(none)'}"
        f"  ({row.get('p1_cluster') or 'no cluster'})",
    ]
    if row.get("source_url"):
        block.append(f"      source: {row['source_url']}")
    if row.get("description"):
        block.append(f"      description: {row['description']}")
    if row.get("quick_insights"):
        block.append(f"      quick insights: {row['quick_insights']}")
    return block


def _inline(counts: dict[str, int]) -> str:
    if not counts:
        return "(none recorded)"
    return ", ".join(f"{k} {v}" for k, v in counts.items())
