# KSP POC — Product Requirements

**For:** Claude Code build agent
**Owner:** Temasek Trust, Strategic Knowledge & Insights
**Date:** 14 August 2026

---

## 0. Read this first

**All sixteen analyses are declared. Two are implemented. Fourteen must fail loudly.**

The agent routes a user's question to the right skill. If that skill is not implemented, the agent **refuses, names the missing field, and stops.** It does not substitute a different analysis, and it does not attempt the analysis anyway.

This is the single most important behaviour in the build. An unimplemented skill that quietly answers with the wrong analysis is the failure mode this whole system is designed against.

**Do not implement the fourteen.** They depend on fields that do not exist. An agent told to attempt them will infer from free text and produce confident output backed by nothing.

Where a requirement below conflicts with the background documents, this PRD wins.

---

## 1. What is being built

Three things:

1. **Two data stores** — LEAD (actors) and LAB (documents), created empty, as local files (§4)
2. **A skill registry** — 16 named analyses, 2 implemented, 14 that refuse by name
3. **A routing agent** — takes a plain-language question, picks the right skill, runs it or refuses

The user fills the stores by hand. Nothing scans, syncs or self-populates.

### What this is for

Temasek Trust needs to find where it could deploy capital against a problem nobody else is addressing. The system surfaces **candidates worth a closer look**, with reasoning shown. A person decides whether any is worth acting on.

### Success criterion

Two things, both required:

1. Given a theme and geography, the agent returns a gap analysis where **every claim names its source** and the evidence base is stated up front.
2. Given a question it cannot answer, the agent **says so and names why** — rather than answering with a different analysis.

An answer that sounds right but cannot be traced to a source is a failure, not a partial success. So is a plausible answer produced by the wrong skill. Capital decisions rest on this.

---

## 2. Explicitly out of scope

Do not build these. Do not add "just in case" fields for them.

| Excluded | Reason |
|---|---|
| Any scanner, sync, watcher or scheduled job | Stores are filled by hand |
| An agent that populates LEAD from LAB | Deferred |
| The LION store — retaining gaps between runs | Deferred. Each run starts fresh. |
| Network analysis / centrality / clustering | Storage supports it later; do not build it |
| Transaction records, fund flows, additionality | Data does not exist |
| Implementing the other 14 analyses | Fields do not exist. They are **declared** in the registry (§6.2) so the agent can refuse them by name. |
| Deduplication, fuzzy name matching, confidence scoring | Store is small enough to eyeball |
| Multi-user features, permissions, contributor tracking | One user |
| A web front end | Runs in Claude Code |

---

## 3. Controlled vocabularies

**Build these before anything else.** Every filter and comparison depends on exact matching. Free text forces the agent to re-interpret values at query time, differently each run.

| List | Values |
|---|---|
| **Geography** | Two levels — country and region — plus Global. Multi-select. A document on Indonesia carries both `Indonesia` and `Southeast Asia`. Seed with the countries and regions in scope; do not allow free entry. |
| **Pillar (4P)** | Planet, People, Progress, Peace |
| **Sub-pillar** | Existing Temasek Trust list. Multi-select. |
| **Source type** | Research, Policy, Media, Industry, Internal |
| **Publisher status** | Named publisher, `Internal`, `Unknown` — never "Not Found" |
| **Actor form** | Person, Organisation |
| **Actor type** | Researcher, Implementer, Funder, Government, Advocate, Other |
| **Record type** | Document, Folder |

**On `Unknown` vs `Internal`:** an internal convening paper has no external publisher. Marking it "not found" makes *"there isn't one"* look identical to *"we didn't look."* This distinction recurs throughout the system and is not cosmetic.

---

## 4. Storage and file layout

**Everything is local.** No Notion, no database server, no API calls to fetch content. The agent reads files and tables directly from disk, the same way it reads any other file in the project.

*Rationale:* Claude Code opens local files natively. Anything hosted adds a fetch step before the agent can read a single document — build work that buys nothing at this scale. Local also means the whole store is portable, inspectable and easy to back up.

### Directory layout

```
ksp/
├── lab/
│   ├── documents/          # the actual PDFs, docx, etc.
│   │   ├── Air_Pollution_Convenings.pdf
│   │   └── Heat_PM25_Study.pdf
│   └── sources.csv         # one row per document
├── lead/
│   ├── actors.csv
│   └── authorship.csv
└── vocab/
    ├── geography.csv       # controlled lists (§3)
    ├── sub_pillar.csv
    └── actor_type.csv
```

### Table format

**CSV, UTF-8, header row.** Chosen over JSON because the user edits these by hand — CSV opens in any spreadsheet, JSON does not survive manual editing.

**Multi-select fields** (Geography, Pillar, Sub-pillar) are semicolon-separated in a single cell:

```
Geography
Indonesia;Southeast Asia
```

**Link fields** hold the target's ID:

| Field | Holds |
|---|---|
| `actors.affiliation_id` | An Actor ID — e.g. `12` |
| `authorship.actor_id` | An Actor ID |
| `authorship.source_file` | A LAB filename |
| `actors.source_files` | Semicolon-separated LAB filenames |

### How a LAB row finds its file

**By filename.** `sources.csv` has a `file` column holding the exact name of a file in `lab/documents/`.

**LAB has no stable ID** — a deliberate decision (§4.1). The row and the file are joined by a string match and nothing else. Rename the file on disk and the link breaks silently.

### Integrity check — REQUIRED

**On every agent start, verify that every `file` value in `sources.csv` exists in `lab/documents/`, and report any that do not.**

This is not optional. Without it, a renamed file produces a row the agent believes in but cannot open — and the failure surfaces as thin evidence rather than as an error. That is the silence problem again, in a new place.

Also report the reverse: files present in `documents/` with no row in `sources.csv`. An unfiled document is invisible to every query.

Output format:

```
INTEGRITY CHECK
  ✓ 47 rows matched to files
  ✗ 2 rows reference missing files:
      - Clean_Cooking_Review.pdf  (row: Clean Cooking Outcome Bond Review)
      - WHO_Guidelines_2024.pdf   (row: WHO Air Quality Guidelines)
  ⚠ 1 file present but unfiled:
      - Indus_Valley_Report.pdf
```

### Concurrency

None. Single user, single process. No locking, no conflict resolution, no write queue.

---

## 5. Data model

### 5.1 LAB — Sources

One row per document. The file itself is stored; metadata is attached.

| Field | Type | Required | Note |
|---|---|---|---|
| Name | Text | Yes | |
| file | Filename | Yes | Exact name of a file in `lab/documents/` — see §4 |
| Record type | Select | Yes | Folders must be excludable from queries |
| Description | Long text | Yes | |
| Quick insights | Long text | No | Free text. Not queryable as fields — accepted limitation. |
| Pillar | Multi-select | Yes | |
| Sub-pillar | Multi-select | No | |
| Geography | Multi-select | Yes | What the document is **about** |
| Source type | Select | Yes | |
| Publisher | Text or `Internal` / `Unknown` | Yes | |
| Year published | Number | No | |
| Total author count | Number | No | Recorded for later network weighting; not used now |
| Date added | Date | Auto | |

**No stable ID.** The `file` column is the key — a deliberate decision. Consequence: renaming a document on disk breaks the link silently. **Do not build rename handling or fuzzy matching.** The mitigations are the integrity check (§4) and a user habit: do not rename after filing.

**Folder rows must be excluded from all agent queries.** A folder row has every field blank, and blank rows read as real entries.

### 5.2 LEAD — Actors

| Field | Type | Required | Note |
|---|---|---|---|
| **ID** | Auto number | Yes | **Mandatory.** Affiliation links point at it. |
| Name | Text | Yes | |
| Form | Select | Yes | Person / Organisation |
| Actor type | Select | No | |
| Affiliation | **Link to Actors** | No | People only. A link, not text. |
| Sources | **Link to Sources** | No | Many |
| Geography | Multi-select | No | Inherited from source. Means what they **write about**, not where based. |
| Origin | Select | Yes | Manual / From LAB |
| Basis | Text | No | For manual rows with no source — e.g. *"LinkedIn, checked 14 Aug"* |
| Date added | Date | Auto | |

**Row creation rule:** reject a row with only a name. Require Name, Form, and either a Source link or a Basis. A row that is only a name looks like knowledge and is not.

### 5.3 LEAD — Authorship

One row per person per document.

| Field | Type | Note |
|---|---|---|
| Actor | Link to Actors | |
| Source | Link to Sources | |
| Position | Number | Order printed on the document |
| Role | Formula | Position 1 → `Primary`, else `Co` |

**Store position, derive role.** Changing the rule later means editing one formula, not re-entering rows.

**Do not create a person-to-person table.** Co-authorship is derived from shared Source links. Storing it separately duplicates the fact and goes stale when an author list is corrected.

**Where a document has no named author, the publisher becomes the Actor** with Position 1.

---

## 6. The agent

### 6.1 How it works

The user asks a question in plain language. The agent:

1. **Routes** the question to a skill in the registry (§6.2)
2. **Runs** it if implemented, or **refuses** if not
3. **States which skill it chose**, always — never routes silently

### Routing rules

**Ambiguous questions:** if more than one skill could fit, the agent says which it chose and why. If nothing fits well, it asks the user rather than defaulting to whichever skill happens to be implemented.

**No graceful degradation.** The tempting behaviour — *"scale mismatch isn't built, but here's a gap analysis instead"* — is forbidden. It is the core failure mode wearing a helpful face. Refuse, name the blocker, stop.

**A refusal must never look like a finding.** These three outcomes must be visibly, unmistakably different in the output:

| Outcome | Means |
|---|---|
| `NOT IMPLEMENTED` | The analysis does not exist yet. Names the missing field. |
| `NO DATA` | The skill ran; the store holds nothing for this query. |
| `RESULT` | The skill ran and found something. |

Never collapse these into silence or into each other.

### Refusal format

```
NOT IMPLEMENTED — Scale mismatch (#5)

This analysis compares a stated need against a stated response.
It needs: a Stated quantity field on LAB (one column).

Implemented skills that may be relevant: Coverage check (#1), Gap analysis (#12).
```

The refusal names the blocker because that turns every refusal into a signal about what to build next. Demand becomes observable instead of guessed.

---

### 6.2 Skill registry

Sixteen skills. **Two implemented.** Numbering matches `KSP_Analysis_Catalogue.md`.

| # | Skill | Status | Missing field |
|---|---|---|---|
| 1 | **Coverage check** — what the store holds | **IMPLEMENTED** | — |
| 2 | Adjacent actors — who to talk to | NOT IMPLEMENTED | None. Buildable; deferred. |
| 3 | Network position — who connects the field | NOT IMPLEMENTED | Code execution + author-count weighting |
| 4 | Policy–implementation gap | NOT IMPLEMENTED | Commitment identification on LAB |
| 5 | Scale mismatch | NOT IMPLEMENTED | Stated quantity field on LAB |
| 6 | Proven but unscaled | NOT IMPLEMENTED | Solution maturity field on LAB |
| 7 | Actor mix | NOT IMPLEMENTED | Actor type populated in LEAD |
| 8 | Venue shift | NOT IMPLEMENTED | Source type field **plus** 12+ months of collection |
| 9 | Transferability — worked in A, might work in B | NOT IMPLEMENTED | Enabling conditions list per case study |
| 10 | Sub-pillar co-occurrence | NOT IMPLEMENTED | None. Buildable; deferred. |
| 11 | Problem rising, response static | NOT IMPLEMENTED | 12+ months of continuous collection |
| 12 | **Gap analysis** — documented problem, few actors | **IMPLEMENTED** | — |
| 13 | Well resourced, not working | NOT IMPLEMENTED | Outcome data (does not exist anywhere) |
| 14 | Fund flows | NOT IMPLEMENTED | Transaction records + historical time series |
| 15 | Failure mapping | NOT IMPLEMENTED | Failure capture against LEAD actors |
| 16 | Crowded field | NOT IMPLEMENTED | Actor type populated in LEAD |

**Skills 2 and 10 need no new fields.** They are deferred by choice, not blocked. Their refusal message should say so — *"buildable, not yet built"* — rather than naming a field.

---

### 6.3 Skill #1 — Coverage check (IMPLEMENTED)

**Input:** theme, geography (either may be blank)
**Output:** document count, actor count, date range, breakdown by source type and sub-pillar

Counting and grouping only. No inference over content.

**Must be runnable on its own**, not solely as part of #12. The user checks coverage *before* asking a question that depends on it — otherwise thin evidence is discovered after a gap analysis has already convinced someone.

This is the only output that is certainly true, because it describes the store rather than the world.

---

### 6.4 Skill #12 — Gap analysis (IMPLEMENTED)

**Input:** theme, geography

**Process:**
1. Filter Sources by theme and geography. **Exclude folder rows.**
2. Read each document's Description and Quick insights. Classify as describing the **problem** (getting worse / larger than addressed) or the **response** (someone is acting). A document may be both.
3. Query Actors for the same theme and geography.
4. Compare the two sides.
5. Record what was searched for and not found.
6. Assemble the output below.

**Step 2 is inference at query time.** There is no stored problem/response field — a deliberate decision. Consequence: **classification is not stable between runs.** The same question may sort documents differently on different days. Do not add caching to hide this; disclosure is the mitigation.

**Known limitation, state it in the output.** This is the **lowest-trust** candidate type in the catalogue — the one most likely to reflect thin reading rather than a real absence, and the one users find most convincing. It is implemented first only because it is the only one the current fields support. Section 1 of the output is not optional for this reason.

#### Output structure

Six sections, this order, **every time, including when a section is empty.** An empty heading is informative; a missing heading is invisible.

| # | Section | Contents |
|---|---|---|
| 1 | **Evidence base** | Document count, actor count, date range, geography, source type breakdown |
| 2 | **Problem side** | Claims that the problem is growing. Each names its document. |
| 3 | **Response side** | What indicates someone is acting — **from LAB and LEAD, separately labelled** |
| 4 | **The gap** | The mismatch, in one sentence |
| 5 | **What is missing** | What was searched for and not found |
| 6 | **What would change this** | What evidence would overturn it, in one sentence |

**Section 1 goes first.** A caveat read after the argument is too late to change how the argument landed.

**Section 3 must query LEAD, not only LAB.** A named organisation working on a problem is stronger response-side evidence than a paper about the topic. This is the main reason LEAD exists.

**Section 4 is a quality gate.** If the mismatch cannot be stated in one sentence, the reasoning has not converged — say so rather than padding.

**Section 5 must distinguish two states:**

| Label | Meaning |
|---|---|
| `Coverage gap` | Not found in the stores. May exist in the world. |
| `Confirmed absent` | Searched and genuinely not there. Rare — requires the stores to cover this ground well. |

Default to `Coverage gap`. `Confirmed absent` is a strong claim and must be justified in the text.

---

### 6.5 Hard rules — all skills

1. **Every claim names its source.** No claim without one.
2. **Never merge LAB and LEAD into one voice.** Each claim is labelled by store.
3. **Never state absence as fact.** "Nothing in the store" and "nothing in the world" are different claims.
4. **Do not recommend.** Output states a mismatch. It does not say what to do, whether to fund, or what instrument fits.
5. **Do not use the word "opportunity" in output.** Use *gap* or *candidate*.
6. **No coverage threshold.** Never withhold a result for thin evidence — produce it and disclose the evidence base.
7. **Refuse cleanly outside the two themes.** Pollution and Water only.
8. **Empty store is not a finding.** Return `NO DATA` with an explanation, never silence.
9. **Never substitute one skill for another.** Refuse instead.

---

### 6.6 Runtime

Claude Code. Local. Single user. No web interface, no messaging integration, no scheduled execution.

---

## 7. Build order

| # | Deliverable | Done when |
|---|---|---|
| 1 | Controlled vocabularies | All lists defined, no free-text entry where a list exists |
| 2 | Directory layout + LAB `sources.csv` | A document can be filed with all required fields |
| 2b | **Integrity check** | Reports missing files and unfiled files on start |
| 3 | LEAD Actors + Authorship tables | An actor can be created manually and from a document |
| 4 | **Skill registry + routing + refusals** | All 16 declared; the 14 return `NOT IMPLEMENTED` with the correct missing field |
| 5 | Skill #1 — coverage check | Returns correct counts on a hand-checked sample |
| 6 | Skill #12 — gap analysis | Returns all six sections on a populated theme |
| 7 | Empty-store and out-of-scope handling | Return `NO DATA` and a clean refusal, not silence |

**Build the registry before the skills.** If routing and refusal come last, the natural intermediate state is an agent that answers everything with the one analysis it has — which is exactly the behaviour this design exists to prevent.

**Test with an empty store first.** Most failure modes appear as silence, and silence is the specific thing this system must not produce.

### Routing test cases

| Ask | Expect |
|---|---|
| *"What do we hold on water in Indonesia?"* | Skill #1 runs |
| *"Where's the gap in air pollution in Vietnam?"* | Skill #12 runs |
| *"Is the funding response the right size for clean cooking?"* | `NOT IMPLEMENTED` #5, names Stated quantity field |
| *"Which solutions work but haven't scaled?"* | `NOT IMPLEMENTED` #6, names Solution maturity field |
| *"Who should I talk to about air quality in Jakarta?"* | `NOT IMPLEMENTED` #2, says buildable not blocked |
| *"Tell me about semiconductor supply chains"* | Out of scope refusal |
| *(any query on an empty theme)* | `NO DATA`, not silence, not a fabricated gap |
| *(a row whose file was renamed on disk)* | Integrity check reports it at start — never surfaces as thin evidence |

---

## 8. Accepted costs — do not "fix" these

The build agent should not add features to solve these. They were decided deliberately.

| Behaviour | Why it stays |
|---|---|
| Problem/response classification varies between runs | No stored field. Disclosure is the mitigation. |
| Renaming a LAB file breaks references | No stable IDs in LAB. User habit is the mitigation. |
| Weak gaps are produced, not suppressed | Disclosure over threshold. |
| Nothing persists between runs | No LION store in POC. |
| LEAD skews to researchers | Authors are researchers. Manual entry covers the rest. |
| Duplicate actors possible | Store too small to justify matching logic. |
| 14 skills always refuse | Deliberate. Each refusal names the field that would unlock it, which turns user demand into a build roadmap. |
| The one implemented analysis is the weakest of the 16 | It is the only one the current fields support. Section 1 disclosure is the mitigation. |

---

## 9. Open items — confirm before building

| # | Item |
|---|---|
| 1 | One gap per request, or several to compare? |
| 2 | Does Section 4 carry a confidence marker, or does Section 1 do that work? |
| 3 | Seed values for the Geography list — which countries and regions |
| 4 | Existing sub-pillar list — needs supplying |
| 5 | Should skills #2 and #10 be implemented too? Neither needs a new field — both are deferred by choice, not blocked. |

---

## 10. Accompanying documents

| Document | Status |
|---|---|
| `KSP_POC_Scope.md` | Background. Reasoning behind each decision. |
| `LION_Output_Template.md` | **Normative** for §6.2. Contains a worked example — the example is fabricated and illustrates shape only. |
| `KSP_Analysis_Catalogue.md` | **Normative for the skill registry (§6.2)** — skill numbering, names and missing fields come from here. **Do not implement beyond #1 and #12.** Each entry carries a *caveat for decision makers* explaining how that analysis can mislead; these should inform refusal messages and future work, not be built now. |
