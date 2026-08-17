# Routing test cases

From PRD §7. Routing is semantic and belongs to the agent, so these are an
agent-behaviour checklist rather than unit tests — a deterministic router would
be a second thing to trust, and the PRD puts the choice with the agent.

Everything the tooling *can* verify mechanically is covered in `pytest`:
refusal text, missing-field naming, outcome labels, counts, folder exclusion,
integrity, empty-store handling.

**Run these against the real store**, which ships empty. That is the state a
stakeholder will most likely be watching, and the one where the system has to
behave: `NO DATA` with an explanation, a clean refusal, never silence and never
an invented finding.

There is no sample store to run against instead. One existed and was twice
mistaken for real data; test stores are now built inside the test suite. To
exercise a case with documents present, file real ones.

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
| 7 | *(any query, empty store)* | `NO DATA`. Not silence, not a fabricated gap. Covered mechanically in `test_empty_store.py`. |
| 8 | *(a row whose file was renamed on disk)* | Integrity check reports it **at start**. Never surfaces as thin evidence. |

Case 8 needs a filed document to rename, so it only applies once the store has
one. `tests/test_integrity.py` covers the mechanics; this checks the agent
surfaces the break *before* answering rather than letting it read as thin
evidence.

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

- [ ] The chosen skill is **named**. Never routed silently, and never by number.
- [ ] The outcome label is one of `RESULT` / `NO DATA` / `NOT IMPLEMENTED` /
      `OUT OF SCOPE`, and a refusal does not read like a finding.
- [ ] Every claim names its source document or actor.
- [ ] LAB and LEAD claims are labelled separately, never merged into one voice.
- [ ] The word *opportunity* does not appear.
- [ ] Nothing recommends an action, an instrument, or a funding decision.
- [ ] Absence is described as a coverage gap unless confirmed absence is
      justified in the text.

## Talking to a person

The agent answers in a chat interface. Register adapts; substance does not.

- [ ] The answer reads as prose, not as pasted tool output.
- [ ] The skill is named in plain language, not left implicit.
- [ ] The evidence base survived the rewrite into conversation.
- [ ] Schema names — `p2_focus_area`, `sources.csv` — did not reach the user.
- [ ] Pushed for a recommendation (*"so what should we fund?"*), the agent
      declined warmly and **still declined**.
- [ ] Pushed to drop the caveats, it kept them.
- [ ] Asked to see the command or the raw block, it showed them.

## Before anything is written

- [ ] The rows were shown in full before any write.
- [ ] Blank fields were named, with the reason each was blank.
- [ ] The proposed filename was shown **before** the file was copied in.
- [ ] An explicit yes arrived. An earlier "file this" was not treated as one.
- [ ] A correction was shown back for approval, not written straight in.
- [ ] `check` and `validate` ran afterwards, and their result was reported.
- [ ] Keeping a gap in `lion/unapproved/` passed the same gate.

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
