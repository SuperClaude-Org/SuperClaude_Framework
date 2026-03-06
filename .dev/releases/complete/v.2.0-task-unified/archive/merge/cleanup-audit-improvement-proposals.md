# sc:cleanup-audit Improvement Proposals

**Date**: 2026-02-20
**Method**: 4-agent parallel debate on 15 findings from Phase 1 analysis
**Agents**: System Architect, Quality Engineer, Performance Engineer, Refactoring Expert

---

## Debated Priority Ranking (Consensus)

After rigorous debate across all 4 agents, the implementation priority differs from the original classification. The agents reached consensus on a revised ordering based on impact-to-cost ratio:

### Tier 1: Must Implement (Highest ROI)

| # | Finding | Original | Revised | Rationale |
|---|---------|----------|---------|-----------|
| 1 | **Cross-Reference Resolution Phase** (F8) | HIGH | CRITICAL | Only mechanism that detects cross-boundary dead code. Operates on scanner outputs (bounded cost). Adds a capability category that is entirely absent. |
| 2 | **Credential File Scanning Fix** (F6) | HIGH | CRITICAL | False negative on real credentials is a correctness failure. The cost of reading 5-10 env files (~10K tokens) is bounded; the cost of missing real secrets is unbounded. Non-negotiable. |
| 3 | **Coverage Guarantee** (F13) | HIGH | CRITICAL | Structural prerequisite for trusting any audit output. Implement as tiered coverage contracts (100% critical files, 95% high, 80% standard, 60% low). |
| 4 | **Evidence-Mandatory KEEP** (F2) | CRITICAL | CRITICAL | Tiered approach: full 3-field check for high-risk files (top 10-20%), pattern-match for config/generated, relational for tests/docs. |

### Tier 2: Should Implement (High Value)

| # | Finding | Original | Revised | Rationale |
|---|---------|----------|---------|-----------|
| 5 | **File-Type-Specific Verification** (F4) | HIGH | HIGH | Reframed as Contextual Risk Classification with tiered rule registry loaded from project config. |
| 6 | **Batch Decomposition** (F3) | CRITICAL | HIGH | Dynamic batch generation (not static file lists). Risk-weighted parallel scanning with logged assignments for reproducibility. |
| 7 | **Anti-Lazy-Agent Enforcement** (F9) | HIGH | HIGH | Reframed as structured output validation with calibration files, not minimum tool-call counts. |
| 8 | **Recommendation Categories** (F10) | MEDIUM | HIGH | Two-tier system: Primary action (DELETE/KEEP/MODIFY) + secondary qualifier (archive-first, consolidate-with, flag:issue). |

### Tier 3: Implement with Constraints

| # | Finding | Original | Revised | Rationale |
|---|---------|----------|---------|-----------|
| 9 | **Documentation Audit Pass** (F1) | CRITICAL | MEDIUM | Opt-in flag (`--pass documentation`). Cap at 20% of token budget. Pre-filter auto-generated and historical docs. |
| 10 | **Known-Issue Tracking** (F5) | HIGH | MEDIUM | Post-hoc deduplication in consolidator instead of sequential registry. Preserves parallelism. |
| 11 | **Subagent Specialization** (F12) | MEDIUM | MEDIUM | Scan profile detection as lightweight Pass 0. Model assignment by domain (Haiku for mechanical, Sonnet for semantic). |
| 12 | **Progressive Depth** (F11) | MEDIUM | MEDIUM | Two-level triggered approach (50 lines default, full file on signal triggers), not four-level ladder. |

### Tier 4: Enhancements

| # | Finding | Original | Revised | Rationale |
|---|---------|----------|---------|-----------|
| 13 | **Incremental Save** (F7) | MEDIUM | LOW | Pass-level checkpointing in orchestrator (4 file writes total), not file-level saves. |
| 14 | **Broken Reference Collection** (F14) | LOW | LOW | Mandatory output section in comparator pass with severity classification. |
| 15 | **Gitignore Consistency** (F15) | MEDIUM | LOW | Pre-audit gate with risk sub-classification. Separate from main audit loop. |

---

## Proposal 1: Cross-Reference Resolution Phase

**Debate outcome**: Unanimous support. Highest ROI improvement.

### Approach
Add a mandatory post-scan synthesis phase that:
1. **Pre-scan**: Publish a required output schema to all domain scanners
2. **Post-scan Stage 1**: Build a directed graph (files as nodes, import/export as edges)
3. **Post-scan Stage 2**: Flag nodes with no incoming edges as cross-boundary dead code candidates
4. **Confidence-weighted output**: Files >3 hops from entry points get DELETE-CANDIDATE; 1-3 hops get INVESTIGATE

### Output Schema for Scanners
```json
{
  "scanner_id": "frontend-components",
  "domain": "frontend/components/",
  "files": [{
    "path": "frontend/components/Button.tsx",
    "classification": "KEEP",
    "evidence": { "import_references": [...], "last_commit_days": 14 },
    "external_dependencies": ["frontend/hooks/useWizard.ts"],
    "export_targets": ["frontend/components/index.ts"]
  }]
}
```

### Key Constraint (from debate)
Cross-boundary findings should use INVESTIGATE classification (not DELETE) when the evidence chain exceeds 3 hops. Re-export barrel files and dynamic imports create false positives at shallow depth.

---

## Proposal 2: Credential File Scanning Fix

**Debate outcome**: Unanimous — non-negotiable fix. Not a depth tradeoff.

### Approach
Targeted file enumeration with explicit template detection:
1. Enumerate by priority: `.env.production` → `.env.prod` → `.env` → `.env.local/.staging/.test`
2. Skip template files by convention: `.env.example`, `.env.template`, `.env.sample`
3. Pattern-match for real credentials: `sk-*`, `ghp_*`, `AKIA*`, base64 >40 chars, `BEGIN RSA`
4. Pattern-match for templates: `CHANGE_ME_*`, `YOUR_*_HERE`, `<placeholder>`
5. **Never print credential values** — only confirm presence/absence

### Key Constraint (from debate)
This is not a security audit substitute. Include explicit disclaimer in output: "This credential scan is limited to .env file detection. Use dedicated tools (truffleHog, detect-secrets) for comprehensive security scanning."

---

## Proposal 3: Coverage Guarantee (Tiered)

**Debate outcome**: Strong support with threshold refinement.

### Approach: Manifest-First Execution
```
1. Pre-audit: Generate file manifest with tier classification
   - Critical: deployment scripts, CI/CD, migrations → 100% coverage
   - High: configs, compose, env templates → 95% coverage
   - Standard: source code, tests → 80% coverage
   - Low: assets, generated, docs → 60% coverage
2. During audit: Manifest tracks examined/pending status per file
3. Post-audit: Coverage report per tier
4. Unexamined files: Auto-flagged as REVIEW with "unexamined_by_audit" rationale
```

### Key Constraint (from debate)
The manifest must define a clear exclusion list (node_modules, .git, generated output) as first-class config. The 80% threshold is a guideline, not a gate — the audit should always complete and report coverage, never fail silently.

---

## Proposal 4: Evidence-Mandatory KEEP (Tiered)

**Debate outcome**: Strong support with stratification.

### Approach: Stratified Evidence Requirements
- **Tier A (feature code)**: Full 3-field check — import reference, commit recency, test coverage
- **Tier B (config/generated)**: Pattern-match classification with source annotation
- **Tier C (test/doc/script)**: Relational classification (annotated with file they serve)
- **Tier D (core framework)**: Structural position classification (framework-required)

### Key Constraint (from debate)
Tier A = top 10-20% of files by deletion risk (no test coverage, long no-commit period, single-location import). Do NOT require import-graph evidence for config files (loaded by tooling, not code) or dynamic imports. Produce "unverified KEEP" category for Tier B/C/D.

---

## Proposal 5: File-Type-Specific Verification (Contextual Risk Classification)

**Debate outcome**: Support with reframing from extension-based to risk-based.

### Approach: Tiered Rule Registry
```yaml
# Loaded from audit.config.yaml (project-specific)
risk_tiers:
  critical:
    path_patterns: ["**/infrastructure/**/*.sh", "**/scripts/deploy*", "**/.github/workflows/*.yml"]
    checks: [canonical_ports, destructive_ops, secret_patterns]
  high:
    path_patterns: ["**/migrations/*.sql", "**/docker-compose*.yml", "**/*.env*"]
    checks: [canonical_ports, secret_patterns, service_drift]
  standard:
    path_patterns: ["**/*.py", "**/*.ts", "**/*.tsx"]
    checks: [skip_markers, debug_statements, todo_density]
```

### Key Constraint (from debate)
Port lists and destructive patterns must be loaded from project config, not hardcoded. Command should fail explicitly if config is absent rather than silently applying defaults. Template files (heredoc env vars) should not be flagged as hardcoded values.

---

## Proposal 6: Dynamic Batch Decomposition

**Debate outcome**: Support with emphasis on dynamic generation over static file lists.

### Approach: Two-Phase Risk-Weighted Scanning
**Phase 1 (Pre-audit, 30-60s)**: Lightweight directory analysis producing:
- Batch manifest (JSON) mapping scanner IDs to file lists
- Risk scores per directory (0.0-1.0)
- Cross-reference annotations for high-traffic import boundaries

**Phase 2 (Parallel scanning)**: Risk-calibrated depth:
- Risk > 0.7: Deep profile (full 5-field check per file)
- Risk 0.4-0.7: Standard profile (3-field check)
- Risk < 0.4: Shallow profile (exists + commit date)

### Key Constraint (from debate)
Log the generated batch assignments at audit start for reproducibility. Target: no directory with risk > 0.5 has <30% files profiled at standard depth.

---

## Proposal 7: Anti-Lazy-Agent Enforcement (Output Validation)

**Debate outcome**: Support with reframing from procedural enforcement to output quality validation.

### Approach: Structured Output Validation with Calibration Files
1. **Required decision schema**: `file_path`, `decision` (enum), `rationale_category` (enum), `evidence_reference` (optional), `confidence` (0.0-1.0)
2. **Calibration files**: Include known-good and known-bad files in every batch. Agent failing calibration checks triggers full re-review of its batch.
3. **Cross-agent consistency**: Compare KEEP/DELETE decisions across agents for overlapping file sets. Inconsistency triggers targeted re-review.
4. **"Insufficient evidence" rationale**: Allowed but triggers escalation, not rejection.

### Key Constraint (from debate)
Do NOT enforce minimum tool-call counts (gameable, penalizes correct simple-file judgments). Enforce output structure and calibration correctness instead.

---

## Proposal 8: Two-Tier Recommendation Categories

**Debate outcome**: Strong support for composable two-tier system.

### Approach
**Primary Action** (what to do):
- `DELETE` — remove the file
- `KEEP` — no action needed
- `MODIFY` — keep but change something

**Secondary Qualifier** (specifics):
- DELETE: `standard` | `archive-first`
- KEEP: `standard` | `monitor`
- MODIFY: `fix-references` | `consolidate-with:[target]` | `update-content` | `flag:[issue]`

### Report Structure
```
Executive Summary
├── DELETE (standard): N files
├── DELETE (archive-first): N files
├── MODIFY (consolidate): N pairs
├── MODIFY (fix-references): N files
├── MODIFY (flag:issue): N files
└── KEEP: N files (M unverified)
```

---

## Proposal 9: Documentation Audit Pass (Opt-In)

**Debate outcome**: Support as opt-in, not default.

### Approach
- Activated via `--pass documentation` or `--pass all` flag
- Pre-filter: Exclude auto-generated, ADRs, changelogs, third-party docs
- Classify remaining: API-reference, setup-guide, architecture, conceptual
- Claim spot-checking: 3 claims per doc, only for API-reference and setup-guide categories
- Output: CURRENT / OUTDATED / ARCHIVE / DELETE
- **Hard cap**: 20% of total audit token budget

---

## Proposal 10: Post-Hoc Deduplication (Not Registry)

**Debate outcome**: Deduplication in consolidator, not inter-pass registry.

### Approach
Add to consolidator prompt:
1. Group findings by file path
2. Cluster within-file findings by issue category
3. Keep highest-severity instance of duplicates
4. Mark cross-pass-confirmed findings as "high confidence"
5. Remove remaining duplicates before synthesis

**Cost**: ~500 tokens in consolidator prompt. Zero runtime overhead. Zero parallelism loss.

---

## Proposal 11: Scan Profile Detection + Model Assignment

**Debate outcome**: Support as lightweight Pass 0.

### Approach
```
Pass 0 (Haiku, 30s): Profile repository
  Output: { domains_detected: [infrastructure, source, assets, docs], file_counts: {...} }

Pass 1+: Domain-parallel scanning with model assignment
  - Infrastructure (mechanical): Haiku
  - Assets (grep-only): Haiku
  - Source code (semantic): Sonnet
  - Documentation (semantic): Sonnet
```

### Key Constraint
Repositories without detected domains don't spawn those scanners. `--scan-profile auto|infra|source|assets|docs|all` flag for override.

---

## Proposal 12: Signal-Triggered Depth (Two-Level)

**Debate outcome**: Support for simplified two-level system, not four-level ladder.

### Approach
- Default: 50-line read per file
- Triggers for full-file read:
  - Credential-adjacent imports (dotenv, config, secrets)
  - TODO/FIXME/HACK in first 50 lines
  - Complex conditional logic
  - `eval`, `exec`, `dangerouslySetInnerHTML`
  - File size > 300 lines

**Estimated overhead**: +15-20% analysis tokens (vs 60% for four-level system).

---

## Estimated Impact Summary

| Metric | Current | After Tier 1 | After Tier 1+2 | After All |
|--------|---------|-------------|----------------|-----------|
| Runtime | ~45 min | ~55 min | ~65 min | ~75 min |
| Token cost | Baseline | +25% | +50% | +80% |
| Files profiled | 12 | ~200 | ~500+ | ~700+ |
| Cross-boundary detection | None | Full | Full | Full |
| Credential scanning | Wrong answer | Correct | Correct | Correct |
| Coverage tracking | None | Tiered | Tiered | Tiered |
| Recommendation types | 3 | 3 | 6 (two-tier) | 6+ |
| Documentation audit | None | None | None | Opt-in |

---

*Generated by 4-agent parallel debate | 2026-02-20*
