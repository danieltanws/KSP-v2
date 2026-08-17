"""Skill #12 - the deterministic half of gap analysis.

This gathers and counts. It does **not** decide what is problem-side and what
is response-side: PRD 6.4 step 2 is inference at query time, performed by the
agent reading each document, and there is no stored problem/response field.

Consequence, which the agent must state in its output: classification is not
stable between runs. The same question may sort documents differently on
different days. Caching it here would hide that, so nothing is cached.

What comes back is a brief for the agent to reason over - never something to
paste as the answer.
"""

from __future__ import annotations

from .query import filter_actors, filter_sources, linked_sources, tally, year_range
from .registry import NO_DATA
from .store import Store, split_multi
from .vocab import Vocab

ALL_SOURCE_TYPES = ["Research", "Policy", "Media", "Industry", "Internal"]


def run(store: Store, vocab: Vocab, theme: dict, geography: str | None = None) -> str:
    sources = filter_sources(store, theme, geography)
    actors = filter_actors(store, theme, geography, sources)
    docs = sources.documents

    if not docs and not sources.global_documents:
        return "\n".join(
            [
                f"{NO_DATA} — Gap analysis",
                "",
                f"Scope: theme {theme['theme']}"
                + (f", geography {geography}" if geography else ", all geographies"),
                "",
                "The store holds no documents matching this scope, so there is nothing to",
                "compare a problem side against a response side.",
                "",
                "This is a coverage gap, not a finding. No gap is produced, because producing",
                "one from an empty store would be fabrication.",
                f"\nWhole store: {len(store.documents())} document(s), {len(store.actors)} actor(s).",
            ]
        )

    earliest, latest, undated = year_range(docs)
    by_type = tally(docs, "source_type")

    lines = [
        "EVIDENCE BRIEF — inputs for Gap analysis",
        "",
        "This is raw material, not an answer. Classify each document below as problem side,",
        "response side, or both, then write the six sections. Do not paste this brief.",
        "",
    ]
    if not docs and geography:
        # No threshold suppresses this (rule 6), so the disclosure has to be
        # impossible to skim past.
        lines.extend(
            [
                f"  ⚠ NOTHING SPECIFIC TO {geography.upper()}",
                f"    No document names {geography}. Everything below is tagged Global.",
                "    Any gap written from this describes the absence of reading about",
                f"    {geography}, not the absence of activity in it. Say so in Sections 1 and 5.",
                "",
            ]
        )
    lines.extend([
        "── SECTION 1 MATERIAL: evidence base ──",
        f"  LAB documents      {len(docs)}",
        f"  LEAD actors        {len(actors)} linked by a matching document",
    ])
    if actors.via_global_only:
        lines.append(f"  LEAD actors       +{len(actors.via_global_only)} via a Global document only")
    if actors.by_tag:
        lines.append(f"  LEAD actors       +{len(actors.by_tag)} tagged with this focus area, no document")
    if actors.geography_only:
        lines.append(f"  LEAD actors       +{len(actors.geography_only)} geography-only, no document or tag")
    if sources.global_documents:
        lines.append(f"  Global documents  +{len(sources.global_documents)} tagged Global, counted separately")
    if earliest is None:
        lines.append("  Date range         no years recorded")
    else:
        span = str(earliest) if earliest == latest else f"{earliest}–{latest}"
        lines.append(f"  Date range         {span}" + (f" ({undated} undated)" if undated else ""))
    lines.append(f"  Source types       {_inline(by_type)}")
    lines.append(f"  Geographies        {_inline(tally(docs, 'geography', multi=True))}")

    lines.extend(["", "── LAB DOCUMENTS: classify each one ──"])
    for row in docs:
        lines.extend(_document_block(row))
    for row in sources.global_documents:
        lines.extend(_document_block(row, tag=" [Global — not specific to this geography]"))

    lines.extend(["", "── LEAD ACTORS: response-side evidence ──"])
    if actors.by_document:
        for actor, via in actors.by_document:
            actor_type = actor.get("actor_type") or "type not recorded"
            lines.append(f"  • {actor.get('name')} — {actor.get('form')}, {actor_type}")
            lines.append(f"      linked via: {', '.join(via)}")
            if actor.get("geography"):
                lines.append(f"      writes about: {actor.get('geography')}")
    else:
        lines.append("  (none linked by a matching document)")
    if actors.via_global_only:
        lines.append("")
        lines.append("  Reached only via a Global document — does not evidence presence here:")
        for actor, via in actors.via_global_only:
            lines.append(f"  • {actor.get('name')} — linked via: {', '.join(via)}")
    if actors.by_tag:
        lines.append("")
        lines.append("  Tagged with this focus area, but no document backs it — cite the basis:")
        for actor in actors.by_tag:
            lines.append(f"  • {actor.get('name')} — {actor.get('basis') or 'no basis recorded'}")
    if actors.geography_only:
        lines.append("")
        lines.append("  Geography-only actors — no document or tag ties them to this theme:")
        for actor in actors.geography_only:
            basis = actor.get("basis") or "no basis recorded"
            lines.append(f"  • {actor.get('name')} — {basis}")

    lines.extend(["", "── SECTION 5 MATERIAL: what the store does not hold ──"])
    lines.extend(_absences(store, docs, sources.global_documents, actors, theme, geography))

    lines.extend(
        [
            "",
            "── MANDATORY DISCLOSURES for the output ──",
            "  · Problem/response classification is inferred now, not stored. It may differ",
            "    on another run. Name which documents you placed on each side.",
            "  · Gap analysis is the lowest-trust candidate type in the catalogue: the one",
            "    most likely to reflect thin reading rather than real absence, and the one",
            "    readers find most convincing. Section 1 is not optional.",
            "  · Default Section 5 to 'Coverage gap'. 'Confirmed absent' is a strong claim and",
            "    must be justified in the text.",
        ]
    )
    return "\n".join(lines)


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


def _absences(store, docs, global_docs, actors, theme, geography) -> list[str]:
    """State what was looked for and not found, so Section 5 is not guesswork."""
    out = []
    scope = f"for {geography}" if geography else "in this scope"
    present_types = {row.get("source_type") for row in docs}
    global_types = {row.get("source_type") for row in global_docs}

    missing_types = [t for t in ALL_SOURCE_TYPES if t not in present_types]
    for source_type in missing_types:
        if source_type in global_types:
            out.append(
                f"  · No {source_type} documents {scope} — the only one held is tagged Global"
            )
        else:
            out.append(f"  · No {source_type} documents {scope}")
    if "Policy" not in present_types and "Policy" not in global_types:
        out.append("  · No policy-focused documents — government and multilateral activity is unobserved")
    if not actors.by_document:
        out.append("  · No LEAD actors are linked to any matching document")

    untyped = [a for a, _ in actors.by_document if not a.get("actor_type")]
    if untyped:
        out.append(
            f"  · {len(untyped)} of {len(actors.by_document)} matched actors have no actor_type recorded — "
            "the mix of researchers, implementers and funders cannot be read"
        )
    if geography:
        specific = [r for r in docs if geography in split_multi(r.get("geography"))]
        out.append(f"  · {len(specific)} document(s) name {geography} specifically")
    out.append(
        f"  · Whole store for context: {len(store.documents())} document(s), {len(store.actors)} actor(s). "
        "Thin totals mean thin reading."
    )
    return out


def _inline(counts: dict[str, int]) -> str:
    if not counts:
        return "(none recorded)"
    return ", ".join(f"{k} {v}" for k, v in counts.items())
