#!/usr/bin/env python3
"""Regenerate outputs/CONTROLLED_VALUES.md from ksp/vocab/.

The ingest spec is handed to people and agents outside this repo, so the list
of allowed values has to travel with it as a readable document. Generating it
means the handed-over copy cannot quietly disagree with what the validator
enforces. A test fails if the two fall out of step.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from kspcore.store import read_csv, repo_root

VOCAB = repo_root() / "ksp" / "vocab"
TARGET = repo_root() / "outputs" / "CONTROLLED_VALUES.md"

SIMPLE = [
    ("source_type.csv", "Source type", "`source_type` on sources.csv. Single value."),
    ("record_type.csv", "Record type", "`record_type` on sources.csv. Single value."),
    ("actor_form.csv", "Actor form", "`form` on actors.csv. Single value."),
    ("actor_type.csv", "Actor type", "`actor_type` on actors.csv. Single value, optional."),
    ("origin.csv", "Origin", "`origin` on actors.csv. Single value."),
]


def render() -> str:
    out = [
        "# Controlled values",
        "",
        "Every value permitted in a controlled field. Nothing else is accepted —",
        "not a synonym, not a variant, not a close match.",
        "",
        "Companion to `INGEST_SPEC.md`. Hand both over together.",
        "",
        "<!-- Generated from ksp/vocab/ - do not edit by hand. -->",
        "<!-- Regenerate: python3 tools/render_vocab_doc.py -->",
        "",
        "---",
        "",
        "## Themes in scope",
        "",
        "The system answers questions on these two only. Everything else is refused",
        "as out of scope — which is not a reason to skip tagging it correctly.",
        "",
        "| Theme | Pillar | P-1 cluster | P-2 focus area |",
        "|---|---|---|---|",
    ]
    for row in read_csv(VOCAB / "theme.csv"):
        out.append(
            f"| **{row['theme']}** | {row['pillar']} | {row['p1_cluster']} | {row['p2_focus_area']} |"
        )

    out += [
        "",
        "---",
        "",
        "## The 4P taxonomy — three columns",
        "",
        "Three levels, **one column each**, on both `sources.csv` and `actors.csv`:",
        "",
        "| Column | Example |",
        "|---|---|",
        "| `pillar` | `PLANET` |",
        "| `p1_cluster` | `Urban Liveability` |",
        "| `p2_focus_area` | `Pollution` |",
        "",
        "Each P-2 belongs to exactly one P-1, and each P-1 to exactly one pillar, so the",
        "chain must be consistent. Writing a focus area under the wrong cluster is an",
        "error, not a style lapse. Multi-select still applies within a column:",
        "`p2_focus_area = Urban Heat;Pollution`.",
        "",
    ]
    sub = read_csv(VOCAB / "taxonomy.csv")
    for pillar in [r["value"] for r in sub if r["level"] == "P"]:
        out.append(f"### {pillar}")
        out.append("")
        for cluster in [r for r in sub if r["pillar"] == pillar and r["level"] == "P-1"]:
            focus = [
                r["value"]
                for r in sub
                if r["level"] == "P-2" and r["parent_p1"] == cluster["value"]
            ]
            out.append(f"**{cluster['value']}** — {' · '.join(focus)}")
            out.append("")
            if cluster["impact_statement"]:
                out.append(f"> {cluster['impact_statement']}")
                out.append("")

    out += [
        "---",
        "",
        "## Geography",
        "",
        "Two levels plus Global. **Tag the country and its region together**, in one",
        "cell: `Indonesia;Southeast Asia`. A document about a whole region carries",
        "just the region. A worldwide document carries `Global` alone.",
        "",
    ]
    geo = read_csv(VOCAB / "geography.csv")
    out.append("**Global** — for documents with no specific geography.")
    out.append("")
    for region in [r["value"] for r in geo if r["level"] == "Region"]:
        countries = [r["value"] for r in geo if r.get("parent_region") == region]
        out.append(f"**{region}**" + (f" — {', '.join(countries)}" if countries else " — (no countries listed)"))
        out.append("")

    out += ["---", "", "## The remaining lists", ""]
    for filename, title, note in SIMPLE:
        values = [r["value"] for r in read_csv(VOCAB / filename)]
        out += [f"### {title}", "", note, "", ", ".join(f"`{v}`" for v in values), ""]

    out += [
        "### Publisher",
        "",
        "`publisher` on sources.csv. A publisher name, **or** one of these two:",
        "",
    ]
    for row in read_csv(VOCAB / "publisher_status.csv"):
        out.append(f"- `{row['value']}` — {row['meaning']}")
    out += [
        "",
        "`Not Found` is rejected. It makes *\"there isn't one\"* look identical to",
        "*\"we didn't look\"*, and those are different facts.",
        "",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    TARGET.write_text(render(), encoding="utf-8")
    print(f"wrote {TARGET.relative_to(repo_root())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
