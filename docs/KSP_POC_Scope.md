# Knowledge Synthesis Platform — POC Scope

**Owner:** Temasek Trust — Strategic Knowledge & Insights
**Status:** Decisions recorded 14 August 2026
**Themes in scope:** Pollution, Water

---

## 1. Context and purpose

### Who this is for

Temasek Trust, to find where the Trust could deploy capital against a problem that is not already being addressed by someone else. Users are the Trust's programme, investment, partnership and strategy teams.

### What the system produces

**Candidates worth a closer look.** The agent finds an **asymmetry**: a problem that is documented and growing, set against a response that is thin or absent. It surfaces that, with its reasoning shown. Whether anything is worth acting on is a human call.

The document uses *gap* throughout for what the agent produces. Nothing hangs on the word — it is a label for "the agent found a mismatch here," not a formal category.

### The one distinction that does matter

Little response-side evidence has three possible causes, and they look identical in the output.

| | What it is | Worth pursuing? |
|---|---|---|
| 1 | **Nobody is working on it** | Possibly |
| 2 | **Someone is, but we have not read it** | No — this is our reading list, not the world |
| 3 | **Nobody is working on it for a reason** — no viable intervention, no counterparty, someone tried and failed | No — real absence, still not actionable |

**At current store size, case 2 will be the most common by a wide margin.**

Section 5 of the output template — *what is missing* — is the agent's attempt to flag case 2. It cannot catch it fully, because it only sees what has been collected. A person who knows the field is the actual filter.

Case 3 has no defence at all in the current design: a failed programme rarely gets written up, so "nobody tried" and "someone tried and it failed" produce the same silence. Capturing failures against actors in LEAD is the only thing that would distinguish them.

### How to frame this to stakeholders

**Say:** the system surfaces candidates, and the first job is filtering out the ones that reflect our reading rather than the world.

**Avoid:** anything implying most candidates convert. When four out of five turn out to be coverage artefacts, the system looks broken. Under the framing above, a low conversion rate is the system working correctly.

Internally the word *opportunity* is fine and everyone will understand it. In a deck, "the system identified twelve opportunities" will be read as twelve fundable things, and the meeting goes on that instead of the work.

### What comes later

Two questions the POC deliberately does not answer:

1. **Additionality** — would commercial or state capital close this anyway?
2. **Actionability** — is there a workable instrument and a real counterparty?

Neither can be attempted now. The stores hold nothing about instruments, counterparties or capital flows, so any attempt would be inference without evidence. Both become possible once the Transactions table (§6) is populated.

### What the POC proves

One thing: that a stored, well-tagged body of evidence can answer real questions with sources attached, and can identify gaps with the reasoning shown — instead of an analyst team doing it by hand.

**Defensible is the operative word.** An answer that sounds right but cannot be traced to a source is worse than no answer, because capital allocation decisions rest on it.

### What it is not

- Not a live scanning system
- Not a forecasting engine
- Not an investment recommendation — it surfaces candidates, it does not decide what to fund
- Not a test of additionality or actionability — those need evidence the stores do not yet hold
- Not a replacement for judgment

Those are later phases, or not the system's job at all.

---

## 2. Architecture

```
USER
  ↓
SINGLE QUERY AGENT  ── answers per store, labels which store each claim came from
  ↓
LEAD          LAB           LION
(actors)      (evidence)    (gaps)
```

### Changes from the earlier design

| Was | Now | Why |
|---|---|---|
| Three scanner agents keeping stores current | No scanners | POC only. Stores are loaded and curated by hand. |
| One agent per store + human routing | One agent across all three | Simpler to build and demo. |
| Stores fully disconnected | Agent may read all three | See guard below. |
| "The ecosystem keeps itself current" | Stores are static between manual updates | The old claim is false without scanners and must not appear in any deck. |

### The guard on the single agent

The original rule was that a human, not the machine, combines material across stores — because blended answers destroy attribution.

A single agent puts that combining back inside the machine. This is a deliberate POC trade-off. The condition is:

> The agent answers **per store**, labelling which store each claim came from. It does not merge everything into one undifferentiated voice.

Query order: **LEAD and LAB first, LION last.** A LION entry is only meaningful alongside the actors and evidence that produced it.

---

## 3. The three stores

### LEAD — Leaders, Experts, Advocates and Doers
Actors and experts relevant to the themes. Mostly tells you **who is already doing something** about a problem. **Structured** — rows of fields, not documents. See §5.

### LAB — Landscapes, Assessments and Beyond
Signals, developments, trends, case studies — everything that happens, as opposed to everyone it happens to. The raw evidence base, carrying **both sides**: how big a problem is getting, and what is already being done about it. **Unstructured** — files with labels attached. See §4.

*Transactions belong on this side conceptually but need their own structured table. Specified in §6, not built for the POC.*

### LION — Levers, Innovations, Opportunities and Nexus
White spaces and gaps. **Not built for this POC.** LION defines the *shape of the agent's output*, not a store. See §7.

### Why LAB and LEAD are shaped differently

| | What the store holds | What you do with it |
|---|---|---|
| **LAB** | A file, with labels attached | Read it |
| **LEAD** | Rows of fields — no file underneath | Compute over it |

The difference follows the job. LAB answers *"what do we know about air pollution"* — the agent finds the right documents and a person reads them. LEAD answers *"who works on this, and who do they work with"* — counting, grouping and following links, which only works if the facts sit in fields.

This is a deliberate asymmetry, not an inconsistency to tidy up. It is also why a manual LEAD entry needs no document at all: in LAB the document is the thing, in LEAD the row is the thing.

---

## 4. LAB: how documents are stored

**Decision: store the document, attach metadata to it.** No separate agent-written signal card for the POC.

Cheaper to maintain, and upgradeable to claim-level cards later without rebuilding the store.

### What this trades away

1. **The "Quick Insights" field is a signal card by another name.** It holds claims, but as free text. Nothing inside it is queryable as a field — no isolated numbers, no confidence, no direction. The agent cannot compare across documents on anything living in that column.

2. **Attribution is document-level.** The agent can say *"this came from AI SMR Learnings.pdf"* but not which page. Fine for a demo. Not sufficient for a funding decision without a human opening the file.

### Field list

| Field | Status |
|---|---|
| Name | Existing |
| Description | Existing |
| Quick Insights | Existing |
| Pillar (4P) — multi-select | Existing |
| Sub-pillar — multi-select | Existing |
| Publisher | Existing — needs the fix below |
| Year Published | Existing |
| Modified By | Existing |
| **Geography — multi-select** | **DECIDED: add** |
| Problem / Response direction | **DECIDED: no field — agent infers at query time** |
| Stable ID | **DECIDED: no — file names are the key.** Note: LEAD differs, see §5 |
| Record type (Document / Folder) | Open — see §8 |

### Geography — build note

Needs at least two levels. A document can be about Indonesia, about Southeast Asia, or global. If only country names are allowed, regional and global documents get left blank — and blank reads as *"not relevant anywhere,"* the opposite of what a global report means.

**Fixed list, not free text.** An agent filling this later will write "SE Asia," "Southeast Asia" and "ASEAN" as three values, and grouping silently fragments. Fix the vocabulary now, while it costs nothing.

Multi-select, so one document can carry both *Indonesia* and *Southeast Asia*.

### Two defects in the current sheet

- **`Publisher: Not Found`** on an internal convening document. It has no external publisher — but "Not Found" makes *"there isn't one"* look identical to *"we didn't look."* Split into **Internal** and **Unknown**.
- **A folder row with all fields empty** sits alongside document rows. The agent will read blank rows as real entries. Exclude folders from the queryable set, or add a record type field.

---

## 5. LEAD: how actors are stored

**Decision: three tables — Sources, Actors, Authorship.** Structured throughout.

### Extraction scope

**Authors only.** When a document is added, what gets pulled out is: author names, their organisations, and the geography the document concerns.

Authorship is printed on the document — a fact, not a judgment. This keeps extraction clean and avoids the alternative failure: harvesting every named entity produces 300 rows of noise within a month and buries the useful 30.

**Content claims do not go in LEAD.** New developments, innovations, failures and policy directions belong to LAB. The exception is when a claim is attached to a named actor — *"this organisation's programme failed"* is actor track record and belongs in LEAD. *"Programme failures are common in this sector"* is a signal and belongs in LAB.

### Table 1 — Sources

As specified in §4, plus geography (what the document concerns).

### Table 2 — Actors

| Field | Type | Note |
|---|---|---|
| **ID** | Auto number | **Required.** See below. |
| Name | Text | |
| Form | Person / Organisation | |
| Affiliation | **Link to another Actor row** | People only. A link, not text — this is what makes it traversable. |
| Geography | Multi-select, fixed list | Inherited from the source |
| Origin | Manual / From LAB | Tells you later whether harvesting earns its keep |
| Basis | Text | For manual entries with no source — e.g. *"LinkedIn profile, checked 14 Aug"* |
| Date added | Date | |

**Stable IDs are required here, unlike LAB.** Two reasons: the Affiliation link needs something durable to point at, and manual entry plus LAB harvest will both produce "World Bank" with different spelling. An auto-number column is the entire cost. This deliberately differs from the LAB decision — different job, different requirement.

### Table 3 — Authorship

One row per person per document. Four columns.

| Actor | Source | Position | Role |
|---|---|---|---|
| Jane Smith | Heat–PM2.5 study | 1 | *(formula)* |
| Wei Chen | Heat–PM2.5 study | 2 | *(formula)* |
| Jane Smith | Cookstove review | 3 | *(formula)* |
| World Bank | Outcome bond brief | 1 | *(formula)* |

**Why this table exists.** Authorship role cannot live on the actor or on the document — the same person is first author on one paper and fourth on another. The role belongs to the pairing.

**Store position, derive role.** Position is free (documents print authors in order) and strictly more informative. `Role` is a formula: position 1 → Primary, otherwise Co. A later change to the rule means editing one formula, not re-entering every row.

**Do not store person-to-person edges.** Co-authorship falls out of shared sources — two actors on the same document are co-authors. Storing it separately duplicates the fact and the copy goes stale the moment an author list is corrected.

### What computes from this

| Question | How |
|---|---|
| Main authors A is connected to | Documents A appears on → who holds position 1 on those → minus A |
| A's co-authors | Same document set, positions 2+ |
| What A is main or co author of | Count A's own rows, split by role |

### Manual entry

Same table, same fields. `Origin` = Manual, `Sources` blank, `Basis` filled in.

Three routes in, all landing in the same place: actors already known (the 39 existing cards), actors surfaced by the agent while answering something, and actors named by a colleague.

**Minimum required to create a row:** Name, Form, and either a source or a basis. A row that is only a name looks like knowledge and is not — six months on nobody can reconstruct why it is there. Everything else can be filled in later.

### No named author

Institutional reports usually have no byline — the European Commission page in the current sample has none. **Rule: where there is no named author, the publisher becomes the actor.** Without this, those documents yield nothing.

### Four warnings

1. **LEAD will skew heavily to Experts.** Authors are researchers. The actors who *do* things — a bank issuing a bond, a coalition running a programme — appear in documents as subjects, not authors. Treat this as a division of labour: **harvest gives you Experts, manual entry gives you everyone else.** Do not later read a thin Doer count as a finding about the field.

2. **Author position is a reliable fact but an unreliable measure of importance.** Conventions differ across the sources in scope: in much of the natural sciences the *last* author is the senior figure; in economics author order is often alphabetical and carries no meaning; in institutional reports it is frequently arbitrary. Safe to store, risky as a proxy for influence.

3. **One large report will distort the whole network.** A 40-author institutional report creates 780 co-authorship pairs from a single load, making everyone in it look exceptionally well connected — including people who wrote a paragraph. *Fix:* record total author count on the source, and either exclude documents above a threshold from network measures or weight their edges down. **Decide the threshold before looking at the graph,** not after — otherwise it is tuned until it shows what was expected.

4. **Geography here means subject, not base.** Inherited from the document, it says what an actor *writes about*. The old LEAD guide separated institutional base from operating footprint deliberately. This gives a rough footprint only; base stays manual.

### Storage vs computation

Notion stores this fine but will not compute it. Real network measures — bridges, centrality, clusters — need an export to Python or Gephi. Not a POC blocker: the storage is what makes it possible later. Do not expect the graph to appear inside Notion.

### Deferred from the old LEAD guide

The 100-point scoring framework, engagement status, the three evidence types, and the general relationships table (funder→grantee, board membership, coalitions). All heavier than a POC needs. The Authorship table covers the only edges that come free.

---

## 6. Transactions — specified now, built later

**NOT IN THE POC.** Specified here so the LEAD schema is built with it in mind.

### Why it exists

LEAD is *who*. LAB is *what happens*. A transaction is something that happened, so it sits on the LAB side conceptually — but LAB as a store holds documents, and a transaction is not a document.

This is the same argument already accepted for LEAD. There are documents *about* actors, but each actor gets a structured row because the job is to compute over actors, not read about them. Transactions are identical: answering *"is commercial capital already moving here"* means summing and grouping deals. Free text in a Description field cannot be summed.

So: same conceptual side as LAB, its own table. Populated by extraction from documents — exactly as Authorship already is. Not a fourth store; the LAB side gaining structure where structure is needed.

### What it unlocks

**Additionality** — *would commercial or state capital close this gap anyway?* Answering it means seeing whether capital is already moving in adjacent areas. That is a pattern across many transactions. Documents that happen to mention funding give anecdotes, not coverage.

Without this table, additionality cannot be tested. See §1.

### Fields

| Field | Type | Note |
|---|---|---|
| ID | Auto number | |
| Funder | **Link to Actor row** | Uses LEAD actor IDs |
| Recipient | **Link to Actor row** | Uses LEAD actor IDs |
| Instrument type | Select | Grant, concessional debt, guarantee, first-loss, equity, outcome-based, other |
| Amount | Number | |
| Currency | Select | |
| Date | Date | |
| Geography | Multi-select, fixed list | Shared vocabulary with LAB and LEAD |
| Source | **Link to Source row** | Where this was extracted from |

### The dependency to lock in now

A transaction points at a funder and a recipient, both of which are LEAD rows. **This is a further reason the LEAD stable IDs in §5 are required, not optional.** Building LEAD without them would mean rebuilding it before transactions can be added.

Nothing else needs to change now. The table stays unbuilt.

### Why not in the POC

Not a schema problem — a sourcing problem.

Every other part of the POC is filled from documents already held. Transaction data is not: deal terms are largely unpublished, scattered across announcements, or behind paid databases. Building the table now means maintaining an empty one while also standing up two stores and an agent.

**This is a resourcing conversation, not a build one.** Worth having with C3H before the POC rather than after — their capital-structure questions are blocked by evidence nobody has collected, not by system design.

---

## 7. LION: the gap-finding agent

**DECIDED: do not build the LION store for this POC.** The deliverable is an agent that reads LAB and LEAD and produces a gap with its reasoning attached.

The store can wait. You cannot design it until you know what the output looks like, and you cannot know that until you have seen a few. LION is the shape of the output, not a database to populate.

### What the agent produces

A **gap** — the problem growing while the response stays flat or absent. A candidate worth a closer look, with the reasoning shown. See §1.

### Output structure

Fixed, six sections, same order every time, **even when a section is empty**. Free-form reasoning varies in shape each run, which makes two gaps impossible to compare and a weak one impossible to spot. An empty heading is informative; a missing heading is invisible.

| # | Section | Carries |
|---|---|---|
| 1 | Evidence base | Document count, actor count, date range, geography — **first, not last** |
| 2 | Problem side | What says this is getting worse, every claim naming its document |
| 3 | Response side | What says someone is already on it — **from LAB and LEAD both** |
| 4 | The gap | The asymmetry, in one sentence |
| 5 | What is missing | What was looked for and not found, separating coverage gap from confirmed absence |
| 6 | What would change this | What evidence would overturn the call, in one sentence |

Full specification with worked example: **`LION_Output_Template.md`**.

### Three points that carry weight

**Section 1 goes first.** A caveat read after the argument is too late to change how the argument landed.

**Section 3 must read LEAD, not just LAB.** A named organisation working on a problem is stronger response-side evidence than a paper about the topic. This is the main reason LEAD exists.

**Section 6 is the cheapest form of a falsification test.** Not prediction — no horizon, no probability. Just what would make this wrong. One sentence, and it is what separates an argument from an assertion.

**Section 4 doubles as a quality check.** If the gap cannot be stated in one sentence, the reasoning above it has not converged and the gap is not ready.

### Coverage

**DECIDED: no minimum threshold. The agent always states its evidence base.**

The most honest option — no arbitrary number pretending to be a standard, and the reader sees exactly what the call rests on.

**The trade-off, stated plainly.** A threshold would stop a weak gap being produced at all. Disclosure produces it anyway and relies on the reader noticing "based on 3 documents" and discounting it. Some will not — a well-argued gap reads as solid regardless of the number above it.

### A second supply-side measure

LEAD network density is evidence about the response side. A dense actor cluster on a theme means a crowded field — measured structurally rather than by counting documents, which makes it more robust than LAB document counts alone.

**Subject to the same caution:** a sparse network usually means little has been read, not that a field is under-served. See §8.

---

## 8. Correctness rules

Applies across all three stores. These are the difference between a useful system and a confident-sounding one.

1. **Silence is not a finding.** *"Nothing in the store"* and *"nothing in the world"* must never be returned as the same answer.

2. **A thin evidence base is not "no opportunity."** When the agent finds little, it says so in section 1 and section 5 rather than returning silence a stakeholder will read as *"nothing there."*

3. **A sparse network is not an under-networked field.** The graph maps what has been read, not the field. This is rule 1 applied to network topology, and it is the most dangerous place for it — a graph looks objective in a way a paragraph does not.

4. **Defensibility over plausibility.** Every claim traces to a named source. Plausible-sounding inference without a source does not ship.

5. **The agent states a mismatch; it does not recommend.** Problem > response tells you a hole exists, not that it is a hole for the Trust. Whether to act is a human call, and additionality and actionability are the tests — neither of which the stores can support. See §1.

6. **Watch the file names in LAB.** With no stable IDs there, renaming a filed document silently breaks any LION entry pointing at it. Nobody notices until someone tries to check a source. *Habit: do not rename after filing. Add rather than edit.*

   *Evidence this matters:* in the existing Air Pollution sample, Opportunity 2 is headed "Connected to Signal 2" while its own body says "flagged in Signal 1" — Signal 1 is correct. Opportunity 3 is headed "Signals 4 and 5"; its body says "Signal 3." Signal 4's card cites "Signal 3 (EU)" when EU is Signal 2. Part B promises five signal cards and contains four. Everything shifted by one when a card was removed.

---

## 9. Consequences accepted

Decisions that trade rigour for speed. Recorded so nobody is surprised later.

| Decision | What it costs |
|---|---|
| Agent infers problem/response at query time | Answers are not stable. The same question may sort documents differently on different days, so LION can propose an opening one day and not the next. No record of which documents the agent counted on each side. |
| No stable IDs in LAB | Renaming a file breaks every reference to it, silently. |
| Disclosure instead of a coverage threshold | Weak gaps get produced. Nothing stops them at creation — only the reader's attention does. |
| Authors-only extraction into LEAD | The store skews to Experts. Leaders, Advocates and Doers depend entirely on manual entry. |
| LEAD populated by one person | The graph reflects one person's reading and network. A thin area now has two possible causes, not one. If the graph is ever shown to anyone, say whose graph it is. |
| No author-count limit on network measures | Until weighting is applied at the analysis step, the graph mostly shows who appears on large reports. That is a real pattern but it is not collaboration. **Centrality must not be quoted from an unweighted graph.** |
| No LION store | Gaps are not retained. Each run starts from nothing, so duplicate reasoning across sessions is invisible and nothing accumulates. This also makes the theme-level question — *"is there a proposition here"* — unanswerable, since it needs many gaps taken together. |
| No Transactions table | Additionality cannot be tested. Blocked by data collection, not by design. |

---

## 10. Where the mitigations went

Each was a rule for the agent's output rather than a schema change.

| # | Mitigation | Addresses |
|---|---|---|
| M1 | When proposing an opening, the agent names which documents it placed on the problem side and which on the response side | Restores an audit trail without the tagging column |
| M3 | Evidence base stated at the **top** of a gap, not the bottom | Read after the argument, a caveat is too late to change how the argument landed |
| M4 | The agent names **what is missing**, not just what it has — e.g. *"no documents covering government or multilateral activity in this region"* | Far more useful than a count, and the honest form of "silence is not a finding" |

**M2 (showing Proposed / Confirmed state) has dropped out** — there is no store, so there is no state to show.

**M1, M3 and M4 are now built into the output template** as sections 2/3, 1 and 5 respectively. They are no longer optional add-ons; they are the structure. Listed here only to record where they went.

---

## 11. Still open

| # | Question | Blocks |
|---|---|---|
| 1 | Does the agent produce one gap per request, or several to compare? One forces it to pick a winner and hide the alternatives; several show what it considered and rejected — more useful while testing, more noise once trusted. | Output template |
| 2 | Should section 4 carry a confidence marker, or does the evidence base in section 1 already do that work? | Output template |
| 3 | Replace the fabricated worked example in the template with real agent output | Template being followed rather than copied |
| 4 | Do the 39 existing actor cards get imported, and with what geography? | Whether the first graph looks emptier than actual knowledge |
| 5 | Fix `Publisher: Not Found` → Internal / Unknown | Data quality |
| 6 | Exclude folder rows from the queryable set, or add a record type field | Agent returning blank rows as real entries |
| 7 | Do the existing 82 LAB records get geography tagged? | Migration effort |

### Not yet written down anywhere: what a good answer looks like

LAB, LEAD and the gap-finding agent are all specified. Nothing says what *correct* looks like.

*"Who works on air pollution in Indonesia"* could return three names or thirty, with or without reasoning shown. Without some notion of correctness there is no way to tell whether the POC succeeded — only that it produced output.

**Cheapest version:** write five questions worth answering, and for each, what a good answer contains. Half a page. It becomes the test set, and it is what shows whether this was worth building.

---

## 12. Deliberately out of scope

| Excluded | Returns when |
|---|---|
| Scanner agents / auto-refresh | After the POC proves answer quality is there |
| An agent that updates LEAD from LAB automatically | Later. For the POC the schema is the deliverable; a separate agent does the updating downstream. |
| The LION store itself, and the Proposed / Confirmed gate | Once enough gaps have been produced to know what is worth retaining. The output template defines the shape if it is stored later. |
| Additionality and actionability testing | Once gap-finding works **and** the Transactions table (§6) is populated. Needs evidence on instruments, counterparties and capital flows that nobody has collected yet. |
| The Transactions table | When someone commits to sourcing deal data. Fields specified in §6; the LEAD stable IDs are already built for it. |
| Claim-level cards with page locators | When document-level attribution proves insufficient |
| General relationships table — funder→grantee, board membership, coalitions | When edges beyond authorship are needed |
| LEAD scoring framework and engagement status | When prioritisation for engagement becomes the job |
| Prediction and forecasting | Requires a horizon, a direction and a falsifier — and far more evidence than exists |
| Cross-store synthesis by the machine without labelling | Not planned to return |

**On the word "prediction":** real prediction needs a stated horizon, a direction, and a test that would prove the call wrong. The POC has none of these and no volume of evidence to support them. LION is a **structured judgment aid** that makes an asymmetry visible and auditable. That is defensible. "Prediction system" is not, yet.

---

## 13. Next steps

The posture across all decisions is consistent: minimum filing work, maximum disclosure, structure carried by the output rather than the schema.

**Two deliverables:**
1. **The stores** — LEAD three tables, LAB metadata additions. Schema is the artefact.
2. **The gap-finding agent** — reads LAB and LEAD, outputs the six-section template.

**Build order:**

1. Set up the LEAD three tables and the LAB metadata additions.
2. Import the 39 actor cards and tag the 82 LAB records with geography.
3. Write the agent's system prompt, carrying:
   - Per-store labelling of every claim — LAB and LEAD never merged into one voice
   - The six-section output structure, sections present even when empty
   - Response side reads LEAD as well as LAB
   - Coverage gap distinguished from confirmed absence
   - Refusal language for questions outside the two themes
4. Run it on a real question. Replace the fabricated example in the template.
5. Write the five test questions (§10) — this is what tells you whether it worked.
