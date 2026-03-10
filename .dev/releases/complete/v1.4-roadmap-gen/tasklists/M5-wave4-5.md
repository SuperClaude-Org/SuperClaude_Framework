# Tasklist: M5 - Wave 4-5 Implementation (Validation & Completion)

## Metadata
- **Milestone**: M5
- **Dependencies**: M4
- **Estimated Complexity**: Medium-High
- **Primary Persona**: Backend, QA
- **Deliverables**: 5

---

## Tasks

### T5.1: Implement Quality-Engineer Task Validation
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. **CRITICAL**: Implement Task call WITHOUT `subagent_type` parameter
2. Embed agent specialization in prompt text:
   ```
   Task:
     description: "Quality validation of roadmap artifacts"
     prompt: |
       You are a quality-engineer agent performing roadmap validation.

       Focus areas:
       1. **Completeness**: Are all spec requirements covered?
       2. **Correctness**: Is milestone ordering logical?
       3. **Consistency**: Are IDs traceable across documents?
       4. **Compliance**: Do paths follow SuperClaude conventions?

       Review artifacts: [roadmap.md, extraction.md, tasklists/]

       Output JSON: {"quality_score": 0-100, "issues": [...], "rationale": "..."}
   ```
3. Parse quality_score from response
4. Store issues for reporting

#### Acceptance Criteria
- [ ] Task call uses correct pattern (NO subagent_type)
- [ ] Agent type embedded in prompt
- [ ] Quality score extracted (0-100)
- [ ] Issues captured for review
- [ ] Timeout handled gracefully

#### Verification
```bash
# Validate Task call pattern in SKILL.md
grep -A10 "quality-engineer" .claude/skills/sc-roadmap/SKILL.md
# Should NOT contain "subagent_type"
# Should contain embedded agent description
```

---

### T5.2: Implement Self-Review Validation Protocol
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement 4-question validation per spec Section 3.5:
   - Q1: "Did I read the entire specification before generating?"
     → Cite specific sections from spec
   - Q2: "Are all paths using correct SuperClaude conventions?"
     → Verify: .claude/skills/, plugins/superclaude/agents/
   - Q3: "Did I avoid the critical mistakes (see Section 6)?"
     → Check: No subagent_type, TodoWrite 3 states, etc.
   - Q4: "Is every claim traceable to the input specification?"
     → Map roadmap items to spec requirements
2. Generate evidence for each question
3. Calculate review_score (0-100)
4. List gaps found

#### Acceptance Criteria
- [ ] All 4 questions answered
- [ ] Evidence provided for each
- [ ] Score calculated
- [ ] Gaps identified and documented

#### Verification
```bash
# Check self-review output
# Should contain answers to all 4 questions with evidence
```

---

### T5.3: Implement Score Aggregation System
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Apply score weights per spec Section 3.5:
   - Quality Engineer: 60%
   - Self Review: 40%
2. Calculate weighted average:
   ```
   final_score = (quality_score * 0.6) + (review_score * 0.4)
   ```
3. Determine decision:
   - PASS: final_score >= 85%
   - REVISE: 70% <= final_score < 85%
   - REJECT: final_score < 70%
4. Execute decision actions:
   - PASS: Proceed to Wave 5, mark artifacts validated
   - REVISE: Generate improvement suggestions, allow proceed or iterate
   - REJECT: Preserve drafts with .draft extension, report failures

#### Acceptance Criteria
- [ ] Weights applied correctly (60%/40%)
- [ ] Thresholds enforced (85%, 70%)
- [ ] Decision actions executed
- [ ] Drafts preserved on REJECT

#### Verification
```bash
# Check validation output
# Should show final_score and decision (PASS/REVISE/REJECT)
```

---

### T5.4: Implement Completion Check
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Call `think_about_whether_you_are_done()` via Serena MCP
2. Verify completion criteria:
   - [ ] All 5 artifacts generated?
   - [ ] Validation passed or acknowledged?
   - [ ] No unresolved issues?
3. If criteria not met:
   - List missing items
   - Suggest next actions
4. If criteria met:
   - Proceed to memory persistence

#### Acceptance Criteria
- [ ] think_about_whether_you_are_done() called
- [ ] All 3 completion criteria checked
- [ ] Clear reporting of completion status
- [ ] Actionable suggestions if incomplete

#### Verification
```bash
# Check completion status output
# Should confirm all 5 artifacts and validation status
```

---

### T5.5: Implement Memory Persistence
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Call `write_memory` via Serena MCP
2. Memory content structure:
   ```yaml
   memory_name: "roadmap-gen-{spec-name}"
   content:
     version: "v1.4"
     spec_path: "<input file>"
     output_path: "<output directory>"
     artifacts_generated:
       - roadmap.md
       - extraction.md
       - tasklists/
       - test-strategy.md
       - execution-prompt.md
     validation_score: <final_score>
     completion_status: "success|partial|failed"
     timestamp: "<ISO8601>"
   ```
3. Handle Serena MCP unavailability:
   - Use circuit breaker pattern
   - Fallback: Log warning, continue without persistence
4. Confirm memory written

#### Acceptance Criteria
- [ ] write_memory called with correct structure
- [ ] Session information captured
- [ ] Circuit breaker handles MCP failure
- [ ] Fallback behavior documented

#### Verification
```bash
# Check memory via Serena
# list_memories should show roadmap-gen-{spec-name}
```

---

## Milestone Completion Checklist

- [ ] T5.1: Quality-engineer validation working
- [ ] T5.2: Self-review protocol implemented
- [ ] T5.3: Score aggregation correct
- [ ] T5.4: Completion check functional
- [ ] T5.5: Memory persistence working

## Dependencies

```
Wave 4 Output ──► T5.1 (quality-engineer) ──► T5.3 (aggregation)
             └──► T5.2 (self-review) ────────┘
                                             │
                                             ▼
                                    T5.4 (completion check)
                                             │
                                             ▼
                                    T5.5 (memory persistence)
```

## Critical Implementation Notes

### Task Tool Warning (Critical Correction #1)
The Task tool does **NOT** have a `subagent_type` parameter.

**WRONG**:
```yaml
Task:
  subagent_type: quality-engineer  # THIS DOES NOT EXIST
  prompt: "..."
```

**CORRECT**:
```yaml
Task:
  description: "Quality validation"
  prompt: |
    You are a quality-engineer agent...
    [Full agent specification in prompt]
```

### Score Thresholds Reference
| Score Range | Decision | Action |
|-------------|----------|--------|
| >= 85% | PASS | Proceed to completion |
| 70-84% | REVISE | Allow proceed or iterate |
| < 70% | REJECT | Preserve drafts, report |

---

*Tasklist generated by SuperClaude Roadmap Generator v1.0*
