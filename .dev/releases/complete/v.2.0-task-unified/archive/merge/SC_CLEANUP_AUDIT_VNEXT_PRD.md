# sc:cleanup-audit vNext — PRD / Specification

**Date:** 2026-02-20
**Repo context:** `/config/workspace/GFxAI`
**Primary inputs:**
- Gap analysis: `docs/generated/repo-cleanup/SC_CLEANUP_AUDIT_PROMPT_GAP_ANALYSIS.md`
- Current audit output sample: `.dev/analysis/.claude-audit-2/FINAL-REPORT.md`
- Legacy prompt set: `.dev/releases/current/repo-cleanup/cleanup-prompts/CLEANUP-audit-prompt*.md`

---

## 1) Problem statement

The current `sc:cleanup-audit` command produces strong **Pass 1–3** (surface triage + structural profiles + cross-cutting duplication matrices), but it fails to reliably produce several **high-leverage outcomes** that the legacy cleanup-audit prompt set forced:

1. **No first-class docs QA pass** (legacy Pass 4). Documentation correctness and overlap are mostly deferred.
2. **No known-issues suppression / continuity mechanism** across passes and across audit runs.
3. **Per-file evidence schema is not consistently applied** outside the small subset of Pass 2 profiles.
4. **Broken-reference reporting is weaker** (format + systematic sweep), especially for docs.
5. **No explicit ARCHIVE-vs-DELETE guidance** for temporal documentation artifacts.

Net effect: the output is often insightful at the repo level but less “engineer-executable” for documentation and for long-lived cleanup programs, where repeated rediscovery and doc drift dominate.

---

## 2) Goals and non-goals

### Goals

G1. Add a **Pass 4: Docs Quality** pass that produces actionable, verifiable doc findings (broken links, overlap groups, archival candidates, claim spot-checks).

G2. Add a **Known Issues Registry** mechanism so repeated findings are suppressed with attribution rather than re-flagged each run.

G3. Harden output schemas so critical buckets are consistently emitted:
- `BROKEN_REFERENCES` in checklist format
- `ARCHIVE` (temporal artifacts) distinct from `DELETE`
- `FLAG` (requires code changes)
- `REMAINING / NOT_YET_AUDITED` coverage accounting

G4. Preserve the current system’s strengths: evidence-backed triage, duplication matrices, conservative deletion.

G5. Maintain cost control: avoid unbounded doc analysis and keep outputs scannable.

### Non-goals

N1. This is not a “cleanup executor.” vNext remains read-only. No automated delete/move operations.

N2. This is not a full semantic doc correctness checker. Pass 4 focuses on **structural correctness** (paths, referenced files, ports, scripts), plus overlap detection and link integrity.

N3. No attempt to eliminate human judgment; archive/delete decisions remain recommendations.

---

## 3) Target users and core use cases

- **Repo maintainers** running periodic audits to keep repo size, CI, and onboarding sane.
- **Onboarding authors** needing to ensure docs don’t point to dead scripts, wrong paths, or stale architectures.
- **DevOps owners** tracking deploy/config drift and preventing “competing systems sprawl.”

Primary use cases:

U1. “Run audit and get an action list I can execute immediately.”

U2. “Run audit weekly without re-discovering known issues.”

U3. “Find broken doc links and stale release artifacts without reading the entire docs tree.”

---

## 4) vNext functional requirements (what the command must do)

### 4.1 Pass structure

- Pass 1: Surface Scan (existing)
- Pass 2: Structural Audit (existing)
- Pass 3: Cross-Cutting Audit (existing)
- **Pass 4: Docs Quality (new; mandatory when `--pass all`)**

`--pass` must accept `docs` in addition to existing options:
- `--pass surface|structural|cross-cutting|docs|all`

### 4.2 Output artifacts (directory)

The command must emit a stable output bundle containing:

- `pass1/pass1-summary.md`
- `pass2/pass2-summary.md`
- `pass3/pass3-summary.md`
- `pass4/pass4-summary.md` (new)
- `FINAL-REPORT.md` (updated)
- `progress.json` (updated schema; see §6)
- `known-issues.json` (optional, if registry exists)

### 4.3 Pass 4 — Docs Quality outputs (required sections)

Pass 4 summary MUST contain these top-level sections:

1. `SCOPE`
   - Directories/files scanned
   - Sampling policy used (if any)

2. `CONTENT_OVERLAP_GROUPS`
   - Cluster docs by topic/overlap (heuristic allowed)
   - For each group:
     - Canonical doc recommendation
     - Superseded candidates
     - Rationale (short)

3. `BROKEN_REFERENCES`
   - Checklist format:
     - `- [ ] path/to/doc.md:line → missing/relative/path (context)`
   - Only relative links are required by default; external links are optional.
   - Output must be capped (e.g., first N items) with a total count.

4. `CLAIM_SPOT_CHECKS`
   - For sampled docs: verify 3–5 **structural claims** per doc.
   - Allowed claim types:
     - referenced file exists
     - referenced script name exists
     - referenced port matches authoritative spec (if present)
     - referenced docker-compose file exists

5. `TEMPORAL_ARTIFACTS`
   - Explicitly label docs as one of:
     - `KEEP`
     - `ARCHIVE` (move to archive tree)
     - `DELETE`
   - Provide short rationale and (if ARCHIVE) suggested destination.

### 4.4 Known Issues Suppression Registry

The system must support an optional **known issues registry**.

Requirements:

- Input format: JSON (preferred) stored at a predictable path in the audit output root OR repo root (configurable via rule).
- Each known issue entry must include:
  - `id` (stable identifier)
  - `signature` (machine matchable string/regex)
  - `category` (e.g. docs, infra, security, repo-bloat)
  - `created_at` (date)
  - `status` (open|closed|monitor)
  - `reference` (link-like string, e.g. “tracked in cleanup ticket #123”)

Suppression rule:

- If a finding matches a known issue signature, it must be reported **once** under an `ALREADY_TRACKED` section and must not be duplicated under primary finding sections.
- Suppression must be conservative:
  - Prefer matching by “finding signature” (category + key path + short invariant text), not by path alone.
  - If file moved/renamed, suppress only if signature still matches.

### 4.5 Broken-reference sweep (systematic)

- Pass 3 and Pass 4 must have an explicit broken-reference routine.
- Output must be in checklist format and include at least:
  - missing compose/config references from scripts
  - missing relative doc links

### 4.6 “FLAG” bucket (needs code changes)

The audit must contain a dedicated `FLAG` bucket in Pass 3 (and optionally in Final Report), listing actions that require code edits to safely execute the cleanup.

Examples:
- merging compose files requires editing deployment scripts
- moving docs requires updating cross-links

---

## 5) vNext architecture and integration plan (SuperClaude)

### 5.1 Where changes live

Primary implementation surface (existing in SuperClaude):
- `src/superclaude/skills/sc-cleanup-audit/SKILL.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/`
- `src/superclaude/skills/sc-cleanup-audit/templates/`

vNext additions:

- Add rules file:
  - `src/superclaude/skills/sc-cleanup-audit/rules/pass4-docs-quality.md`

- Update SKILL routing/orchestration to include Pass 4 when requested.

- Update templates:
  - `templates/pass-summary.md` (to support Pass 4 sections) OR add a dedicated `templates/pass4-summary.md`
  - `templates/final-report.md` to add:
    - Pass 4 results
    - `ARCHIVE` bucket
    - `ALREADY_TRACKED` bucket
    - `FLAG` section summary

### 5.2 Subagent strategy

Default approach: reuse existing agents and only add a new specialized agent if Pass 4 quality is consistently poor.

Option A (preferred):
- Use existing audit-scanner/audit-analyzer for docs sampling + link extraction.

Option B:
- Add `audit-docs` subagent specialized for markdown/doc analysis and link integrity.

Cost controls (mandatory regardless of option):
- Sampling for large doc trees
- Cap the number of broken-link checklist items emitted
- Prioritize structural claim checks

---

## 6) Data model changes

### 6.1 progress.json schema additions

Add fields:
- `passes.pass4_docs.status` (not_started|in_progress|complete)
- `passes.pass4_docs.sampled_files` (count)
- `passes.pass4_docs.broken_refs_count`
- `known_issues.used` (bool)
- `known_issues.suppressed_count`
- `archive_candidates.count`
- `flag_items.count`

---

## 7) Quality gates and acceptance criteria

### Acceptance criteria (must pass)

A1. Running `--pass all` produces Pass 1–4 outputs and the final report includes Pass 4 sections.

A2. Pass 4 output includes:
- overlap groups
- broken references checklist with `filepath:line → missing` format
- temporal artifacts labeled with KEEP/ARCHIVE/DELETE
- claim spot-checks (3–5 per sampled doc)

A3. If a known issues registry is present, findings matching it:
- appear in `ALREADY_TRACKED`
- do not reappear in primary lists

A4. Pass 3 includes a dedicated `FLAG` section.

A5. Large directories (50+ files) receive a directory-level assessment block including:
- sample list
- assessment label
- recommendation

### Verification approach

- Golden-output fixtures:
  - small synthetic repo containing:
    - a few markdown docs with relative links (some broken)
    - a script referencing a missing compose file
    - a known-issues registry entry that matches one of the above

- Regression checks:
  - ensure Pass 1–3 outputs remain substantially unchanged unless explicitly improved

---

## 8) Expert panel critique synthesis (spec quality improvement)

This section simulates the `/sc:spec-panel --mode critique` output by applying its named frameworks.

### Karl Wiegers (requirements quality)

- Requirements are clear and testable when they define:
  - the exact output sections that must exist (done)
  - caps and sampling rules to prevent runaway output (done)
  - conservative suppression logic to avoid hiding new issues (done)

- Improvement recommendation:
  - Add explicit “default thresholds” (e.g., sampling size, max broken links emitted) so implementations converge.

### Martin Fowler (architecture)

- Keep the change set evolutionary:
  - introduce Pass 4 as an additive pass
  - avoid coupling pass outputs tightly to a specific repo structure

- Improvement recommendation:
  - treat ARCHIVE as a label that can be mapped to “move recommendation,” not a mandatory directory rename.

### Lisa Crispin (testing)

- Ensure testability by using fixture repos and golden outputs.

- Improvement recommendation:
  - define a minimal contract test suite for link parsing, signature matching, and section presence.

---

## 9) Adversarial review (risks and mitigations)

### Risk: Pass 4 token cost explodes on large docs/

Mitigation:
- sampling defaults
- cap broken-link output; provide totals
- restrict claim checks to structural claims

### Risk: Known-issues suppression hides net-new regressions

Mitigation:
- signature-based matching with conservative rules
- output suppressed findings in a dedicated `ALREADY_TRACKED` section
- add “recheck on rename/move” guardrail

### Risk: ARCHIVE label adds decision complexity

Mitigation:
- scope ARCHIVE to docs/ and release artifacts only
- keep a small set of rules: archive temporal evidence, keep canonical references

---

## 10) Implementation backlog (feature sprint)

1. Add Pass 4 rules file and wire it into skill orchestration.
2. Update templates to support Pass 4 sections and ARCHIVE/FLAG/ALREADY_TRACKED buckets.
3. Implement docs relative-link extractor + existence checker; emit checklist format.
4. Implement doc overlap grouping heuristic + canonical doc selection.
5. Implement claim spot-check routine (structural claims only).
6. Implement known-issues registry parsing + conservative signature suppression.
7. Add directory-level assessment blocks for large directories.
8. Add `.env*` key matrix (Pass 3 add-on; optional but cheap).
9. Add golden fixture tests + regression checks.
10. Update documentation for `/cleanup-audit --pass docs|all` usage.
