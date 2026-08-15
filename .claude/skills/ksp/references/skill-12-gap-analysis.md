# Skill #12 — Gap analysis (IMPLEMENTED)

**Input:** theme, geography
**Output:** six sections, fixed order, every time

Run this first:

```bash
python3 tools/ksp.py evidence --theme "<theme>" --geography "<geography>"
```

That returns an **evidence brief** — counts, the documents with their
descriptions and quick insights, the actors with the documents that link them,
and what the store does not hold. It is raw material. **Never paste it as the
answer.**

If it returns `NO DATA`, print that and stop. Producing a gap from an empty
store is fabrication.

---

## What you do that the tooling cannot

**Classify each document as problem side, response side, or both.**

There is no stored problem/response field — a deliberate decision. So this is
inference, performed now, by you, over each document's description and quick
insights.

**Consequence you must disclose:** classification is not stable between runs.
The same question may sort documents differently on another day. Do not hide
this, and do not cache to smooth it over. Name which documents you placed on
each side, so the sorting is auditable even though it is not stable.

---

## The six sections

Same order every time, **including when a section is empty.** An empty heading
is informative. A missing heading is invisible.

### 1. Evidence base

**Goes first**, before any argument. A caveat read after the reasoning is too
late to change how the reasoning landed.

Document count, actor count, date range, geography, source type breakdown.
Take these from the brief.

### 2. Problem side

What says this is getting worse, or is larger than currently addressed.

**Every claim names its document.** No claim without a source.

### 3. Response side

What says someone is already working on this. **Reads both stores, labelled
separately:**

- **From LAB:** documented programmes, funding, policy moves
- **From LEAD:** actors working in this area, and the document that links them

A named organisation is stronger response-side evidence than a paper about the
topic. **This is the main reason LEAD exists — it is not optional here.**

Actors the brief flags as *geography-only* or *via a Global document only* do
not evidence presence in the geography. Keep them separate or leave them out.

### 4. The gap

**One sentence.** The actual claim.

This doubles as a quality gate: if the mismatch cannot be stated in one
sentence, the reasoning above has not converged. **Say so rather than padding.**

No confidence marker — Section 1 does that work.

### 5. What is missing

What you looked for and did not find. Distinguish two states:

| Label | Meaning |
|---|---|
| `Coverage gap` | Not found in the stores. May exist in the world. |
| `Confirmed absent` | Searched and genuinely not there. Rare. |

**Default to `Coverage gap`.** `Confirmed absent` is a strong claim and must be
justified in the text — it requires the stores to cover this ground well, which
at current size they almost never do.

### 6. What would change this

**One sentence.** What evidence would overturn the call.

Not prediction — no horizon, no probability. Just the test that separates an
argument from an assertion.

---

## One gap per request

Produce a single gap. The template is singular and Section 4 is a quality gate;
several gaps weaken it.

If you considered and set aside other candidates, you may name them in a line —
but without reasoning, so they cannot be misread as findings.

---

## State this limitation in the output

#12 is the **lowest-trust** candidate type in the catalogue: the one most
likely to reflect thin reading rather than real absence, and the one users find
most convincing. That combination is the main risk in the whole system.

It is implemented first only because it is the only one the current fields
support. **Section 1 is not optional for this reason.**

---

## Worked shape

> ### 1. Evidence base
> Based on 2 LAB documents (2024–2025) and 3 LEAD actors. Geography: Indonesia.
> All sources are Research. No policy documents. One further document is tagged
> Global and counted separately.
>
> ### 2. Problem side
> - PM2.5 concentrations 4.1% higher on heatwave days — *Heat and PM2.5 compound exposure study* (LAB)
> - Peri-urban exposure largely unmeasured — *Jakarta air quality review* (LAB)
>
> ### 3. Response side
> **From LAB:** one instrument, and it is not specific to this geography —
> $200M clean cooking outcome bond — *Clean cooking outcome bond brief* (Global)
> **From LEAD:** 3 actors, all Researchers — Jane Smith, Wei Chen, Institute of
> Environmental Health. None named as implementing anything.
>
> ### 4. The gap
> Compound heat–pollution exposure is documented as a measured and growing risk
> across two sources, while every actor found is a researcher and the only
> financing instrument identified operates globally rather than here.
>
> ### 5. What is missing
> No policy documents, so government and multilateral activity is unobserved. No
> implementers or funders in LEAD for this geography. **Coverage gap, not
> confirmed absence** — the store holds 6 documents in total, and none are
> policy-focused, so the silence describes the store.
>
> ### 6. What would change this
> This would not hold if a national air quality programme is already operating
> in Jakarta and simply has not been filed.

*(Shape only. The numbers above come from the test fixture, not the real store.)*
