# Skill registry

**16 analyses declared. 3 implemented, 2 POC, 11 refuse by name.**

Numbering matches `docs/KSP_Analysis_Catalogue.md`.

<!-- Generated from ksp/registry/skills.csv - do not edit by hand. -->
<!-- Regenerate: python3 tools/render_registry_doc.py -->

| # | Skill | Status | Blocker |
|---|---|---|---|
| 1 | **Coverage check** | **IMPLEMENTED** | — |
| 2 | Adjacent actors | NOT IMPLEMENTED | *buildable, not yet built* |
| 3 | **Network position** | **IMPLEMENTED** | — |
| 4 | Policy-implementation gap | NOT IMPLEMENTED | Commitment identification on LAB |
| 5 | Scale mismatch | NOT IMPLEMENTED | Stated quantity field on LAB |
| 6 | **Proven but unscaled** | **POC** | Solution maturity field on LAB |
| 7 | Actor mix | NOT IMPLEMENTED | Actor type populated in LEAD |
| 8 | Venue shift | NOT IMPLEMENTED | Source type field plus 12+ months of collection |
| 9 | **Transferability** | **POC** | Enabling conditions list per case study |
| 10 | Sub-pillar co-occurrence | NOT IMPLEMENTED | *buildable, not yet built* |
| 11 | Problem rising, response static | NOT IMPLEMENTED | 12+ months of continuous collection |
| 12 | **Gap analysis** | **IMPLEMENTED** | — |
| 13 | Well resourced, not working | NOT IMPLEMENTED | Outcome data (does not exist anywhere) |
| 14 | Fund flows | NOT IMPLEMENTED | Transaction records + historical time series |
| 15 | Failure mapping | NOT IMPLEMENTED | Failure capture against LEAD actors |
| 16 | Crowded field | NOT IMPLEMENTED | Actor type populated in LEAD |

## POC skills

A **POC** skill is a prompt file in `.claude/skills/ksp/analyses/` and nothing
else — no stored field, no Python. The agent reads the documents and works out
the method itself, so its output is improvised rather than computed. The
`Blocker` column shows what the proper version would need.

**Adding one is dropping in a file** named `NN-slug.md` and setting the status
cell in `ksp/registry/skills.csv` to `POC`. No code change.

## Why the 11 refuse

Each refusal names the field that would unlock it. That turns user demand
into a build roadmap: what people keep asking for is what to build next.

**Skills 2 and 10 need no new field.** They are deferred by choice, not
blocked, and their refusal says so rather than naming a field.

## What each one would mislead about, if built

From the catalogue's *caveat for decision makers*. These inform future work;
they are not built now.

- **#1 Coverage check** — Tells you nothing about the world. A well-covered cell means we have read a lot, not that a field is crowded.
- **#2 Adjacent actors** — Adjacency is judged on tags, not on knowledge of the field. A starting point for a conversation, not a shortlist of the right people.
- **#3 Network position** — The graph maps what we have read, not the field, and it skews to authors. Centrality must not be quoted until author-count weighting is applied.
- **#4 Policy-implementation gap** — A commitment with no implementer in the store may still have implementers in the world. Public commitment removes the demand-side uncertainty, not the response-side one.
- **#5 Scale mismatch** — The two numbers usually come from different sources with different scopes. Report the mismatch, never the multiple.
- **#6 Proven but unscaled** — Success is self-reported. A pilot described as successful in its own write-up may not have been.
- **#7 Actor mix** — LEAD is filled largely by harvesting authors, and authors are overwhelmingly researchers. Every field will look research-heavy whether or not it is.
- **#8 Venue shift** — Venue shift only works if you are reading all the venues. Without even coverage across source types this measures reading habits rather than the world.
- **#9 Transferability** — Most transfer failures happen because a condition nobody wrote down was doing the work. The only analysis here where being wrong costs money directly rather than costing attention.
- **#10 Sub-pillar co-occurrence** — Most non-co-occurrences are simply unrelated things. Any two topics can be made to sound like a promising intersection after the fact.
- **#11 Problem rising, response static** — The corpus was assembled, not accumulated. An apparent rise may simply be recent reading. Treat any trend line as a description of collection activity.
- **#12 Gap analysis** — The output most likely to be a coverage artefact and the one people find most convincing. Never present it without the coverage figure from Coverage check alongside it.
- **#13 Well resourced, not working** — Reporting is systematically positive. A field can look like it is working while producing nothing, and the stores will never show the difference.
- **#14 Fund flows** — Rate-of-change analysis on incomplete data mostly measures changes in disclosure practice. The failure mode that looks most like a finding.
- **#15 Failure mapping** — What gets recorded as failure is a fraction of what failed. Absence of a recorded failure is not evidence that nothing was tried.
- **#16 Crowded field** — LEAD is not a funder database. Funders rarely author documents. Reading 'no funders present' as 'no funders active' would be a serious error.
