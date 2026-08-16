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
| `demo_store/` | 9 documents + 1 folder row, 8 actors, 8 authorship rows. Validates clean. |
| `empty_store/` | Headers only. The state the real store ships in. |

Neither carries a `vocab/` directory — vocabularies are global, so the tooling
falls back to `ksp/vocab/`. Fixtures therefore validate against the real
controlled lists, which is the point.

## What demo_store is shaped to exercise

- A **folder row** with every field blank, to prove folder rows never reach a query.
- A document tagged **`Global`**, to prove global documents and the actors
  reached only through them are counted separately from a country.
- An actor with **only a basis**, no source link and **no topic tag** (Clean Air
  Fund), to prove an untagged manual actor stays a geography match only.
- An actor with **a topic tag and no document** (Helena Thybell), the case that
  motivated the tag column: found on a website, tagged by hand, and therefore
  counted as theme evidence citing her basis rather than a document.
- A `source_url` on two rows, pointing at `example.org` so nobody follows it.
- An **organisation as author** (World Bank), the no-named-author rule.
- Both themes, so sibling focus areas can be shown not to bleed together.
- A **Policy** document under Water & Waste only, so the Pollution queries have
  a genuine source-type absence to report.

## The water case study, and what it is shaped to catch

`Vietnam_Water_Kiosk.pdf` is the case study the POC skills (#6, #9) run
against. Its `quick_insights` name two enabling conditions on purpose —
commune-level permitting, and households already paying private vendors — with
no replication reported elsewhere.

`Indonesia_Water_Access_Baseline.pdf` is the transfer target, and it is written
to leave **both** of those conditions unevidenced: willingness-to-pay "not
assessed", district permitting "not catalogued".

That is the point. A transfer check against this pair must come back negative,
because #9's rule is **default to no** — a condition with no target evidence is
not met, not "probably fine". If an agent reads these two documents and
concludes the model transfers, the skill's discipline has failed and the
fixture has done its job.
