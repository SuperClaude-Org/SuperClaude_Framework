---
comparison_pair: 8
ic_component: Cleanup-Audit CLI
lw_component: Automated QA Workflow + Anti-Hallucination Rules
ic_source: src/superclaude/cli/cleanup_audit/executor.py, src/superclaude/cli/audit/dead_code.py, src/superclaude/cli/audit/classification.py
lw_source: .gfdoc/scripts/automated_qa_workflow.sh, .gfdoc/rules/core/anti_hallucination_task_completion_rules.md
mapping_type: partial
verdict_class: IC stronger
confidence: 0.80
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Cleanup-Audit CLI (IC) vs Automated QA Workflow + Anti-Hallucination (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude cleanup-audit CLI is **purpose-built for read-only static analysis** with a layered, evidence-mandatory architecture. The three-tier dependency graph (Tier-A: AST-resolved imports at 0.95 confidence; Tier-B: grep text matching at 0.70; Tier-C: co-occurrence inference at 0.40) provides graduated confidence evidence for every deletion recommendation. The `classify_finding()` pure-Python function is deterministic — same inputs always produce same classification. The conservative bias (REVIEW when `has_references=True`) explicitly trades recall for precision, accepting missed deletions over false positives.

**Key strengths** (`src/superclaude/cli/audit/dead_code.py:108`, `src/superclaude/cli/audit/classification.py:110`):
- AST-resolved import detection (Tier-A, confidence 0.95): not just text matching
- 3-tier confidence-graded dependency graph: confidence annotated per edge type
- `classify_finding()`: pure Python, deterministic, testable independently
- Conservative bias: false negatives (missed deletes) preferred over false positives (wrong deletes)
- Stratified spot-check sampling with `seed=42`: reproducible validation
- `audit-validator`: CRITICAL FAIL on false negative DELETE — hard safety gate

### LW Advocate Position
The llm-workflows combination of automated QA workflow + anti-hallucination rules provides **stronger verification rigor** through the fail-closed PABLOV artifact chain and Presumption of Falsehood. LW's anti-hallucination rules require explicit "Verified" status per claim with a mandatory source reference. IC's cleanup-audit uses LLM agents for classification passes (G-001 surface scan via Haiku, G-002 structural via Sonnet), which are non-deterministic. LW's batch state machine with immutable batch numbers provides better auditability than IC's 6-step pipeline without a formal state file.

**Key strengths** (`automated_qa_workflow.sh:4972-5322`, `anti_hallucination_task_completion_rules.md:59-82`):
- Presumption of Falsehood: every claim starts "Incorrect" — burden of proof on agent
- Fail-closed verdict: mismatch between claim and proof = FAIL
- Immutable batch numbers: Batch 5 always means the same items
- Mandatory negative evidence: "Not found" must be documented (IC has no equivalent)
- DNSP recovery: pipeline never permanently stalls on missing artifact

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/cli/audit/dead_code.py` | 108 | Dead code detection: zero Tier-A + zero Tier-B importers + not entry point |
| `src/superclaude/cli/audit/dependency_graph.py` | 198 | 3-tier dependency graph: Tier-A (0.95), Tier-B (0.70), Tier-C (0.40) |
| `src/superclaude/cli/audit/classification.py` | 110 | `classify_finding()` pure Python, deterministic, maps to V2Tier + V2Action |
| `src/superclaude/cli/cleanup_audit/executor.py` | 54 | `execute_cleanup_audit()` with SignalHandler and OutputMonitor |
| `src/superclaude/cli/audit/spot_check.py` | 49 | `_stratified_sample()` seed=42 for reproducibility |
| `src/superclaude/agents/audit-validator.md` | — | CRITICAL FAIL on false negative DELETE |
| `src/superclaude/cli/cleanup_audit/commands.py` | 24 | `--pass surface|structural|cross-cutting|all` independent execution |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 59-66 | Presumption of Falsehood: default status "Incorrect" |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 76-82 | FAS -100: forgery = immediate task failure |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 83-89 | Mandatory negative evidence documentation |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 3129-3132 | Fail-closed: taskspec vs. programmatic handoff mismatch = FAIL |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 4972-5322 | Batch state machine with immutable state transitions |
| `.gfdoc/scripts/automated_qa_workflow.sh` | 5302-5303 | Overrun detection: quarantine unauthorized completions |
| `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md` | 128-137 | Strict COMPLETE definition: no suppressed warnings, all claims verified |

## 3. Adversarial Debate

**IC attacks LW**: LW's audit capability does not exist. LW's automated QA workflow is an execution orchestrator for tasks — it does not perform dead code detection, dependency analysis, or static audit of codebases. Comparing LW's QA workflow to IC's cleanup-audit is comparing execution infrastructure to static analysis tooling. IC's Tier-A AST import analysis, 3-tier dependency graph, and conservative DELETE classification have no LW analogs. This is a partial mapping, not a direct one.

**LW attacks IC**: IC's audit passes (G-001, G-002) are driven by Haiku and Sonnet LLM agents whose outputs are non-deterministic. Two runs against the same codebase will produce different per-file classifications. LW's batch state machine tracks what was claimed and what was proved — IC has no equivalent tracking of which agent produced which claim and whether that claim was independently verified beyond the 10% spot-check sample. 90% of IC's audit findings are never independently verified.

**IC counter**: LW's 100% claim verification (Presumption of Falsehood per-claim) would be prohibitively expensive for an audit producing hundreds of findings. IC's 10% stratified spot-check is a proportional quality strategy: verify a representative sample with a hard safety gate (CRITICAL FAIL on false-negative DELETE), then accept the remaining 90% under the conservative bias policy. The CRITICAL FAIL condition specifically catches the highest-severity audit error at relatively low spot-check cost.

**LW counter**: IC's `classify_finding()` confidence thresholds (0.90 for DELETE, 0.60 for INVESTIGATE) are hard-coded and not recalibratable without source code changes. LW's PABLOV verification is adaptive to the specific batch content. Additionally, IC has no formal mechanism for documenting "not found" evidence (mandatory in LW) — an IC audit may simply omit a finding without recording why.

**Convergence**: IC is decisively stronger for its intended purpose (static audit with graduated evidence). LW's contribution is in verification philosophy (Presumption of Falsehood, mandatory negative evidence documentation) which IC could adopt as behavioral NFRs for its audit agents.

## 4. Verdict

**Verdict class: IC STRONGER**

**Rationale**: IC's cleanup-audit has purpose-built capability LW entirely lacks: AST-resolved import detection, 3-tier confidence-graded dependency graph, deterministic `classify_finding()` function, and conservative bias policy. The comparison is partially asymmetric — LW's automated QA workflow is not designed for static codebase analysis. IC wins on capability grounds.

**Conditions where LW patterns should be adopted into IC**:
- Presumption of Falsehood for audit agent claims (IC agents should default to "classification unverified" until evidence gathered)
- Mandatory negative evidence (IC audit should document "no importers found" not just skip the entry)
- Fail-closed verdict for spot-check: IC's <20% discrepancy threshold → consider whether "any CRITICAL error" should be unconditional fail regardless of percentage

**Confidence: 0.80**

**Adopt patterns, not mass**: From LW: Presumption of Falsehood as IC audit agent's default epistemic stance, mandatory negative evidence documentation for every classification, and the strict COMPLETE definition (all claims verified, no suppressed warnings) as IC audit completion criteria. From IC: AST-resolved import detection (Tier-A), confidence-graded dependency graph, deterministic pure-Python classification function, conservative bias policy (prefer false negatives over false positives), and stratified spot-check with seeded reproducibility. Do NOT adopt: LW's bash implementation for audit logic, the full PABLOV artifact chain overhead for a static analysis tool, or the per-claim evidence table for every audit finding.
