# Skill #3 — Network position (IMPLEMENTED)

**Input:** theme, geography — **either may be blank**
**Output:** clusters, bridges, and an author-count weighted connection score

```bash
python3 tools/ksp.py network --theme "<theme>" --geography "<geography>"
```

Both flags are optional. Leaving `--theme` off is often the point: an actor who
connects Pollution to Water & Waste is invisible inside either one.

---

## What it computes

Two actors are adjacent when one document links both. A **bridge** is an actor
whose removal leaves the graph in more pieces than before — the formal version
of "who connects the field", not an approximation of it.

**Every edge is author-count weighted.** A document with 40 authors creates 780
pairs on its own; counted flat, the most-connected actor would always be whoever
signed the largest report. Each document contributes `1/(n-1)` per pair, so a
two-author paper contributes a full unit and a forty-author report contributes
1/39.

`n` comes from `total_author_count` where the document declares one, and from
the filed authorship rows where it does not. The output says which was used,
because the second understates a long author list that was only partly filed.

---

## Reading it out

### Never quote an unweighted count

The tool does not compute one, and it should not be reconstructed. This is the
condition the analysis was blocked on, and it is the whole reason the numbers
are safe to give out at all.

Give the weighted score as what it is — a comparison between actors *in this
store*, not a measure with meaning outside it. "1.00" means one document's worth
of connection, not a rank in the field.

### Three sections, three different strengths of evidence

| Section | What it means |
|---|---|
| **Clusters** | Who shares documents with whom. Isolated actors are named as isolated. |
| **Bridges** | Removing this actor splits the graph. The strong claim. |
| **Appearing on more than one document** | Weaker. They span documents but share none with another actor, so the graph cannot see them as connectors. |

**Do not merge the last two.** An actor who is the sole actor on three documents
forms no edge at all — they are connective in a real sense, but not the sense a
bridge is, and reporting them together would overstate it.

### The publisher-as-actor trap

Where a document has no byline, the filing rule puts the publisher at position 1.
So an institution can span several documents purely by that convention, without
having done anything connective. The tool says so; keep it in your answer when
an organisation appears in the spanning list.

At small store sizes this is the most likely reason anything shows up there at
all. Check before you report it as a finding.

---

## State this limitation in the output

> The graph maps what we have read, not the field, and it skews to authors.

Both halves matter and neither is optional:

- **It maps the reading list.** An actor central here is central among filed
  documents. One who connects nothing may be the most connected person in the
  field.
- **It skews to authors.** LEAD is filled largely by harvesting authors, and
  authors are researchers. A graph of implementers and funders would look
  entirely different, and this one cannot show it.

An empty `BRIDGES` section is a normal result at this store size, not a finding
about the field. Say which it is.

---

## What it is not

Not centrality in the bibliometric sense — no eigenvector, no betweenness, no
clustering coefficient. Those measures need a graph that approximates a real
field, and this one approximates a reading list. Adding them would produce
numbers with more precision than the data supports, which is the failure mode
this analysis is closest to.
