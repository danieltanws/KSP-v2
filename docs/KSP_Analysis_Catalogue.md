# KSP — What the System Can Produce

**Organised by outcome, not by method.** Each entry: what comes out, what you do with it, what it needs, and how much to trust it.

Drawn from five disciplines: bibliometrics, foresight, philanthropic landscape analysis, blended finance, and policy transfer.

---

## The four kinds of outcome

Most discussion of this system is about finding gaps. Gaps are only one of four things it can produce, and not the most useful.

| Kind | What changes | Entries |
|---|---|---|
| **Changes what you read** | Your collection priorities | 1 |
| **Changes who you call** | Your next conversation | 2, 3 |
| **Changes what you consider** | Your candidate list | 4–14 |
| **Changes what you avoid** | What you stop pursuing | 15, 16 |

Candidate types (4–14) are ranked by **how much you can trust them**, strongest first. That ranking is deliberate and runs against intuition: the types that sound most like a discovery are the ones most likely to be an artefact of what you have read.

**The uncomfortable pattern:** the most actionable outputs are the least impressive-sounding. A reading list, a list of names, and a "don't bother" are things someone can act on tomorrow. Most gap-finding produces *"look into this,"* which is weak actionability dressed up as analysis.

---

# Changes what you read

## 1. Where our knowledge is thin

**Outcome:** A map of which theme × geography cells are empty, thin, or well covered.
**Action:** A collection priority list. What to read next.
**Analysis:** Coverage profiling — cross-tabulate LAB by pillar, sub-pillar, geography, year.
**Data:** LAB metadata only. Available now.
**Trust:** **Highest of anything here.** It is counting, not inference. It is also the only output that is certainly true, because it describes the store rather than the world.

**Why it comes first:** every other output depends on knowing whether the store is thin. Without it, a weak result is discovered *after* it has already convinced someone.

**Caveat for decision makers:** this tells you nothing about the world. A well-covered cell means we have read a lot, not that a field is crowded.

---

# Changes who you call

## 2. Who to talk to about this

**Outcome:** A named list of actors adjacent to a candidate — same theme, same geography, related sub-pillar.
**Action:** Direct. These are people to contact.
**Analysis:** Adjacent actor lookup, run after a candidate is produced.
**Data:** LEAD. Available now.
**Trust:** High. These are real rows, not inferences.

**Note:** the most directly actionable output on this list, and the cheapest to build.

**Caveat for decision makers:** adjacency is judged on tags, not on knowledge of the field. The list is a starting point for a conversation, not a shortlist of the right people.

## 3. Who connects this field

**Outcome:** Actors bridging otherwise separate clusters.
**Action:** Who to approach for convening, or who to ask about the field.
**Analysis:** Network analysis over Actors and Authorship.
**Data:** LEAD + Authorship + total author count. Needs code execution — fine in Claude Code.
**Trust:** **Low at current size.** At 39 actors you can see this by looking. The measures start earning their keep in the hundreds.

**Caveat for decision makers — two distortions:**
1. **The graph maps what we have read, not the field.** A sparse network looks like a finding and usually means thin reading. A graph looks objective in a way a paragraph does not, which makes this the most dangerous place for that error.
2. **It skews to authors.** Co-authorship is easy to extract from papers, so researchers appear highly connected. Practitioners and funders rarely publish, so they appear isolated even when they are the best-connected people in the field.

Also: with no author-count limit applied, one large institutional report creates hundreds of connections at once and will dominate every measure. **Centrality must not be quoted until weighting is applied at the analysis step.**

---

# Changes what you consider

Ranked by **how much you can trust the output**, strongest first. The ranking runs against intuition: several of the weakest types are the ones that feel most like a discovery.

## 4. Promised, but nobody is implementing

**Outcome:** A commitment on the public record — a limit value, an NDC, a COP pledge — with no actor delivering it.
**Action:** The strongest candidate type. Worth a closer look with confidence.
**Analysis:** Policy–implementation gap.
**Data:** LAB policy documents + LEAD actors. Available now.
**Trust:** **Highest of any candidate type.** The demand side is *stated*, not inferred from problem documents. Someone has publicly committed. The existing air pollution samples are full of this material.

**Caveat:** a commitment with no implementer in the store may still have implementers in the world. Public commitment removes the demand-side uncertainty, not the response-side one.

## 5. Response is the wrong size

**Outcome:** A documented need and a documented response that differ by orders of magnitude. The existing sample has one — an $8B annual clean cooking funding gap against a $200M outcome bond.
**Action:** A strong candidate. Nothing is inferred from silence.
**Analysis:** Scale mismatch — compare stated need against stated response for the same theme and geography.
**Data:** Quantities from LAB. Currently buried in free-text Quick Insights; needs a **stated quantity** field to be reliable.
**Trust:** **High — and the only candidate type that does not depend on absence.** Someone stated the need, someone stated the response, and the two do not meet. This sidesteps the coverage problem running through everything else here.

**Caveat for decision makers:** the two numbers usually come from different sources with different scopes. An $8B *global annual* gap against a $200M *single-instrument* commitment is not like-for-like — the mismatch is real but the ratio is not meaningful. **Report the mismatch, never the multiple.** Check both figures cover the same geography, period and definition before treating the comparison as evidence.

## 6. Works somewhere, has not spread

**Outcome:** A solution that succeeded in one place and has not scaled.
**Action:** The highest-conversion candidate type in philanthropy. Risk is proven; the barrier is usually financing or adoption — precisely what catalytic capital is for.
**Analysis:** Proven-but-unscaled identification.
**Data:** LAB case studies + **a solution maturity field that does not exist yet** (early-stage / proven-but-unscaled / mature).
**Trust:** High once the field exists. **Cannot be inferred reliably from free text** — an agent cannot consistently tell "piloted successfully in Kenya" from "under development."

**Two of five expert views ranked this first, independently. It is one column.**

**Caveat:** success is self-reported. A pilot described as successful in its own write-up may not have been. Independent evaluation is rare.

## 7. Wrong mix of actors

**Outcome:** A field with researchers but no implementers, or implementers but no funders.
**Action:** Tells you **what kind** of support is missing — capacity, money, or delivery. This is what turns a candidate into something with a shape.
**Analysis:** Actor-type composition.
**Data:** LEAD form and type. Needs an actor type taxonomy — one column plus a decision.
**Trust:** Medium. Depends on LEAD being populated beyond authors.

**Caveat for decision makers:** LEAD is filled largely by harvesting authors, and **authors are overwhelmingly researchers.** Implementers and funders rarely publish. So every field will look research-heavy and implementer-poor whether or not it is. This measure is only as good as the manual entry behind it.

## 8. Venue shift

**Outcome:** A topic that appeared only in research three years ago and now appears in regulator consultations or industry material. Status has changed, regardless of volume.
**Action:** An early signal — the strongest form available without a subscription, because a small number of documents can carry it.
**Analysis:** Track which *kind* of source discusses a topic, over time.
**Data:** LAB year + **a source type field** (research / policy / media / industry / internal). One column, not built.
**Trust:** Medium once the clock has been running. The mechanism is sound; the data is not there yet.

**Caveat for decision makers:** venue shift only works if you are reading **all** the venues. If the store is mostly research papers, policy documents will look like a new development when they are simply a category you had not been collecting. Without deliberate, even coverage across source types, this measures reading habits rather than the world.

## 9. Worked in A, might work in B

**Outcome:** A *match* rather than an absence — a case study whose enabling conditions also appear elsewhere.
**Action:** A candidate with a specific proposal already attached, which is rare and valuable.
**Analysis:** Transferability analysis. Four steps: decompose the case, separate the solution from its scaffolding, check each condition in the target, **default to no**.
**Data:** LAB case studies + **an enabling conditions list per case study**. Not one column — a structured list. Not built.
**Trust:** **Low without conditions data, and dangerous.**

**Caveat for decision makers:** most transfer failures happen because **a condition nobody wrote down was doing the work.** Similarity gets judged on visible features; the decisive condition is usually invisible. This is the only output on this list where being wrong costs money directly rather than costing attention.

*Discipline that helps:* write the conditions **before** looking at the target. Written after, you will list the ones the target happens to have.

*Note:* this is the matching layer scoped earlier — same mechanism, same rules. Offline, slow clock, default to rejection, absence of evidence never a pass.

## 10. Two things that never meet

**Outcome:** Two well-covered sub-pillars that rarely appear together.
**Action:** A hypothesis for a domain expert. Not a finding.
**Analysis:** Sub-pillar co-occurrence.
**Data:** LAB tags only. Available now.
**Trust:** **Low, and the easiest thing here to over-read.**

**Caveat for decision makers:** most non-co-occurrences are simply unrelated things. The compound heat–pollution example is the good case; there will be many bad ones. Any two topics can be made to sound like a promising intersection after the fact.

## 11. Problem rising, response static

**Outcome:** Evidence about a problem growing year on year while actor count stays flat. The field may be adequately staffed for the problem as it was five years ago and not for what it is becoming.
**Action:** A candidate with urgency attached.
**Analysis:** Compare LAB document volume by year against LEAD actor count for the same theme.
**Data:** LAB year + LEAD. Available now, unreliably.
**Trust:** **Low until collection has been running for a year or more.**

**Caveat for decision makers:** the corpus was **assembled, not accumulated.** Documents were gathered at a point in time rather than collected continuously, so an apparent rise may simply be recent reading — a topic looks like it is growing because someone searched for it last month. Until the store has been built steadily over time, treat any trend line as a description of collection activity, not of the world.

## 12. Documented problem, no actors

**Outcome:** A theme or geography with evidence of a problem and few organisations working on it.
**Action:** Weak — *"look into this."*
**Analysis:** Actor–topic concentration; geographic footprint.
**Data:** LEAD + LAB. Available now.
**Trust:** **Lowest of the types available today.**

**Caveat for decision makers:** this is the output most likely to be a coverage artefact **and** the one people find most convincing. That combination makes it the main risk in the whole system. Never present it without the coverage figure from #1 alongside it.

## 13. Well resourced, not working

**Outcome:** A field with actors, funding and attention that is not producing results.
**Action:** Arguably the better catalytic target — money is not the constraint, approach is.
**Analysis:** Compare response-side presence against outcome evidence.
**Data:** Outcome data. **Almost nothing in the stores says whether a programme worked.**
**Trust:** **Very low.** The mechanism is sound; the evidence is absent.

**Caveat for decision makers:** reporting is systematically positive. Programmes publish what went well; almost nobody publishes what did not. A field can look like it is working while producing nothing, and the stores will never show the difference. Same blind spot as #15.

## 14. Capital moving, or not moving

**Outcome:** Direction and rate of change of funding into a theme. Practitioners read three things: rate of change rather than level; *who* is moving, since DFI money often precedes commercial money by years, making DFI entry without commercial follow-on a specific and readable signal; and stage, since money into pilots but not scale-up locates the constraint at the scaling step.
**Action:** The strongest form of "is this crowded or opening up" — when it works.
**Analysis:** Fund flow analysis.
**Data:** **Transaction records in LAB** (see below), and critically a *time series* of them. A snapshot cannot show rate of change.
**Trust:** **Lowest of anything in this document. Do not attempt on current data.**

**Caveat for decision makers — three compounding problems:**

1. **The data does not exist yet.** Not a build problem — nobody has collected it. Historical deal data must be bought or accumulated over years.
2. **The available data is bad.** Commercial deal databases skew heavily toward deals someone chose to publicise. Philanthropic flows are barely captured anywhere.
3. **Rate-of-change analysis on incomplete data mostly measures changes in disclosure practice.** A sector that appears to be attracting more capital may simply have become more willing to announce it. This is the failure mode that looks most like a finding.

*What to say:* this is the right question and the one we cannot answer. Answering it needs a data subscription and someone maintaining it — a budget conversation, not a system limitation.

### Where transactions live

**In LAB.** LAB is *what happens*; a transaction is something that happened. The production store is assumed to hold both unstructured documents and structured records — infrastructure decided later.

For analysis, transactions need structure: funder, recipient, instrument type, amount, date, geography, source. Funder and recipient point at LEAD actor rows, which is a further reason the LEAD stable IDs are required.

---

# Changes what you avoid

## 15. Tried before, did not work

**Outcome:** A record of what has been attempted and failed.
**Action:** Stops a known dead end being pursued. Negative value, but large.
**Analysis:** Failure and lesson mapping.
**Data:** **Failures captured against LEAD actors.** A field plus a collection habit. Not built.
**Trust:** High when the data exists — but it rarely does anywhere, because failures are seldom written up.

**Why this matters structurally:** it is the *only* thing that distinguishes "nobody tried" from "someone tried and failed." Every other analysis sees identical silence in both cases. This is the most differentiated element in the design.

**Caveat for decision makers:** what gets recorded as failure is a fraction of what failed. Absence of a recorded failure is not evidence that nothing was tried.

## 16. Already crowded

**Outcome:** A theme with many actors, or many capital providers, already present.
**Action:** Do not pursue — no additionality.
**Analysis:** Capital provider presence; actor concentration read in reverse.
**Data:** LEAD organisations tagged by type. Available with the type taxonomy.
**Trust:** Low as a funding signal.

**Caveat for decision makers:** **LEAD is not a funder database.** Absence of funders in LEAD says almost nothing about who is funding — funders rarely author documents, so they are the actor type least likely to appear at all. Reading "no funders present" as "no funders active" would be a serious error.

---

# What cannot be produced

| Wanted | Blocked by |
|---|---|
| Financing gap size, concessionality, capital stack, crowding-in, **additionality** | Transaction data — structured records in LAB, not yet collected. Convergence (subscription, partial, publicity-skewed), OECD DAC (reliable, too aggregated), IJGlobal (costly). **A budget conversation, not a build one.** |
| Emerging issue detection, trend extrapolation | Continuous collection. The corpus was **assembled, not accumulated** — a signal appearing now cannot be told apart from a document read recently. Start the clock; usable in about a year. |
| Citation analysis, topic clustering | A bibliographic source, and several hundred documents minimum. |

---

# What to build, in order

| Order | Outcome | Why here |
|---|---|---|
| 1 | **#1 Where knowledge is thin** | Everything else is uninterpretable without it. Cheapest to build. |
| 2 | **#4 Promised but unimplemented** | Highest-confidence candidate. Demand is on the record. |
| 3 | **#2 Who to talk to** | Most directly actionable thing on the list. |
| 4 | **#5 Response is the wrong size** | The only candidate type that does not rest on absence. |
| 5 | **#12 Documented problem, no actors** | The general-purpose method — but never present it without #1 alongside. |
| 6 | **#7 Wrong mix of actors** | Gives candidates a shape. |

Then stop and use them for a month.

**In parallel, add the solution maturity field.** One column, unlocks #5, ranked first by two independent expert views.

---

# Enhancements, by value per unit of effort

| # | Add | Unlocks | Cost |
|---|---|---|---|
| 1 | **Solution maturity field** (LAB) | #6 | One column |
| 2 | **Stated quantity field** (LAB) | #5 — the only absence-free candidate type | One column |
| 3 | **Source type field** (LAB) — research / policy / media / industry / internal | #8, and it starts the clock for early signals | One column |
| 4 | **Actor type taxonomy** (LEAD) | #7, #16 | One column + a decision |
| 5 | **Failure capture** (LEAD) | #15, and partly #13 | A field + a habit |
| 6 | **Total author count** (LAB) | Correct weighting for #3 | One column |
| 7 | **Enabling conditions** per case study | #9 | A structured list — not trivial |
| 8 | **LION store** (retain candidates) | Theme-level questions; C3H's main question | A table |
| 9 | **Transaction records** in LAB | #14 and everything blocked above | Structure + a data subscription |
| 10 | **Continuous scanning** | #11, and makes #8 usable | An ongoing commitment |

**Items 1–3 are one column each and unlock three of the strongest candidate types.** Do these first regardless of anything else.

---

# Three limits nothing escapes

**1. Absence cannot be falsified from inside a corpus.** Every gap-type output returns "nothing found." Bibliometrics normally works against near-complete databases, where absence means something. This is a reading list. No method distinguishes the two — only a person who knows the field.

**2. Source diversity may matter more than volume.** Sixty documents from sixty vantage points beats six hundred from one worldview. If the store is dominated by Western institutional reports, every candidate found is a candidate in *that* worldview. **More of the same reading makes candidates look better-evidenced without making them more true.** Worth checking before adding volume.

**3. People act on things they can picture themselves doing.** Sound analyses routinely identify genuinely underserved areas and go nowhere, because nobody can answer *"what would we do on Monday, and with whom."*

**The test:** take the best candidate to a programme colleague and ask what they would do with it. If they cannot answer, the analysis is not finished — however sound the method.
