# Tier Classification Rules

Read-only reference extracted from SKILL.md Section 5.3 and Appendix. This file exists for human review; the skill uses its own inline copy.

---

## Priority Order (Conflict Resolution)

```
STRICT (1) > EXEMPT (2) > LIGHT (3) > STANDARD (4)
```

---

## Compound Phrase Overrides (check first)

Before keyword matching, check for compound phrases:

### LIGHT overrides
- "quick fix", "minor change", "fix typo", "small update"
- "update comment", "refactor comment", "fix spacing", "fix lint"
- "rename variable"

### STRICT overrides (security always wins)
- "fix security", "add authentication", "update database"
- "change api", "modify schema"
- Any LIGHT modifier + security keyword -> STRICT

If compound phrase matches, use that tier with +0.15 confidence boost.

---

## Tier Keyword Matching

### STRICT keywords (+0.4 each match)
- **Security**: authentication, security, authorization, password, credential, token, secret, encrypt, permission, session, oauth, jwt
- **Data**: database, migration, schema, model, transaction, query
- **Scope**: refactor, remediate, restructure, overhaul, multi-file, system-wide, breaking change, api contract

### EXEMPT keywords (+0.4 each match)
- **Questions**: what, how, why, explain, understand, describe, clarify
- **Exploration**: explore, investigate, analyze (read-only), review, check, show
- **Planning**: plan, design, brainstorm, consider, evaluate
- **Git**: commit, push, pull, merge, rebase, status, diff, log

### LIGHT keywords (+0.3 each match)
- **Trivial**: typo, spelling, grammar, format, formatting, whitespace, indent
- **Minor**: comment, documentation (inline), rename (simple), lint, style
- **Modifiers**: minor, small, quick, trivial, simple, tiny, brief

### STANDARD keywords (+0.2 each match)
- **Development**: implement, add, create, update, fix, build, modify, change, edit
- **Removal**: remove, delete, deprecate

---

## Context Boosters

### File count boosters
- Task affects >2 files: +0.3 toward STRICT
- Task affects exactly 1 file: +0.1 toward LIGHT

### Path pattern boosters
- Paths contain `auth/`, `security/`, `crypto/`: +0.4 toward STRICT
- Paths contain `docs/`, `*.md`: +0.5 toward EXEMPT
- Paths contain `tests/`: +0.2 toward STANDARD

### Operation boosters
- Read-only operation: +0.4 toward EXEMPT
- Git operation: +0.5 toward EXEMPT

---

## Verification Routing

| Tier | Verification Method | Agent | Token Budget | Timeout |
|------|---------------------|-------|--------------|---------|
| STRICT | Sub-agent spawn | quality-engineer | 3-5K | 60s |
| STANDARD | Direct test execution | N/A | 300-500 | 30s |
| LIGHT | Quick sanity check | N/A | ~100 | 10s |
| EXEMPT | Skip verification | N/A | 0 | 0s |

---

## Quick Reference Tables

### Compound Phrase Overrides
| Phrase | Tier | Rationale |
|--------|------|-----------|
| "quick fix" | LIGHT | Modifier indicates triviality |
| "fix typo" | LIGHT | Content indicates triviality |
| "fix security" | STRICT | Security domain |
| "add authentication" | STRICT | Security domain |
| "update database" | STRICT | Data integrity |

### Context Booster Summary
| Signal | Tier Boost | Amount |
|--------|------------|--------|
| >2 files affected | STRICT | +0.3 |
| auth/security/crypto path | STRICT | +0.4 |
| docs/*.md path | EXEMPT | +0.5 |
| read-only operation | EXEMPT | +0.4 |
| git operation | EXEMPT | +0.5 |
