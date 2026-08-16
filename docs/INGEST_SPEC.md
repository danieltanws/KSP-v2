# Ingest specification — for the agent populating these stores

Hand this document, plus everything in `ksp/vocab/`, to whatever crawls the
source repository. It is written to be read without any other context.

**Deliverables: three CSV files.** UTF-8, header row exactly as given, one
header row and no other formatting. No extra columns — a column this spec does
not list will fail validation.

```
ksp/lab/sources.csv       one row per document
ksp/lead/actors.csv       one row per person or organisation
ksp/lead/authorship.csv   one row per person per document
```

Validate what you produce with `python3 tools/ksp.py validate`. It names the
row and the field for every problem. Nothing is accepted until it passes.

---

## Rule 0 — controlled values are exact

Every field marked *controlled* accepts **only** the values in the matching
file under `ksp/vocab/`. Not a synonym, not a variant, not a close match.

`SE Asia`, `S.E. Asia` and `ASEAN` are three different wrong answers.
`Southeast Asia` is the value.

If a document does not fit an existing value, **leave the field blank and flag
the row** rather than inventing a value. A new value is a decision for the
store owner, not the crawler.

## Rule 1 — multi-select is semicolon-separated in one cell

```
Indonesia;Southeast Asia
```

No spaces around the semicolon. No quotes unless the cell also contains a
comma, in which case use standard CSV quoting.

## Rule 2 — hierarchical fields carry both levels

Two fields are hierarchical, and both work the same way: **tag the specific
value and its parent, in the same cell.**

| Field | Specific | Parent | Cell |
|---|---|---|---|
| geography | Indonesia | Southeast Asia | `Indonesia;Southeast Asia` |
| sub_pillar | Pollution | Urban Liveability | `Pollution;Urban Liveability` |

A document about a whole region carries just the region: `Southeast Asia`.
A document about the world carries `Global` alone.

Omitting the parent produces a validation warning, not an error — but do not
rely on that. Grouping fragments when the convention is not followed.

---

# File 1 — `ksp/lab/sources.csv`

```
name,file,record_type,description,quick_insights,pillar,sub_pillar,geography,source_type,publisher,year_published,total_author_count,date_added
```

| Column | Required | Controlled | What goes in it |
|---|---|---|---|
| `name` | **Yes** | — | The document's title, as printed on it |
| `file` | **Yes** | — | Exact filename in `ksp/lab/documents/`, including extension. See "The file column" below. |
| `record_type` | **Yes** | `record_type.csv` | `Document` or `Folder` |
| `description` | **Yes** | — | What the document is. One or two sentences. Factual, not evaluative. |
| `quick_insights` | No | — | The substantive claims, with figures. See below — this field does more work than its name suggests. |
| `pillar` | **Yes** | `pillar.csv` | `PLANET` / `PEOPLE` / `PROGRESS` / `PEACE`. Multi-select. |
| `sub_pillar` | No | `sub_pillar.csv` | P-2 focus area **and** its P-1 cluster. Multi-select. |
| `geography` | **Yes** | `geography.csv` | What the document is **about**, not where it was published. Country **and** region. Multi-select. |
| `source_type` | **Yes** | `source_type.csv` | `Research` / `Policy` / `Media` / `Industry` / `Internal` |
| `publisher` | **Yes** | partly | A publisher name, or `Internal`, or `Unknown`. **Never `Not Found`.** |
| `year_published` | No | — | Four digits. Blank if genuinely unknown — do not guess. |
| `total_author_count` | No | — | Whole number. Recorded for later network weighting; nothing uses it yet. |
| `date_added` | No | — | `YYYY-MM-DD`, the date you filed it |

### `quick_insights` — write this properly

Two of the analyses read nothing but `description` and `quick_insights`. A row
with a thin description is a document the system effectively cannot see.

Put the **specific, quotable claims** here: figures with units, dates,
geographies, named programmes, stated commitments, and anything the document
reports as a result. Prefer the document's own numbers over your summary of
them.

> Twelve kiosks operating after five years; 78% still financially
> self-sustaining at year three. The model relied on existing commune-level
> permitting and on households already paying private vendors for water. No
> replication outside the Delta provinces reported.

Write what the document says. Do not add interpretation, significance, or
implication — a later reader must be able to tell the document's claim from
someone's gloss on it.

### `publisher` — the distinction that matters

| Value | Means |
|---|---|
| A name | There is an external publisher and this is it |
| `Internal` | Produced internally. **There is no external publisher.** |
| `Unknown` | We looked and could not establish one. |

`Not Found` is rejected by the validator because it makes *"there isn't one"*
look identical to *"we didn't look."* Those are different facts and the
difference recurs throughout the system.

### `record_type` — folders

If the source repository has folder entries, they may be filed with
`record_type = Folder` and every other column blank. They are excluded from all
queries. If you can simply skip folders, do that instead.

### The `file` column, and where documents live

A LAB row is joined to its document **by filename and nothing else.** There are
no stable IDs. If the filename in the CSV does not match a real file in
`ksp/lab/documents/`, the row exists but cannot be opened.

So: **the documents must be copied into `ksp/lab/documents/`.** A link back to
the source system is not sufficient — the integrity check verifies the file is
present on disk and reports every row that fails.

Two consequences to design your crawl around:

- **Filenames must be unique across the whole store**, since they are the key.
  If two folders both contain `Report.pdf`, one must be renamed before filing.
- **Nothing may be renamed after filing.** A rename breaks the link silently.
  Settle the naming convention before the first row is written.

If copying documents is not possible, stop and raise it — it changes the
design, and it is not something to work around by inventing a URL column.

---

# File 2 — `ksp/lead/actors.csv`

```
id,name,form,actor_type,affiliation_id,source_files,geography,origin,basis,date_added
```

| Column | Required | Controlled | What goes in it |
|---|---|---|---|
| `id` | **Yes** | — | A whole number, unique, never reused. Other rows point at it. |
| `name` | **Yes** | — | As printed on the document |
| `form` | **Yes** | `actor_form.csv` | `Person` or `Organisation` |
| `actor_type` | No | `actor_type.csv` | `Researcher` / `Implementer` / `Funder` / `Government` / `Advocate` / `Other`. Leave blank rather than guessing. |
| `affiliation_id` | No | — | The `id` of the organisation this person belongs to. **People only** — setting it on an Organisation is an error. |
| `source_files` | No | — | Semicolon-separated LAB filenames this actor is tied to |
| `geography` | No | `geography.csv` | Inherited from the document. Means what they **write about**, not where they are based. |
| `origin` | **Yes** | `origin.csv` | `From LAB` for anything harvested from a document. `Manual` for hand-entered rows. |
| `basis` | No | — | Why this row exists, when there is no source. E.g. *"LinkedIn profile, checked 14 Aug"* |
| `date_added` | No | — | `YYYY-MM-DD` |

### The row-creation rule

**A row needs `name`, `form`, and either a `source_files` entry or a `basis`.**
The validator rejects anything less.

A row that is only a name looks like knowledge and is not — six months on,
nobody can reconstruct why it is there.

### Where a document has no named author

Institutional reports usually have no byline. **The publisher becomes the
actor**, with `form = Organisation`, and takes position 1 in authorship.
Without this rule those documents yield nothing.

### Extract authors only

Pull **author names, their organisations, and the geography the document
concerns.** Nothing else.

Do not harvest every named entity. Every organisation mentioned in passing,
every person quoted, every body referenced in a footnote — that produces
hundreds of rows of noise within a month and buries the useful ones.
Authorship is printed on the document: it is a fact, not a judgment, and that
is what makes it safe to automate.

Claims about an actor do not belong here either. *"This organisation's
programme failed"* is actor track record and would belong in LEAD if there were
a field for it — there is not, so leave it out. *"Programme failures are common
in this sector"* is a signal and belongs in the LAB document's
`quick_insights`.

### Duplicates

Do not build matching logic. If "World Bank" appears twice, that is accepted —
the store is small enough to eyeball. Reusing an existing `id` for a
near-match is worse than a duplicate row, because it asserts an identity
nobody checked.

---

# File 3 — `ksp/lead/authorship.csv`

```
actor_id,source_file,position
```

| Column | Required | What goes in it |
|---|---|---|
| `actor_id` | **Yes** | An `id` from `actors.csv` |
| `source_file` | **Yes** | A `file` from `sources.csv` |
| `position` | **Yes** | Author order as printed, starting at 1 |

One row per person per document. A duplicate pair is an error.

**Do not add a `role` column.** Role is derived from position — 1 is Primary,
anything else is Co. Storing it would mean re-entering every row if the rule
ever changes.

**Do not create a person-to-person table.** Co-authorship falls out of shared
documents. A stored copy goes stale the moment an author list is corrected.

---

# Scope

## Tag everything; only two themes are answerable

The full taxonomy is 4 pillars × 3 P-1 clusters × 3 P-2 focus areas = **36
focus areas**, all valid values. Tag whatever you crawl with the correct ones.

But the system currently answers questions on **two themes only**:

```
PLANET → Urban Liveability → Pollution
PLANET → Urban Liveability → Water & Waste
```

Anything else is refused as out of scope. That is not a reason to skip tagging
it — the data is correct and costs nothing to hold, and scope may widen. It is
a reason not to expect answers about it.

Note the third sibling in that cluster, **Urban Heat**, is *not* in scope. Tag
it accurately where it applies; queries will not reach it.

## What not to produce

- **No inferred fields.** If the document does not say it, leave it blank.
  Blank is a fact. A confident guess is not.
- **No summaries that editorialise.** Description and quick insights record
  what the document claims, not whether it is right or important.
- **No rows for documents you could not open.** A row whose content was never
  read is indistinguishable from one that was, and it will be counted as
  evidence.

---

# Checklist before handing the files back

- [ ] `python3 tools/ksp.py validate` passes with no errors
- [ ] `python3 tools/ksp.py check` reports every row matched to a file, and no
      unfiled documents
- [ ] Every `file` value corresponds to a real file in `ksp/lab/documents/`
- [ ] Filenames are unique store-wide and final — nothing will be renamed
- [ ] No `publisher` cell contains `Not Found`
- [ ] Every actor row has a source or a basis
- [ ] Hierarchical fields carry both levels
- [ ] No columns were added
- [ ] Any value you wanted but could not find in the vocabularies is listed
      separately for the store owner, not invented
