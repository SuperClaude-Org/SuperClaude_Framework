# Tasklist: M2 - Wave 1 Implementation (Detection & Analysis)

## Metadata
- **Milestone**: M2
- **Dependencies**: M1
- **Estimated Complexity**: High
- **Primary Persona**: Backend
- **Deliverables**: 5

---

## Tasks

### T2.1: Implement Specification File Validation
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Implement file existence check using Read tool
2. Implement file readability validation (content length > 0)
3. Implement minimum content check (> 100 characters)
4. Implement required section detection (title, requirements)
5. Implement error messages per spec Section 8.1:
   - File not found: "Specification file not found: <path>"
   - Empty file: "Specification file is empty"
   - No requirements: "No requirements found in specification"

#### Acceptance Criteria
- [ ] File existence validated before processing
- [ ] Empty file detection working
- [ ] Requirements section detection working
- [ ] Clear error messages displayed
- [ ] STOP behavior on critical errors

#### Verification
```bash
# Test with non-existent file
/sc:roadmap nonexistent.md
# Expected: STOP with "Specification file not found"

# Test with empty file
touch empty.md && /sc:roadmap empty.md
# Expected: STOP with "Specification file is empty"
```

---

### T2.2: Implement Requirements Extraction Engine
**Type**: FEATURE
**Priority**: P0-Critical
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Parse specification structure for headings
2. Extract title from H1 heading (or filename fallback)
3. Extract Functional Requirements (FR-XXX pattern)
4. Extract Non-Functional Requirements (NFR-XXX pattern)
5. Extract scope boundaries (In Scope / Out of Scope)
6. Extract dependencies section
7. Extract success criteria
8. Extract risks and mitigations
9. Store extracted items with IDs for traceability

#### Acceptance Criteria
- [ ] Title extracted correctly
- [ ] FR/NFR patterns recognized
- [ ] Scope boundaries identified
- [ ] Dependencies listed
- [ ] Success criteria captured
- [ ] Risks identified
- [ ] All items have unique IDs

#### Verification
```bash
# Run extraction on sample spec
/sc:roadmap sample-spec.md --dry-run
# Check extraction.md output for completeness
```

---

### T2.3: Implement Domain Analysis Classifier
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Define domain keywords per spec Section 3.2:
   - frontend: UI, components, UX, accessibility, responsive
   - backend: API, database, services, infrastructure, server
   - security: auth, encryption, compliance, vulnerabilities, tokens
   - performance: optimization, caching, scaling, latency
   - documentation: guides, references, migration, docs
2. Scan extracted requirements for keywords
3. Calculate domain distribution percentages
4. Output domain_distribution object

#### Acceptance Criteria
- [ ] All 5 domains recognized
- [ ] Keywords correctly mapped
- [ ] Percentages sum to 100%
- [ ] Multi-domain specs classified correctly

#### Verification
```bash
# Domain distribution output should match spec content
# Example: security-heavy spec should show security > 40%
```

---

### T2.4: Implement Complexity Scoring System
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Count requirements for `requirement_count` factor
2. Analyze dependencies for `dependency_depth` factor
3. Count unique domains for `domain_spread` factor
4. Assess risks for `risk_severity` factor
5. Evaluate scope for `scope_size` factor
6. Apply weighted formula:
   ```
   score = (req_count * 0.25) + (dep_depth * 0.25) +
           (domain_spread * 0.20) + (risk_sev * 0.15) +
           (scope_size * 0.15)
   ```
7. Normalize to 0.0-1.0 scale
8. Classify: LOW (<0.4), MEDIUM (0.4-0.7), HIGH (>0.7)

#### Acceptance Criteria
- [ ] All 5 factors calculated
- [ ] Weights applied correctly (sum = 1.0)
- [ ] Score normalized to 0.0-1.0
- [ ] Classification correct per thresholds
- [ ] Score documented in extraction.md

#### Verification
```bash
# Check complexity score in extraction.md
grep "Complexity Score" extraction.md
# Should show score between 0.0-1.0
```

---

### T2.5: Implement Persona Auto-Activation
**Type**: FEATURE
**Priority**: P1-High
**Files Affected**:
- `.claude/skills/sc-roadmap/SKILL.md`

#### Steps
1. Use domain distribution from T2.3
2. Calculate confidence per persona based on domain coverage
3. Apply activation rules per spec Section 3.2:
   - Primary: Domain ≥40% coverage, confidence ≥85%
   - Consulting: Domain ≥15% coverage, confidence ≥70%
   - Fallback: architect for system-wide concerns
4. Select primary persona (highest qualifying coverage)
5. Select consulting personas (all qualifying)
6. Document selection in extraction.md

#### Acceptance Criteria
- [ ] Primary persona selected when threshold met
- [ ] Consulting personas identified correctly
- [ ] Fallback to architect when no primary
- [ ] Confidence thresholds enforced (85%, 70%)
- [ ] Selection documented with rationale

#### Verification
```bash
# Check persona assignment in extraction.md
grep -A5 "Persona Assignment" extraction.md
# Should show Primary, Consulting roles
```

---

## Milestone Completion Checklist

- [ ] T2.1: File validation working
- [ ] T2.2: Requirements extraction complete
- [ ] T2.3: Domain classification working
- [ ] T2.4: Complexity scoring accurate
- [ ] T2.5: Persona activation correct

## Dependencies
- M1 must be complete (skill directory exists)
- T2.1 must complete before T2.2
- T2.2 must complete before T2.3, T2.4, T2.5
- T2.3, T2.4, T2.5 can execute in parallel after T2.2

---

*Tasklist generated by SuperClaude Roadmap Generator v1.0*
