# sc:cleanup-audit prompt gap analysis (old prompts → new output)

**Date:** 2026-02-20
**Repo:** `/config/workspace/GFxAI`
**Old prompt set:** `/config/workspace/GFxAI/.dev/releases/current/repo-cleanup/cleanup-prompts/`
- Pass 1: `CLEANUP-audit-prompt.md`
- Pass 2: `CLEANUP-audit-prompt-2.md`
- Pass 3: `CLEANUP-audit-prompt-3.md`
- Pass 4: `CLEANUP-audit-prompt-4.md`

**New audit output analyzed:** `/config/workspace/GFxAI/.dev/analysis/.claude-audit-2/`
- `FINAL-REPORT.md`
- `pass1/pass1-summary.md`
- `pass2/pass2-summary.md`
- `pass3/pass3-summary.md`
- `progress.json`

**Purpose:** Identify which old prompt requirements/constraints produced desirable outcomes that are **missing or weaker** in the new `sc:cleanup-audit` output, and propose a concrete incorporation approach for a next version.

---

## Executive findings (what the old prompts forced that the new output is missing)

### Highest-impact missing outcomes

1. **Docs quality pass (Pass 4) is absent**
   - The old process had a dedicated documentation QA pass with claim spot-checks, overlap grouping, temporal-artifact handling, and ARCHIVE vs DELETE decisions.
   - The new output does **not** execute any equivalent pass; documentation is mostly deferred to “review later”.

2. **Known-issues suppression / continuity across passes is absent**
   - Old Pass 3 prompt required a *known issues list* (34 items) and a “don’t re-flag, link to issue #N” rule.
   - New output has no explicit mechanism for “already-known” findings, so audits can waste effort re-discovering items.

3. **Per-file profile schema is weaker / inconsistently enforced in practice**
   - Old prompts demanded per-file structured profiles for audited files.
   - New run produced **12 structural profiles** (Pass 2) but Pass 3 output is largely aggregate matrices/tables; many actionable items (esp. docs) have no per-file profile.

4. **Broken-reference reporting format and systematic sweep are weaker**
   - Old prompts required explicit checklist format `filepath:line → missing` (especially for docs).
   - New output surfaced at least one broken reference, but does not provide a systematic docs link sweep and does not consistently use checklist formatting.

5. **Archive-vs-delete for temporal documentation artifacts is missing**
   - Old Pass 4 explicitly distinguished: KEEP vs DELETE vs ARCHIVE (`docs/archive/`).
   - New output uses DELETE/REVIEW/KEEP/UNTRACK but no explicit ARCHIVE guidance for docs and release artifacts.

---

## Evidence-backed delta (Pass-by-pass synthesis)

### Pass 1 (surface scan): key deltas

**Old prompt intent:** conservative classification, incremental save discipline, reference checks, “err on KEEP”, explicit sections including “Add to .gitignore”.

**New output strengths:**
- Strong top-level triage and repo-scale metrics.
- Corrected prior false positives (local-only `.pyc`, logs, caches).

**New output gaps vs old prompt requirements:**
- Gitignore recommendations are not consistently elevated into a dedicated section.
- Incremental save discipline is implemented differently (multi-file report artifacts), but “coverage bookkeeping” per cluster/directory is less explicit.

### Pass 2 (structural audit): key deltas

**Old prompt intent:** file-by-file proof, mandatory profile fields, verification discipline, explicit “Needs Flagging” for items requiring code changes.

**New output strengths:**
- The 12 “mandatory structural profiles” are high-signal and include evidence commands.

**New output gaps vs old prompt requirements:**
- Profiles exist for a small subset; many REVIEW items don’t receive profile-level evidence.
- “Nature taxonomy” and some doc-specific claim verification behaviors are weaker than what old prompt demanded.
- A dedicated “Needs Flagging” output category is not consistently present as an explicit section.

### Pass 3 (cross-cutting): key deltas

**Old prompt intent:** “compare, don’t just catalog”, duplication matrices, directory-level assessments for large dirs, known-issues suppression, broken reference checklists, completion/remaining tracking.

**New output strengths:**
- Duplication matrices (compose/deploy/playwright/nginx/deployment systems) are the best part of the new output and align with the old intent.

**New output gaps vs old prompt requirements:**
- No explicit known-issues suppression mechanism.
- Large directories (docs, releases, generated artifacts) are often summarized but not assessed with “sample reviewed files + assessment label”.
- Missing “Remaining/not-yet-audited” and other integrity-style completion artifacts.

### Pass 4 (docs audit): missing entirely

**Old prompt intent:** docs claim spot-checks (3–5 claims/doc), overlap groups, broken links, superseded-by checks vs authoritative doc trees, temporal artifact handling, ARCHIVE vs DELETE.

**New output status:**
- No pass 4.
- Docs are frequently deferred, so the audit has near-zero signal about documentation correctness.

---

## Concrete incorporation proposals (best approach to bring the old improvements into sc:cleanup-audit)

This section focuses on changes to the **sc:cleanup-audit system** (rules/templates/orchestration) that reliably yield the missing outcomes.

### P0 (must-have): Add Pass 4 “Docs Quality” as a first-class pass

**Scope:** `docs/` (exclude known reference trees if desired), root markdown files, `.dev/releases/complete/` or similar temporal doc areas.

**Outputs:**
- Content Overlap Groups (topic clusters + canonical doc)
- Broken References (checklist format)
- ARCHIVE candidates (move to `docs/archive/`)
- DELETE candidates
- KEEP candidates with “currently useful” rationale

**Cost control:**
- Use directory-level sampling for huge trees (sample 5–10 representative docs).
- Constrain claim verification to *structural claims* first (paths, filenames, ports, referenced scripts).

### P0 (must-have): Known-issues suppression registry

**Mechanism:**
- Pass 3 (and Pass 4) receives a “Known issues list” derived from prior passes + previous audit runs.
- Output rule: if finding matches a known issue, report it once as `Already tracked as issue #N` and do not re-flag.

**Value:**
- Prevents the “audit thrash” where each run re-discovers the same problems.

### P1: Enforce broken-reference checklist formatting + systematic docs sweep

**Mechanism:**
- Output schema requires:
  - `- [ ] filepath:line → missing/path - context`
- Add a docs link extraction step for relative links.

### P1: Expand “FLAG” section (needs code changes) as a formal output bucket

**Why:**
- Many consolidation actions are not file operations; they require code edits.

**Output:**
- A dedicated list of items requiring code changes before cleanup execution.

### P1: Directory-level assessment blocks for “50+ file” directories

**Mechanism:**
- For large directories, output:
  - Sample list
  - Overall assessment label (actively maintained / stale / bulk dump / mixed)
  - Recommendation

### P2: .env key matrix comparison (cheap, high impact)

**Mechanism:**
- Extract keys across `.env*` templates.
- Output a key-presence matrix.

---

## Adversarial debate (validate + sanity-check the proposals)

### Proposal: Add Pass 4 docs audit

**FOR:**
- The audit currently has near-zero evidence about doc correctness; stale docs cause onboarding failures.

**AGAINST:**
- High token cost; docs correctness can be subjective.

**MITIGATIONS:**
- Restrict to structural claim checks (paths/ports/names) and overlap grouping; avoid deep semantic correctness unless triggered by anomalies.

### Proposal: Known-issues suppression registry

**FOR:**
- Eliminates repeated rediscovery and allows audits to focus on net-new drift.

**AGAINST:**
- Requires maintaining a registry and avoiding false suppression.

**MITIGATIONS:**
- Suppress by “finding signature” not by filepath alone; include a “recheck if file moved/renamed” rule.

### Proposal: Broken-reference checklist + systematic docs sweep

**FOR:**
- Produces directly actionable tasks; docs broken links are easy wins.

**AGAINST:**
- Can generate lots of noise.

**MITIGATIONS:**
- Limit to relative links; cap output to top N broken links + counts.

---

## Implementation pointers (where this likely lives in SuperClaude)

The sc:cleanup-audit skill is defined in SuperClaude at:
- `src/superclaude/skills/sc-cleanup-audit/SKILL.md`

Rules/templates exist for:
- Pass 1: `src/superclaude/skills/sc-cleanup-audit/rules/pass1-surface-scan.md`
- Pass 2: `src/superclaude/skills/sc-cleanup-audit/rules/pass2-structural-audit.md`
- Pass 3: `src/superclaude/skills/sc-cleanup-audit/rules/pass3-cross-cutting.md`

**Notably missing:** no Pass 4 rules file exists in the skill’s rules directory.

---

## Next deliverables

1. `/sc:reflect` style validation of the above proposals (consistency, feasibility, and whether they actually address observed gaps).
2. A PRD/spec for “sc:cleanup-audit vNext” incorporating Pass 4 + known-issues suppression + output schema hardening.
