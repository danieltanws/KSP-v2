#!/usr/bin/env python3
"""Regenerate .claude/skills/ksp/references/registry.md from skills.csv.

Run after editing the registry. A test fails if the two fall out of step.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kspcore.registry import Registry
from kspcore.store import repo_root

TARGET = repo_root() / ".claude" / "skills" / "ksp" / "references" / "registry.md"


def main() -> int:
    TARGET.write_text(Registry.load().render_markdown(), encoding="utf-8")
    print(f"wrote {TARGET.relative_to(repo_root())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
