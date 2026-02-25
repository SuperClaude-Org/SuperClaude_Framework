# D-0003 — Tier Classification Policy for Executable `.md` Files

**Task**: T01.03 — Tier Classification Policy
**Roadmap Item**: R-003
**Date**: 2026-02-24
**Decision Reference**: D-T01.03

---

## Policy Statement (Rule 7.6)

**Executable `.md` files are NOT documentation. They are executable specifications and MUST be classified as STANDARD minimum compliance tier.**

### Definition

An executable `.md` file is any markdown file that:
1. Contains behavioral instructions that Claude Code interprets and executes
2. Has YAML frontmatter with `allowed-tools:`, `name:`, or `description:` fields
3. Resides in one of these paths:
   - `src/superclaude/commands/*.md` — Command files (Tier 0)
   - `src/superclaude/skills/*/SKILL.md` — Skill protocol files (Tier 1)
   - `src/superclaude/agents/*.md` — Agent definition files
4. Is loaded by Claude Code as part of the invocation chain

### Classification Rule

| File Type | Location Pattern | Minimum Tier | Rationale |
|-----------|-----------------|--------------|-----------|
| Command file | `commands/*.md` | STANDARD | Modifies invocation behavior; incorrect frontmatter breaks tool dispatch |
| SKILL.md | `skills/*/SKILL.md` | STANDARD | Full behavioral protocol; errors cause incorrect agent behavior |
| Agent definition | `agents/*.md` | STANDARD | Agent dispatch instructions; errors cause wrong agent selection |
| Ref file | `skills/*/refs/*.md` | STANDARD | Step-specific detail; errors cause incorrect step execution |
| Documentation | `docs/**/*.md`, `*.md` (root) | EXEMPT | No executable behavior; read-only reference |
| Planning artifacts | `.dev/**/*.md` | EXEMPT | No executable behavior; planning/tracking only |

### Override Conditions

Tier may be escalated above STANDARD when:
- File involves security-sensitive paths (`auth/`, `security/`, `crypto/`) → STRICT
- File involves multi-file atomic changes (e.g., command + skill rename pair) → STRICT
- File involves complex protocol decomposition (e.g., Wave 2 Step 3) → STRICT

Tier may NOT be reduced below STANDARD for executable `.md` files. The `.md` extension does not make a file documentation.

---

## Downstream Task Tier Assignments

Per this policy, the following downstream tasks that modify executable `.md` files are assigned compliance tiers:

| Task ID | File(s) Modified | Assigned Tier | Rationale |
|---------|-----------------|---------------|-----------|
| T02.01 | `roadmap.md` (command) | LIGHT | Single frontmatter field addition |
| T02.02 | `SKILL.md` (skill) | LIGHT | Single frontmatter field addition |
| T02.03 | `SKILL.md` (skill) | STRICT | Complex protocol decomposition (3a-3f) |
| T02.04 | `roadmap.md` (command) | LIGHT | Section rewrite, simple content |
| T02.05 | 5 skill directories + SKILL.md files | STRICT | Multi-file rename with cross-references |
| T06.03 | `task-unified.md` (command) + SKILL.md | STRICT | Major extraction (-461 lines) |
| T06.04 | 4 command files | STRICT | Multi-file `## Activation` additions |

**Verification**: All 9 tasks that modify executable `.md` files have STANDARD or higher tier. Zero EXEMPT assignments for executable `.md` modifications.

---

## Consistency Check

This policy is consistent with:
- Sprint-spec Decision D-T01.03: "executable `.md` files NOT exempt"
- Tasklist header Section 5.3: tier classification algorithm
- ORCHESTRATOR.md tier classification routing

---

*Artifact produced by T01.03 — Tier Classification Policy*
*Policy: `.md` extension ≠ documentation; SKILL.md is code*
