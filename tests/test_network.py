"""Skill #3 - Network position.

The two things this analysis can get catastrophically wrong are naming a clique
as a set of bridges, and letting a large author list decide who looks connected.
Both are tested directly rather than through the rendered output alone.
"""

from __future__ import annotations

import pytest

from conftest import DEMO_ACTORS, DEMO_AUTHORSHIP, DEMO_SOURCES, actor, build_store, source
from kspcore import network
from kspcore.store import Store


@pytest.fixture
def water(vocab):
    return vocab.theme["Water & Waste"]


@pytest.fixture
def pollution(vocab):
    return vocab.theme["Pollution"]


# -- the graph itself ------------------------------------------------------


def test_a_clique_contains_no_bridges(tmp_path, vocab):
    """Eight co-authors of one report connect nobody to nobody.

    Removing any one of them leaves the rest connected, so none is a bridge.
    Reporting all eight would name the authors of the largest report as the
    people who hold the field together - the exact failure this analysis is
    least able to afford.
    """
    sources = [source("Big report", "Big.pdf", total_author_count="8")]
    actors = [actor(i, f"Author {i}", source_files="Big.pdf") for i in range(1, 9)]
    authorship = [
        {"actor_id": str(i), "source_file": "Big.pdf", "position": str(i)}
        for i in range(1, 9)
    ]
    store = Store.load(build_store(tmp_path / "clique", sources, actors, authorship))

    text = network.run(store, vocab, None)
    assert "No actor bridges two clusters." in text
    for i in range(1, 9):
        assert f"removing them splits" not in text


def test_a_genuine_bridge_is_found(tmp_path, vocab):
    """Two pairs joined only through one actor. Remove them and it splits."""
    sources = [
        source("Left", "Left.pdf", total_author_count="2"),
        source("Right", "Right.pdf", total_author_count="2"),
    ]
    actors = [
        actor(1, "Left Only", source_files="Left.pdf"),
        actor(2, "The Hinge", source_files="Left.pdf;Right.pdf"),
        actor(3, "Right Only", source_files="Right.pdf"),
    ]
    authorship = [
        {"actor_id": "1", "source_file": "Left.pdf", "position": "1"},
        {"actor_id": "2", "source_file": "Left.pdf", "position": "2"},
        {"actor_id": "2", "source_file": "Right.pdf", "position": "1"},
        {"actor_id": "3", "source_file": "Right.pdf", "position": "2"},
    ]
    store = Store.load(build_store(tmp_path / "hinge", sources, actors, authorship))

    text = network.run(store, vocab, None)
    section = text.split("BRIDGES")[1].split("WEIGHTED")[0]
    assert "removing them splits the graph" in section

    # Exactly one actor is named as a bridge, and it is the hinge. The leaves
    # appear only as its neighbours, which is why this counts bullets rather
    # than searching for the names.
    named = [ln.strip()[2:] for ln in section.splitlines() if ln.strip().startswith("· ")]
    assert named == ["The Hinge"]


def test_author_count_weighting_discounts_a_long_author_list(tmp_path, vocab):
    """A pair on a 2-author paper outweighs a pair on a 20-author one.

    Without this, connectedness measures report size and nothing else.
    """
    sources = [
        source("Small", "Small.pdf", total_author_count="2"),
        source("Large", "Large.pdf", total_author_count="20"),
    ]
    actors = [actor(1, "Small A", source_files="Small.pdf"),
              actor(2, "Small B", source_files="Small.pdf")]
    actors += [actor(i, f"Large {i}", source_files="Large.pdf") for i in range(3, 23)]
    authorship = [
        {"actor_id": "1", "source_file": "Small.pdf", "position": "1"},
        {"actor_id": "2", "source_file": "Small.pdf", "position": "2"},
    ] + [
        {"actor_id": str(i), "source_file": "Large.pdf", "position": str(i - 2)}
        for i in range(3, 23)
    ]
    store = Store.load(build_store(tmp_path / "weight", sources, actors, authorship))

    text = network.run(store, vocab, None)
    scores = {}
    for line in text.split("WEIGHTED CONNECTION")[1].splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] in ("Small", "Large"):
            scores[" ".join(parts[:2])] = float(parts[2])

    # Each of the 19 pairs a large-report author has is worth 1/19, summing to 1.
    # The small pair is one pair worth a full unit. Equal totals, and that is the
    # point: neither is inflated by how many people signed the report.
    assert scores["Small A"] == pytest.approx(1.0)
    assert scores["Large 3"] == pytest.approx(1.0)


def test_an_unweighted_count_is_never_printed(demo, vocab):
    text = network.run(demo, vocab, None)
    assert "Author-count weighted" in text
    assert "must not be quoted" in text


# -- what it must disclose -------------------------------------------------


def test_it_says_the_graph_maps_the_reading_list(demo, vocab):
    text = network.run(demo, vocab, None)
    assert "not of the field" in text
    assert "skews to researchers" in text


def test_tagged_and_geography_only_actors_carry_no_edge(demo, vocab, water):
    """They have no document, so nothing ties them to anyone. Including them
    would invent a link that no source supports."""
    text = network.run(demo, vocab, water)
    assert "excluded from the graph" in text
    assert "A Tagged Advocate" not in text.split("READ THIS AS")[0].split("CLUSTERS")[1]


def test_spanning_actors_are_kept_apart_from_bridges(demo, vocab):
    """Institute of Environmental Health is the sole actor on two documents, so
    it forms no edge - real connective work, but not a bridge."""
    text = network.run(demo, vocab, None)
    section = text.split("BRIDGES")[1].split("WEIGHTED")[0]
    assert "Appearing on more than one document" in section
    assert "Institute of Environmental Health" in section
    assert "publisher is filed as its actor" in section


def test_triage_points_at_the_real_command_not_brief():
    """brief is the generic POC gatherer. An implemented skill sent through it
    would run the wrong analysis under the right name."""
    from kspcore.registry import Registry
    from kspcore.triage import run as triage_run

    text = triage_run(Registry.load(), "who connects the field?")
    assert "ksp.py network" in text
    assert "brief --skill 3" not in text


def test_the_empty_store_returns_no_data(empty, vocab, pollution):
    text = network.run(empty, vocab, pollution)
    assert text.startswith("NO DATA — Network position")
    assert "describes the store, not the field" in text


def test_a_store_with_documents_but_no_actors_still_runs(tmp_path, vocab):
    """A document nobody is linked to is a real state, not an error."""
    store = Store.load(
        build_store(tmp_path / "lonely", [source("Alone", "Alone.pdf")], [], [])
    )
    text = network.run(store, vocab, None)
    assert text.startswith("RESULT — Network position")
    assert "There is no graph." in text
