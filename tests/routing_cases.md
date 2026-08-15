# Routing test cases

From PRD §7. Routing is semantic and belongs to the agent, so these are an
agent-behaviour checklist rather than unit tests — a deterministic router would
be a second thing to trust, and the PRD puts the choice with the agent.

Everything the tooling *can* verify mechanically is covered in `pytest`:
refusal text, missing-field naming, outcome labels, counts, folder exclusion,
integrity, empty-store handling.

Run each against `tests/fixtures/demo_store`, then again against
`tests/fixtures/empty_store`.

---

## The eight cases

| # | Ask | Expect |
|---|---|---|
| 1 | *"What do we hold on water in Indonesia?"* | Skill **#1** runs. `RESULT`. |
| 2 | *"Where's the gap in air pollution in Vietnam?"* | Skill **#12** runs. Six sections, all present. |
| 3 | *"Is the funding response the right size for clean cooking?"* | `NOT IMPLEMENTED` **#5**, names *Stated quantity field on LAB*. |
| 4 | *"Which solutions work but haven't scaled?"* | Triage puts **#6** top as `READY (POC)`, naming *Solution maturity field on LAB* as what the proper version needs. Nothing runs until confirmed. |
| 5 | *"Who should I talk to about air quality in Jakarta?"* | `NOT IMPLEMENTED` **#2**, says *buildable, not blocked*. Names **no** field. |
| 5a | *"Which water solutions work but haven't spread?"* | Triage puts **#6** top as `READY (POC)`. Nothing runs until confirmed. |
| 5b | *"Could the Vietnam kiosk model work in Indonesia?"* | Triage puts **#9** top as `READY (POC)`. Nothing runs until confirmed. |
| 6 | *"Tell me about semiconductor supply chains"* | `OUT OF SCOPE`. Not `NOT IMPLEMENTED`. |
| 7 | *(any query on an empty theme)* | `NO DATA`. Not silence, not a fabricated gap. |
| 8 | *(a row whose file was renamed on disk)* | Integrity check reports it **at start**. Never surfaces as thin evidence. |

Case 8 setup:

```bash
cp -r tests/fixtures/demo_store /tmp/broken
mv /tmp/broken/lab/documents/Heat_PM25_Study.pdf /tmp/broken/lab/documents/Heat_v2.pdf
python3 tools/ksp.py --store /tmp/broken check
```

---

## Triage, on every question

- [ ] Triage ran and the shortlist was **shown to the user**.
- [ ] Nothing was run before they picked.
- [ ] Where the top match was blocked, no command was offered for the ones below
      it, and the output said they answer *different questions*.

## For a POC skill (#6, #9)

- [ ] The evidence base is first and **unedited**, including its `Not stored` line.
- [ ] Every claim still names a document or actor, despite the free-form body.
- [ ] Inferred conditions or judgments are stated as inferred, not as fields.

## What to check in every answer

- [ ] The chosen skill is **named**, with its number. Never routed silently.
- [ ] The outcome label is one of `RESULT` / `NO DATA` / `NOT IMPLEMENTED` /
      `OUT OF SCOPE`, and a refusal does not read like a finding.
- [ ] Every claim names its source document or actor.
- [ ] LAB and LEAD claims are labelled separately, never merged into one voice.
- [ ] The word *opportunity* does not appear.
- [ ] Nothing recommends an action, an instrument, or a funding decision.
- [ ] Absence is described as a coverage gap unless confirmed absence is
      justified in the text.

## For #12 specifically

- [ ] All six sections present, in order, **even when empty**.
- [ ] Section 1 is first.
- [ ] Section 3 cites LEAD actors, not only LAB documents.
- [ ] Section 4 is one sentence — or says the reasoning has not converged.
- [ ] Section 5 labels `Coverage gap` or `Confirmed absent`.
- [ ] Section 6 is one sentence, and is a falsifier rather than a prediction.
- [ ] The output states that classification is inferred and may vary between
      runs, and names which documents went on each side.

---

## Not yet written: what a good answer looks like

The PRD's own §11 note, still open. LAB, LEAD and the agent are specified;
nothing says what *correct* looks like.

*"Who works on air pollution in Indonesia"* could return three names or thirty,
with or without reasoning shown. Without some notion of correctness there is no
way to tell whether the POC succeeded — only that it produced output.

**Cheapest version:** five questions worth answering, and for each, what a good
answer contains. Half a page. It becomes the test set, and it is what shows
whether this was worth building.

That needs a domain judgment this repo cannot supply on its own.
