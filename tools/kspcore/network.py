"""Skill #3 - Network position. Which actors connect otherwise separate clusters.

Two actors are adjacent when one document links both. A **bridge** is an actor
whose removal leaves the graph in more pieces than it was in before - the formal
version of "who connects the field".

**Author-count weighting is not optional, and it is why this was blocked.** A
document with 40 authors creates 780 pairs on its own. Counted flat, an actor's
connectedness would measure the size of the reports they appear on rather than
how they connect anything, and the most-connected actor would always be whoever
signed the largest report. Each document therefore contributes ``1/(n-1)`` to
every pair it creates, so a two-author paper contributes a full unit per pair
and a forty-author report contributes 1/39.

``n`` is the document's declared ``total_author_count`` where it has one. Where
it does not, the count of filed authorship rows stands in - which understates a
long author list that was only partly filed, so the basis is reported rather
than assumed.

**What this graph maps.** It is built from documents that have been filed, so it
describes the reading list. An actor central here is central *among what we have
read*, and LEAD is filled largely by harvesting authors, so the graph skews to
researchers whatever the field actually looks like. Both facts go in the output
every time; neither is a caveat the reader can be left to infer.

Bridges are found by removing each actor and recounting components. That is the
definition rather than an approximation of it, and at this store's size the cost
of doing it exactly is nothing.
"""

from __future__ import annotations

from collections import deque

from .query import filter_actors, filter_sources
from .registry import NO_DATA, RESULT
from .store import Store
from .vocab import Vocab


def run(store: Store, vocab: Vocab, theme: dict | None, geography: str | None = None) -> str:
    sources = filter_sources(store, theme, geography)
    actors = filter_actors(store, theme, geography, sources)
    docs = sources.documents

    scope = _scope_line(theme, geography)

    if not docs and not sources.global_documents:
        return "\n".join([
            f"{NO_DATA} — Network position",
            "",
            f"Scope: {scope}",
            "",
            "The store holds no documents matching this scope, so there is no graph to",
            "build. No actor can be shown to connect anything.",
            "",
            "This describes the store, not the field.",
            f"\nWhole store: {len(store.documents())} document(s), {len(store.actors)} actor(s).",
        ])

    # Only document-backed actors carry an edge. A tagged actor has no document,
    # so nothing ties them to anyone else - including them would invent a link.
    linked = {a["id"]: (a, files) for a, files in actors.by_document if a.get("id")}
    by_file = _actors_per_file(linked)
    edges, basis = _weighted_edges(store, docs + sources.global_documents, by_file)

    names = {aid: pair[0].get("name", "(unnamed)") for aid, pair in linked.items()}
    adjacency = _adjacency(edges)
    clusters = _components(set(linked), adjacency)
    bridges = _bridges(set(linked), adjacency, clusters)

    lines = [
        f"{RESULT} — Network position",
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
        lines.append(
            f"  LEAD actors           +{len(actors.by_tag)} tagged with this focus area, no document "
            "— carries no edge, excluded from the graph"
        )
    if actors.geography_only:
        lines.append(
            f"  LEAD actors           +{len(actors.geography_only)} geography-only "
            "— carries no edge, excluded from the graph"
        )
    lines.append(f"  Weighting basis        {_basis_line(basis)}")

    lines.extend(_cluster_block(clusters, names, adjacency))
    lines.extend(_bridge_block(bridges, names, clusters, adjacency, linked))
    lines.extend(_weighted_degree_block(edges, names, linked))

    lines.extend([
        "",
        "READ THIS AS: a map of what has been read, not of the field. An actor connects",
        "documents that happen to be filed here; one who connects nothing may still be",
        "central in the world. LEAD is filled largely by harvesting authors, so the graph",
        "skews to researchers whether or not the field does.",
    ])
    return "\n".join(lines)


# -- building the graph ----------------------------------------------------


def _actors_per_file(linked: dict) -> dict[str, list[str]]:
    """Which in-scope actors each document links, keyed by filename."""
    per_file: dict[str, list[str]] = {}
    for actor_id, (_, files) in linked.items():
        for filename in files:
            per_file.setdefault(filename, []).append(actor_id)
    return per_file


def _weighted_edges(store, documents, by_file) -> tuple[dict, dict]:
    """{(a, b): weight} plus how each document's author count was established.

    A document linking one actor creates no pair and so no edge - it tells you
    nothing about who connects to whom.
    """
    edges: dict[tuple[str, str], float] = {}
    basis: dict[str, str] = {}
    rows = {row.get("file"): row for row in documents}

    for filename, actor_ids in by_file.items():
        if len(actor_ids) < 2:
            continue
        row = rows.get(filename, {})
        count, how = _author_count(row, len(actor_ids), store, filename)
        basis[filename] = how
        weight = 1.0 / (count - 1) if count > 1 else 0.0
        for i, first in enumerate(sorted(actor_ids)):
            for second in sorted(actor_ids)[i + 1:]:
                edges[(first, second)] = edges.get((first, second), 0.0) + weight
    return edges, basis


def _author_count(row, linked_count: int, store: Store, filename: str) -> tuple[int, str]:
    """The n to weight by, and how it was established.

    The declared count wins where it is at least as large as what was filed. A
    declared count *below* the filed rows is a contradiction in the data, so the
    filed rows are used and the basis says so rather than silently trusting one.
    """
    declared = (row.get("total_author_count") or "").strip()
    filed = len(store.authors_of(filename)) or linked_count
    if declared.isdigit() and int(declared) >= max(linked_count, filed):
        return int(declared), "declared"
    return max(linked_count, filed), "filed"


def _adjacency(edges: dict) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for first, second in edges:
        graph.setdefault(first, set()).add(second)
        graph.setdefault(second, set()).add(first)
    return graph


def _components(nodes: set[str], adjacency: dict) -> list[set[str]]:
    """Connected components, largest first. Isolated actors are their own."""
    seen: set[str] = set()
    found: list[set[str]] = []
    for node in sorted(nodes):
        if node in seen:
            continue
        group, queue = set(), deque([node])
        while queue:
            current = queue.popleft()
            if current in group:
                continue
            group.add(current)
            queue.extend(adjacency.get(current, set()) - group)
        seen |= group
        found.append(group)
    return sorted(found, key=lambda g: (-len(g), sorted(g)))


def _bridges(nodes: set[str], adjacency: dict, clusters: list[set[str]]) -> list[str]:
    """Actors whose removal leaves the graph in more pieces than before.

    An isolated actor is never a bridge: removing them lowers the count by one,
    which is the opposite of what a bridge does.

    Removing a connected actor who is *not* a bridge leaves the count unchanged
    - their cluster shrinks but stays whole. So the test is strictly greater
    than the count before, not greater than one less than it. Getting that wrong
    reports every member of a clique as a bridge, which is the failure this
    analysis is least able to afford: it would name eight co-authors of one
    report as the people who connect the field.
    """
    before = len(clusters)
    out = []
    for node in sorted(nodes):
        if not adjacency.get(node):
            continue
        remaining = nodes - {node}
        trimmed = {k: (v - {node}) for k, v in adjacency.items() if k != node}
        if len(_components(remaining, trimmed)) > before:
            out.append(node)
    return out


# -- rendering -------------------------------------------------------------


def _cluster_block(clusters, names, adjacency) -> list[str]:
    connected = [c for c in clusters if len(c) > 1]
    alone = [c for c in clusters if len(c) == 1]

    lines = ["", "CLUSTERS"]
    if not clusters:
        lines.append("  No actor in this scope is linked to a document. There is no graph.")
        return lines
    lines.append(
        f"  {len(clusters)} cluster(s) across {sum(len(c) for c in clusters)} document-backed actor(s)"
    )
    for group in connected:
        members = ", ".join(names[a] for a in sorted(group, key=lambda x: names[x]))
        lines.append(f"  · {len(group)} connected: {members}")
    if alone:
        lines.append(
            f"  · {len(alone)} actor(s) share no document with anyone: "
            + ", ".join(names[next(iter(c))] for c in alone)
        )
    if not connected:
        lines.append(
            "    Every actor stands alone, so nothing here connects anything. That is a"
        )
        lines.append(
            "    statement about how little has been filed, not about an unconnected field."
        )
    return lines


def _bridge_block(bridges, names, clusters, adjacency, linked) -> list[str]:
    lines = ["", "BRIDGES"]
    if bridges:
        for actor_id in sorted(bridges, key=lambda a: names[a]):
            neighbours = ", ".join(sorted(names[n] for n in adjacency.get(actor_id, set())))
            lines.append(f"  · {names[actor_id]}")
            lines.append(f"      removing them splits the graph; connects: {neighbours}")
    else:
        lines.append("  No actor bridges two clusters.")
        lines.append(
            "  Nothing would be split by removing any one of them. Do not read this as"
        )
        lines.append(
            "  a field with no connectors — with this much filed, it is the expected shape."
        )

    # Weaker, and kept apart for the same reason the actor buckets are: an actor
    # who is the sole actor on several documents forms no edge at all, so the
    # graph above cannot see them. Spanning documents is connective work, but it
    # is not the same evidence as sharing one with somebody.
    spanning = sorted(
        (a for a in linked if len(linked[a][1]) > 1 and a not in bridges),
        key=lambda a: names[a],
    )
    if spanning:
        lines.append("")
        lines.append("  Appearing on more than one document, but sharing none with another actor:")
        for actor_id in spanning:
            files = ", ".join(sorted(linked[actor_id][1]))
            lines.append(f"  · {names[actor_id]} — {files}")
        lines.append(
            "    Weaker than a bridge and not interchangeable with one. Where a document"
        )
        lines.append(
            "    has no byline the publisher is filed as its actor, so an institution can"
        )
        lines.append(
            "    span documents by that convention rather than by doing anything."
        )
    return lines


def _weighted_degree_block(edges, names, linked) -> list[str]:
    degree = {aid: 0.0 for aid in linked}
    for (first, second), weight in edges.items():
        degree[first] = degree.get(first, 0.0) + weight
        degree[second] = degree.get(second, 0.0) + weight

    lines = ["", "WEIGHTED CONNECTION", "  Author-count weighted. An unweighted count is not"
             " reported and must not be quoted."]
    if not degree:
        lines.append("  (no document-backed actors in this scope)")
        return lines
    width = max(len(names[a]) for a in degree)
    ranked = sorted(degree.items(), key=lambda kv: (-kv[1], names[kv[0]]))
    for actor_id, score in ranked:
        docs = len(linked[actor_id][1])
        lines.append(
            f"  {names[actor_id].ljust(width)}   {score:5.2f}   {docs} document(s)"
        )
    return lines


def _basis_line(basis: dict) -> str:
    if not basis:
        return "no document links two actors, so nothing was weighted"
    declared = sum(1 for how in basis.values() if how == "declared")
    filed = len(basis) - declared
    parts = []
    if declared:
        parts.append(f"declared author count on {declared} document(s)")
    if filed:
        parts.append(f"filed authorship rows on {filed} (may understate a long author list)")
    return "; ".join(parts)


def _scope_line(theme: dict | None, geography: str | None) -> str:
    parts = [f"theme {theme['theme']}" if theme else "all themes"]
    parts.append(f"geography {geography}" if geography else "all geographies")
    return ", ".join(parts)
