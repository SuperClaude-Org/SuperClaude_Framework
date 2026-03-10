# Execution Prompt: /sc:roadmap Implementation

## Metadata
- **Target**: `/sc:roadmap` SuperClaude Skill
- **Generated**: 2026-01-26
- **Generator**: SuperClaude Roadmap Generator v1.0
- **Source Roadmap**: `.roadmaps/v.1.4-roadmap-gen/roadmap.md`

---

## Overview

This document provides step-by-step instructions for implementing the `/sc:roadmap` command, a SuperClaude skill that generates comprehensive release roadmaps from specification documents.

**Total Milestones**: 6
**Total Deliverables**: 28
**Primary Persona**: Backend
**Estimated Complexity**: HIGH (0.78)

---

## Prerequisites

Before starting implementation, verify:

- [ ] SuperClaude framework installed (v4.1.9+)
- [ ] Access to MCP servers (Sequential, Context7, Serena)
- [ ] Write access to `.claude/skills/` directory
- [ ] Write access to `plugins/superclaude/templates/` directory
- [ ] Git repository initialized
- [ ] Read all input documents:
  - [ ] SC-ROADMAP-FEATURE-SPEC.md
  - [ ] extraction.md
  - [ ] roadmap.md

---

## Execution Order

Execute milestones in this order (respecting dependencies):

```
M1 → M2 → M3 → M4 → M5 → M6
```

### Milestone Dependency Graph

```
M1 (Foundation)
 │
 └─► M2 (Wave 1 - Detection)
     │
     └─► M3 (Wave 2 - Planning)
         │
         └─► M4 (Wave 3 - Generation)
             │
             └─► M5 (Wave 4-5 - Validation)
                 │
                 └─► M6 (Testing)
```

---

## Milestone Instructions

### M1: Foundation & Skill Setup
**Complexity**: Low | **Dependencies**: None

#### Key Tasks
1. Create skill directory: `.claude/skills/sc-roadmap/`
2. Create SKILL.md with correct frontmatter
3. Create template directory: `plugins/superclaude/templates/roadmaps/`
4. Create 6 template files (feature, quality, docs, security, performance, migration)

#### Critical Notes
- **Path Convention**: Skills MUST be at `.claude/skills/{name}/SKILL.md`
- **Template Creation**: Directory does NOT exist by default (Critical Correction #2)

#### Verification
```bash
test -d .claude/skills/sc-roadmap && \
test -f .claude/skills/sc-roadmap/SKILL.md && \
test -d plugins/superclaude/templates/roadmaps && \
echo "M1 PASS" || echo "M1 FAIL"
```

---

### M2: Wave 1 Implementation
**Complexity**: High | **Dependencies**: M1

#### Key Tasks
1. Implement spec file validation (exists, readable, has requirements)
2. Implement requirements extraction (FR, NFR, scope, deps)
3. Implement domain analysis (keyword classification → percentages)
4. Implement complexity scoring (5-factor formula)
5. Implement persona auto-activation (threshold-based selection)

#### Critical Notes
- **Complexity Formula**:
  ```
  score = (req_count * 0.25) + (dep_depth * 0.25) +
          (domain_spread * 0.20) + (risk_sev * 0.15) +
          (scope_size * 0.15)
  ```
- **Persona Thresholds**: Primary ≥85%, Consulting ≥70%

#### Verification
```bash
# Test with sample spec
/sc:roadmap fixtures/sample_spec.md --dry-run
# Check extraction.md for domain distribution and complexity score
```

---

### M3: Wave 2 Implementation
**Complexity**: Medium | **Dependencies**: M2

#### Key Tasks
1. Implement template discovery (local → user → plugin → inline)
2. Implement template scoring (4 factors, 80% threshold)
3. Implement inline template generation (milestone count formula)
4. Implement TodoWrite initialization

#### Critical Notes
- **TodoWrite States**: ONLY `pending`, `in_progress`, `completed`
- **NO "blocked" state** - Use `[BLOCKED: reason]` prefix (Critical Correction #4)
- **Milestone Count Formula**:
  ```
  base_count + floor((requirement_count - 5) / 5) + (1 if domain_spread > 2 else 0)
  ```

#### Verification
```bash
# Verify TodoWrite usage
grep -r "blocked" .claude/skills/sc-roadmap/ | grep -v "BLOCKED:"
# Should return empty (no "blocked" state)
```

---

### M4: Wave 3 - Artifact Generation
**Complexity**: High | **Dependencies**: M3

#### Key Tasks
1. Implement roadmap.md generator
2. Implement extraction.md generator
3. Implement tasklist generator (per-milestone files)
4. Implement test-strategy.md generator
5. Implement execution-prompt.md generator
6. Implement parallelization for concurrent artifacts

#### Critical Notes
- **ID Schema**:
  - Milestones: `M{1digit}`
  - Deliverables: `D{milestone}.{seq}`
  - Tasks: `T{milestone}.{seq}`
- **Parallelization**: test-strategy and execution-prompt can generate concurrently

#### Verification
```bash
# Check all 5 artifacts generated
ls .roadmaps/*/
# Should show: roadmap.md, extraction.md, test-strategy.md, execution-prompt.md, tasklists/
```

---

### M5: Wave 4-5 - Validation & Completion
**Complexity**: Medium-High | **Dependencies**: M4

#### Key Tasks
1. Implement quality-engineer Task validation
2. Implement self-review validation (4-question protocol)
3. Implement score aggregation (60%/40% weighting)
4. Implement completion check
5. Implement memory persistence via Serena

#### Critical Notes
- **Task Tool Pattern**: DO NOT use `subagent_type` parameter (Critical Correction #1)
- **Correct Pattern**:
  ```yaml
  Task:
    description: "Quality validation"
    prompt: |
      You are a quality-engineer agent...
  ```
- **Score Thresholds**: PASS ≥85%, REVISE 70-84%, REJECT <70%

#### Verification
```bash
# Check Task implementation
grep "subagent_type" .claude/skills/sc-roadmap/
# Should return empty (no subagent_type parameter)

# Check for embedded agent type
grep -A5 "quality-engineer" .claude/skills/sc-roadmap/SKILL.md
# Should show agent type in prompt
```

---

### M6: Testing & Documentation
**Complexity**: Low-Medium | **Dependencies**: M5

#### Key Tasks
1. Create unit tests (>80% coverage)
2. Create integration tests (wave pipelines)
3. Create compliance tests (critical corrections)
4. Update COMMANDS.md with /sc:roadmap entry

#### Critical Notes
- Test ALL 6 critical corrections
- Verify TodoWrite state compliance
- Verify Task tool pattern compliance

#### Verification
```bash
# Run all tests
pytest tests/sc-roadmap/ -v --cov

# Verify compliance
pytest tests/sc-roadmap/compliance/ -v
# All tests should pass
```

---

## Post-Execution Checklist

After completing all milestones:

### Functional Verification
- [ ] `/sc:roadmap` skill invocable via command
- [ ] 5-wave orchestration pipeline functional
- [ ] Multi-agent validation working
- [ ] All 5 artifacts generated correctly
- [ ] MCP circuit breakers functional

### Compliance Verification
- [ ] TodoWrite uses 3 states only
- [ ] Task tool embeds agent type in prompt
- [ ] All paths follow SuperClaude conventions
- [ ] Template directory created (not assumed to exist)

### Quality Verification
- [ ] Unit test coverage >80%
- [ ] Integration tests passing
- [ ] Compliance tests passing
- [ ] Validation score ≥85%

---

## Troubleshooting

### Common Issues

#### Issue: "Specification file not found"
**Cause**: File path incorrect or file doesn't exist
**Solution**: Verify path is correct and file is readable
```bash
test -f path/to/spec.md && echo "File exists" || echo "File not found"
```

#### Issue: TodoWrite state error
**Cause**: Using "blocked" state
**Solution**: Use `[BLOCKED: reason]` prefix with `pending` status
```yaml
# WRONG
status: blocked

# CORRECT
content: "[BLOCKED: waiting] Task description"
status: pending
```

#### Issue: Task validation failing
**Cause**: Using `subagent_type` parameter
**Solution**: Embed agent type in prompt text
```yaml
# WRONG
Task:
  subagent_type: quality-engineer

# CORRECT
Task:
  prompt: "You are a quality-engineer agent..."
```

#### Issue: Template not found
**Cause**: Template directory not created
**Solution**: Create directory and templates
```bash
mkdir -p plugins/superclaude/templates/roadmaps/
# Create template files
```

#### Issue: MCP server unavailable
**Cause**: Sequential/Serena/Context7 not responding
**Solution**: Circuit breaker will activate fallback
- Sequential fallback: Native Claude reasoning
- Serena fallback: Basic file operations
- Context7 fallback: WebSearch

---

## Success Verification

Run final verification after all milestones:

```bash
# 1. Verify skill structure
test -f .claude/skills/sc-roadmap/SKILL.md && echo "Skill: OK"

# 2. Verify templates
ls plugins/superclaude/templates/roadmaps/*.md | wc -l
# Should output: 6

# 3. Run compliance tests
pytest tests/sc-roadmap/compliance/ -v
# All tests should pass

# 4. Test skill invocation
/sc:roadmap fixtures/sample_spec.md --dry-run
# Should complete without errors

# 5. Generate and validate roadmap
/sc:roadmap fixtures/sample_spec.md
# Validation score should be ≥85%
```

---

## Next Steps After Implementation

1. **Execute Roadmap**: Follow generated tasklists M1 → M6
2. **Monitor Validation**: Track validation scores
3. **Iterate if Needed**: Address REVISE issues
4. **Document Learnings**: Update memory with patterns discovered

---

*Execution Prompt generated by SuperClaude Roadmap Generator v1.0*
*Source: roadmap.md for /sc:roadmap skill*
