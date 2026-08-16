# KSP — Knowledge Synthesis Platform (POC)

**Temasek Trust, Strategic Knowledge & Insights.**

Finds where the Trust could deploy capital against a problem that is not
already being addressed by someone else. The system surfaces **candidates worth
a closer look**, with every claim traced to a named source. A person decides
whether any is worth acting on.

Themes in scope: **Pollution** and **Water & Waste**.

---

## What this proves

One thing: that a stored, well-tagged body of evidence can answer real
questions with sources attached, and can identify gaps with the reasoning
shown — instead of an analyst team doing it by hand.

**Defensible is the operative word.** An answer that sounds right but cannot be
traced to a source is worse than no answer, because capital allocation
decisions rest on it.

### What it is not

Not a live scanning system. Not a forecasting engine. Not an investment
recommendation. Not a test of additionality or actionability. Not a replacement
for judgment.

---

## The design in one line

**Sixteen analyses are declared. Two are implemented, two are POC, twelve refuse
by name.**

Each refusal names the field that would unlock it, which turns user demand into
a build roadmap: what people keep asking for is what to build next.

```
$ python3 tools/ksp.py refuse 5

NOT IMPLEMENTED — Scale mismatch (#5)

A documented need and a documented response that differ by orders of magnitude.

It needs: Stated quantity field on LAB.
The only candidate type that does not depend on absence.

Caveat if it is built: The two numbers usually come from different sources with
different scopes. Report the mismatch, never the multiple.

Implemented skills that may be relevant: Coverage check (#1), Gap analysis (#12).
```

---

## Triage — what would answer this?

Ask what analysis fits before running one. It suggests and stops; you pick.

```
$ python3 tools/ksp.py triage "could the Vietnam kiosk model work in Indonesia?"

ROUTING — "could the Vietnam kiosk model work in Indonesia?"

  ← #9   Transferability  READY (POC)
        matched: work in

Nothing has been run.
```

If the closest match is **blocked**, that is the answer — the analyses below it
answer different questions, and no command is offered for them. A ranked list
must never become a fallback chain; substituting one analysis for another is
the single thing this system exists to prevent.

## POC skills

Two analyses (#6 proven-but-unscaled, #9 transferability) are **placeholders**:
a prompt file in `.claude/skills/ksp/analyses/` and nothing else. No stored
field, no code. The agent reads the documents and works out the method itself,
so the output is improvised rather than computed.

The point is modularity. **Adding one is dropping in a file** named `NN-slug.md`
and setting a status cell to `POC` — no code change. Making it real means adding
the field it names, writing the analysis, flipping the status to `IMPLEMENTED`,
and deleting the prompt.

A POC answer carries the same `RESULT` label as a computed one. The evidence
base is where the difference shows:

```
EVIDENCE BASE
  LAB documents          5
  LEAD actors            3 linked by a matching document
  Date range             2023–2026
  Not stored             Enabling conditions list per case study
                         → identified by reading, not by a field.
                           Improvised, not computed.
```

## Getting started

No install step — Python 3.9+ standard library only.

```bash
python3 tools/ksp.py check                 # integrity check; run this first, always
python3 tools/ksp.py triage "<question>"   # which analyses fit; runs nothing
python3 tools/ksp.py registry              # the 16 declared skills
python3 tools/ksp.py themes                # what is in scope
```

The stores ship **empty**. To see the system working, point it at the demo
fixture:

```bash
python3 tools/ksp.py --store tests/fixtures/demo_store coverage \
    --theme Pollution --geography Indonesia

python3 tools/ksp.py --store tests/fixtures/demo_store evidence \
    --theme Pollution --geography Indonesia

python3 tools/ksp.py --store tests/fixtures/demo_store brief \
    --skill 9 --theme "Water & Waste"
```

In Claude Code, just ask — the `ksp` skill routes the question, names the skill
it chose, and runs it or refuses.

---

## Bulk ingest

Populating the stores from an existing document repository — by hand or with
another agent — needs two documents, handed over together:

| Document | What it is |
|---|---|
| `outputs/INGEST_SPEC.md` | Column-by-column spec for all three CSVs, the rules, and a pre-handover checklist |
| `outputs/CONTROLLED_VALUES.md` | Every permitted value. Generated from `ksp/vocab/`, so it cannot drift |

Both are written to be read without any other context. Validate the result with
`ksp.py validate` and `ksp.py check` before accepting it.

**The one thing to settle first:** documents must be copied into
`ksp/lab/documents/`, and filenames must be unique store-wide and final. A LAB
row is joined to its file by filename and nothing else.

## Filing a document

1. Put the file in `ksp/lab/documents/`.
2. Add a row to `ksp/lab/sources.csv` with the exact filename in the `file`
   column.
3. Run `python3 tools/ksp.py validate`.

Required: `name`, `file`, `record_type`, `description`, `pillar`, `geography`,
`source_type`, `publisher`.

**Do not rename a document after filing.** LAB has no stable IDs — the row and
the file are joined by a string match and nothing else, so a rename breaks the
link. The integrity check catches it; the habit avoids it.

**Publisher is never "Not Found."** Use `Internal` (produced internally, there
is no external publisher) or `Unknown` (we looked and could not establish it).
That distinction recurs throughout the system and is not cosmetic — "there
isn't one" and "we didn't look" are different facts.

### Adding an actor

A row in `ksp/lead/actors.csv` needs `name`, `form`, and **either** a source
link **or** a basis. A row that is only a name looks like knowledge and is not
— six months on, nobody can reconstruct why it is there.

Where a document has no named author, **the publisher becomes the actor** at
position 1. Institutional reports usually have no byline; without this rule
they yield nothing.

---

## Layout

```
ksp/
├── lab/
│   ├── documents/          the files themselves
│   └── sources.csv         one row per document
├── lead/
│   ├── actors.csv          mandatory stable ID; affiliation links point at it
│   └── authorship.csv      one row per person per document
├── vocab/                  controlled lists - no free text where a list exists
└── registry/skills.csv     the 16 declarations

tools/ksp.py                check · validate · registry · refuse · triage ·
                            coverage · evidence · brief
.claude/skills/ksp/         the routing agent
.claude/skills/ksp/analyses/  one prompt file per POC skill
docs/                       specifications; KSP_POC_PRD.md governs
outputs/                    what this agent produces - INGEST_SPEC.md and
                            CONTROLLED_VALUES.md for bulk loading
tests/                      pytest, plus empty and demo fixture stores
```

---

## The three stores

| | Holds | What you do with it | Shape |
|---|---|---|---|
| **LAB** | Landscapes, Assessments and Beyond — a file, with labels attached | Read it | Unstructured |
| **LEAD** | Leaders, Experts, Advocates and Doers — rows of fields, no file underneath | Compute over it | Structured |
| **LION** | Levers, Innovations, Opportunities and Nexus | — | **Not built.** It defines the *shape of the agent's output*, not a store. |

The asymmetry between LAB and LEAD is deliberate, not an inconsistency to tidy
up. LAB answers *"what do we know about air pollution"* — the agent finds
documents and a person reads them. LEAD answers *"who works on this"* —
counting, grouping and following links, which only works if the facts sit in
fields.

---

## Known limits

Read these before quoting any output.

- **Absence cannot be falsified from inside a corpus.** Every gap-type output
  returns "nothing found". This is a reading list, not a near-complete
  database, and no method distinguishes the two — only a person who knows the
  field.
- **Little response-side evidence has three causes** that look identical:
  nobody is working on it; someone is and we have not read it; nobody is for a
  reason. **At current store size the middle one is the most common by a wide
  margin.**
- **LEAD skews to researchers.** Authors are researchers. Implementers and
  funders rarely publish, so every field looks research-heavy whether or not it
  is.
- **A POC skill's answer is improvised.** #6 and #9 have no stored field behind
  them; the agent invents the method by reading. Check the `Not stored` line in
  the evidence base before quoting either.
- **The implemented gap analysis (#12) is the weakest of the sixteen** — the
  one most likely to reflect thin reading, and the one readers find most
  convincing. It is implemented first only because it is the only one the
  current fields support.
- **Classification is not stable between runs.** There is no stored
  problem/response field, so the same question may sort documents differently
  on different days. Disclosure is the mitigation, by design.

**Framing:** the system surfaces candidates, and the first job is filtering out
the ones that reflect our reading rather than the world. A low conversion rate
is the system working correctly.

---

## Development

```bash
pytest -q                              # 164 tests
python3 tools/render_registry_doc.py   # after editing ksp/registry/skills.csv
python3 tools/render_vocab_doc.py      # after editing anything in ksp/vocab/
```

Contributor notes, accepted costs, and the do-not-build list are in
`CLAUDE.md`. Build decisions and the taxonomy note are in `docs/DECISIONS.md`.
