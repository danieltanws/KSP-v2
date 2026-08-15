# #6 — Proven but unscaled  *(POC skill)*

**Status: POC.** This is a prompt, not an implementation. There is no solution
maturity field in LAB, so nothing tells you which documents describe a proven
solution — you work that out by reading.

Get the material first:

```bash
python3 tools/ksp.py brief --skill 6 --theme "<theme>" --geography "<geography>"
```

---

## What this analysis is for

Finding a solution that **worked somewhere and has not spread**.

Why it matters: the risk is already proven. What is usually missing is
financing or adoption — which is what catalytic capital is for. Two of five
expert views in the catalogue ranked this the most useful analysis of the
sixteen, independently.

## How to do it

Your call. Read the documents in the brief and work out which of them describe
something that was tried and worked, then work out whether anything in the
store shows it happening anywhere else.

Some things that tend to matter, none of them binding:

- A pilot write-up, an evaluation, or a programme description usually reads
  differently from a survey or a policy paper.
- "Piloted successfully in Kenya" and "under development" are genuinely hard to
  tell apart in free text. Where you cannot tell, say you cannot tell.
- Spread shows up as the same approach appearing under a different geography or
  a different actor.

## The trap in this one

**You cannot prove something has not spread.** The store not showing it
elsewhere means the store does not show it elsewhere — nothing more. Say
`Coverage gap`, not confirmed absence.

**Success is self-reported.** A pilot described as successful in its own
write-up may not have been. Independent evaluation is rare, and if the only
source is the implementer's own document, say so.

## Output

The evidence base block from the brief goes **first, unedited**. It names the
field this analysis would properly use and states that it is not stored — that
line is how a reader can tell this from a computed answer, so do not drop it.

After that the shape is yours. The hard rules still bind: every claim names its
document, LAB and LEAD stay labelled apart, absence in the store is never
absence in the world, and you state a mismatch rather than recommending.

---

*Replacing this: add a `solution_maturity` column to `ksp/lab/sources.csv`
(`early-stage` / `proven-but-unscaled` / `mature`) with a vocab file, write the
analysis in `tools/kspcore/`, and set #6 to `IMPLEMENTED` in
`ksp/registry/skills.csv`. This file then goes away.*
