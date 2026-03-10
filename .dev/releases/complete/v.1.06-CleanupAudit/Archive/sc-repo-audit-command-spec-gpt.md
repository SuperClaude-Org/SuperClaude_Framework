# Custom Command Specification (PRD): `/sc:cleanup-audit` (Read‑Only Repo Cleanup Audit)
_Date: 2026-02-18_

This document follows the requested `/sc:analyze` flow (**Discover → Scan → Evaluate → Recommend → Report**) and implements the 4 phases in your objective.

---

## Phase 1 — Prompt Methodology Deconstruction (Prompt → reusable principles)

### Pass 1 prompt: “surface sweep” (obvious junk triage)
**Source**: `.dev/releases/current/repo-cleanup/cleanup-prompts/CLEANUP-audit-prompt.md`

- **Stated goal (generic)**: quickly classify obvious junk/duplicates/artifacts as **KEEP / DELETE / REVIEW** via light read + reference search.
- **Classification taxonomy**: `KEEP | DELETE | REVIEW` plus sectioned output lists (“Safe to Delete”, “Need Decision”, etc.).
- **Verification protocol**: read a small slice, then search the repo for references/imports before deletion.
- **Safety constraints**:
  - hard read‑only boundary: “**DO NOT edit… ANY file**” `.dev/.../CLEANUP-audit-prompt.md:12`
  - conservative bias: “**Err on the side of KEEP**” `.dev/.../CLEANUP-audit-prompt.md:13`
  - scope control: “**Max 25-50 files per agent**” `.dev/.../CLEANUP-audit-prompt.md:16`
- **Output schema**: summary lists grouped by delete/decision/keep + gitignore suggestions.
- **Escalation intent**: catch “what’s obviously wrong” first; deeper structural correctness is deferred to Pass 2/3.
- **Orchestration model**: per-agent limited file scope; incremental saves.

### Pass 2 prompt: “directory deep audit” (structural correctness & proof)
**Source**: `.dev/releases/current/repo-cleanup/cleanup-prompts/CLEANUP-audit-prompt-2.md`

- **Stated goal (generic)**: validate placement, staleness, broken references, and structural issues (things that “look fine” but aren’t).
- **Classification taxonomy (evolves)**:
  - finding categories: `MISPLACED | STALE | STRUCTURAL ISSUE | BROKEN REFS | VERIFIED OK` `.dev/.../CLEANUP-audit-prompt-2.md:86`
  - action recommendations: `KEEP | MOVE | DELETE | FLAG`
- **Verification protocol (stronger)**: “PROVE KEEP” by checking references and conventions; avoid handwaving:
  - “Lazy agents who mark files KEEP without evidence will be caught.” `.dev/.../CLEANUP-audit-prompt-2.md:70`
  - requires structured evidence: “### **MANDATORY: Per-File Deep Profile**” `.dev/.../CLEANUP-audit-prompt-2.md:88`
- **Safety constraints**: read-only remains; still scoped to 25–50 files per agent.
- **Output schema**: mandatory per-file profile (even for KEEP) + summary buckets for delete/move/flag/broken refs/verified ok.
- **Escalation logic**: Pass 2 addresses Pass 1’s biggest weakness: “KEEP by vibes” and doc claims not actually verified.

### Pass 3 prompt: “full-repo cross-cutting audit” (sprawl, duplication, consolidation)
**Source**: `.dev/releases/current/repo-cleanup/cleanup-prompts/CLEANUP-audit-prompt-3.md`

- **Stated goal (generic)**: find cross-directory duplication/sprawl and near-duplicates that per-directory audits miss.
- **Classification taxonomy (expands)**:
  - adds `CONSOLIDATE` explicitly: `.dev/.../CLEANUP-audit-prompt-3.md:158` (and template includes “Files to CONSOLIDATE”)
- **Verification protocol (amplified)**:
  - “actually **DIFF**… **Quantify the overlap**” `.dev/.../CLEANUP-audit-prompt-3.md:24`
  - “Compare, don’t just catalog.” `.dev/.../CLEANUP-audit-prompt-3.md:276`
- **Safety constraints**:
  - “ALREADY-KNOWN ISSUES — DO NOT RE-FLAG” `.dev/.../CLEANUP-audit-prompt-3.md:29`
  - completion discipline: “audit is not complete until every file… profiled… if low on context… list remaining” `.dev/.../CLEANUP-audit-prompt-3.md:273`
- **Output schema**: action-grouped sections including CONSOLIDATE + “Remaining” + “Completion Criteria”.

### Pass 3 batch orchestration plan (26 batches)
**Source**: `.dev/releases/current/repo-cleanup/cleanup-prompts/CLEANUP-p3-batch-assignments.md`

- **Agent orchestration model**:
  - strict exclusions (avoid waste): excludes `node_modules/`, `.git/`, caches, and also excludes `.dev/` itself in this pass `.dev/.../CLEANUP-p3-batch-assignments.md:6`
  - batch sizing: “Target per batch: 20-50 files” `.dev/.../CLEANUP-p3-batch-assignments.md:7`
  - prioritization: “Run HIGH priority batches first (1-4)” `.dev/.../CLEANUP-p3-batch-assignments.md:348`
  - binary asset handling: oversized batches are allowed because they’re filename-grep operations `.dev/.../CLEANUP-p3-batch-assignments.md:354`

---

### Phase 1 → Reusable cleanup-command principles (generic)

1. **Read-only by default**: audit output only; no repo edits.
2. **Conservative bias**: uncertainty ⇒ REVIEW/FLAG, not DELETE.
3. **Proof standards rise each pass**: Pass1 quick triage → Pass2 per-file proof → Pass3 cross-cutting diff/overlap proof.
4. **Mandatory evidence**: every KEEP/DELETE needs verifiable anchors (refs + file:line).
5. **Incremental-save protocol**: reduce loss and drift; checkpoint frequently.
6. **Scope discipline**: cap files per agent; explicit exclusions; prevent “audit the world”.
7. **Orchestrated batching**: priority-first batches, parallel where independent, special fast-path for binary dirs.
8. **Noise control**: “already-known issues” registry to prevent re-flagging.
9. **Completion criteria & Remaining list**: transparency beats pretending completeness.
10. **Output schema as a quality gate**: reports must be machine-checkable (consistent fields).

---

## Phase 2 — Output Quality Assessment (Pass 2 outputs in `cleanup-todo/`)

### Score table (1–10), per requested 6 dimensions
(Completeness, Profile quality, Verification depth, Classification accuracy, Cross-reference quality, Novel findings; plus aggregate avg.)

| Report | Completeness | Profile | Verify | Classify | X-ref | Novel | Avg |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cleanup-todo/CLEANUP-p2-frontend-wizard-doc-ui.md` | 8 | 8 | 6 | 7 | 7 | 6 | 7.00 |
| `cleanup-todo/CLEANUP-p2-frontend-root-components.md` | 8 | 8 | 6 | 7 | 7 | 7 | 7.20 |
| `cleanup-todo/CLEANUP-p2-frontend-streaming.md` | 9 | 8 | 7 | 7 | 8 | 7 | 7.70 |
| `cleanup-todo/CLEANUP-p2-frontend-tests.md` | 9 | 8 | 7 | 6 | 7 | 8 | 7.50 |
| `cleanup-todo/CLEANUP-p2-frontend-root-config.md` | 9 | 9 | 9 | 9 | 10 | 9 | 9.20 |
| `cleanup-todo/CLEANUP-p2-frontend-src-lib-config.md` | 9 | 9 | 9 | 9 | 8 | 8 | 8.70 |
| `cleanup-todo/CLEANUP-p2-frontend-src-remaining.md` | 9 | 9 | 9 | 9 | 8 | 8 | 8.70 |
| `cleanup-todo/CLEANUP-p2-frontend-src-pages.md` | 9 | 8 | 8 | 9 | 8 | 8 | 8.30 |
| `cleanup-todo/CLEANUP-p2-frontend-src-test-pages.md` | 10 | 9 | 8 | 9 | 7 | 7 | 8.33 |
| `cleanup-todo/CLEANUP-p2-k8s-helm.md` | 10 | 10 | 10 | 10 | 10 | 9 | 9.83 |
| `cleanup-todo/CLEANUP-p2-terraform-modules.md` | 10 | 9 | 9 | 9 | 8 | 8 | 8.83 |
| `cleanup-todo/CLEANUP-p2-ue-manager.md` | 10 | 10 | 9 | 10 | 9 | 8 | 9.33 |
| `cleanup-todo/CLEANUP-p2-scripts-root.md` | 9 | 9 | 8 | 8 | 9 | 8 | 8.50 |
| `cleanup-todo/CLEANUP-p2-small-dirs.md` | 9 | 9 | 8 | 8 | 8 | 8 | 8.30 |
| `cleanup-todo/CLEANUP-p2-tests-root.md` | 10 | 9 | 9 | 9 | 9 | 9 | 9.20 |
| `cleanup-todo/README.md` *(index doc)* | 7 | 4 | 5 | 6 | 6 | 6 | 5.70 |

**Rollups (from the 15 “real” audits, excluding README):**
- Unweighted avg ≈ **8.44/10**
- Weighted by audited-file counts (sum “Files audited” across reports = **327**) ≈ **8.50/10**

### Phase 2: systemic observations (quality)

**Consistent strengths**
- Most reports actually follow the Pass 2 “mandatory per-file profile” pattern and cite file:line references frequently.
- Several reports demonstrate real cross-system reasoning (especially infra + tests).

**Consistent weaknesses (lowest-scoring dimensions cluster around “verify/x-ref”)**
- Some “no imports / not used” claims are not always accompanied by reproducible grep evidence snippets.
- Cross-repo verification depth varies: a few reports primarily check code imports but not CI scripts/compose/tooling references.
- The `cleanup-todo/README.md` is useful operationally but scores low on “profile quality” because it’s not an audit output—this is expected and should be treated separately in the command design.

---

## Phase 3 — Effectiveness Scoring Framework + Overall Score (0–100)

### Framework (as requested)
Weights and interpretation:

| Dimension | Weight | How scored here |
|---|---:|---|
| Coverage Breadth | 20% | audited files w/ profiles ÷ tracked files |
| Evidence Quality | 25% | weighted evidence index from Phase 2 (profile+verify+x-ref) |
| False Positive Rate | 15% | inverse score: higher = fewer “DELETE but needed” risks |
| False Negative Rate | 15% | inverse score: higher = fewer missed issues |
| Actionability | 15% | can a dev execute without more research |
| Escalation Effectiveness | 10% | Pass2 clearly deeper than Pass1; Pass3 design quality but execution evidence varies |

### Applying the framework (observed, using available artifacts)

**Inputs used**
- Tracked files: `git ls-files | wc -l` ⇒ **5942**
- Pass 2 audited file count: sum of “Files audited” lines across the 15 audit reports ⇒ **327** (upper bound on unique files)

#### Sub-scores (0–100) + justification examples

1) **Coverage Breadth: 6 / 100**
- Calculation: 327 ÷ 5942 ≈ **5.5%** deep-profiled.
- Interpretation: Pass 2 audits are high quality but represent a small fraction of repo file count; Pass 3 batching is designed to fix this, but Pass 3 outputs were not part of the evaluated artifacts.

2) **Evidence Quality: 85 / 100**
- Derived from a weighted evidence index across reports (profile+verify+x-ref).
- Examples of strong evidence behavior:
  - infra drift identified with concrete anchors (e.g., k8s/helm CI vs deploy mismatch and specific YAML defect in `CLEANUP-p2-k8s-helm.md`)
  - test integrity issues tied to config + scripts (e.g., Playwright project mismatch in `CLEANUP-p2-frontend-root-config.md`)
- Main evidence gap: some “not imported anywhere” assertions lack embedded grep excerpts in lower-scoring frontend reports.

3) **False Positive Resistance (low false positives): 80 / 100**
- Evidence the approach avoids reckless deletion:
  - `CLEANUP-p2-terraform-modules.md` explicitly recommends **not deleting** substantive unused modules (risk-calibrated KEEP/FLAG posture).
  - `CLEANUP-p2-small-dirs.md` treats “aspirational infra” (e.g., runners/vault) as FLAG/decision, not DELETE.
- Residual risk: some aggressive deletes in frontend areas depend on import-graph assumptions and should add “dynamic usage” checks.

4) **False Negative Resistance (low missed issues): 60 / 100**
- Strong at catching *within-scope* structural issues (dual routing, misplaced API endpoints, CI drift).
- But constrained by:
  - low overall breadth (coverage gap)
  - Pass 3 “diff & consolidate cross-cutting duplicates” is required by prompt but not evidenced here, so repo-wide duplication/sprawl can remain under-detected.

5) **Actionability: 85 / 100**
- Many reports provide concrete, executable steps (paths, line numbers, explicit DELETE/MOVE/FLAG lists).
- High-actionability examples:
  - `CLEANUP-p2-ue-manager.md` port inconsistency called out across multiple artifacts (clear multi-file alignment task).
  - `CLEANUP-p2-tests-root.md` identifies tests that always pass / are skipped (clear delete/consolidate targets).
- Actionability gap: some “FLAG” items would benefit from a minimal verification checklist (“what evidence would settle this?”).

6) **Escalation Effectiveness: 70 / 100**
- Pass 2 *clearly* catches what Pass 1 structurally cannot (e.g., fabricated READMEs, CI-vs-deploy drift, misplaced Next API routes).
- Pass 3 escalation is well-designed on paper (diff/overlap, already-known issues, completion criteria) but not demonstrated by evaluated outputs.

### Overall effectiveness score (weighted)

**Overall = 63 / 100**

Breakdown:
- Coverage 6×0.20 = 1.2
- Evidence 85×0.25 = 21.25
- False positives 80×0.15 = 12
- False negatives 60×0.15 = 9
- Actionability 85×0.15 = 12.75
- Escalation 70×0.10 = 7
**Total ≈ 63.2 → 63/100**

**Interpretation**: The methodology + Pass 2 execution quality is strong, but the *program-level* effectiveness is capped by breadth (and by the absence of demonstrated Pass 3 consolidation outputs).

---

## Phase 4 — Custom Command PRD (for `.claude/commands/`)

## 1) Command name & purpose

**Name**: `/sc:cleanup-audit`
**Purpose**: Perform a **read-only, evidence-backed, multi-pass repo cleanup audit** that produces an executable cleanup plan (DELETE/MOVE/CONSOLIDATE/FLAG/KEEP) with verifiable citations.

## 2) Objectives (generic, monorepo-ready)

- Identify **safe deletions** (true orphans, obsolete artifacts, redundant configs, dead tests).
- Identify **misplacements** (files in wrong directory structure).
- Identify **stale or lying documentation** (docs that reference non-existent files or wrong behavior).
- Identify **broken references** across code/docs/config/CI/scripts.
- Identify **cross-cutting duplication and sprawl** (near-duplicate compose files, deploy scripts, test configs).
- Produce a **prioritized, risk-calibrated action plan** with verification steps.

## 3) Multi-pass architecture (3-pass escalation model)

### Pass 1: Surface sweep (triage)
- Goal: fast classification of obvious junk.
- Evidence: light read + repo-wide reference check.
- Output: delete/keep/review lists + gitignore suggestions.

### Pass 2: Deep directory audit (prove correctness)
- Goal: per-file truth verification + structural correctness.
- Mandatory: per-file profiles for **every** file in scope.
- Output: per-file evidence + grouped action summaries.

### Pass 3: Cross-cutting consolidation audit (diff & dedupe)
- Goal: compare similar artifacts across repo; quantify overlap; recommend consolidation.
- Mandatory: diff/overlap quantification + “already-known issues” suppression + “Remaining” list.

## 4) Classification taxonomy (unified)

### Actions (primary)
- **KEEP** (verified; has evidence)
- **DELETE** (safe to remove; includes proof of non-usage + replacement context if applicable)
- **MOVE** (wrong location; includes target location + references to update)
- **FLAG** (needs code changes / decision / further verification)
- **CONSOLIDATE** (merge duplicates; specify canonical file and what to port)

### Finding types (secondary, for Pass 2/3)
- **MISPLACED**, **STALE**, **STRUCTURAL ISSUE**, **BROKEN REFS**, **VERIFIED OK**

## 5) Verification protocol (mandatory evidence steps)

For each file (or file group), the audit must:

1. **Read** enough to understand intent (depth depends on pass).
2. **Search references**:
   - code imports/includes
   - scripts and CI configs
   - docker-compose / k8s / helm / terraform references
   - docs references / links
3. **Check conventions**:
   - directory ownership & naming patterns
   - expected location per framework conventions
4. **Decide with a two-signal rule** for DELETE/CONSOLIDATE:
   - no consumers found **and**
   - either (a) superseded by a known replacement, or (b) clearly an artifact (cache/log/tmp/demo)
5. **If dynamic loading is plausible**, downgrade DELETE → FLAG unless proven.

## 6) Agent orchestration (batching, parallelism, priority)

- Default batch size: **20–50 files per agent** (source: Pass 1/2 prompts; Pass 3 plan).
- Exclusions: `.git/`, `node_modules/`, build outputs, caches, vendor dirs.
- Priority ordering (generic):
  1) cross-cutting infra sprawl (compose/deploy/CI)
  2) runtime-critical config
  3) tests and tooling (prevent “false green” CI)
  4) docs and ancillary assets
- Parallelization:
  - Run independent directory audits in parallel.
  - For binary/asset dirs: “filename-grep audit” mode (high throughput).

## 7) Output schema (standardized report format)

### Global required sections (all passes)
- Scope definition (dirs/files covered; exclusions)
- Summary counts (DELETE/MOVE/FLAG/CONSOLIDATE/KEEP)
- “Remaining / Not audited” (mandatory if incomplete)
- “Already-known issues not re-flagged” (Pass 3)

### Pass 2/3 per-file profile (mandatory fields)
- What it does
- References (file:line citations)
- Superseded by / duplicates (if any)
- Risk notes (runtime/CI/test/doc impact)
- Recommendation (KEEP/MOVE/DELETE/FLAG/CONSOLIDATE)
- Verification notes (what you checked)

## 8) Safety rails

- **Read-only enforcement**: audit writes only to the report.
- **Err-on-KEEP bias**: uncertainty ⇒ FLAG/REVIEW.
- **No speculative deletions**.
- **Incremental saving**: checkpoint frequently; never hold large unsaved batches.
- **No vendor-dir scanning** by default (performance + noise control).

## 9) Quality gates (minimum evidence thresholds)

A recommendation is invalid unless:

- **DELETE** has: (a) reference check across code+CI+scripts+docs, (b) explicit “no consumers found” statement, and (c) dynamic-use risk addressed.
- **MOVE** has: (a) clear target location rationale, (b) list of refs to update.
- **CONSOLIDATE** has: (a) diff/overlap quantification, (b) canonical file chosen + migration notes.
- **KEEP** has: (a) at least one concrete consumer/reference or convention proof.
- Reports missing mandatory per-file profiles (Pass 2) are **failed**.

## 10) Effectiveness score (from Phase 3)

**Observed score: 63/100**
- Strong evidence & actionability, but breadth and Pass 3 consolidation execution evidence cap the score.

## 11) Improvement recommendations (to raise effectiveness score)

1. **Coverage tracking**: auto-generate scope file lists and compute coverage vs `git ls-files` (closes the 6/100 breadth gap).
2. **Evidence snippets for “no refs”**: require embedding a short grep result summary (pattern + count) for every DELETE.
3. **Dynamic-use checklist**: codify common dynamic reference patterns (env vars, string-based loaders, plugin registries) so “no imports” isn’t overtrusted.
4. **Pass 3 consolidation enforcement**: require a “duplication matrix” (compose/deploy/tests/configs) with overlap %.
5. **Workflow-to-config mapping**: for test/CI findings, explicitly map workflow file → command → config used, so test integrity claims are reproducible.
6. **Portable output paths**: eliminate any absolute machine paths in templates; use `$REPO_ROOT` + relative output locations.
