# Decisions taken at build time

Records the PRD §9 open items and the one place the build departs from the
PRD's assumed data model. Nothing here overrides the PRD; where it resolves an
item the PRD left open, this is the resolution.

---

## PRD §9 open items

| # | Item | Resolution | Source |
|---|---|---|---|
| 1 | One gap per request, or several? | **One.** The LION template is singular and §6.4 makes Section 4 a quality gate — several gaps weaken it. Alternatives considered may be named in a line, without reasoning, so they cannot be misread as findings. | Build default |
| 2 | Confidence marker on Section 4? | **No marker.** §2 lists confidence scoring as out of scope; Section 1's evidence base does that work. | Resolved from the PRD itself |
| 3 | Geography seed values | **Asia-focused seed.** SEA / South Asia / East Asia countries with parent regions, plus Global and the non-Asia places the specs name. 63 rows in `ksp/vocab/geography.csv`. | User decision |
| 4 | Sub-pillar list | **Supplied** as `docs/TT_Ps.xlsx`. See below. | User supplied |
| 5 | Implement skills #2 and #10? | **No — both keep refusing.** §0 ("do not implement the fourteen") governs. Their refusal says *buildable, not yet built* and names no field. | Build default |

Items 1, 2 and 5 are build defaults, not user instructions. Each is reversible.

---

## The taxonomy, and the one model change it forced

`TT_Ps.xlsx` gives the real Temasek Trust 4P structure: **4 pillars × 3 P-1
clusters × 3 P-2 focus areas = 36 focus areas.** Verified from row grouping —
the sheet has no merged cells, so the labels were read from position, in
regular blocks of nine and three.

The PRD assumed a single flat "Sub-pillar" list (§3, §5.1). There are two
levels. Three consequences, all carried into the build:

### 1. Sub-pillar stays one multi-select field

It holds values from either level, mirroring how the PRD already specifies
Geography (`Indonesia;Southeast Asia`). Same shape, and one validator rule
covers both hierarchies — a child value tagged without its parent produces a
warning, never a silent rewrite of the user's data.

This is the minimum departure from the PRD's field list: §5.1 has one
`Sub-pillar | Multi-select` row, and it still does.

### 2. Theme filters target P-2, never P-1

Both in-scope themes are siblings inside one cluster:

```
PLANET → Urban Liveability → { Urban Heat, Water & Waste, Pollution }
```

Filtering on `Urban Liveability` would sweep in Urban Heat and quietly widen
every answer. `ksp/vocab/theme.csv` therefore maps each theme to its P-2 focus
area, and `resolve_theme` rejects the cluster name as a theme.

### 3. The second theme is named `Water & Waste`

The taxonomy has no standalone "Water" — the focus area bundles water with
waste. The theme is named `Water & Waste` in vocab, prompts and output, so what
was filtered on is what the reader sees. A water question can therefore return
waste-focused documents; the output says so.

*(The alternative — keeping the PRD's looser "Water" label and filtering
`Water & Waste` behind it — was rejected in favour of naming the tag actually
used.)*

---

## `theme.csv` — an addition beyond PRD §3

§3's list of controlled vocabularies does not include themes, but §6.5 rule 7
restricts the agent to two of them and §6.3/§6.4 both take theme as an input.
The two-value list has to exist somewhere. Putting it in `ksp/vocab/` keeps the
restriction data-driven rather than hardcoded in a prompt, and gives the
out-of-scope refusal something to name.

It also carries aliases, so *"air quality in Jakarta"* resolves to Pollution.
Aliases match on word boundaries — `wash` must not fire on "Washington".

---

## Global documents and the actors reached through them

Not specified in the PRD; decided during the build.

A document tagged `Global` does cover Indonesia, but folding it into an
Indonesia count would overstate what has actually been read about Indonesia.
Both skills therefore count global documents **separately**, and an actor
reached *only* through a global document is separated for the same reason — it
is not evidence of presence in the geography.

This follows the PRD's posture throughout: disclose the distinction rather than
silently resolve it either way.

---

## Where the deterministic line falls

Skill #1 is "counting and grouping only, no inference" (§6.3) and is described
as the only output that is certainly true. It is scripted, so it cannot be
re-derived differently each run.

Skill #12 step 2 — classifying documents as problem side or response side — is
explicitly inference at query time with no stored field. It stays with the
agent. `ksp.py evidence` gathers and counts, then hands over a brief; it never
classifies, and nothing is cached, because §6.4 names caching as a way of
hiding the instability rather than fixing it.
