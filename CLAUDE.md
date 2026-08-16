# KSP — Knowledge Synthesis Platform (POC)

Temasek Trust, Strategic Knowledge & Insights.

Finds where the Trust could deploy capital against a problem nobody else is
addressing. Surfaces **candidates worth a closer look**, with reasoning shown.
A person decides whether any is worth acting on.

**Use the `ksp` skill for every question against the stores.** It routes to one
of sixteen declared analyses and either runs it or refuses by name.

---

## The rule that governs everything

**Sixteen analyses are declared. Two are implemented, two are POC, twelve must
fail loudly.**

If the right analysis is unavailable, refuse, name the missing field, and stop.
Do not substitute a different analysis. Do not attempt it anyway.

An unavailable skill that quietly answers with the wrong analysis is the
failure mode this whole system is designed against.

**Do not implement the twelve.** They depend on fields that do not exist.

### The two POC skills

**#6 Proven but unscaled** and **#9 Transferability** are placeholders: a
prompt file in `.claude/skills/ksp/analyses/` and nothing else. No stored
field, no Python. The agent reads the documents and works out the method
itself, so the output is **improvised, not computed**.

This is a knowing departure from the PRD, which warns that an agent told to
attempt these will *"infer from free text and produce confident output backed
by nothing."* The POC exists to prove the architecture, not the analysis.

Their output carries the ordinary `RESULT` label — an owner decision. The
evidence base is therefore the only place a reader can tell an improvised
answer from a computed one, which makes its `Not stored` line load-bearing.
**Never drop it, and never let it become boilerplate on skills that do compute.**

### Adding or replacing a POC skill

- **To add one:** write `.claude/skills/ksp/analyses/NN-slug.md`, set that
  skill's `status` to `POC` in `ksp/registry/skills.csv`, regenerate the doc.
  No code change — this is the modularity the POC is proving.
- **To make it real:** add the field it names, write the analysis in
  `tools/kspcore/`, flip the status to `IMPLEMENTED`, delete the prompt file.

Leave `missing_field` populated on a POC skill. It is what the evidence base
discloses.

### Triage

`ksp.py triage "<question>"` shortlists analyses and shows whether each is
ready. It runs nothing, and the agent shows the shortlist and waits.

**The shortlist is not a fallback chain.** If the closest match is blocked, the
answer is that analysis and its blocker — never the next one down.

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
.claude/skills/ksp/analyses/  POC skill prompts - one file per POC skill
tools/ksp.py              CLI - check, validate, registry, refuse, triage,
                          coverage, evidence, brief
docs/                     the specifications; two are normative.
                          INGEST_SPEC.md is the handover doc for bulk loading
tests/                    pytest, plus fixture stores
```

`python3 tools/ksp.py check` runs automatically at session start via
`.claude/settings.json`, and must run before any question is answered.

---

## Working on this repo

- **Python: standard library only.** The stores are CSV so they open in a
  spreadsheet; the tooling should run anywhere with no install step.
- **Tests:** `pytest -q` from the repo root. 161 tests, all fast.
- **After editing `ksp/registry/skills.csv`,** run
  `python3 tools/render_registry_doc.py` — a test fails otherwise.
- **After editing anything in `ksp/vocab/`,** run
  `python3 tools/render_vocab_doc.py` — a test fails otherwise. The generated
  `docs/CONTROLLED_VALUES.md` is handed to external ingest agents, so it must
  never disagree with the validator.
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
| 12 skills always refuse | Each refusal names the field that would unlock it, which turns user demand into a build roadmap. |
| A POC skill's method varies run to run | It has no stored field to compute from. That is what POC means here. |
| A POC answer looks like a computed one | Owner decision. The evidence base carries the distinction. |
| The one implemented gap analysis is the weakest of the 16 | It is the only one the current fields support. Section 1 disclosure is the mitigation. |
| Triage ranks on keyword cues, not meaning | It is a shortlist, not a decision. The agent routes; cues only surface candidates. |

### Out of scope — do not build

Scanners, sync, watchers, scheduled jobs. An agent that populates LEAD from
LAB. The LION store. Network analysis, centrality, clustering. Transaction
records, fund flows, additionality. Deduplication, fuzzy name matching,
confidence scoring. Multi-user features. A web front end.
