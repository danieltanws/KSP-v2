# Skill #1 — Coverage check (IMPLEMENTED)

**Input:** theme, geography — **either may be blank**
**Output:** document count, actor count, date range, breakdown by source type
and sub-pillar

```bash
python3 tools/ksp.py coverage --theme "<theme>" --geography "<geography>"
```

Both flags are optional. Omit `--geography` for every geography; omit
`--theme` for the whole store.

---

## What it is

Counting and grouping only. **No inference over content.**

This is the only output that is certainly true, because it describes the store
rather than the world.

## Run it on its own

Not solely as part of #12. The point is to check coverage **before** asking a
question that depends on it — otherwise thin evidence is discovered after a gap
analysis has already convinced someone.

Everything else in the registry is uninterpretable without this.

---

## Reading it out

Give the counts, the breakdowns that matter, and the caveat. The tool's block
carries all three already — read it and say what it holds rather than pasting
the table, unless the reader wants the table.

Two things to add in your own words when they apply:

- **Global documents are counted separately.** A report tagged `Global` does
  cover Indonesia, but folding it into an Indonesia count would overstate what
  has actually been read about Indonesia.
- **Actors reached only through a Global document** are separated for the same
  reason. They do not evidence presence in the geography.

## What it does not tell you

Never let this be read as a statement about the world.

> A well-covered cell means we have read a lot, not that a field is crowded.
> A thin cell means we have read little, not that the subject is neglected.

The tool prints that line. Say it in your own words if you like, but it does
not get dropped — it is the whole reason a count is safe to give out.
