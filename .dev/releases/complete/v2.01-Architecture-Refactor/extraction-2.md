---
spec_source: ".dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md"
spec_type: "architecture-refactor"
spec_lines: 1175
extraction_timestamp: "2026-02-25"
extraction_method: "chunked (>500 lines)"
schema_version: "1.0"

complexity:
  score: 0.85
  class: "HIGH"
  factors:
    multi_domain: 0.20          # 4 distinct domains
    file_count: 0.20            # ~30+ files touched
    architectural_scope: 0.20  # 3-tier model enforcement
    dependency_density: 0.15   # strict linear DAG with atomic groups
    migration_risk: 0.10       # rollback incident precedent

domains:
  - name: "Architecture/Design"
    weight: 0.35
    evidence: "3-tier model, naming conventions, policy doc, verbatim templates"
  - name: "Build/CI"
    weight: 0.25
    evidence: "Makefile lint-architecture, sync-dev, verify-sync heuristic removal"
  - name: "Code Refactoring"
    weight: 0.25
    evidence: "5 skill renames, 5 command refactors, task-unified extraction"
  - name: "Testing/QA"
    weight: 0.15
    evidence: "integration tests, return contract routing, validation scripts"

personas:
  primary: "architect"
  secondary: ["analyzer", "devops", "qa"]
  activation_rationale: "Multi-domain architectural refactor with build system and CI/QA components"

requirements:
  functional:
    - id: "REQ-001"
      priority: "CRITICAL"
      source: "§1 Overview, §18 Policy Reference"
      statement: "Architecture policy document must exist at docs/architecture/command-skill-policy.md defining 3-tier model, naming conventions, component contracts"
      acceptance: "File exists, is not a duplicate of src/superclaude/ARCHITECTURE.md (BUG-004 resolution)"
      phase: "P1"
      task: "T01.02"

    - id: "REQ-002"
      priority: "CRITICAL"
      source: "§7 Skills to Rename"
      statement: "5 skill directories renamed to -protocol suffix: sc-adversarial→sc-adversarial-protocol, sc-cleanup-audit→sc-cleanup-audit-protocol, sc-roadmap→sc-roadmap-protocol, sc-task-unified→sc-task-unified-protocol, sc-validate-tests→sc-validate-tests-protocol"
      acceptance: "No old directory names exist; new directories present in both src/ and .claude/; SKILL.md name: fields updated"
      phase: "Layer 1 (DAG)"
      task: "T06.04 (part)"
      notes: "Treat all staged rogue-agent work as untrusted; redo from scratch"

    - id: "REQ-003"
      priority: "CRITICAL"
      source: "§5 Component Definitions, §8 Invocation Wiring"
      statement: "5 paired command files must have ## Activation sections referencing Skill sc:<name>-protocol and Skill in allowed-tools frontmatter"
      acceptance: "BUG-001 fixed; grep -l '## Activation' commands/ returns 5 files; all 5 have Skill in allowed-tools"
      phase: "P2 + P6"
      task: "T02.04, T06.04"

    - id: "REQ-004"
      priority: "CRITICAL"
      source: "§9 Fallback Protocol, §13 Phase Plan T02.03"
      statement: "Wave 2 Step 3 in sc-roadmap-protocol/SKILL.md decomposed into 6 sub-steps (3a-3f) with explicit tool bindings, fallback F1/F2-3/F4-5 protocol, and return contract routing"
      acceptance: "8-point audit passes (per §13 T02.03 compliance note); convergence threshold 0.6 documented"
      phase: "P2"
      task: "T02.03"

    - id: "REQ-005"
      priority: "CRITICAL"
      source: "§12 Bug Inventory BUG-006"
      statement: "roadmap.md ## Activation section rewritten to reference 'Skill sc:roadmap-protocol' (not old file path)"
      acceptance: "grep 'Skill sc:roadmap-protocol' src/superclaude/commands/roadmap.md returns match"
      phase: "P2"
      task: "T02.04"

    - id: "REQ-006"
      priority: "HIGH"
      source: "§10 Return Contract Schema"
      statement: "10-field canonical return contract schema defined and implemented: status, merged_output_path, convergence_score, artifacts_dir, unresolved_conflicts (list[string]), fallback_mode, base_variant, schema_version, failure_stage, invocation_method"
      acceptance: "Schema in SKILL.md ## Return Contract section matches 10-field table; unresolved_conflicts is list[string] not integer"
      phase: "P4"
      task: "T04.01"

    - id: "REQ-007"
      priority: "HIGH"
      source: "§11 Enforcement Mechanisms, §13 T03.02"
      statement: "make lint-architecture target implemented with 6 of 10 designed policy checks: (1) command→skill link, (2) skill→command link, (3) command size warn, (4) command size error, (6) activation section present, (8) skill frontmatter complete, (9) protocol naming consistency"
      acceptance: "make lint-architecture exits 0 on clean tree; exits 1 on any ERROR finding"
      phase: "P3"
      task: "T03.02"
      notes: "Checks 5 and 7 marked NEEDS DESIGN; not in scope"

    - id: "REQ-008"
      priority: "HIGH"
      source: "§11 Enforcement, §13 T03.01"
      statement: "Makefile sync-dev and verify-sync: remove 4-line skill-skip heuristic from sync-dev and 5-line skip heuristic from verify-sync"
      acceptance: "make sync-dev copies ALL skills including -protocol ones; make verify-sync checks ALL skills"
      phase: "P3"
      task: "T03.01"

    - id: "REQ-009"
      priority: "HIGH"
      source: "§12 BUG-001"
      statement: "All 5 command files (adversarial.md, cleanup-audit.md, roadmap.md, task-unified.md, validate-tests.md) have Skill in allowed-tools frontmatter"
      acceptance: "grep 'Skill' src/superclaude/commands/{adversarial,cleanup-audit,roadmap,task-unified,validate-tests}.md all return matches"
      phase: "P2 + P6"
      task: "T02.01, T02.02, T06.04"

    - id: "REQ-010"
      priority: "MEDIUM"
      source: "§12 BUG-002"
      statement: "validate-tests.md line 63 stale path updated from skills/sc-validate-tests/classification-algorithm.yaml to sc-validate-tests-protocol/"
      acceptance: "grep stale path returns no results"
      phase: "P6"
      task: "T06.06"

    - id: "REQ-011"
      priority: "MEDIUM"
      source: "§12 BUG-003"
      statement: "Orchestrator threshold aligned to >= 3 (not >= 5) in sc-roadmap-protocol/SKILL.md"
      acceptance: "No reference to '>= 5' for orchestrator threshold in SKILL.md"
      phase: "P6"
      task: "T06.06"

    - id: "REQ-012"
      priority: "MEDIUM"
      source: "§12 BUG-004"
      statement: "Architecture policy duplication resolved: docs/architecture/command-skill-policy.md is canonical; src/superclaude/ARCHITECTURE.md becomes symlink or cross-reference"
      acceptance: "Two files are not byte-identical; canonical source clearly designated"
      phase: "P6"
      task: "T06.05"

    - id: "REQ-013"
      priority: "MEDIUM"
      source: "§12 BUG-005"
      statement: "sc-roadmap-protocol/SKILL.md Wave 0 Step 5 stale path updated from sc-adversarial/SKILL.md to sc-adversarial-protocol/SKILL.md"
      acceptance: "No reference to 'sc-adversarial/' (old path) in SKILL.md"
      phase: "P2/P6"
      task: "T06.04 (part)"

    - id: "REQ-014"
      priority: "MEDIUM"
      source: "§13 T06.03"
      statement: "task-unified.md major extraction: reduce from 567 lines to ~106 lines by extracting protocol to sc-task-unified-protocol/SKILL.md"
      acceptance: "wc -l task-unified.md returns ≤350; protocol content in SKILL.md"
      phase: "P6"
      task: "T06.03"

    - id: "REQ-015"
      priority: "MEDIUM"
      source: "§9 Fallback Protocol Step 3e"
      statement: "Return contract routing implemented in Wave 2 Step 3e: PASS (>=0.6), PARTIAL (>=0.5), FAIL (<0.5); missing-file guard; YAML parse error fallback 0.5"
      acceptance: "Sub-steps 3e routing logic present in SKILL.md; convergence_score used for 3-way routing"
      phase: "P2"
      task: "T02.03"

    - id: "REQ-016"
      priority: "LOW"
      source: "§13 T05.01"
      statement: "Verb-to-tool glossary added to disambiguate 'Invoke' (Bash/claude -p) vs 'Dispatch' (Task tool) vs 'Skill' (Skill tool)"
      acceptance: "Glossary section exists in policy or SKILL.md"
      phase: "P5"
      task: "T05.01"

    - id: "REQ-017"
      priority: "LOW"
      source: "§13 T05.02"
      statement: "Wave 1A Step 2 semantic alignment fix"
      acceptance: "Step 2 semantics consistent with SKILL-DIRECT invocation approach"
      phase: "P5"
      task: "T05.02"

    - id: "REQ-018"
      priority: "LOW"
      source: "§13 T05.03"
      statement: "Pseudo-CLI invocation converted to executable tool bindings throughout SKILL.md"
      acceptance: "No bare 'Invoke X' verbs without explicit tool binding in SKILL.md"
      phase: "P5"
      task: "T05.03"

    - id: "REQ-019"
      priority: "LOW"
      source: "§13 T06.01"
      statement: "Cross-skill invocation pattern documented (how one protocol skill invokes another)"
      acceptance: "Documentation exists in policy or dedicated ref file"
      phase: "P6"
      task: "T06.01"

    - id: "REQ-020"
      priority: "LOW"
      source: "§13 T06.02"
      statement: "Tier 2 ref loader design (claude -p script) documented"
      acceptance: "Design document or section in policy exists"
      phase: "P6"
      task: "T06.02"

  non_functional:
    - id: "NFR-001"
      category: "Size Constraint"
      statement: "Command files paired with protocol skills: target ≤150 lines; WARN at 200 lines; ERROR at 500 lines"
      enforcement: "make lint-architecture checks 3 and 4"

    - id: "NFR-002"
      category: "CI Gate"
      statement: "make lint-architecture must exit 0 (no ERRORs) before any Layer 3 (command migration) work begins — Rule 7.5"
      enforcement: "Phase 3 exit criteria block Phase 4+ work"

    - id: "NFR-003"
      category: "Atomicity"
      statement: "Atomic change groups must be applied together. Group A: per-command unit (4 files). Group B: Makefile enforcement (4 targets)"
      enforcement: "Partial application risk matrix in §16b"

    - id: "NFR-004"
      category: "Invocation Variant"
      statement: "FALLBACK-ONLY variant: TOOL_NOT_AVAILABLE probe (D-0001). Task agent dispatch is sole viable invocation mechanism until D-0001 is re-verified"
      enforcement: "T01.01 probe must re-verify; D-0001 reversal may change this"

    - id: "NFR-005"
      category: "DAG Compliance"
      statement: "Migration must follow Layer 0→1→2→3→4→5 DAG with no circular dependencies. No out-of-order execution."
      enforcement: "Phase exit criteria at each milestone boundary"

out_of_scope:
  - "RC3/RC5 fixes (deferred v2.02)"
  - "Full claude -p headless implementation"
  - "Runtime scope control"
  - "Remaining 4 CI checks (#5 and #7 need design)"
  - "Agent registry / framework-level dispatch (v5.0)"
  - "v2.02-Roadmap-v3 improvements"

deferred_items:
  - id: "DEFER-001"
    item: "RC3: Agent dispatch mechanism (subagent_type dead metadata)"
    rationale: "Latent defect; surfaces only after RC1/RC2/RC4 fixed. Score 0.70 below v2.01 cut line."
    target: "v2.02"
  - id: "DEFER-002"
    item: "RC5: Full Claude behavioral fallback quality gate (2-tier)"
    rationale: "Partial coverage in v2.01 fallback protocol; full gate is v2.02 work"
    target: "v2.02"
  - id: "DEFER-003"
    item: "CI checks 5 and 7 (inline protocol detection, activation correctness)"
    rationale: "Marked NEEDS DESIGN; architecture not finalized"
    target: "v2.02"

open_issues:
  - id: "ISSUE-001"
    severity: "HIGH"
    statement: "Runtime scope control not designed — root cause of 68-file rollback incident"
  - id: "ISSUE-002"
    severity: "HIGH"
    statement: "T01.01 probe result (D-0001: TOOL_NOT_AVAILABLE) must be re-verified in current environment"
  - id: "ISSUE-003"
    severity: "MEDIUM"
    statement: "unresolved_conflicts field type was integer in prior implementation; must be list[string]"
  - id: "ISSUE-004"
    severity: "MEDIUM"
    statement: "refs/headless-invocation.md and probe fixtures don't exist yet"
---

# Extraction Report — v2.01 Architecture Refactor

## Overview

Extraction from `sprint-spec.md` (1175 lines, chunked method). This is a **strict architectural refactor** — NOT a feature release. Purpose: enforce clean separation between Commands (doors), Skills (rooms), and Refs (drawers) to fix agents not following `/sc:command` instructions.

**Core problem**: `sc:roadmap` attempts to invoke `sc:adversarial` via natural language prose — this silently fails. 68-file rollback incident confirmed the severity.

## Requirement Counts

| Priority | Count |
|----------|-------|
| CRITICAL | 5 |
| HIGH | 4 |
| MEDIUM | 6 |
| LOW | 5 |
| **Total** | **20** |
| Non-Functional | 5 |
| Out-of-Scope (documented) | 6 |
| Deferred (v2.02) | 3 |

## Domain Distribution

```
Architecture/Design  ████████████████████████████████████ 35%
Build/CI             █████████████████████████ 25%
Code Refactoring     █████████████████████████ 25%
Testing/QA           ███████████████ 15%
```

## Bug Inventory (from §12)

| Bug | Severity | Phase |
|-----|----------|-------|
| BUG-001: Skill missing from allowed-tools (all 5 commands) | HIGH | P2+P6 |
| BUG-002: validate-tests stale path line 63 | MEDIUM | P6 |
| BUG-003: Orchestrator threshold inconsistency (3 vs 5) | MEDIUM | P6 |
| BUG-004: Architecture policy duplicated (byte-identical) | MEDIUM | P6 |
| BUG-005: roadmap SKILL.md stale adversarial path | MEDIUM | P2/P6 |
| BUG-006: roadmap.md Activation references old file path | HIGH | P2 |

## Key Design Decisions (Preserved from §17)

| Decision | Value |
|----------|-------|
| D-0001 | TOOL_NOT_AVAILABLE (re-verify in T01.01) |
| D-0002 | FALLBACK-ONLY variant for sprint |
| D-0006 | Wave 2 Step 3 decomposition (3a-3f) |
| D-0008 | Return contract routing inline in Step 3e |
| Convergence threshold | 0.6 (PASS) / 0.5 (PARTIAL) / <0.5 (FAIL) |
| Fallback sentinel | 0.5 (deliberately below threshold → Partial path) |
| Orchestrator threshold | >= 3 agents (not >= 5) |

## Current Branch State (at rollback, commit 5733e32)

| Component | src/ Status | .claude/ Status |
|-----------|------------|----------------|
| Commands (37) | All present | IN SYNC |
| sc-adversarial-protocol | Exists | EMPTY (0 files) |
| sc-cleanup-audit-protocol | Exists | EMPTY (0 files) |
| sc-roadmap-protocol | Exists | EMPTY (0 files) |
| sc-task-unified-protocol | Exists | EMPTY (0 files) |
| sc-validate-tests-protocol | Exists | EMPTY (0 files) |

**Critical state**: Only 1 command has `## Activation` (roadmap.md — broken path). 0 commands have `Skill` in `allowed-tools`.
