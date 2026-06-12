# Four CLAUDE.md Principles for LLM-Driven Development

Four principles that reduce the mistakes LLMs most commonly make when writing
code. Designed to be pasted into a project's CLAUDE.md (a ready-made starter
template lives at [docs/Templates/CLAUDE.template.md](../Templates/CLAUDE.template.md)).

**Trade-off**: these bias caution over speed. For trivial tasks, skipping them
is a judgment call, not a violation.

**Attribution**: adapted from the CLAUDE.md in
[andrej-karpathy/skills](https://github.com/andrej-karpathy/skills) (translated
and modified).

---

## Copy-paste-able section

```markdown
## Coding Principles

Trade-off: these bias caution over speed. Skip them for trivial tasks at your discretion.

### 1. Think before coding

**Don't assume. Don't hide confusion. Surface trade-offs.**

Before implementing:
- State your assumptions. If unsure, ask.
- If multiple interpretations exist, present all of them. Don't silently pick one.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what you don't know and ask.

### 2. Simple first

**The minimum code that solves the problem. Nothing speculative.**

- Don't add features nobody asked for.
- Don't introduce abstractions for code used once.
- Don't add "flexibility" or "configurability" that wasn't requested.
- Don't handle errors for scenarios that can't occur.
- If you wrote 200 lines and 50 would do, rewrite.

Ask yourself: "Would a senior engineer look at this and say it's overbuilt?"
If yes, simplify.

### 3. Surgical changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor what isn't broken.
- Match the existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it. Don't delete it.

When your change orphans something:
- Delete imports/variables/functions that *your* change made unused.
- Leave pre-existing dead code alone unless asked.

Test: every changed line traces directly back to the user's request.

### 4. Goal-driven execution

**Define success criteria. Loop until verified.**

Convert tasks into verifiable goals:
- "Add validation" → "write a test with invalid input, make it pass"
- "Fix the bug" → "write a reproducing test, make it pass"
- "Refactor X" → "confirm tests pass before and after"

For multi-step tasks, show a brief plan:

1. [step] → verify: [check]
2. [step] → verify: [check]

Strong success criteria enable autonomous loops. Weak criteria ("make it work")
force constant check-ins.
```

---

## Signs the guidelines are working

- Diffs contain fewer unrelated changes.
- Fewer rewrites caused by over-implementation.
- Clarifying questions arrive *before* implementation, not after the mistake.
