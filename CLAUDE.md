# KSP — Knowledge Synthesis Platform (POC)

Temasek Trust, Strategic Knowledge & Insights.

Finds where the Trust could deploy capital against a problem nobody else is
addressing. Surfaces **candidates worth a closer look**, with reasoning shown.
A person decides whether any is worth acting on.

**Use the `ksp` skill for every question against the stores.** It routes to one
of sixteen declared analyses and either runs it or refuses by name.

---

## The rule that governs everything

**Sixteen analyses are declared. Two are implemented. Fourteen must fail loudly.**

If the right analysis is not implemented, refuse, name the missing field, and
stop. Do not substitute a different analysis. Do not attempt it anyway.

An unimplemented skill that quietly answers with the wrong analysis is the
failure mode this whole system is designed against.

**Do not implement the fourteen.** They depend on fields that do not exist. An
agent told to attempt them will infer from free text and produce confident
output backed by nothing.

---

## Hard rules for any output

1. Every claim names its source.
2. Never merge LAB and LEAD into one voice — label each claim by store.
3. Never state absence as fact. "Nothing in the store" ≠ "nothing in the world".
4. Do not recommend. State the mismatch.
5. Never write "opportunity". Use *gap* or *candidate*.
6. No coverage threshold — produce the result and disclose the evidence base.
7. Pollution and Water & Waste only.
8. An empty store is not a finding. Return `NO DATA`, never silence.
9. Never substitute one skill for another. Refuse instead.

Full text and reasoning: `.claude/skills/ksp/references/hard-rules.md`.

---

## Layout

```
ksp/lab/sources.csv       one row per document; files live in lab/documents/
ksp/lead/actors.csv       actors, mandatory stable ID
ksp/lead/authorship.csv   one row per person per document
ksp/vocab/                controlled lists - no free text where a list exists
ksp/registry/skills.csv   the 16 declarations
tools/ksp.py              CLI - check, validate, registry, refuse, coverage, evidence
docs/                     the specifications; two are normative
tests/                    pytest, plus fixture stores
```

`python3 tools/ksp.py check` runs automatically at session start via
`.claude/settings.json`, and must run before any question is answered.

---

## Working on this repo

- **Python: standard library only.** The stores are CSV so they open in a
  spreadsheet; the tooling should run anywhere with no install step.
- **Tests:** `pytest -q` from the repo root. 88 tests, all fast.
- **After editing `ksp/registry/skills.csv`,** run
  `python3 tools/render_registry_doc.py` — a test fails otherwise.
- **The real store ships empty.** Test data lives in `tests/fixtures/`, never
  in `ksp/`. Fabricated rows in the real store would destroy the one thing this
  system is for.

### Accepted costs — do not "fix" these

Decided deliberately. Adding features to solve them makes the system worse.

| Behaviour | Why it stays |
|---|---|
| Problem/response classification varies between runs | No stored field. Disclosure is the mitigation. |
| Renaming a LAB file breaks references | No stable IDs in LAB. The integrity check and user habit are the mitigations. |
| Weak gaps are produced, not suppressed | Disclosure over threshold. |
| Nothing persists between runs | No LION store in the POC. |
| LEAD skews to researchers | Authors are researchers. Manual entry covers the rest. |
| Duplicate actors possible | Store is too small to justify matching logic. |
| 14 skills always refuse | Each refusal names the field that would unlock it, which turns user demand into a build roadmap. |
| The one implemented gap analysis is the weakest of the 16 | It is the only one the current fields support. Section 1 disclosure is the mitigation. |

### Out of scope — do not build

Scanners, sync, watchers, scheduled jobs. An agent that populates LEAD from
LAB. The LION store. Network analysis, centrality, clustering. Transaction
records, fund flows, additionality. Deduplication, fuzzy name matching,
confidence scoring. Multi-user features. A web front end.
