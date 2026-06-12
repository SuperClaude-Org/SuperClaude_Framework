<!--
  Minimal starter CLAUDE.md.
  Copy to your repo root as CLAUDE.md and fill in the placeholders.
  Background and more entries: docs/knowledge/ in SuperClaude_Framework
  (https://github.com/SuperClaude-Org/SuperClaude_Framework/tree/v5/docs/knowledge).
  Keep the whole file lean — every line is loaded on every turn.
-->

# CLAUDE.md

<!-- One sentence: what this project is. -->
{{PROJECT_DESCRIPTION}}

## Commands

```bash
{{BUILD_COMMAND}}        # build
{{TEST_COMMAND}}         # run tests
{{LINT_COMMAND}}         # lint / format
```

## Structure

<!-- Only the directories an agent must know. 5-10 lines max. -->
```
{{KEY_DIRECTORY_1}}/     # {{what it holds}}
{{KEY_DIRECTORY_2}}/     # {{what it holds}}
```

## Conventions

<!-- The 3-5 rules that actually get violated. Delete the rest. -->
- {{e.g. runtime/package manager rules: "all Python through uv run"}}
- {{e.g. commit style: "conventional commits"}}
- {{e.g. branch/PR rules}}

## Coding Principles

Trade-off: these bias caution over speed. Skip them for trivial tasks at your discretion.

### 1. Think before coding

Don't assume. Don't hide confusion. State assumptions; if unsure, ask. Present
competing interpretations instead of silently picking one. If a simpler
approach exists, say so.

### 2. Simple first

The minimum code that solves the problem. No unrequested features, no
abstractions for single-use code, no speculative flexibility, no error handling
for impossible scenarios. If 200 lines could be 50, rewrite.

### 3. Surgical changes

Touch only what the request requires. Don't "improve" adjacent code or refactor
what isn't broken; match the existing style. Delete only what *your* change
orphaned. Test: every changed line traces back to the request.

### 4. Goal-driven execution

Define success criteria, then loop until verified: "fix the bug" means "write a
reproducing test and make it pass". For multi-step work, show a short plan with
a verification step per item.

<!--
  Principles adapted from github.com/andrej-karpathy/skills.
  Full version with rationale: docs/knowledge/claude-md-principles.md
-->
