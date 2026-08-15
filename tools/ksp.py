#!/usr/bin/env python3
"""KSP command line.

    ksp.py check                       integrity check (run this first, always)
    ksp.py validate                    stores against the controlled vocabularies
    ksp.py registry                    the 16 declared skills
    ksp.py refuse N                    the NOT IMPLEMENTED block for skill N
    ksp.py coverage --theme T          skill #1
    ksp.py evidence  --theme T         skill #12 inputs
    ksp.py themes                      the in-scope themes

Every command takes ``--store`` to point at a different ksp/ directory, which
is how the tests run against fixtures.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kspcore import coverage, evidence, integrity
from kspcore.registry import Registry, render_out_of_scope
from kspcore.store import Store, repo_root
from kspcore.vocab import ERROR, Vocab, validate


def _load(args) -> tuple[Store, Vocab]:
    base = Path(args.store) if args.store else repo_root() / "ksp"
    # Vocabularies are global, not per-store, so a fixture store without its
    # own vocab/ directory validates against the project's real lists.
    vocab_dir = base / "vocab"
    if not vocab_dir.is_dir():
        vocab_dir = repo_root() / "ksp" / "vocab"
    return Store.load(base), Vocab.load(vocab_dir)


def _resolve_theme(vocab: Vocab, text: str | None, question: str = ""):
    """Return (theme_row, refusal_text). Exactly one is meaningful."""
    if not text:
        return None, None
    theme = vocab.resolve_theme(text)
    if theme is None:
        return None, render_out_of_scope(question or text, vocab.theme_names())
    return theme, None


def cmd_check(args) -> int:
    store, _ = _load(args)
    report = integrity.check(store)
    print(report.render())
    return 0 if report.ok else 1


def cmd_validate(args) -> int:
    store, vocab = _load(args)
    problems = validate(store, vocab)
    if not problems:
        print("VALIDATION\n  ✓ every row conforms to the controlled vocabularies")
        return 0
    errors = [p for p in problems if p.level == ERROR]
    warnings = [p for p in problems if p.level != ERROR]
    print("VALIDATION")
    print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")
    for problem in errors + warnings:
        print(problem)
    return 1 if errors else 0


def cmd_registry(args) -> int:
    print(Registry.load().render_list())
    return 0


def cmd_refuse(args) -> int:
    registry = Registry.load()
    try:
        print(registry.render_refusal(args.number))
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_coverage(args) -> int:
    store, vocab = _load(args)
    theme, refusal = _resolve_theme(vocab, args.theme)
    if refusal:
        print(refusal)
        return 1
    print(coverage.run(store, vocab, theme, args.geography))
    return 0


def cmd_evidence(args) -> int:
    store, vocab = _load(args)
    theme, refusal = _resolve_theme(vocab, args.theme)
    if refusal:
        print(refusal)
        return 1
    if theme is None:
        print("error: --theme is required for gap analysis", file=sys.stderr)
        return 2
    print(evidence.run(store, vocab, theme, args.geography))
    return 0


def cmd_themes(args) -> int:
    _, vocab = _load(args)
    print("THEMES IN SCOPE")
    for name, row in vocab.theme.items():
        print(f"  {name}  —  {row['pillar']} › {row['p1_cluster']} › {row['p2_focus_area']}")
    print("\nAnything else is out of scope and must be refused, not approximated.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ksp.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--store", help="path to a ksp/ directory (default: this repo's)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="integrity check").set_defaults(func=cmd_check)
    sub.add_parser("validate", help="validate stores against vocabularies").set_defaults(func=cmd_validate)
    sub.add_parser("registry", help="list the 16 declared skills").set_defaults(func=cmd_registry)
    sub.add_parser("themes", help="list in-scope themes").set_defaults(func=cmd_themes)

    refuse = sub.add_parser("refuse", help="render a NOT IMPLEMENTED block")
    refuse.add_argument("number", type=int)
    refuse.set_defaults(func=cmd_refuse)

    for name, func, helptext in (
        ("coverage", cmd_coverage, "skill #1 - what the store holds"),
        ("evidence", cmd_evidence, "skill #12 - gap analysis inputs"),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--theme")
        p.add_argument("--geography")
        p.set_defaults(func=func)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
