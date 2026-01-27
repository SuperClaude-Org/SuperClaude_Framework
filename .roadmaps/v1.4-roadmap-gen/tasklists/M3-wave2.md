# Tasklist: M3 - Wave 2 Implementation (Planning & Template Selection)

## Metadata
- **Milestone**: M3
- **Dependencies**: M2
- **Estimated Complexity**: Medium
- **Primary Persona**: Backend
- **Deliverables**: 4

---

## Tasks

### T3.1: Implement Template Discovery Hierarchy
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement search order per spec Section 3.3:
   ```
   1. Local: ./templates/roadmaps/
   2. User: ~/.claude/templates/roadmaps/
   3. Plugin: plugins/superclaude/templates/roadmaps/
   4. Inline: Generate variant from domain analysis (fallback)
   ```
2. Check each path for template files
3. Return first matching template or trigger inline generation
4. Log discovery path for debugging

#### Acceptance Criteria
- [ ] All 4 search paths checked in order
- [ ] First match returned
- [ ] Inline fallback triggered when no match
- [ ] Discovery path logged

#### Verification
```bash
# Test with template in plugin path
ls plugins/superclaude/templates/roadmaps/
# Should find templates from M1.T4

# Test with empty paths (should fallback)
# Move templates temporarily and verify inline generation
```

---

### T3.2: Implement Template Scoring Algorithm
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement scoring factors per spec Section 3.3:
   - domain_alignment: 40%
   - structure_fit: 30%
   - complexity_match: 20%
   - optional_section_relevance: 10%
2. Score each discovered template
3. Apply threshold logic:
   - ≥80%: Select template directly
   - <80%: Create variant with adjustments
4. Document selection rationale

#### Acceptance Criteria
- [ ] All 4 scoring factors implemented
- [ ] Weights applied correctly (sum = 100%)
- [ ] Threshold logic working (80%)
- [ ] Best template selected

#### Verification
```bash
# Check template selection in output
# Should show score and rationale
```

---

### T3.3: Implement Inline Template Generation
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement milestone count formula per spec Section 3.3.1:
   ```
   base_count + floor((requirement_count - 5) / 5) + (1 if domain_spread > 2 else 0)
   ```
2. Apply complexity-based range clamping:
   - LOW (<0.4): 3-4 milestones
   - MEDIUM (0.4-0.7): 4-6 milestones
   - HIGH (>0.7): 5-8 milestones
3. Implement base milestone names per complexity
4. Handle domain mapping:
   - Single primary: Add 1 domain-specific milestone
   - Multi primary (≥40% each): Add max 2 domain milestones
   - No primary: Use generic milestones + WARN
5. Generate required sections per milestone:
   - Objective, Type, Priority, Deliverables
   - Dependencies, Acceptance_Criteria, Risk_Level
   - Files_Affected

#### Acceptance Criteria
- [ ] Milestone count formula correct
- [ ] Range clamping working
- [ ] Domain-specific milestones added
- [ ] All required sections present
- [ ] WARN logged when no primary domain

#### Verification
```bash
# Test with high complexity spec
# Should generate 5-8 milestones

# Test with security-primary spec
# Should include "Security Audit" milestone
```

---

### T3.4: Implement TodoWrite Task Initialization
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Create initial TodoWrite call with generation tasks
2. Use ONLY 3 valid states:
   - `pending` - Ready for execution
   - `in_progress` - Currently active (ONE at a time)
   - `completed` - Successfully finished
3. **CRITICAL**: Do NOT use "blocked" state
4. For blocked items, use workaround pattern:
   ```yaml
   todos:
     - content: "[BLOCKED: reason] Task description"
       status: pending
       activeForm: "Task description (blocked)"
   ```
5. Initialize all Wave tasks as pending
6. Set first task as in_progress

#### Acceptance Criteria
- [ ] TodoWrite called with valid structure
- [ ] Only 3 states used (pending, in_progress, completed)
- [ ] NO "blocked" state anywhere
- [ ] Blocked items use prefix workaround
- [ ] Single in_progress task at a time

#### Verification
```bash
# Check TodoWrite call structure
# Should NOT contain "blocked" state
# Should have [BLOCKED: reason] prefix for blocked items
```

---

## Milestone Completion Checklist

- [ ] T3.1: Template discovery working
- [ ] T3.2: Template scoring implemented
- [ ] T3.3: Inline generation functional
- [ ] T3.4: TodoWrite correctly initialized

## Dependencies
- M2 must be complete (extraction data available)
- T3.1 must complete before T3.2
- T3.2 may trigger T3.3 (if no match found)
- T3.4 can execute after milestone structure determined

## Critical Notes
**TodoWrite State Warning**: This is Critical Correction #4 from the spec.
- The TodoWrite tool has exactly 3 states: `pending`, `in_progress`, `completed`
- There is NO "blocked" state
- For blocked items: Use `[BLOCKED: reason]` prefix in content field

---

*Tasklist generated by SuperClaude Roadmap Generator v1.0*
