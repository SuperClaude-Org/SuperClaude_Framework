---
comparison_pair: 5
ic_component: Task-Unified Tier System
lw_component: Quality Gates + Task Builder
ic_source: .claude/commands/sc/task-unified.md, .claude/skills/sc-tasklist-protocol/rules/tier-classification.md
lw_source: .gfdoc/rules/core/quality_gates.md, .claude/commands/rf/taskbuilder.md
mapping_type: functional_analog
verdict_class: IC stronger
confidence: 0.78
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Task-Unified Tier System (IC) vs Quality Gates + Task Builder (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude task-unified tier system provides **automatic task classification with transparent confidence scoring** that eliminates the user-decision burden of selecting appropriate verification levels. The STRICT → EXEMPT priority ordering with compound phrase overrides handles semantic edge cases (e.g., "minor auth change" → STRICT because auth always wins). The critical path override (security paths always trigger CRITICAL verification) provides a safety backstop that cannot be bypassed by keyword classification. The system routes to tier-appropriate verification (quality-engineer sub-agent for STRICT, direct tests for STANDARD) without requiring the user to know which agent or test level is appropriate.

**Key strengths** (`src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md:76`, `.claude/commands/sc/task-unified.md`):
- Automatic classification: same task description → same tier, every time
- STRICT > EXEMPT > LIGHT > STANDARD conflict resolution priority
- Critical path override: `auth/`, `security/`, `crypto/` paths always CRITICAL
- Compound phrase overrides: `"fix security"` → STRICT despite `"fix"` → STANDARD default
- Confidence threshold: <70% triggers user confirmation before execution begins
- `--skip-compliance` escape hatch with <12% usage target

### LW Advocate Position
The llm-workflows quality gates system provides **universal principles that apply across all output types**, with output-type-specific gate tables that prevent over-checking (applying code linting to docs) and under-checking (skipping evidence gates for analysis). The six universal principles (Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy) are more comprehensive than IC's tier keyword-matching approach. Anti-sycophancy as a first-class gate principle (not optional) is stronger than IC's keyword-based sycophancy detection.

**Key strengths** (`quality_gates.md:57-64`, `quality_gates.md:86-131`):
- Six universal quality principles applied to all output types
- Output-type-specific gate tables: code gates vs. analysis gates vs. opinion gates
- Three-tier severity system: Sev 1 (block), Sev 2 (cycle), Sev 3 (when able)
- Anti-sycophancy as a universal gate principle, not optional
- Task completion checklist: six mandatory conditions including "no placeholder content"

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` | 76 | Tier-to-verification routing: STRICT → quality-engineer (3-5K tokens, 60s) |
| `.claude/commands/sc/task-unified.md` | — | Classification decision tree: override → compound → keyword → context → conflict |
| `src/superclaude/core/ORCHESTRATOR.md` | 152 | Context boosters: >2 files +0.3 STRICT; security paths +0.4 STRICT |
| `.claude/commands/sc/task-unified.md` | — | STRICT MCP requirement: Sequential + Serena; fallback NOT allowed |
| `.claude/commands/sc/task-unified.md` | — | Critical path override: auth/, security/, crypto/ always CRITICAL |
| `.claude/skills/sc-tasklist-protocol/rules/tier-classification.md` | — | Compound phrase: "minor auth change" → STRICT; "quick fix" → LIGHT |
| `.claude/commands/sc/task-unified.md` | — | Confidence <70% → prompt user before execution begins |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.gfdoc/rules/core/quality_gates.md` | 57-64 | Six universal quality principles |
| `.gfdoc/rules/core/quality_gates.md` | 86-131 | Output-type-specific gate tables: code, analysis, opinion |
| `.gfdoc/rules/core/quality_gates.md` | 157-165 | Three-tier severity: Sev 1 (block), Sev 2 (cycle), Sev 3 (when able) |
| `.gfdoc/rules/core/quality_gates.md` | 149-156 | Task completion checklist: 6 mandatory conditions |
| `.gfdoc/rules/core/quality_gates.md` | 64 | Anti-sycophancy as universal gate principle |
| `.gfdoc/rules/core/quality_gates.md` | 167-185 | Automation as future work; current enforcement is agent-behavioral |
| `.gfdoc/rules/core/quality_gates.md` | 134-148 | Evidence table requirement for all technical claims |

## 3. Adversarial Debate

**IC attacks LW**: LW's quality gates are **agent-behavioral**, not programmatic. The document explicitly defers automation to future work (`quality_gates.md:167-185`). If the QA agent does not correctly apply the gates, they provide no protection. IC's classification and routing is programmatic: same task description produces same tier, tier determines which verification agent is invoked, and STRICT tier blocks on MCP unavailability rather than proceeding. IC's gates cannot be silently bypassed by an inattentive agent.

**LW attacks IC**: IC's classification uses keyword matching, which cannot handle semantic context. "Update authentication token expiry" should be STRICT, but "update" is STANDARD by default — only the "authentication" keyword escalates it. If a task description omits the security keyword, IC's classification will miss the elevation. LW's quality principles are content-based (Verifiability, Completeness) and apply regardless of how the task is described.

**IC counter**: The critical path override (paths matching `auth/`, `security/`, `crypto/`) provides the semantic safety net that keyword matching misses for code-level tasks. Even if a task description is vague, operating on authentication files triggers CRITICAL verification. The compound phrase override system (`"fix security"` → STRICT) handles the most common semantic edge cases.

**LW counter**: IC's output-type awareness is limited — STRICT/STANDARD/LIGHT/EXEMPT applies uniformly to all task types. LW's output-type-specific gates (different tables for code outputs vs. analysis outputs vs. opinion outputs) prevent both over-checking and under-checking. IC would apply code-level verification overhead to documentation tasks that don't warrant it.

**Convergence**: IC's classification automation is a genuine advantage over LW's manual gate application. LW's content-based universal principles are more comprehensive than IC's keyword-based classification. Combining IC's automatic routing with LW's universal principles would produce a stronger system than either alone.

## 4. Verdict

**Verdict class: IC STRONGER**

**Rationale**: Automatic classification with confidence scoring eliminates a category of user error that LW's manual gate application cannot prevent. The critical path override (filesystem-path-based safety backstop) provides semantic safety beyond keyword matching. The STRICT MCP requirement block (rather than degraded execution) is a safety decision LW has no equivalent for.

**Conditions where LW patterns should be adopted into IC**:
- Output-type-specific gate tables (IC applies uniform tier overhead; LW's content-type discrimination is more precise)
- Universal quality principles as NFR baseline (IC's tier system routes to verification agents, but LW's six principles define what those agents should actually verify)
- Anti-sycophancy as a universal gate principle (not just a tier-level feature)
- Mandatory task completion checklist (six conditions before "complete" status)

**Confidence: 0.78**

**Adopt patterns, not mass**: From LW: the six universal quality principles (Verifiability, Completeness, Correctness, Consistency, Clarity, Anti-Sycophancy) as the IC verification agent's check framework, output-type-specific gate application (code gates for code tasks, evidence gates for analysis tasks), and the three-tier severity model (Sev 1 blocks immediately, Sev 2 fixes in cycle, Sev 3 when able). From IC: automatic tier classification with confidence scoring, compound phrase overrides, critical path filesystem override, STRICT MCP unavailability blocking (vs. graceful degradation). Do NOT adopt: LW's manual gate application without automation, the evidence table overhead for all output types at all tiers.
