# LION Gap — Output Template

**What this is:** the fixed shape of every gap the agent produces. Same six sections every time, in this order, even when a section is empty.

**What the agent produces is a candidate worth a closer look** — labelled a *gap* throughout. Nothing hangs on the word. What matters is that the output states a mismatch and shows its evidence; whether anything is worth acting on is a human call.

**Why the shape is fixed:** free-form reasoning varies in shape each run. You cannot compare two gaps, and you cannot spot a weak one, if they are not built the same way. An empty heading is informative. A missing heading is invisible.

---

## The six sections

### 1. Evidence base

Goes **first**, before any argument. A caveat read after the reasoning is too late to change how the reasoning landed.

Contains:
- How many LAB documents were read
- How many LEAD actors were found
- Date range of the sources
- Geography covered

> *Example:* Based on 7 LAB documents (2023–2026) and 4 LEAD actors. Geography: Indonesia, Southeast Asia. No sources later than March 2026.

---

### 2. The problem side

What says this is getting worse, or is larger than currently addressed.

Every claim names its document. No claim without a source.

> *Example:*
> - PM2.5 concentrations are 4.1% higher on heatwave days — *Heat–PM2.5 study*
> - Annual funding gap of $8B for clean cooking — *Clean Cooking Alliance estimate*

---

### 3. The response side

What says someone is already working on this. **Reads both stores.**

- **From LAB:** documented programmes, funding, policy moves
- **From LEAD:** actors working in this area — organisations, and what they are named as doing

A named organisation is stronger response-side evidence than a paper about the topic. LEAD is not optional here.

> *Example:*
> - World Bank Clean Cooking Outcome Bond, $200M — *Outcome bond brief*
> - LEAD: 3 organisations active in this geography — Clean Air Fund, CCAC, [org]

---

### 4. The asymmetry

**One sentence.** The actual claim.

If it cannot be stated in one sentence, the reasoning above has not converged and the gap is not ready.

> *Example:* The problem is documented across 5 sources and growing, while response activity is limited to one instrument and two actors, neither operating in this geography.

---

### 5. What is missing

What the agent looked for and did not find. Distinguish two things:

| | Meaning |
|---|---|
| **Not found in the stores** | May exist in the world. A coverage gap. |
| **Searched and confirmed absent** | Rare. Only where the stores genuinely cover this ground well. |

Default to the first. The second is a strong claim and needs justifying.

> *Example:* No documents covering government or multilateral activity in this geography. No LEAD actors with an operating footprint here. This is a coverage gap, not confirmed absence — the store holds 7 documents on this theme and none are policy-focused.

---

### 6. What would change this

**One sentence.** What evidence would overturn the call.

Not prediction — no horizon, no probability. Just the test that separates an argument from an assertion.

> *Example:* This would not hold if a major bilateral programme is already operating in this geography and simply is not in the stores.

---

## Rules the agent follows

1. **Every claim names its source.** No claim without one. This is the whole basis of the output being defensible.

2. **Sections appear even when empty.** An empty response side is the single most informative thing the output can contain — it must not be silently dropped.

3. **Never state absence as fact.** *"Nothing in the store"* and *"nothing in the world"* are different claims. Section 5 exists to keep them apart.

4. **Do not recommend.** Section 4 states a mismatch, not a course of action. Whether something is fundable requires two tests the agent cannot run — additionality (would other capital close this anyway) and actionability (is there an instrument and a counterparty). The stores hold no evidence on either, so any attempt would be inference without evidence.

5. **Do not merge the stores into one voice.** LAB evidence and LEAD evidence are labelled separately throughout.

---

## Worked example

> ### Evidence base
> Based on 7 LAB documents (2023–2026) and 4 LEAD actors. Geography: Indonesia, Southeast Asia. No sources later than March 2026.
>
> ### Problem side
> - PM2.5 concentrations 4.1% higher on heatwave days; compound exposure raises cardiovascular risk — *Heat–PM2.5 study*
> - Vulnerable populations lack agency to act on warnings — *Air Pollution Convenings Learning*
> - [further claims]
>
> ### Response side
> **From LAB:** one financing instrument identified — World Bank Clean Cooking Outcome Bond, $200M — *Outcome bond brief*
> **From LEAD:** 3 organisations active on air quality in Southeast Asia. None identified as working on compound heat–pollution exposure specifically.
>
> ### Gap
> Compound heat–pollution exposure is documented across 4 sources as a distinct and growing risk, while every identified response addresses heat or air quality separately, not the interaction.
>
> ### What is missing
> No documents on early warning system design for compound exposure. No LEAD actors named as working on the interaction. **Coverage gap, not confirmed absence** — the store holds no documents on early warning systems at all, so silence here describes the store.
>
> ### What would change this
> This would not hold if existing heat early warning systems already incorporate air quality thresholds and simply are not documented in the stores.

---

## Open

| # | Question |
|---|---|
| 1 | Does the agent produce one gap per request, or several to compare? |
| 2 | Does the output go anywhere, or stay in the conversation? (Storage deferred — this template defines the shape if it is stored later.) |
| 4 | Later: does the system support additionality and actionability testing, or do those stay entirely with a person? |
| 3 | Should section 4 carry a confidence marker, or does the evidence base in section 1 do that work? |
