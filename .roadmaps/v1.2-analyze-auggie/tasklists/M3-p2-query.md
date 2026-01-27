# Tasklist: M3 - P2 Query Enhancement

## Metadata
- **Milestone**: M3
- **Dependencies**: M2 (P1 Core Features)
- **Estimated Complexity**: Medium
- **Risk Level**: LOW (R11: user confusion with levels)
- **Duration**: Week 3
- **ROI Range**: 6.10 - 6.43

---

## Tasks

### T3.1: Language-Aware Query Templates
**Type**: FEATURE
**Priority**: P2-Medium
**ROI Score**: 6.43
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Define query template structure for each language
2. Implement language detection from file extensions and content
3. Create Python security query templates
4. Create JavaScript/TypeScript security query templates
5. Create Go security query templates
6. Create Java security query templates
7. Implement template selection based on detected language
8. Add extensibility mechanism for custom templates

#### Acceptance Criteria
- [ ] Python templates include f-string injection patterns
- [ ] JavaScript templates include prototype pollution patterns
- [ ] Go templates include path traversal patterns
- [ ] Java templates include XXE patterns
- [ ] Correct template selected based on codebase language
- [ ] Mixed-language codebases use appropriate templates per file

#### Query Templates

**Python Security Templates**:
```yaml
python_security:
  sql_injection:
    - "SQL injection vulnerabilities including f-string formatting"
    - "String concatenation in database queries"
    - "Raw SQL execution without parameterization"
  deserialization:
    - "Pickle deserialization and untrusted data loading"
    - "YAML/JSON deserialization without safe loaders"
  code_execution:
    - "__import__, exec, eval usage patterns"
    - "Dynamic code execution vulnerabilities"
  framework_specific:
    - "Django ORM raw queries and extra() usage"
    - "Flask request.args without validation"
```

**JavaScript/TypeScript Security Templates**:
```yaml
javascript_security:
  xss:
    - "XSS vulnerabilities in DOM manipulation"
    - "Insecure use of innerHTML or dangerouslySetInnerHTML"
    - "Document.write usage patterns"
  prototype_pollution:
    - "Prototype pollution attack vectors"
    - "Deep merge without prototype filtering"
  code_execution:
    - "eval() and Function() constructor usage"
    - "setTimeout/setInterval with string arguments"
  authentication:
    - "JWT handling and token storage issues"
    - "Insecure cookie configurations"
```

**Go Security Templates**:
```yaml
go_security:
  sql_injection:
    - "SQL injection in database/sql queries"
    - "String formatting in SQL statements"
  file_operations:
    - "Path traversal in file operations"
    - "Insecure file permissions"
  tls:
    - "Insecure TLS configurations"
    - "Certificate validation bypass"
  command_injection:
    - "Command injection via os/exec"
    - "Shell command construction vulnerabilities"
```

**Java Security Templates**:
```yaml
java_security:
  sql_injection:
    - "SQL injection in JDBC and JPA"
    - "PreparedStatement vs Statement usage"
  xxe:
    - "XXE vulnerabilities in XML parsing"
    - "DocumentBuilderFactory without secure configuration"
  deserialization:
    - "Insecure deserialization patterns"
    - "ObjectInputStream without validation"
  ldap:
    - "LDAP injection vulnerabilities"
    - "JNDI lookup injection"
```

#### Verification
```bash
# Test language detection
uv run pytest tests/analyze/test_language_templates.py -v
```

---

### T3.2: Iterative Query Refinement
**Type**: FEATURE
**Priority**: P2-Medium
**ROI Score**: 6.23
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Implement quality scoring for Auggie results
2. Define refinement threshold (quality_score < 0.7)
3. Implement refinement strategies (narrow, broaden, rephrase, decompose)
4. Set max iterations per depth tier (0/1/3)
5. Add refinement trace to verbose output
6. Implement early termination on quality threshold met

#### Acceptance Criteria
- [ ] Refinement triggers when quality_score < 0.7
- [ ] Max iterations: quick=0, deep=1, comprehensive=3
- [ ] Refinement trace shown in --verbose output
- [ ] Quality score improves after refinement
- [ ] Early termination when threshold met

#### Refinement Strategies
```yaml
refinement_strategies:
  narrow_scope:
    trigger: "results > 50"
    action: "Add specificity to query"
    example: "security vulnerabilities" → "SQL injection in user input handlers"

  broaden_scope:
    trigger: "results < 3"
    action: "Remove constraints from query"
    example: "async SQL injection" → "SQL injection vulnerabilities"

  rephrase:
    trigger: "relevance_score < 0.6"
    action: "Use alternative terminology"
    example: "auth bypass" → "authentication vulnerabilities"

  decompose:
    trigger: "mixed relevance scores"
    action: "Split into specific queries"
    example: "security issues" → ["input validation", "authentication", "encryption"]
```

#### Quality Score Calculation
```python
def calculate_quality_score(results):
    if not results:
        return 0.0

    relevance_scores = [r.relevance for r in results]
    avg_relevance = sum(relevance_scores) / len(relevance_scores)

    # Penalize too many or too few results
    result_count = len(results)
    count_penalty = 0
    if result_count > 50:
        count_penalty = 0.2
    elif result_count < 3:
        count_penalty = 0.1

    return max(0, avg_relevance - count_penalty)
```

#### Verification
```bash
# Test iterative refinement
uv run pytest tests/analyze/test_acceptance.py::test_at7_iterative_refinement -v
```

---

### T3.3: Aggressiveness Flag Implementation
**Type**: FEATURE
**Priority**: P2-Medium
**ROI Score**: 6.10
**Files Affected**:
- `src/superclaude/commands/analyze.md`

#### Steps
1. Add `--aggressiveness` flag to command definition
2. Define multiplier values for each level
3. Implement query count adjustment
4. Implement token budget adjustment
5. Document use cases for each level
6. Set `balanced` as default
7. Validate flag values

#### Acceptance Criteria
- [ ] Flag accepts: minimal, balanced, aggressive, maximum
- [ ] Default is `balanced` (1.0x multipliers)
- [ ] Query count adjusted by multiplier
- [ ] Token budget adjusted by multiplier
- [ ] Invalid values rejected with helpful error

#### Aggressiveness Levels
```yaml
aggressiveness_levels:
  minimal:
    query_multiplier: 0.5
    token_multiplier: 0.7
    use_case: "Quick sanity checks, CI pipelines"
    description: "Minimal queries, fastest execution"

  balanced:
    query_multiplier: 1.0
    token_multiplier: 1.0
    use_case: "Standard development workflow"
    description: "Default - good balance of speed and thoroughness"

  aggressive:
    query_multiplier: 1.5
    token_multiplier: 1.3
    use_case: "Pre-merge reviews, security-sensitive code"
    description: "More thorough, catches subtle issues"

  maximum:
    query_multiplier: 2.0
    token_multiplier: 1.5
    use_case: "Security audits, compliance reviews"
    description: "Most thorough, highest resource usage"
```

#### Flag Interaction with Tier Classification
```yaml
tier_aggressiveness_interaction:
  # Tier classification can set auto-aggressiveness
  # User flag overrides auto setting

  STRICT_auto: aggressive   # Can be overridden to maximum
  STANDARD_auto: balanced   # Can be overridden to any
  LIGHT_auto: minimal       # Can be overridden to any
  EXEMPT_auto: minimal      # Can be overridden to any

  # Example: STRICT tier with --aggressiveness maximum
  # Result: maximum (user override wins)
```

#### Verification
```bash
# Test aggressiveness flag
uv run pytest tests/analyze/test_acceptance.py::test_at5_aggressiveness -v
```

---

### T3.4: Aggressiveness Level Documentation
**Type**: DOC
**Priority**: P2-Medium
**Files Affected**:
- `docs/user-guide/analyze-aggressiveness.md`

#### Steps
1. Create documentation file
2. Document each aggressiveness level
3. Provide use case examples
4. Document interaction with tier classification
5. Add decision flowchart for level selection
6. Include performance impact estimates

#### Acceptance Criteria
- [ ] All 4 levels documented with use cases
- [ ] Examples provided for common scenarios
- [ ] Tier classification interaction explained
- [ ] Performance impact clearly stated
- [ ] Decision flowchart included

#### Documentation Structure
```markdown
# Aggressiveness Levels in /sc:analyze

## Overview
The `--aggressiveness` flag controls query intensity...

## Levels

### minimal (0.5x queries, 0.7x tokens)
**Use Case**: CI pipelines, quick sanity checks
**Example**: `/sc:analyze @src --aggressiveness minimal`
...

### balanced (1.0x queries, 1.0x tokens) [DEFAULT]
**Use Case**: Standard development workflow
...

### aggressive (1.5x queries, 1.3x tokens)
**Use Case**: Pre-merge reviews, security-sensitive code
...

### maximum (2.0x queries, 1.5x tokens)
**Use Case**: Security audits, compliance reviews
...

## Decision Flowchart
[Include ASCII or mermaid diagram]

## Interaction with Tier Classification
[Explain auto-aggressiveness and override behavior]

## Performance Impact
[Table showing time/token impact]
```

#### Verification
```bash
# Verify documentation exists and is complete
test -f docs/user-guide/analyze-aggressiveness.md && echo "File exists"
```

---

## Milestone Completion Checklist

- [ ] T3.1: Language-Aware Query Templates - completed
- [ ] T3.2: Iterative Query Refinement - completed
- [ ] T3.3: Aggressiveness Flag Implementation - completed
- [ ] T3.4: Aggressiveness Level Documentation - completed
- [ ] All verification commands pass
- [ ] Integration tests with M2 features pass
- [ ] Memory checkpoint saved

## Checkpoint Command
```
mcp__serena__write_memory("analyze-auggie-m3", {
  status: "completed",
  deliverables: ["M3-D1", "M3-D2", "M3-D3", "M3-D4"],
  roi_delivered: [6.43, 6.23, 6.10],
  languages_supported: ["python", "javascript", "typescript", "go", "java"],
  issues: [],
  verified: true
})
```

---

*Tasklist M3 - Generated by SuperClaude Roadmap Generator v1.0*
