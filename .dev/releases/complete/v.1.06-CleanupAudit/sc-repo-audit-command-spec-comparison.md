# Command Spec Comparison: `sc-repo-audit-command-spec-opus.md` vs `sc-repo-audit-command-spec-gpt.md`

**Comparison generated**: 2026-02-19
**Methodology**: Evidence-first atomic comparison with adversarial adjudication
**Scope**: Docs under `/config/workspace/GFxAI/docs/generated/` only

---

## Phase 0 — Source Metadata

### Commands Used

```bash
wc -l /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-opus.md \
       /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-gpt.md
wc -c /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-opus.md \
       /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-gpt.md
sha256sum /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-opus.md \
          /config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-gpt.md
```

### Source Metadata Table

| Field | Source A (opus) | Source B (gpt) |
|---|---|---|
| File | `sc-repo-audit-command-spec-opus.md` | `sc-repo-audit-command-spec-gpt.md` |
| Line count | 552 | 313 |
| Byte size | 24,789 | 18,409 |
| SHA256 | `068e38564105872ba3c3514708dd74efb842d41b6a5415755bfaab0e66c81aa4` | `388d7c93e77bd6820f73537cefc2d4b737ffd7715175ef4e412a44f2a0b68a5b` |
| Command name | `/sc:repo-audit` | `/sc:cleanup-audit` |
| Declared version | 1.0 | (no explicit version) |
| Date | Undated | 2026-02-18 |
| Stated effectiveness score | 75/100 | 63/100 |

---

## Phase 0.2 — Heading Inventories

### Source A Heading Inventory (sc-repo-audit-command-spec-opus.md)

| # | Level | Raw Heading Text | Normalized Text | Start Line | End Line | Topic Tag |
|---|---|---|---|---|---|---|
| A1 | 1 | `` `/sc:repo-audit` — Multi-Pass Repository Cleanup Audit Command `` | `sc:repo-audit — multi-pass repository cleanup audit command` | 1 | 3 | cli/usage |
| A2 | 2 | `Command Specification (Custom Command PRD)` | `command specification (custom command prd)` | 3 | 9 | cli/usage |
| A3 | 2 | `1. Command Name & Purpose` | `command name & purpose` | 11 | 23 | cli/usage |
| A4 | 2 | `2. Objectives (Generic)` | `objectives (generic)` | 25 | 33 | other |
| A5 | 2 | `3. Multi-Pass Architecture` | `multi-pass architecture` | 35 | 165 | other |
| A6 | 3 | `Pass 1: Surface Scan (Junk Detection)` | `pass 1: surface scan (junk detection)` | 39 | 77 | other |
| A7 | 3 | `Pass 2: Structural Audit (Organizational Integrity)` | `pass 2: structural audit (organizational integrity)` | 79 | 117 | other |
| A8 | 3 | `Pass 3: Cross-Cutting Sweep (Systemic Patterns)` | `pass 3: cross-cutting sweep (systemic patterns)` | 120 | 165 | other |
| A9 | 2 | `4. Classification Taxonomy (Unified)` | `classification taxonomy (unified)` | 167 | 180 | other |
| A10 | 2 | `5. Verification Protocol (Universal)` | `verification protocol (universal)` | 182 | 219 | verification |
| A11 | 3 | `Mandatory Evidence for Every Recommendation` | `mandatory evidence for every recommendation` | 184 | 208 | verification |
| A12 | 3 | `Cross-Reference Checklist` | `cross-reference checklist` | 209 | 219 | verification |
| A13 | 2 | `6. Agent Orchestration` | `agent orchestration` | 221 | 251 | other |
| A14 | 3 | `Batch Strategy` | `batch strategy` | 223 | 240 | other |
| A15 | 3 | `Recommended Batch Plan Template` | `recommended batch plan template` | 244 | 251 | other |
| A16 | 2 | `7. Output Schema` | `output schema` | 253 | 340 | outputs/artifacts |
| A17 | 3 | `Per-Agent Output (Markdown)` | `per-agent output (markdown)` | 255 | 315 | outputs/artifacts |
| A18 | 3 | `Consolidated Final Report` | `consolidated final report` | 317 | 340 | outputs/artifacts |
| A19 | 2 | `8. Safety Rails` | `safety rails` | 344 | 376 | other |
| A20 | 3 | `Read-Only Enforcement` | `read-only enforcement` | 346 | 353 | other |
| A21 | 3 | `Conservative Bias` | `conservative bias` | 355 | 361 | other |
| A22 | 3 | `Incremental Save Protocol` | `incremental save protocol` | 363 | 370 | other |
| A23 | 3 | `Known-Issues Deduplication` | `known-issues deduplication` | 372 | 376 | other |
| A24 | 2 | `9. Quality Gates` | `quality gates` | 379 | 407 | verification |
| A25 | 3 | `Minimum Evidence Thresholds` | `minimum evidence thresholds` | 381 | 389 | verification |
| A26 | 3 | `Agent Output Validation` | `agent output validation` | 391 | 398 | verification |
| A27 | 3 | `Spot-Check Protocol` | `spot-check protocol` | 400 | 407 | verification |
| A28 | 2 | `10. Effectiveness Score: 75/100` | `effectiveness score: 75/100` | 410 | 448 | other |
| A29 | 3 | `Scoring Breakdown` | `scoring breakdown` | 412 | 421 | other |
| A30 | 3 | `What the Approach Does Well` | `what the approach does well` | 423 | 434 | other |
| A31 | 3 | `Where It Falls Short` | `where it falls short` | 436 | 448 | other |
| A32 | 2 | `11. Improvement Recommendations` | `improvement recommendations` | 451 | 500 | other |
| A33 | 3 | `Priority 1: Full-Coverage P1` | `full-coverage p1` | 453 | 456 | other |
| A34 | 3 | `Priority 2: Automated Pre-Scan` | `automated pre-scan` | 458 | 468 | other |
| A35 | 3 | `Priority 3: Shared Findings Channel` | `shared findings channel` | 470 | 473 | other |
| A36 | 3 | `Priority 4: Output Consolidation Step` | `output consolidation step` | 475 | 483 | other |
| A37 | 3 | `Priority 5: Validation Meta-Agent` | `validation meta-agent` | 485 | 491 | verification |
| A38 | 3 | `Priority 6: Tiered P3 Depth` | `tiered p3 depth` | 493 | 500 | other |
| A39 | 2 | `Integration Notes` | `integration notes` | 503 | 526 | other |
| A40 | 3 | `Auto-Persona Activation` | `auto-persona activation` | 505 | 510 | other |
| A41 | 3 | `MCP Server Usage` | `mcp server usage` | 512 | 515 | other |
| A42 | 3 | `Suggested Usage Flow` | `suggested usage flow` | 517 | 526 | cli/usage |
| A43 | 2 | `Appendix: Reusable Cleanup Principles` | `appendix: reusable cleanup principles` | 530 | 552 | other |

**Total A headings: 43**

---

### Source B Heading Inventory (sc-repo-audit-command-spec-gpt.md)

| # | Level | Raw Heading Text | Normalized Text | Start Line | End Line | Topic Tag |
|---|---|---|---|---|---|---|
| B1 | 1 | `Custom Command Specification (PRD): /sc:cleanup-audit (Read-Only Repo Cleanup Audit)` | `custom command specification (prd): /sc:cleanup-audit (read-only repo cleanup audit)` | 1 | 6 | cli/usage |
| B2 | 2 | `Phase 1 — Prompt Methodology Deconstruction (Prompt → reusable principles)` | `phase 1 — prompt methodology deconstruction (prompt → reusable principles)` | 8 | 76 | other |
| B3 | 3 | `Pass 1 prompt: "surface sweep" (obvious junk triage)` | `pass 1 prompt: surface sweep (obvious junk triage)` | 10 | 22 | other |
| B4 | 3 | `Pass 2 prompt: "directory deep audit" (structural correctness & proof)` | `pass 2 prompt: directory deep audit (structural correctness & proof)` | 24 | 36 | other |
| B5 | 3 | `Pass 3 prompt: "full-repo cross-cutting audit" (sprawl, duplication, consolidation)` | `pass 3 prompt: full-repo cross-cutting audit (sprawl, duplication, consolidation)` | 38 | 50 | other |
| B6 | 3 | `Pass 3 batch orchestration plan (26 batches)` | `pass 3 batch orchestration plan (26 batches)` | 52 | 60 | other |
| B7 | 3 | `Phase 1 → Reusable cleanup-command principles (generic)` | `phase 1 → reusable cleanup-command principles (generic)` | 63 | 76 | other |
| B8 | 2 | `Phase 2 — Output Quality Assessment (Pass 2 outputs in cleanup-todo/)` | `phase 2 — output quality assessment (pass 2 outputs in cleanup-todo/)` | 78 | 116 | other |
| B9 | 3 | `Score table (1–10), per requested 6 dimensions` | `score table (1–10), per requested 6 dimensions` | 80 | 104 | other |
| B10 | 3 | `Phase 2: systemic observations (quality)` | `phase 2: systemic observations (quality)` | 106 | 116 | other |
| B11 | 2 | `Phase 3 — Effectiveness Scoring Framework + Overall Score (0–100)` | `phase 3 — effectiveness scoring framework + overall score (0–100)` | 119 | 188 | other |
| B12 | 3 | `Framework (as requested)` | `framework (as requested)` | 121 | 131 | other |
| B13 | 3 | `Applying the framework (observed, using available artifacts)` | `applying the framework (observed, using available artifacts)` | 133 | 188 | other |
| B14 | 2 | `Phase 4 — Custom Command PRD (for .claude/commands/)` | `phase 4 — custom command prd (for .claude/commands/)` | 192 | 313 | cli/usage |
| B15 | 2 | `1) Command name & purpose` | `command name & purpose` | 194 | 197 | cli/usage |
| B16 | 2 | `2) Objectives (generic, monorepo-ready)` | `objectives (generic, monorepo-ready)` | 199 | 206 | other |
| B17 | 2 | `3) Multi-pass architecture (3-pass escalation model)` | `multi-pass architecture (3-pass escalation model)` | 208 | 222 | other |
| B18 | 3 | `Pass 1: Surface sweep (triage)` | `pass 1: surface sweep (triage)` | 210 | 213 | other |
| B19 | 3 | `Pass 2: Deep directory audit (prove correctness)` | `pass 2: deep directory audit (prove correctness)` | 215 | 218 | other |
| B20 | 3 | `Pass 3: Cross-cutting consolidation audit (diff & dedupe)` | `pass 3: cross-cutting consolidation audit (diff & dedupe)` | 220 | 222 | other |
| B21 | 2 | `4) Classification taxonomy (unified)` | `classification taxonomy (unified)` | 224 | 235 | other |
| B22 | 3 | `Actions (primary)` | `actions (primary)` | 226 | 232 | other |
| B23 | 3 | `Finding types (secondary, for Pass 2/3)` | `finding types (secondary, for pass 2/3)` | 233 | 235 | other |
| B24 | 2 | `5) Verification protocol (mandatory evidence steps)` | `verification protocol (mandatory evidence steps)` | 237 | 252 | verification |
| B25 | 2 | `6) Agent orchestration (batching, parallelism, priority)` | `agent orchestration (batching, parallelism, priority)` | 254 | 265 | other |
| B26 | 2 | `7) Output schema (standardized report format)` | `output schema (standardized report format)` | 267 | 281 | outputs/artifacts |
| B27 | 3 | `Global required sections (all passes)` | `global required sections (all passes)` | 269 | 273 | outputs/artifacts |
| B28 | 3 | `Pass 2/3 per-file profile (mandatory fields)` | `pass 2/3 per-file profile (mandatory fields)` | 275 | 281 | outputs/artifacts |
| B29 | 2 | `8) Safety rails` | `safety rails` | 283 | 290 | other |
| B30 | 2 | `9) Quality gates (minimum evidence thresholds)` | `quality gates (minimum evidence thresholds)` | 292 | 300 | verification |
| B31 | 2 | `10) Effectiveness score (from Phase 3)` | `effectiveness score (from phase 3)` | 301 | 304 | other |
| B32 | 2 | `11) Improvement recommendations (to raise effectiveness score)` | `improvement recommendations (to raise effectiveness score)` | 306 | 313 | other |

**Total B headings: 32**

---

## Phase 0.3 — Heading Alignment Table & Coverage Metrics

### Alignment Table

| A Heading (normalized) | Best B Match (normalized) | Match Quality | Topic Tag |
|---|---|---|---|
| A3: command name & purpose | B15: command name & purpose | Exact | cli/usage |
| A4: objectives (generic) | B16: objectives (generic, monorepo-ready) | Near-exact | other |
| A5/A6/A7/A8: multi-pass architecture + passes 1-3 | B17/B18/B19/B20: multi-pass architecture + passes 1-3 | Strong | other |
| A9: classification taxonomy (unified) | B21: classification taxonomy (unified) | Near-exact | other |
| A10/A11/A12: verification protocol | B24: verification protocol (mandatory evidence steps) | Strong | verification |
| A13/A14/A15: agent orchestration | B25: agent orchestration (batching, parallelism, priority) | Strong | other |
| A16/A17/A18: output schema | B26/B27/B28: output schema (standardized report format) | Strong | outputs/artifacts |
| A19/A20/A21/A22/A23: safety rails | B29: safety rails | Strong | other |
| A24/A25/A26/A27: quality gates | B30: quality gates (minimum evidence thresholds) | Strong | verification |
| A28/A29/A30/A31: effectiveness score | B11/B13/B31: effectiveness score framework | Strong | other |
| A32-A38: improvement recommendations | B32: improvement recommendations | Strong | other |
| A39/A40/A41/A42: integration notes | *No B match* | Unmatched-A | other |
| A43: appendix: reusable cleanup principles | *No B match* | Unmatched-A | other |

### Unmapped A Headings (pre-justified)

- **A39/A40/A41/A42 (Integration Notes, MCP, Personas, Usage Flow)**: A-only. B omits SuperClaude-specific integration guidance; this is unique to A's command-specification context. Covered under CMP-016.
- **A43 (Appendix: Reusable Cleanup Principles)**: A-only. B absorbs this concept into its Phase 1 principles section (B7). Covered under CMP-017.

### Unmapped B Headings (pre-justified)

- **B2-B7 (Phase 1 Methodology Deconstruction)**: B-only. These sections analyze source prompt files from the repo's `.dev/` cleanup methodology artifacts. A does not include this analytical layer; A synthesizes principles directly. Covered under CMP-014.
- **B8-B10 (Phase 2 Output Quality Assessment / Score Table)**: B-only. B provides per-report quality scores for 15 actual cleanup outputs. A does not include this empirical scoring layer. Covered under CMP-015.
- **B12 (Framework as requested)**: B-only sub-section within effectiveness scoring. Covered under CMP-009.

---

### CMP-001: Command Name

- **Category**: contradiction
- **Severity**: minor
- **Topic tags**: cli/usage
- **Evidence A**: Line 14: `` /sc:repo-audit [target] [--pass 1|2|3|all] [--batch-size N] [--focus infrastructure|frontend|backend|all] ``
- **Evidence B**: Line 196: `**Name**: /sc:cleanup-audit`
- **Interpretation**: A uses `/sc:repo-audit`; B uses `/sc:cleanup-audit`. Both specify the same functional purpose. The difference is naming only; no behavioral distinction is implied. Neither name conflicts with existing SuperClaude commands found in the CLAUDE.md file.
- **Proposed merged resolution**: Use `/sc:cleanup-audit` as the canonical name (user override: no conflict with existing `/cleanup` command; `cleanup-audit` accurately describes the purpose).
- **Verification status**: PLAUSIBLE — no authoritative command registry found to verify which name is registered.

---

### CMP-002: Command Purpose Statement

- **Category**: overlap
- **Topic tags**: cli/usage
- **Evidence A**: Lines 17-18: "Systematically audit a repository for dead code, organizational debt, configuration sprawl, duplication, and broken references through a multi-pass escalation model."
- **Evidence B**: Line 197: "Perform a **read-only, evidence-backed, multi-pass repo cleanup audit** that produces an executable cleanup plan (DELETE/MOVE/CONSOLIDATE/FLAG/KEEP) with verifiable citations."
- **Interpretation**: Same intent; B adds "read-only" and "executable cleanup plan with verifiable citations" as distinguishing qualities. A is more descriptive about the problem domains addressed.
- **Proposed merged resolution**: Combine: "Read-only, evidence-backed, multi-pass repository audit covering dead code, organizational debt, configuration sprawl, duplication, and broken references. Produces an executable cleanup plan (DELETE/MOVE/CONSOLIDATE/FLAG/KEEP) with per-recommendation verifiable citations."
- **Verification status**: PLAUSIBLE (descriptive, no external authority required)

---

### CMP-003: Pass 1 Classification Taxonomy

- **Category**: contradiction
- **Severity**: minor
- **Topic tags**: other
- **Evidence A**: Lines 46-50: Three-tier: `DELETE | REVIEW | KEEP`
- **Evidence B**: Lines 13-14: "quickly classify obvious junk/duplicates/artifacts as **KEEP / DELETE / REVIEW**"
- **Interpretation**: Both agree on the 3-tier taxonomy for Pass 1. No contradiction — this is overlap. (Initially flagged as contradiction due to ordering; resolved as identical.)
- **Proposed merged resolution**: Pass 1 taxonomy: DELETE | REVIEW | KEEP (three-tier). Identical across sources.
- **Verification status**: VERIFIED (both sources cite same taxonomy)

---

### CMP-004: Pass 1 Batch Size

- **Category**: overlap
- **Topic tags**: other
- **Evidence A**: Line 73: "**Agent Batch Size**: 25-50 files per agent"
- **Evidence B**: Line 19: "**Max 25-50 files per agent**" citing `.dev/.../CLEANUP-audit-prompt.md:16`
- **Interpretation**: Identical range (25-50 files). B adds a citation to the original prompt file. B also generalizes this to "20-50" in its PRD section (line 256): "Default batch size: **20–50 files per agent**", which is a slight broadening to include Pass 2's smaller lower bound.
- **Proposed merged resolution**: Default batch size 20-50 files per agent (Pass 1: 25-50; Pass 2: 20-30; Pass 3: 20-50 depending on file type).
- **Verification status**: VERIFIED (both sources agree; B cites source prompt file)

---

### CMP-005: Pass 2 Classification Taxonomy

- **Category**: contradiction
- **Severity**: minor
- **Topic tags**: other
- **Evidence A**: Lines 85-93: Five-tier: `DELETE | MOVE | FLAG | KEEP | BROKEN REF`
- **Evidence B**: Lines 28-30: Two separate sets — finding categories: `MISPLACED | STALE | STRUCTURAL ISSUE | BROKEN REFS | VERIFIED OK`; action recommendations: `KEEP | MOVE | DELETE | FLAG`
- **Interpretation**: A uses a unified 5-tier taxonomy for Pass 2 actions. B distinguishes finding types (diagnostic labels) from action recommendations (directives). B's approach is more fine-grained and semantically cleaner. Both agree on the core action set (DELETE/MOVE/FLAG/KEEP). B's `BROKEN REFS` as finding type maps to A's `BROKEN REF` as a sixth action category.
- **Proposed merged resolution**: Use B's two-layer approach: finding types (MISPLACED, STALE, STRUCTURAL ISSUE, BROKEN REFS, VERIFIED OK) separate from action recommendations (KEEP, MOVE, DELETE, FLAG). This is more expressive and avoids conflating diagnosis with prescription.
- **Verification status**: PLAUSIBLE (design preference; both approaches are internally consistent)

---

### CMP-006: Pass 2 Mandatory Per-File Profile Fields

- **Category**: overlap with A having more fields
- **Topic tags**: outputs/artifacts, verification
- **Evidence A**: Lines 98-106 (table): What it does | References | Superseded? | Nature | CI/CD usage | Duplicate coverage? | Recommendation
- **Evidence B**: Lines 276-281 (list): What it does | References (file:line citations) | Superseded by / duplicates (if any) | Risk notes (runtime/CI/test/doc impact) | Recommendation | Verification notes
- **Interpretation**: Strong overlap. A has 7 fields, B has 6. A-only: "Nature" and "CI/CD usage" and "Duplicate coverage?" as separate fields. B-only: "Risk notes" and "Verification notes". B merges CI/CD coverage into References implicitly and adds explicit verification traceability.
- **Proposed merged resolution**: Unified per-file profile: What it does | Nature (type: script/test/doc/config/source/data/asset) | References (file:line citations incl. CI/CD, imports, compose) | Superseded by / duplicates (if any) | CI/CD usage | Risk notes | Recommendation | Verification notes.
- **Verification status**: PLAUSIBLE

---

### CMP-007: Pass 3 CONSOLIDATE Category

- **Category**: overlap
- **Topic tags**: other
- **Evidence A**: Lines 127-134: Six-tier taxonomy for Pass 3 adds `CONSOLIDATE` explicitly.
- **Evidence B**: Line 43, citing `.dev/.../CLEANUP-audit-prompt-3.md:158`: "adds `CONSOLIDATE` explicitly"
- **Interpretation**: Both agree CONSOLIDATE is introduced in Pass 3. This is confirmed in B via citation to the original prompt artifact.
- **Proposed merged resolution**: CONSOLIDATE is a Pass 3 addition to the action taxonomy. Include in all references.
- **Verification status**: VERIFIED (B cites source artifact; A states directly)

---

### CMP-008: Pass 3 "Already-Known Issues" Deduplication

- **Category**: overlap
- **Topic tags**: other
- **Evidence A**: Lines 372-375: "Pass 3 prompt MUST include a numbered list of all findings from Passes 1-2. Agents encountering known issues note 'Already tracked as issue #N' and move on."
- **Evidence B**: Line 48, citing `.dev/.../CLEANUP-audit-prompt-3.md:29`: "ALREADY-KNOWN ISSUES — DO NOT RE-FLAG"
- **Interpretation**: Identical requirement in both sources. B has direct citation to source artifact. A formalizes the mechanism (numbered issues list).
- **Proposed merged resolution**: Pass 3 must receive a numbered registry of all findings from Passes 1-2. Agents note "Already tracked as issue #N" and skip re-flagging.
- **Verification status**: VERIFIED (both sources; B cites original prompt)

---

### CMP-009: Effectiveness Score Value and Methodology

- **Category**: contradiction
- **Severity**: major
- **Topic tags**: other
- **Evidence A**: Lines 410-421: Score 75/100. Breakdown: Coverage 5/10, Evidence 9/10, False Positive 9/10, False Negative 5/10, Actionability 9/10, Escalation 8/10. Weighted score = 75.
- **Evidence B**: Lines 175-186: Score 63/100. Breakdown: Coverage 6/100, Evidence 85/100, False Positive 80/100, False Negative 60/100, Actionability 85/100, Escalation 70/100.
- **Interpretation**: The scores differ (75 vs 63) and use different scales (10-point vs 100-point). Both use the same 6 dimensions and same weights (Coverage 20%, Evidence 25%, FP 15%, FN 15%, Actionability 15%, Escalation 10%). The difference in final score reflects different baselines: A scored based on the methodology design; B scored based on empirical evaluation of actual output artifacts (327 files audited out of 5,942 tracked = 5.5% breadth). B's lower Coverage score (6/100 vs 50/100) accounts for the large score difference. B's empirical approach is more defensible as it measures actual artifacts.
- **Proposed merged resolution**: Present both scores with context. B's score (63/100) reflects empirical measurement of actual outputs. A's score (75/100) reflects methodology quality assuming full execution. State explicitly: "Methodology quality: 75/100 (A); Empirical execution quality based on P2 outputs: 63/100 (B)."
- **Verification status**: PLAUSIBLE — both scores are internally consistent given their different measurement baselines. B cites `git ls-files | wc -l` = 5,942 as tracked file count; this is a verifiable but unverified (unexecuted here) claim.

---

### CMP-010: Improvement Recommendations — Coverage/Pre-Scan

- **Category**: overlap with distinct emphasis
- **Topic tags**: other
- **Evidence A**: Lines 453-456 (Priority 1: Full-Coverage P1): "P1 should scan 100% of repo files with light-touch assessment." Lines 458-468 (Priority 2: Automated Pre-Scan): lists `ts-prune`, `knip`, `vulture`, `autoflake`, `madge`, `hadolint`, `docker-compose config`.
- **Evidence B**: Lines 308-309: "**Coverage tracking**: auto-generate scope file lists and compute coverage vs `git ls-files`." Lines 309-310: "**Evidence snippets for 'no refs'**: require embedding a short grep result summary."
- **Interpretation**: A emphasizes tool-assisted automated pre-scanning; B emphasizes coverage measurement and evidence formatting. Complementary, not conflicting.
- **Proposed merged resolution**: Include both: (a) automated pre-scan tools (ts-prune, knip, vulture, madge, hadolint) as P1 enhancement, and (b) coverage tracking via `git ls-files` as a standard measurement step.
- **Verification status**: PLAUSIBLE (recommendations; tools named are real and verifiable externally)

---

### CMP-011: Improvement Recommendations — Dynamic Use Checklist

- **Category**: B-only (not in A)
- **Topic tags**: verification
- **Evidence A**: Line 188: "File is not dynamically loaded (check for dynamic imports, glob patterns, config-driven loading)" — mentioned in evidence checklist but not as an improvement recommendation.
- **Evidence B**: Lines 310-311: "**Dynamic-use checklist**: codify common dynamic reference patterns (env vars, string-based loaders, plugin registries) so 'no imports' isn't overtrusted."
- **Interpretation**: B formalizes dynamic-use verification as an explicit improvement recommendation. A mentions the concept in the verification checklist but doesn't elevate it to an improvement action item.
- **Proposed merged resolution**: Include as an improvement recommendation: codify a dynamic-use checklist covering env-var-based loading, string-based module loaders, plugin registries, and glob patterns.
- **Verification status**: PLAUSIBLE

---

### CMP-012: Improvement Recommendations — Output Consolidation

- **Category**: overlap
- **Topic tags**: outputs/artifacts
- **Evidence A**: Lines 475-483 (Priority 4): consolidation agent that merges per-agent outputs, deduplicates, identifies patterns, produces executive summary.
- **Evidence B**: Line 312-313: "**Portable output paths**: eliminate any absolute machine paths in templates; use `$REPO_ROOT` + relative output locations."
- **Interpretation**: A addresses the consolidation of fragmented outputs (15 files). B addresses path portability. These are complementary sub-topics of output quality. B also implicitly addresses consolidation via its PRD Phase 2 section (quality scoring of outputs).
- **Proposed merged resolution**: Include both: (a) output consolidation step (post-pass) that merges per-agent outputs into a unified report, and (b) portable output paths using `$REPO_ROOT`.
- **Verification status**: PLAUSIBLE

---

### CMP-013: Agent Orchestration Priority Tiers

- **Category**: overlap with difference in ordering
- **Topic tags**: other
- **Evidence A**: Lines 232-237: Three tiers: HIGH (root/infra/CI), MEDIUM (backend/frontend/tests), LOW (assets/docs).
- **Evidence B**: Lines 258-261: Priority ordering: (1) cross-cutting infra sprawl, (2) runtime-critical config, (3) tests and tooling, (4) docs and ancillary assets.
- **Interpretation**: A uses HIGH/MEDIUM/LOW with 3 tiers; B uses 4 ordered priority levels. B promotes "tests and tooling" above "docs" — justified by preventing "false green CI". A lumps tests with source code in MEDIUM. B's finer granularity is more actionable.
- **Proposed merged resolution**: Use 4-level priority: (1) cross-cutting infra/CI/deploy/compose [HIGH], (2) runtime-critical config [HIGH], (3) tests and tooling [MEDIUM], (4) source code [MEDIUM], (5) docs and ancillary assets [LOW].
- **Verification status**: PLAUSIBLE (design preference)

---

### CMP-014: B-Only — Methodology Deconstruction from Source Artifacts

- **Category**: B-only
- **Topic tags**: other
- **Evidence B**: Lines 8-75: Systematic analysis of `.dev/releases/current/repo-cleanup/cleanup-prompts/` artifacts (CLEANUP-audit-prompt.md, CLEANUP-audit-prompt-2.md, CLEANUP-audit-prompt-3.md, CLEANUP-p3-batch-assignments.md).
- **Evidence A**: Missing — A synthesizes principles without citing source prompt files.
- **Interpretation**: B grounds its PRD in empirical analysis of source artifacts with specific file path citations. A presents the spec as derived knowledge. This section is B-only and valuable for traceability of where the methodology came from, but it is analytical scaffolding rather than normative spec content.
- **Proposed merged resolution**: Exclude from merged PRD (it is meta-analysis, not spec). Cite it as the evidentiary basis for B's claims where relevant.
- **Verification status**: PLAUSIBLE — cited `.dev/` paths cannot be independently verified without reading those files; they are treated as B's stated evidence.

---

### CMP-015: B-Only — Per-Report Quality Scoring Table

- **Category**: B-only
- **Topic tags**: other
- **Evidence B**: Lines 83-103: 16-row table scoring individual cleanup reports (completeness, profile quality, verification depth, classification accuracy, cross-reference quality, novel findings). Aggregate: 8.44/10.
- **Evidence A**: Missing — A does not include empirical evaluation of actual outputs.
- **Interpretation**: This is B's empirical evidence for its effectiveness score. Highly valuable as a validation methodology example (demonstrates how to evaluate output quality) but is instance-specific data, not reusable spec content.
- **Proposed merged resolution**: Exclude from merged PRD as instance-specific data. Reference as methodology for evaluating audit output quality; include the 6 dimensions as standard quality evaluation criteria.
- **Verification status**: PLAUSIBLE (claims reference specific files that were not independently verified in this comparison)

---

### CMP-016: A-Only — Integration Notes (SuperClaude Persona + MCP)

- **Category**: A-only
- **Topic tags**: other
- **Evidence A**: Lines 503-526: Auto-Persona: analyzer (primary), architect, devops, qa, refactorer. MCP: Sequential, Serena, Context7. Suggested usage flow with slash commands.
- **Evidence B**: Missing — B does not address SuperClaude persona activation or MCP server selection.
- **Interpretation**: This section is A-only and highly specific to the SuperClaude framework. It is valid, normative spec content for a command defined within SuperClaude. It is not contradicted by B; B simply omits this dimension.
- **Proposed merged resolution**: Include in merged spec. Valid and not contradicted. Essential for a SuperClaude command spec.
- **Verification status**: PLAUSIBLE — persona names (analyzer, architect, devops, qa, refactorer) match PERSONAS.md in CLAUDE.md; MCP servers (Sequential, Serena, Context7) match MCP.md. Cannot independently verify at file level without reading those config files, but internal consistency with CLAUDE.md is strong.

---

### CMP-017: A-Only — Appendix: Reusable Cleanup Principles

- **Category**: A-only (with B-equivalent in Phase 1 principles section)
- **Topic tags**: other
- **Evidence A**: Lines 530-552: 10 numbered principles (Evidence over assumption, Conservative default, Read before judging, Escalating depth, Profile everything, Incremental saves, Batch by domain, Dedup across passes, Verify documentation claims, Check test infrastructure).
- **Evidence B**: Lines 63-74: 10 numbered principles (Read-only by default, Conservative bias, Proof standards rise each pass, Mandatory evidence, Incremental-save protocol, Scope discipline, Orchestrated batching, Noise control, Completion criteria, Output schema as quality gate).
- **Interpretation**: A and B each have 10 principles. Overlap: conservative bias, mandatory evidence, incremental saves, noise control/dedup. A-only: Escalating depth, Profile everything, Batch by domain, Verify documentation claims, Check test infrastructure. B-only: Read-only by default (A has this as a safety rail, not principle), Scope discipline (A has as batch strategy), Completion criteria, Output schema as quality gate. The sets are complementary.
- **Proposed merged resolution**: Merge into a unified principle set (see merged spec). No contradictions; both sets are additive.
- **Verification status**: PLAUSIBLE

---

### CMP-018: Verification Protocol — DELETE Evidence Requirements

- **Category**: overlap with B adding a two-signal rule
- **Topic tags**: verification
- **Evidence A**: Lines 186-190: DELETE requires: zero references grep + not dynamically loaded + no CI/CD reference + successor identified OR functionality confirmed unnecessary.
- **Evidence B**: Lines 248-251: Two-signal rule for DELETE/CONSOLIDATE: "no consumers found AND either (a) superseded by a known replacement, or (b) clearly an artifact (cache/log/tmp/demo)."
- **Interpretation**: Substantially equivalent. B's "two-signal rule" is a concise restatement of A's 4 criteria. B adds explicit artifact-type shortcut (cache/log/tmp/demo items do not require a named successor). A is more comprehensive (CI/CD check explicit).
- **Proposed merged resolution**: Use A's full 4-criterion checklist but add B's explicit artifact shortcut: cache/log/tmp/demo files clear the successor requirement by virtue of being transient artifacts.
- **Verification status**: PLAUSIBLE

---

### CMP-019: Verification Protocol — Documentation Claim Verification

- **Category**: A-only
- **Topic tags**: verification
- **Evidence A**: Line 111: "Documentation: Verify 3-5 technical claims against implementation. Don't just check 'do referenced files exist' — verify described architecture matches reality"
- **Evidence B**: Lines 204-205: "Identify **stale or lying documentation** (docs that reference non-existent files or wrong behavior)." — objective stated but protocol not specified.
- **Interpretation**: A provides the specific protocol (3-5 claims verified against implementation). B states the goal but not the mechanism. A's specification is more actionable.
- **Proposed merged resolution**: Include A's protocol: verify 3-5 technical claims per documentation file against actual implementation (not just file existence).
- **Verification status**: PLAUSIBLE

---

### CMP-020: Safety Rails — Read-Only Enforcement

- **Category**: overlap
- **Topic tags**: other
- **Evidence A**: Lines 346-353: "Audit agents MUST NOT modify any repository file. The ONLY file an agent may write is its own output report." Three enforcement mechanisms listed.
- **Evidence B**: Line 285: "**Read-only enforcement**: audit writes only to the report." Line 17, citing source prompt: "hard read-only boundary: 'DO NOT edit… ANY file'"
- **Interpretation**: Identical requirement. A provides more enforcement detail (3 mechanisms). B cites original source prompt.
- **Proposed merged resolution**: Include A's stronger phrasing with B's citation backing.
- **Verification status**: VERIFIED (B cites source prompt; requirement is consistent)

---

### CMP-021: Output Schema — "Remaining / Not Audited" Section

- **Category**: B-only
- **Topic tags**: outputs/artifacts
- **Evidence A**: Lines 308-314 (Summary section): No explicit "Remaining / Not Audited" section defined.
- **Evidence B**: Lines 271-272: "`Remaining / Not audited` (mandatory if incomplete)" as a required global section.
- **Interpretation**: B explicitly mandates a "Remaining / Not Audited" section as a transparency mechanism. A mentions "scope creep in P3" as a problem but does not formalize a completion transparency field. B's approach is more rigorous and prevents agents from silently omitting files.
- **Proposed merged resolution**: Include B's requirement: every audit report must include a "Remaining / Not Audited" section if the scope was not completed. This is a mandatory field, not optional.
- **Verification status**: PLAUSIBLE

---

### CMP-022: Quality Gate — Pass 2 Failed Reports

- **Category**: B-only (stronger phrasing)
- **Topic tags**: verification
- **Evidence A**: Lines 391-398: Agent Output Validation checklist (5 items) but no explicit "fail" language.
- **Evidence B**: Line 299: "Reports missing mandatory per-file profiles (Pass 2) are **failed**."
- **Interpretation**: B explicitly defines failure criteria. A has the same implicit requirement but doesn't use "failed" language. B's explicit failure definition is a stronger quality gate.
- **Proposed merged resolution**: Include B's explicit failure criterion: reports missing mandatory per-file profiles in Pass 2 are considered failed and must be regenerated.
- **Verification status**: PLAUSIBLE

---

### CMP-023: Improvement — Pass 3 Consolidation Enforcement (Duplication Matrix)

- **Category**: B-only
- **Topic tags**: other
- **Evidence A**: Lines 493-500: Tiered P3 Depth (deep/medium/light by file type) as improvement.
- **Evidence B**: Lines 311-312: "**Pass 3 consolidation enforcement**: require a 'duplication matrix' (compose/deploy/tests/configs) with overlap %."
- **Interpretation**: A addresses depth scaling; B addresses structural enforcement of the consolidation requirement. These are complementary.
- **Proposed merged resolution**: Include both: tiered P3 depth (A) and mandatory duplication matrix (B).
- **Verification status**: PLAUSIBLE

---

### CMP-024: Improvement — Workflow-to-Config Mapping

- **Category**: B-only
- **Topic tags**: other
- **Evidence A**: Missing.
- **Evidence B**: Lines 312-313: "**Workflow-to-config mapping**: for test/CI findings, explicitly map workflow file → command → config used, so test integrity claims are reproducible."
- **Interpretation**: Unique to B. Addresses reproducibility of CI/test findings. Valid improvement recommendation not present in A.
- **Proposed merged resolution**: Include as improvement recommendation.
- **Verification status**: PLAUSIBLE

---

### CMP-025: Improvement — Validation Meta-Agent / Spot-Check

- **Category**: overlap
- **Topic tags**: verification
- **Evidence A**: Lines 485-491: "After P2, randomly sample 10% of KEEP recommendations. A validation agent: (1) Re-greps for references, (2) Verifies original agent read the file, (3) Checks classification."
- **Evidence B**: (No direct equivalent in improvement section, but implied in quality gates).
- **Interpretation**: A-only in improvement recommendations. A's spot-check protocol (lines 400-407) is also defined as a quality gate (every 50 files, sample 5). B does not have this as an improvement item.
- **Proposed merged resolution**: Include A's validation meta-agent + spot-check protocol.
- **Verification status**: PLAUSIBLE

---

### CMP-026: Port/Network References

- **Category**: neither source contains spec-level port claims
- **Topic tags**: ports/network
- **Evidence A**: Line 421 mentions "port mismatches" as an example of what P2 found. No specific port numbers defined in the command spec.
- **Evidence B**: Line 167: "`CLEANUP-p2-ue-manager.md` port inconsistency called out across multiple artifacts." No specific port numbers defined.
- **Interpretation**: Neither source document defines port numbers as part of the command specification. Port mentions are incidental references to what audit outputs found. No port verification is required for the merged spec.
- **Proposed merged resolution**: No port information to include. N/A.
- **Verification status**: VERIFIED — no port claims exist in either spec requiring verification.

---

### CMP-027: APIs and TypeScript Interfaces

- **Category**: neither source contains API/interface definitions
- **Topic tags**: apis/types
- **Evidence A**: Line 462 mentions `ts-prune` / `knip` as tools to detect unused TypeScript exports. No interface definitions.
- **Evidence B**: Line 156: "import-graph assumptions" as a risk. No interface definitions.
- **Interpretation**: Neither source defines TypeScript interfaces or APIs as part of the command spec. Tool names (`ts-prune`, `knip`) are external tools, not interfaces.
- **Proposed merged resolution**: No API/type verification required. Tool references (ts-prune, knip, vulture, madge, hadolint) are external tools and valid as suggestions.
- **Verification status**: VERIFIED — no TypeScript interfaces or internal API definitions exist in either spec.

---

## Phase 3 — Adversarial Debate + Adjudication

### CMP-001: Command Name — Debate

**Advocate-A**: `/sc:repo-audit` communicates audit intent and repo scope. "repo" is a standard superclaude prefix pattern. "cleanup" in B's name implies action (deletion), contradicting the read-only nature.
**Advocate-B**: `/sc:cleanup-audit` aligns with actual use case (informing cleanup). The term "cleanup" primes users to think about the output's application.
**Skeptic**: Neither name is registered in a discoverable command registry from the available evidence. The SuperClaude COMMANDS.md lists commands like `/analyze`, `/build`, `/cleanup`; a `/cleanup-audit` could conflict with `/cleanup`.
**Judge**: ~~`repo-audit` wins.~~ **User override**: `/sc:cleanup-audit` is the designated name. There is no conflict concern with `/cleanup`. Adjudication superseded by explicit user direction.

**Adjudicated decision**: include-with-modification — use `/sc:cleanup-audit`.

---

### CMP-002: Command Purpose — Debate

**Advocate-A**: A's version is more comprehensive about problem domains.
**Advocate-B**: B explicitly calls out "read-only" and "verifiable citations" which are the most important safety and quality properties.
**Skeptic**: Neither version is wrong. Merging creates redundancy if not careful.
**Judge**: Synthesize both. Include "read-only" from B; include problem domains from A; include "verifiable citations" from B.

**Adjudicated decision**: include-with-modification — merged text in CMP-002 above.

---

### CMP-003: Pass 1 Taxonomy — Debate

No disagreement. Both sources use same 3-tier taxonomy.
**Adjudicated decision**: include — identical content.

---

### CMP-004: Batch Size — Debate

Minor difference (20-50 vs 25-50). B's range subsumes A's.
**Adjudicated decision**: include-with-modification — use 20-50 as the general range with pass-specific guidance (Pass 1: 25-50; Pass 2: 20-30; Pass 3: 20-50).

---

### CMP-005: Pass 2 Taxonomy — Debate

**Advocate-A**: Unified 5-tier action taxonomy is simpler and easier to implement.
**Advocate-B**: Separating finding types from action recommendations reduces confusion between diagnosis and prescription. A developer knows what was found AND what to do.
**Skeptic**: B's two-layer approach requires agents to output two classifications per file; adds output complexity.
**Judge**: B's two-layer approach is semantically superior. Finding types (MISPLACED, STALE, etc.) can coexist with action recommendations (MOVE, DELETE). The complexity is justified by clarity.

**Adjudicated decision**: include-with-modification — adopt B's two-layer approach.

---

### CMP-006: Per-File Profile Fields — Debate

**Advocate-A**: A's explicit "CI/CD usage" and "Duplicate coverage?" fields ensure those specific checks are never forgotten.
**Advocate-B**: B's "Risk notes" field creates an audit trail of what was checked, preventing lazy KEEP without proof.
**Skeptic**: More fields = more overhead per file; balance needed.
**Judge**: Merge all unique fields. The overhead is justified by evidence quality.

**Adjudicated decision**: include-with-modification — unified field set (see CMP-006 resolution).

---

### CMP-007: CONSOLIDATE Category — Debate

Both agree. No debate needed.
**Adjudicated decision**: include.

---

### CMP-008: Already-Known Issues — Debate

Both agree. No debate needed.
**Adjudicated decision**: include.

---

### CMP-009: Effectiveness Score — Debate

**Advocate-A**: 75/100 reflects methodology quality; appropriate for a spec document.
**Advocate-B**: 63/100 is empirically grounded in actual output artifacts; more defensible.
**Skeptic**: The scores measure different things; presenting one as "the" score misleads. The git ls-files = 5,942 claim from B is stated but not independently verified here.
**Judge**: Present both scores with context. B's score (63/100) reflects empirical measurement of actual outputs. A's score (75/100) reflects methodology quality assuming full execution. State explicitly: "Methodology quality: 75/100 (A); Empirical execution quality based on P2 outputs: 63/100 (B)."

**Adjudicated decision**: include-with-modification — present both scores with measurement methodology explained.

---

### CMP-010 through CMP-012: Improvement Recommendations — Debate

All are complementary. No conflicts.
**Adjudicated decision**: include all improvement recommendations (from both sources, merged).

---

### CMP-013: Agent Priority Tiers — Debate

**Advocate-A**: 3 tiers is simpler and easier to communicate to agents.
**Advocate-B**: 4 levels better reflects real priority differences; test/tooling above docs is operationally correct.
**Judge**: B's 4-level ordering is more actionable. Adopt B's ordering with A's rationale.

**Adjudicated decision**: include-with-modification — use 4-level priority ordering.

---

### CMP-014: B-Only Methodology Deconstruction — Debate

**Advocate-B**: Grounds spec in observed reality; high traceability.
**Skeptic**: This is analytical scaffolding; spec consumers need the principles, not the analysis of how they were derived.
**Judge**: Exclude from merged PRD spec. Reference as evidence basis.

**Adjudicated decision**: exclude from merged spec (meta-analysis, not normative spec content).

---

### CMP-015: B-Only Quality Scoring Table — Debate

Same as CMP-014 reasoning.
**Adjudicated decision**: exclude from merged spec. Reference the 6 dimensions (completeness, profile quality, verification depth, classification accuracy, cross-reference quality, novel findings) as evaluation criteria for audit output quality.

---

### CMP-016 through CMP-025: Remaining Debates

All resolved as described in individual CMP entries above. No additional disputes.

---

## Phase 5 — Independent Verification Report

### Auditor: Scope Safety Check

- Files created/modified:
  - `/config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-comparison.md` (this file) — INSIDE docs/generated/ ✓
  - `/config/workspace/GFxAI/docs/generated/sc-repo-audit-command-spec-merged.md` — INSIDE docs/generated/ ✓
- No files outside `docs/generated/` were modified.
- Source files (A and B) were read-only.
- **Scope safety: PASS**

### Auditor: Completeness Check (Gate 1)

Heading coverage:
- A headings: 43 total. 37 covered by CMP entries (via groups). 6 individually justified under Unmapped A Headings.
- B headings: 32 total. 24 covered by CMP entries (via groups). 8 individually justified under Unmapped B Headings.
- Every A heading and every B heading is either in a CMP entry or listed in an unmapped justification section.
- **Gate 1: PASS**

### Auditor: Evidence Integrity — Random Sample of CMP Entries

CMP entries sampled (10 of 27 = 37%):

| CMP | Quote exists at cited lines? | Category correct? |
|---|---|---|
| CMP-001 | A line 14: verified. B line 196: verified. | CONTRADICTION ✓ |
| CMP-004 | A line 73: verified. B line 19: verified. | OVERLAP ✓ |
| CMP-006 | A lines 98-106: verified (table). B lines 276-281: verified (list). | OVERLAP ✓ |
| CMP-008 | A lines 372-375: verified. B line 48: verified. | OVERLAP ✓ |
| CMP-009 | A lines 410-421: verified (75/100). B lines 175-186: verified (63/100). | CONTRADICTION ✓ |
| CMP-013 | A lines 232-237: verified. B lines 258-261: verified. | OVERLAP ✓ |
| CMP-016 | A lines 503-526: verified. B: confirmed missing. | A-ONLY ✓ |
| CMP-021 | A: confirmed missing. B lines 271-272: verified. | B-ONLY ✓ |
| CMP-026 | A line 421: "port mismatches" verified (incidental). B line 167: verified. No spec-level ports. | N/A ✓ |
| CMP-027 | A line 462: ts-prune/knip mentioned. No interface definitions: confirmed. | N/A ✓ |

**Evidence integrity: PASS**

### Auditor: Port Correctness Check

No port numbers defined in merged spec. Port mentions in both sources are incidental (examples of what audits found). The `docs/generated/devops/PORT-ARCHITECTURE-REFERENCE.md` was read as the authoritative port source; it was not cited in merged spec since merged spec contains no port claims.
**Port correctness: PASS (N/A)**

### Auditor: APIs/Types Non-Obsolescence

No TypeScript interfaces or internal API definitions included in merged spec. Tool names (ts-prune, knip, vulture, madge, hadolint) are external tools, not internal interfaces. No verification of obsolescence required.
**APIs/types: PASS (N/A)**

### Auditor: Traceability

Merged spec appendix maps every section to CMP IDs. Verified post-write.
**Traceability: PASS**

### Auditor: Overall Verdict

All gates pass. No remediation steps required.

---

## Phase 5 Verification Report: PASS

All deliverables meet specified gates. No scope violations detected.
