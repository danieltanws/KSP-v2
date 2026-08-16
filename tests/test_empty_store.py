"""Every command, against an empty store.

This is the state the real store ships in and the state it stays in until
someone files a real document, so it is the configuration most likely to be
running when a stakeholder is watching.

PRD 7 says to test with an empty store first, because most failure modes in
this system appear as silence and silence is the specific thing it must not
produce. An empty store must return `NO DATA` with an explanation, never a
blank answer and never a fabricated finding.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ROOT
from kspcore import brief, coverage, evidence, integrity
from kspcore.registry import NO_DATA, Registry

CLI = ROOT / "tools" / "ksp.py"


@pytest.fixture
def registry() -> Registry:
    return Registry.load()


def run_cli(store: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), "--store", str(store), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


# -- the shipped state ------------------------------------------------------


def test_the_real_store_is_empty():
    """If this fails, someone has put data in ksp/. Test data belongs in tests."""
    for relative in ("lab/sources.csv", "lead/actors.csv", "lead/authorship.csv"):
        lines = (ROOT / "ksp" / relative).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1, f"{relative} has rows; the real store ships empty"


def test_no_documents_are_filed_in_the_real_store():
    files = [
        p.name for p in (ROOT / "ksp" / "lab" / "documents").iterdir()
        if p.is_file() and p.name not in integrity.IGNORED_FILES
    ]
    assert files == [], f"unexpected documents in the real store: {files}"


# -- integrity and validation ----------------------------------------------


def test_integrity_check_passes_and_says_both_checks_ran(empty):
    report = integrity.check(empty)
    assert report.ok
    text = report.render()
    # Silence would be indistinguishable from the check not running at all.
    assert "no rows reference missing files" in text
    assert "no files present but unfiled" in text


def test_validation_passes(empty, vocab):
    from kspcore.vocab import validate

    assert validate(empty, vocab) == []


# -- the skills -------------------------------------------------------------


def test_coverage_returns_no_data_with_an_explanation(empty, vocab):
    text = coverage.run(empty, vocab, vocab.theme["Pollution"], "Indonesia")
    assert text.startswith(NO_DATA)
    assert "describes the store, not the world" in text
    assert "0 document(s)" in text


def test_coverage_with_no_theme_or_geography(empty, vocab):
    """The broadest possible question against nothing at all."""
    text = coverage.run(empty, vocab, None)
    assert text.startswith(NO_DATA)
    assert text.strip()


def test_gap_analysis_refuses_to_invent_one(empty, vocab):
    text = evidence.run(empty, vocab, vocab.theme["Pollution"], "Indonesia")
    assert text.startswith(NO_DATA)
    assert "would be fabrication" in text


@pytest.mark.parametrize("number", [6, 9])
def test_poc_skills_return_no_data_rather_than_improvising(empty, vocab, registry, number):
    """A POC skill invents its method. With nothing to read it must still stop."""
    text = brief.run(empty, vocab, registry, number, vocab.theme["Water & Waste"])
    assert text.startswith(NO_DATA)
    assert "nothing to analyse" in text


@pytest.mark.parametrize("theme", ["Pollution", "Water & Waste"])
def test_every_theme_returns_no_data_not_silence(empty, vocab, theme):
    for text in (
        coverage.run(empty, vocab, vocab.theme[theme]),
        evidence.run(empty, vocab, vocab.theme[theme]),
    ):
        assert text.startswith(NO_DATA)
        assert len(text.splitlines()) > 3, "NO DATA still owes the reader an explanation"


def test_no_output_claims_absence_in_the_world(empty, vocab, registry):
    outputs = [
        coverage.run(empty, vocab, vocab.theme["Pollution"], "Indonesia"),
        evidence.run(empty, vocab, vocab.theme["Pollution"], "Indonesia"),
        brief.run(empty, vocab, registry, 9, vocab.theme["Water & Waste"]),
    ]
    banned = ("nobody is working", "no one is working", "there are no actors working",
              "nothing exists", "no such")
    for text in outputs:
        lowered = text.lower()
        for phrase in banned:
            assert phrase not in lowered, f"empty store asserted absence: {phrase}"


# -- the CLI, end to end ----------------------------------------------------


def test_check_and_validate_exit_clean(empty_path):
    for command in ("check", "validate"):
        result = run_cli(empty_path, command)
        assert result.returncode == 0, f"{command}: {result.stdout}{result.stderr}"
        assert result.stdout.strip()


@pytest.mark.parametrize("args", [
    ("coverage", "--theme", "Pollution"),
    ("coverage", "--theme", "Water & Waste", "--geography", "Indonesia"),
    ("evidence", "--theme", "Pollution", "--geography", "Vietnam"),
    ("brief", "--skill", "6", "--theme", "Pollution"),
    ("brief", "--skill", "9", "--theme", "Water & Waste"),
])
def test_every_skill_command_says_no_data(empty_path, args):
    result = run_cli(empty_path, *args)
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith(NO_DATA), result.stdout[:200]


def test_out_of_scope_still_refuses_on_an_empty_store(empty_path):
    """Scope is decided before the store is read, so emptiness must not change
    an OUT OF SCOPE into a NO DATA."""
    result = run_cli(empty_path, "coverage", "--theme", "semiconductor supply chains")
    assert result.stdout.startswith("OUT OF SCOPE")


def test_a_blocked_skill_still_refuses_on_an_empty_store(empty_path):
    result = run_cli(empty_path, "brief", "--skill", "5", "--theme", "Pollution")
    assert result.stdout.startswith("NOT IMPLEMENTED")
    assert "Stated quantity field on LAB" in result.stdout


def test_registry_and_triage_do_not_depend_on_the_store(empty_path):
    """Both read the registry, not the store, so they work before anything is filed."""
    assert "16 declared" in run_cli(empty_path, "registry").stdout
    triage = run_cli(empty_path, "triage", "where is the gap in air pollution?").stdout
    assert "ROUTING" in triage
    assert "Nothing has been run" in triage
