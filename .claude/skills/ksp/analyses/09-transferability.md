# #9 — Transferability  *(POC skill)*

**Status: POC.** This is a prompt, not an implementation. No enabling
conditions are recorded anywhere, so the conditions you reason about are ones
you infer from reading — which is exactly the weakness described below.

Get the material first:

```bash
python3 tools/ksp.py brief --skill 9 --theme "<theme>" --geography "<geography>"
```

---

## What this analysis is for

Something worked in A. Might it work in B?

Unusually among the sixteen, the output is a **match rather than an absence** —
a candidate with a specific proposal already attached, which is rare and
valuable.

## How to do it

Your call. The four steps in the catalogue are a reasonable starting shape:

1. Decompose the case — what actually happened
2. Separate the solution from its scaffolding
3. Check each condition in the target
4. **Default to no**

**Enabling conditions** are the things that had to be true in the original
place for the solution to work — not the solution itself. Piped supply already
nearby. Households already used to paying. A permit obtainable locally. A
technician left behind by an earlier programme. Move the solution somewhere one
of those does not hold and it fails, even though the visible parts transplant
fine.

## The trap in this one

Read this before writing anything.

**Most transfer failures happen because a condition nobody wrote down was doing
the work.** Similarity gets judged on visible features; the decisive condition
is usually invisible.

**This is the only analysis of the sixteen where being wrong costs money
directly** rather than costing attention.

**In this POC, the conditions are not stored — so you are inferring them from
the same documents you are matching against.** That is the failure mode the
proper version exists to prevent: written after the target is in view, the
conditions you list are the ones the target happens to have. Discipline that
helps: write the full condition list before you look at any target document,
and do not add to it afterwards.

**Default to no.** A condition you cannot find evidence for is **not met** —
not "unknown", not "probably fine". Absence of evidence is never a pass. If
most conditions are unevidenced, the honest answer is that the store cannot
support a transfer judgment.

## Output

The evidence base block from the brief goes **first, unedited**. It names the
field this analysis would properly use and states that it is not stored — that
line is how a reader can tell this from a computed answer, so do not drop it.

After that the shape is yours, but make two things explicit: **which conditions
you inferred**, and **which of them you found no target evidence for**. A
reader who disagrees with one condition should be able to see it and say so.

The hard rules still bind: every claim names its document, LAB and LEAD stay
labelled apart, absence in the store is never absence in the world, and you
state a mismatch rather than recommending.

---

*Replacing this: add `ksp/lab/enabling_conditions.csv` (one row per condition
per case study, filed **with the case study, before any target is chosen**),
write the analysis in `tools/kspcore/`, and set #9 to `IMPLEMENTED` in
`ksp/registry/skills.csv`. This file then goes away.*
