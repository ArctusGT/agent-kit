# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill (frontmatter, how it is reached, and router skills). Everything else about writing it is the universal reference in `SKILL.md`.

## Three ways a skill is reached

A skill's file is always on disk. `disable-model-invocation` decides only whether its description sits in the agent's context; it never stops an agent reading the file. That gives three modes, each trading the two loads differently:

- A **model-invoked** skill keeps its `description` loaded at all times, so the agent fires it on its own when a situation matches. The human can still type its name: a description only ever adds agent discovery, never removes the human's. Permanent context load, bought for discoverability. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill starts only when the human types its name. Zero context load, but it spends cognitive load: the human is the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing: a one-line summary, trigger lists stripped.
- A **by-path** skill is a user-invoked skill that other documents also reach, by naming its file. The pointer at each call site carries the trigger condition, so the pointer-writing rules in `SKILL.md` apply there; the skill's own description stays human-facing. Zero context load until a caller fires, and nothing for the human to remember.

Pick model-invocation only when the agent must reach the skill from a situation no calling document puts in front of it. Pick by-path when every route to the skill runs through another document: a skill, a rule, `AGENTS.md`. Pick user-invocation when only the human ever starts it.

## Calling another skill

Name its file: "read `.agents/skills/<name>/SKILL.md` and follow it". Every project that carries the kit has that path, whether or not it links the skill into `.claude/skills/`, and a missing file is an error in the agent's turn, not a call that silently never happens. Say at the call site when to read it and what to take from it ("follow it", "use its vocabulary"): the callee's description is never consulted on this route. Frontmatter that only the `Skill` tool acts on, such as `argument-hint`, does nothing here, so put what the skill needs in the calling sentence.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own (a trigger word you actually use in your prompts). You pay context load for the new always-loaded description, so that independent reach has to be worth it. Split off a by-path skill when several documents need the same behaviour: it costs no context load, only one pointer line at each caller.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others by path, each with the condition for reaching it, so the human has one skill to remember instead of many. Once the human starts the router, it fires the others itself.
