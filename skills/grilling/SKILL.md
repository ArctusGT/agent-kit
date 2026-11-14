---
name: grilling
description: Draw out the intent behind a request when it is not obvious, by asking the Maintainer questions in rounds. Use when the objective, what to avoid, or a premise behind a request is unclear, or when the Maintainer asks to be grilled.
---

Ask questions until the **intent** is clear: the objective the work must achieve, what it must avoid, and the premises the Maintainer is resting on. The _how_ is not settled here. A question about method that a proof could answer goes to a probe or a prototype, not to the Maintainer.

Work in **rounds**. The **frontier** is every question you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Ask through a **scenario**: give an example of the behaviour that would follow from an answer and let the question fall out of it, rather than putting the abstract question directly. An abstract question arrives carrying your framing, and the user answers inside it — including when the answer they need is outside it. So open broadly and narrow late: leave a particular in play until a later round, or until running the thing makes it obvious, because settling one early for a tidy frontier closes an option the user would have taken once they had seen it work. Save the sharp explicit question for what actually blocks progress.

Each round's answers reshape what is left: recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now.

Stop when the intent is clear enough to weigh a method against: the objective is stated so it could be checked, what to avoid is named, and each premise is either confirmed or paired with the proof that would test it. A question still open then is not a failure: name it beside its proof, stop asking, and hand back to the work that called for this.
