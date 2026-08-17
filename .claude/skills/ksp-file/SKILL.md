---
name: ksp-file
description: Work out a document's LAB metadata and file it. Use when adding a PDF, report, paper or note to the KSP store - reading it, identifying its metadata (title, publisher, year, authors, 4P tagging, geography, source type), writing the sources.csv row and any LEAD actor and authorship rows. Also use to check or correct the metadata on a document already filed.
---

# Filing a document into LAB

Read the document, work out its metadata, **show it and wait**, then write and
validate.

This is a **filing** job, not an analysis. It adds to the store; it answers no
question. For questions, use the `ksp` skill.

> **Nothing is written until the user has seen it.** Steps 1–4 work the filing
> out. Step 5 puts it in front of them. Nothing touches `ksp/` until they say
> yes — not the rows, and not the file itself.

> **The one rule.** Record what the document says about itself. Where it says
> nothing, leave the field blank — never fill a gap with a reasonable guess.
> A blank cell is a fact about the document. A guess is a claim nobody made,
> and it will be read later as evidence.

---

## 1. Read enough of it

Cover, title page, imprint page, contents, executive summary. That is usually
all the metadata a document holds about itself.

Take from the document itself, not from the PDF's file properties. Producer
metadata is often wrong — a real example from this store carried
`/Title: Title Lorem Ipsum` and an `/Author` who was the layout designer, not a
byline.

## 2. Work out the row

Header, and the required fields:

```
name,file,record_type,description,quick_insights,pillar,p1_cluster,
p2_focus_area,geography,source_type,publisher,source_url,year_published,
total_author_count,date_added
```

Required: `name`, `file`, `record_type`, `description`, `pillar`, `geography`,
`source_type`, `publisher`.

Permitted values for every controlled field: the lists in **`ksp/vocab/`**.

| Field | How to decide it |
|---|---|
| `name` | The title as printed. Include the subtitle where it carries meaning. |
| `file` | The filename in `ksp/lab/documents/`, exactly. See §3. |
| `record_type` | `Document`. Only use `Folder` for a container row. |
| `description` | What the document **is**, in one or two sentences. Its type, scope, publisher and date. Factual, not evaluative. |
| `quick_insights` | Its substantive claims. See below — this field does more work than its name suggests. |
| `pillar` / `p1_cluster` / `p2_focus_area` | The 4P chain. Must be consistent; the validator rejects a focus area filed under the wrong cluster. |
| `geography` | What the document is **about**, not where it was published. Country **and** its region: `Indonesia;Southeast Asia`. Worldwide scope is `Global` alone. |
| `source_type` | `Research` / `Policy` / `Media` / `Industry` / `Internal`. A development-bank strategy or guidance note is `Policy`. A technical note with named authors and a methodology is `Research`. |
| `publisher` | The institution. **Never `Not Found`** — use `Internal` (no external publisher) or `Unknown` (looked, could not establish). |
| `source_url` | Where it came from. A DOI printed in the document is ideal. Blank if you do not know — do not reconstruct a plausible URL. |
| `year_published` | The year printed on the document, not the PDF creation date. |
| `total_author_count` | Number of named authors. Blank where there is no byline. |

### `quick_insights` is the load-bearing field

Two of the analyses read nothing but `description` and `quick_insights`. A
document with a thin entry is one the system effectively cannot see.

Put the **specific, quotable claims** here: figures with units, dates, named
programmes, stated targets and commitments, and anything reported as a result.
Prefer the document's own numbers to your summary of them.

> Target: improve water security for 400 million people by 2030 through seven
> scalable solutions. States 2.1 billion people lack safely managed drinking
> water and more than 3.4 billion live without adequate sanitation (JMP 2025).

**Record what it says. Do not add what it means.** No significance, no
implication, no "this suggests". A flattened fact can be recovered by reopening
the document; a flattened judgment cannot, because nobody can tell whose it
was.

## 3. Choose the filename — do not copy yet

Decide the name the document will carry. It gets copied in at step 6, once the
filing is approved.

- **Filenames must be unique across the whole store.** They are the only key —
  there are no IDs in LAB.
- **Nothing gets renamed after filing.** A rename breaks the link silently. The
  integrity check catches it afterwards; not renaming avoids it.
- A useful convention: publisher, subject, year —
  `WBG_Water_Strategy_Implementation_Plan.pdf`.

Because it can never be changed, the filename is one of the things the user
approves at step 5. Do not pick a permanent key on their behalf and copy it in
before they have seen it.

## 4. Work out the LEAD rows

**Authors only.** Author names, their organisations, and the geography the
document concerns. Do not harvest every named entity — every body mentioned in
passing produces hundreds of noise rows within a month and buries the useful
ones. Authorship is printed on the document: a fact, not a judgment.

**Where there is no named author, the publisher becomes the actor** at position
1. Institutional reports usually have no byline; without this rule they yield
nothing.

Take author affiliations from the document's own "About the authors" section
where it has one. If it does not, leave `affiliation_id` blank rather than
assuming someone works where you expect.

An actor row needs `name`, `form`, and **either** a source link **or** a
`basis`. `origin` is `From LAB` when harvested, `Manual` otherwise.

Authorship rows store `actor_id`, `source_file`, `position` — position as
printed. Role is derived, never stored.

## 5. Show it and wait

Put the whole filing in front of the user before any of it exists on disk.

Show:

- **The document row** — every field you filled, in plain language rather than
  raw CSV unless they want the CSV.
- **The filename** you propose, flagged as permanent.
- **The LEAD rows** — each actor, and the authorship positions.
- **Every blank field, and why it is blank.** "No byline, so no author count"
  is a fact about the document. Present it as one.
- **Anything the vocabulary could not express**, per *When the vocabulary does
  not fit* below.

Then stop and wait for an explicit yes.

**Why this step exists.** Everything above is inference. You read a document
and decided what it is about, who wrote it, and which focus area it belongs
under. Once written, none of that reads as inference — it reads as evidence,
and every later analysis treats it that way. The user is not approving that you
may file; they are approving what you concluded.

Being asked to file a document is not this yes. Neither is silence.

If they correct something, change it and show the corrected version. Do not
carry a correction straight into a write.

## 6. Write it

Only now: copy the file into `ksp/lab/documents/` under the approved name, then
write the LAB row and the LEAD rows.

## 7. Validate, always

```bash
python3 tools/ksp.py check      # every row opens its file
python3 tools/ksp.py validate   # every value is permitted, every chain consistent
```

Both must pass before the filing is done. Report what they say.

---

## When the vocabulary does not fit

**Do not invent a value.** A new controlled value is a decision for the store
owner, not for whoever is filing.

Where a document does not fit, either use the existing values that genuinely
apply, or leave the field blank — then **say so explicitly** in your reply, so
the gap becomes a decision rather than a silent approximation.

*Live example:* an ADB guidance note covering "Asia and the Pacific" has no
matching region, because `geography.csv` has no `Asia-Pacific` value. It is
filed against the five regions it actually spans, and the gap was raised rather
than papered over.

## What this skill must never do

- **Write anything into `ksp/` before the user has seen it** — the row, the
  LEAD rows, or the file copy
- Fill a required field with a plausible guess
- Reconstruct a URL that is not printed in the document
- Write interpretation into `description` or `quick_insights`
- Add an actor who is not an author, unless the user asked for that actor
- Put sample or placeholder rows in `ksp/` — test data belongs in the test suite
