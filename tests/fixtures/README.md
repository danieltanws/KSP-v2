# Test fixtures

**Everything in `demo_store/` is synthetic. None of it is real evidence.**

The documents are one-line placeholders, the findings quoted in their
`quick_insights` are invented, and the actors do not represent real
relationships. It exists so the skills can be exercised against something, and
so the demo has something to show.

Do not copy any of it into `ksp/`. The real store ships empty and stays that
way until a person files real documents. Fabricated rows in the real store
would destroy the one property this system is for — that every claim traces to
a source someone can open.

---

| Fixture | Contents |
|---|---|
| `demo_store/` | 6 documents + 1 folder row, 6 actors, 5 authorship rows. Validates clean. |
| `empty_store/` | Headers only. The state the real store ships in. |

Neither carries a `vocab/` directory — vocabularies are global, so the tooling
falls back to `ksp/vocab/`. Fixtures therefore validate against the real
controlled lists, which is the point.

## What demo_store is shaped to exercise

- A **folder row** with every field blank, to prove folder rows never reach a query.
- A document tagged **`Global`**, to prove global documents and the actors
  reached only through them are counted separately from a country.
- An actor with **only a basis** and no source link (Clean Air Fund), to prove
  geography-only actors are not counted as theme evidence.
- An **organisation as author** (World Bank), the no-named-author rule.
- Both themes, so sibling focus areas can be shown not to bleed together.
- A **Policy** document under Water & Waste only, so the Pollution queries have
  a genuine source-type absence to report.
