# Feature Specification: /sc:analyze Auggie MCP Integration

**Version**: 2.0.0
**Date**: 2026-01-26
**Status**: Spec-Panel Reviewed - Ready for Implementation
**Authors**: Expert Panel (Wiegers, Fowler, Nygard, Adzic, Crispin)
**Improvements Incorporated**: 10 (prioritized by ROI score)

---

## 1. Executive Summary

This specification defines the refactoring of the `/sc:analyze` command to incorporate Auggie MCP (`mcp__auggie-mcp__codebase-retrieval`) for semantic code analysis. The enhancement transforms a basic pattern-matching utility into a semantically-aware analysis engine with user-controllable aggressiveness levels, progressive disclosure output, and cross-session memory.

### 1.1 Key Enhancements (v2.0)

| Priority | Enhancement | ROI Score | Description |
|----------|-------------|-----------|-------------|
| P1 | Progressive Disclosure | 7.01 | 3-tier output: Summary → Details → Evidence |
| P1 | Tier Classification | 6.83 | Integration with sc:task-unified (STRICT/STANDARD/LIGHT/EXEMPT) |
| P1 | Cross-Session Memory | 6.71 | Delta tracking and pattern learning |
| P2 | Adaptive Token Budgeting | 6.50 | Size-based budget multipliers |
| P2 | Language-Aware Templates | 6.43 | Per-language query optimization |
| P2 | Iterative Refinement | 6.23 | Quality-based query improvement |
| P2 | Hybrid Validation | 6.11 | 3-stage confidence pipeline |
| P2 | --aggressiveness Flag | 6.10 | User control over query intensity |
| P3 | Quality Scoring | 5.53 | Auggie result metrics |
| P3 | Degradation Feedback | 5.42 | Real-time user notifications |

### 1.2 Scope

**In Scope**:
- Integration of `mcp__auggie-mcp__codebase-retrieval` as primary discovery mechanism
- **NEW**: `--aggressiveness` flag (minimal/balanced/aggressive/maximum)
- **NEW**: Progressive disclosure evidence system (3 output tiers)
- **NEW**: Integration with sc:task-unified tier classification
- **NEW**: Cross-session analysis memory via Serena
- **NEW**: Language-aware query templates
- **NEW**: Iterative query refinement
- **NEW**: Hybrid validation pipeline (Auggie → Serena → Grep)
- **NEW**: Adaptive token budgeting based on codebase size
- **NEW**: Real-time degradation feedback
- Graceful degradation to native tools when MCP unavailable
- Depth-tiered execution (quick/deep/comprehensive)
- Evidence-based findings with verifiable source chains
- Circuit breaker pattern for MCP failure handling

**Out of Scope**:
- Runtime dynamic analysis
- Automated code modification
- Real-time continuous analysis

### 1.3 Key Stakeholders

| Stakeholder | Interest | Success Criteria |
|-------------|----------|------------------|
| Developers | Fast, accurate analysis | <30s for quick, ≥85% precision |
| Security Teams | Vulnerability detection | Zero false negatives for critical issues |
| Architects | System-wide insights | Cross-module dependency mapping |
| Operations | Reliability | <5% failure rate, graceful degradation |
| **NEW** Power Users | Control over analysis | Aggressiveness levels, tier overrides |

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-1: Semantic Code Discovery (UPDATED)
**Priority**: P0 (Must Have)
**Source**: Proposal Section 2

| Attribute | Specification |
|-----------|---------------|
| Description | Use `mcp__auggie-mcp__codebase-retrieval` for semantic code search |
| **Parameters** | `directory_path` (REQUIRED), `information_request` |
| Rationale | Semantic search provides 2-3x better precision than grep patterns |
| Acceptance Criteria | Given a security analysis request, when analyzing auth module, then discover all authentication-related code including implicit dependencies within 5 seconds |
| Verification | Integration test with 3 codebases of varying sizes |

**MCP Tool Specification**:
```yaml
tool: mcp__auggie-mcp__codebase-retrieval
parameters:
  directory_path: "{project_root}"  # REQUIRED - absolute path
  information_request: "{semantic_query}"  # Natural language query
```

#### FR-2: Multi-Domain Analysis
**Priority**: P0 (Must Have)
**Source**: Current analyze.md

| Attribute | Specification |
|-----------|---------------|
| Description | Support analysis across quality, security, performance, and architecture domains |
| Rationale | Comprehensive analysis requires multi-dimensional perspective |
| Acceptance Criteria | Given `--focus security,performance`, when analyzing, then produce findings for both domains with domain-specific evidence |
| Verification | Unit tests for each domain, integration test for combinations |

#### FR-3: Depth-Tiered Execution (UPDATED)
**Priority**: P0 (Must Have)
**Source**: Proposal Section 4, Debate Round 2

| Attribute | Specification |
|-----------|---------------|
| Description | Three execution tiers with distinct resource budgets |
| Tiers | `quick` (smoke test), `deep` (standard), `comprehensive` (audit) |
| **NEW** Aggressiveness | Each tier modified by aggressiveness multiplier |
| Acceptance Criteria | Each tier completes within defined time/token budgets with appropriate confidence levels |
| Verification | Performance benchmarks on standardized test codebases |

**Tier Specifications (v2.0)**:

| Tier | Time Budget | Base Token Budget | Auggie Queries | Output Tier | Iterative Refinement |
|------|-------------|-------------------|----------------|-------------|----------------------|
| quick | 15-30s | 5-8K | 1-2 | Summary only | None |
| deep | 45-90s | 15-25K | 5-10 | Summary + Details | 1 iteration max |
| comprehensive | 2-5min | 30-50K | 15-25 | Summary + Details + Evidence | 3 iterations max |

#### FR-4: Graceful Degradation (UPDATED)
**Priority**: P0 (Must Have)
**Source**: Debate Round 1 Consensus

| Attribute | Specification |
|-----------|---------------|
| Description | Continue analysis using native tools when MCP unavailable |
| **NEW** Degradation Feedback | Real-time user notification when in fallback mode |
| Rationale | Core analysis capability must not depend on external service availability |
| Acceptance Criteria | Given Auggie MCP timeout, when circuit breaker opens, then analysis continues with Glob/Grep/Read and **user notification with impact explanation** |
| Verification | Fault injection tests with MCP service unavailable |

**Tier-Specific Availability Requirements**:

| Tier | Auggie Availability | Behavior if Unavailable | User Message |
|------|---------------------|-------------------------|--------------|
| quick | Optional | Proceed with native tools, no warning | None |
| deep | Preferred | Proceed with warning about reduced precision | "⚠️ Semantic search unavailable - reduced precision expected" |
| comprehensive | Required | Abort with clear error message | "❌ Comprehensive analysis requires semantic search - try --depth deep" |

#### FR-5: Evidence Chain Generation (UPDATED)
**Priority**: P1 (Should Have)
**Source**: Debate Round 2, PRINCIPLES.md

| Attribute | Specification |
|-----------|---------------|
| Description | Every finding includes verifiable evidence chain |
| **NEW** Progressive Disclosure | Evidence shown only when requested (--evidence flag) |
| Rationale | Credibility requires traceable conclusions without overwhelming default output |
| Acceptance Criteria | Each finding includes: file:line reference, code snippet, cross-references, confidence score; full evidence available on request |
| Verification | Audit trail validation on generated reports |

**Evidence Chain Structure (v2.0)**:
```yaml
finding:
  id: "SEC-001"
  severity: "critical"
  summary: "SQL injection vulnerability"

  # Tier 1: Summary (always shown)
  location: "api/users.py:45"
  action_required: true

  # Tier 2: Details (--verbose)
  details:
    context: "Direct string concatenation in SQL query"
    impact: "Allows arbitrary SQL execution, data breach risk"
    fix_suggestion: "Use parameterized queries with SQLAlchemy"

  # Tier 3: Evidence (--evidence)
  evidence:
    code_snippet: "query = f\"SELECT * FROM users WHERE id = {user_id}\""
    validation_chain:
      auggie_relevance: 0.92
      serena_verified: true
      grep_confirmed: true
    cross_references:
      - "validation.py:12 (missing sanitization)"
      - "db_config.py:8 (connection without prepared statements)"
    confidence: 0.94
    methodology: "semantic pattern match + hybrid validation pipeline"
    cross_session:
      first_detected: "2026-01-20"
      status: "recurring"
      previous_analyses: 3
```

#### FR-6: Parallel Query Execution
**Priority**: P1 (Should Have)
**Source**: Proposal Section 6

| Attribute | Specification |
|-----------|---------------|
| Description | Execute independent analysis queries in parallel |
| Rationale | 50% latency improvement through concurrent execution |
| Acceptance Criteria | Given 4 independent focus areas, when analyzing, then queries execute concurrently with results aggregated |
| Verification | Timing tests demonstrating parallel speedup |

#### FR-7: Result Caching (UPDATED → Cross-Session Memory)
**Priority**: P1 (Should Have) - **UPGRADED from P2**
**Source**: Debate Round 2, NEW ROI Analysis

| Attribute | Specification |
|-----------|---------------|
| Description | Cross-session analysis memory with delta tracking |
| **NEW** Memory Storage | Serena write_memory / read_memory |
| **NEW** Delta Analysis | Compare current vs. previous findings |
| **NEW** Pattern Learning | Track recurring issues and hot spots |
| Acceptance Criteria | Second analysis shows delta (new/resolved/recurring findings) and trend indicators |
| Verification | Cross-session tests with memory persistence |

**Memory Schema**:
```yaml
memory_keys:
  analysis_{project_hash}_latest: "Most recent analysis results"
  analysis_{project_hash}_history: "Historical analysis trend"
  patterns_{project_hash}: "Learned patterns and hot spots"

stored_data:
  findings:
    - finding_id, severity, location
    - first_detected_date
    - status: new|recurring|resolved
  patterns:
    - common_issues: [list]
    - hot_spots: [file_list]
    - improvement_trend: [score_history]
```

#### FR-8: Large Codebase Support (UPDATED)
**Priority**: P2 (Nice to Have)
**Source**: Proposal Section 6

| Attribute | Specification |
|-----------|---------------|
| Description | Hierarchical narrowing for codebases >100K LOC |
| **NEW** Adaptive Budgeting | Token budget multiplied by codebase size tier |
| Rationale | Analysis must scale to enterprise codebases |
| Acceptance Criteria | 1M LOC codebase analyzed within 5 minutes with hierarchical sampling |
| Verification | Scalability tests on synthetic large codebases |

#### FR-9: Aggressiveness Control (NEW)
**Priority**: P2 (Should Have)
**Source**: ROI Analysis - Score 6.10

| Attribute | Specification |
|-----------|---------------|
| Description | User-controllable query intensity via --aggressiveness flag |
| Values | minimal, balanced (default), aggressive, maximum |
| Rationale | Different use cases require different thoroughness/speed tradeoffs |
| Acceptance Criteria | `--aggressiveness maximum` uses 2x queries and 1.5x tokens vs. balanced |
| Verification | Flag combination tests across all depth tiers |

**Aggressiveness Levels**:

| Level | Query Multiplier | Token Multiplier | Use Case |
|-------|------------------|------------------|----------|
| minimal | 0.5x | 0.7x | Quick sanity checks, CI pipelines |
| balanced | 1.0x | 1.0x | Standard development workflow |
| aggressive | 1.5x | 1.3x | Pre-merge reviews, security-sensitive code |
| maximum | 2.0x | 1.5x | Security audits, compliance reviews |

#### FR-10: Tier Classification Integration (NEW)
**Priority**: P1 (Should Have)
**Source**: ROI Analysis - Score 6.83

| Attribute | Specification |
|-----------|---------------|
| Description | Auto-adjust analysis rigor based on sc:task-unified tier classification |
| Tiers | STRICT, STANDARD, LIGHT, EXEMPT |
| Rationale | Align analysis depth with task criticality |
| Acceptance Criteria | STRICT tier auto-activates aggressive + deep; LIGHT tier uses minimal + quick |
| Verification | Tier detection tests with various file patterns |

**Tier Mapping**:

| Classification | Auto-Aggressiveness | Auto-Depth | Validation | Evidence Tier |
|----------------|---------------------|------------|------------|---------------|
| STRICT | aggressive | deep minimum | mandatory_hybrid | Full |
| STANDARD | balanced | deep | spot_check | Summary + Details |
| LIGHT | minimal | quick | none | Summary only |
| EXEMPT | minimal | quick | none | Summary only |

#### FR-11: Language-Aware Query Templates (NEW)
**Priority**: P2 (Should Have)
**Source**: ROI Analysis - Score 6.43

| Attribute | Specification |
|-----------|---------------|
| Description | Per-language optimized query templates |
| Languages | Python, JavaScript/TypeScript, Go, Java (extensible) |
| Rationale | Language-specific vulnerabilities require tailored queries |
| Acceptance Criteria | Python security analysis includes f-string injection; JS includes prototype pollution |
| Verification | Language-specific test suites |

**Example Templates**:
```yaml
python_security:
  - "SQL injection vulnerabilities including f-string formatting"
  - "Pickle deserialization and untrusted data loading"
  - "__import__, exec, eval usage patterns"

javascript_security:
  - "XSS vulnerabilities in DOM manipulation"
  - "Prototype pollution attack vectors"
  - "Insecure use of innerHTML or dangerouslySetInnerHTML"
```

#### FR-12: Iterative Query Refinement (NEW)
**Priority**: P2 (Should Have)
**Source**: ROI Analysis - Score 6.23

| Attribute | Specification |
|-----------|---------------|
| Description | Automatic query refinement when initial results have low quality |
| Trigger | Quality score < 0.7 |
| Max Iterations | 0 (quick), 1 (deep), 3 (comprehensive) |
| Acceptance Criteria | Broad query refined to specific when results > 50 or relevance < 0.6 |
| Verification | Refinement trace in verbose output |

**Refinement Strategies**:
- `narrow_scope`: Too many results → add specificity
- `broaden_scope`: Too few results → remove constraints
- `rephrase`: Low relevance → use alternative terminology
- `decompose`: Mixed relevance → split into specific queries

#### FR-13: Hybrid Validation Pipeline (NEW)
**Priority**: P2 (Should Have)
**Source**: ROI Analysis - Score 6.11

| Attribute | Specification |
|-----------|---------------|
| Description | 3-stage validation to reduce false positives |
| Stages | Auggie (semantic) → Serena (structural) → Grep (syntactic) |
| Confidence Assignment | All 3 pass = HIGH (0.9+), 2 pass = MEDIUM (0.7-0.9), 1 pass = LOW (0.5-0.7) |
| Acceptance Criteria | Findings require minimum 2-stage validation for MEDIUM confidence |
| Verification | Validation chain logged for each finding |

#### FR-14: Auggie Result Quality Scoring (NEW)
**Priority**: P3 (Nice to Have)
**Source**: ROI Analysis - Score 5.53

| Attribute | Specification |
|-----------|---------------|
| Description | Score Auggie results before acting on them |
| Metrics | relevance_score, completeness_score, confidence_score |
| Threshold | 0.7 minimum for actionable findings |
| Acceptance Criteria | Low-quality results trigger iterative refinement or fallback |
| Verification | Quality scores logged in verbose output |

#### FR-15: Real-Time Degradation Feedback (NEW)
**Priority**: P3 (Nice to Have)
**Source**: ROI Analysis - Score 5.42

| Attribute | Specification |
|-----------|---------------|
| Description | Inform users when operating in reduced capability mode |
| Triggers | MCP unavailable, partial degradation, circuit breaker open |
| Display | Banner or inline warning with impact explanation |
| Acceptance Criteria | User sees "⚠️ Running in fallback mode" with capability impact |
| Verification | Degradation simulation tests |

### 2.2 Non-Functional Requirements

#### NFR-1: Token Efficiency (UPDATED)
**Priority**: P0 (Must Have)
**Source**: Proposal Section 6, Debate Round 3

| Attribute | Specification |
|-----------|---------------|
| Target | 40-70% reduction vs. skilled native tool usage |
| **NEW** Adaptive Budgeting | Budget × codebase_size_multiplier × aggressiveness_multiplier |
| Measurement | Total workflow tokens including MCP overhead |
| Baseline | Skilled user with Glob/Grep/Read achieving same analysis |
| Verification | A/B testing with token counting on 5+ codebases |

**Adaptive Token Budget Formula**:
```
final_budget = base_budget × size_multiplier × aggressiveness_multiplier × focus_count_factor

Size Multipliers:
  small (<10K LOC): 1.0x
  medium (10-100K): 1.5x
  large (100K-1M): 2.0x
  massive (>1M): 2.5x

Aggressiveness Multipliers:
  minimal: 0.7x
  balanced: 1.0x
  aggressive: 1.3x
  maximum: 1.5x

Focus Count Factor:
  1 focus: 1.0x
  2 focus: 1.3x
  3+ focus: 1.5x
```

**Token Budget Breakdown by Phase**:

| Phase | Quick | Deep | Comprehensive |
|-------|-------|------|---------------|
| Classify & Configure | 1K | 2K | 3K |
| Discovery | 2K | 5K | 10K |
| Analysis | 1.5K | 6K | 12K |
| Synthesis | 0.5K | 1.5K | 3K |
| Report | 1K | 2K | 3K |
| **Base Total** | 6K | 16.5K | 31K |

#### NFR-2: Latency
**Priority**: P0 (Must Have)
**Source**: Proposal Section 8

| Attribute | Specification |
|-----------|---------------|
| Quick Tier | p95 < 30 seconds |
| Deep Tier | p95 < 90 seconds |
| Comprehensive | p95 < 5 minutes |
| Verification | Performance monitoring in production |

#### NFR-3: Analysis Precision (UPDATED)
**Priority**: P1 (Should Have)
**Source**: Proposal Section 8

| Attribute | Specification |
|-----------|---------------|
| Target | ≥85% precision (true positives / all positives) |
| **NEW** Hybrid Validation | 3-stage validation pipeline for high-confidence findings |
| Current Baseline | ~40% with grep patterns |
| Measurement | Human review of 100 random findings |
| Verification | Precision audit on diverse codebases |

#### NFR-4: Analysis Recall
**Priority**: P1 (Should Have)
**Source**: Proposal Section 8

| Attribute | Specification |
|-----------|---------------|
| Target | ≥90% recall (found issues / total issues) |
| Measurement | Comparison against known issue sets |
| Verification | Recall testing with pre-seeded vulnerabilities |

#### NFR-5: Availability
**Priority**: P1 (Should Have)
**Source**: Debate Round 1

| Attribute | Specification |
|-----------|---------------|
| Target | 99% analysis completion rate |
| Graceful Degradation | 100% of quick/deep tiers complete even without MCP |
| **NEW** Degradation Feedback | Users always informed of reduced capability mode |
| Verification | Chaos engineering tests with MCP failures |

#### NFR-6: MCP Overhead
**Priority**: P2 (Nice to Have)
**Source**: Debate Round 3

| Attribute | Specification |
|-----------|---------------|
| Target | <15% overhead vs. hypothetical direct API access |
| Measurement | Explicit tracking of MCP protocol overhead |
| Verification | Profiling of MCP communication costs |

---

## 3. Architecture Decisions

### AD-1: Semantic-First with Layered Fallback (UPDATED)

**Decision**: Use `mcp__auggie-mcp__codebase-retrieval` as primary discovery mechanism with native tools as fallback layer and real-time degradation feedback.

**Status**: Approved (Debate Round 1 Consensus + v2.0 Enhancement)

**Context**:
The current analyze command relies entirely on pattern matching (Grep), resulting in ~50% false positive rates and inability to understand semantic relationships.

**Decision Drivers**:
- Semantic search provides 2-3x precision improvement
- MCP availability cannot be guaranteed
- User trust requires consistent analysis capability
- **NEW**: Users need visibility into degraded operation mode

**Consequences**:
- Positive: High precision when MCP available, graceful degradation when not
- Positive: **NEW** Users always informed of capability limitations
- Negative: Two code paths to maintain, potential inconsistency in results
- Mitigation: Clear messaging to user about analysis mode

**Architecture Diagram (v2.0)**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SEMANTIC ANALYSIS PIPELINE v2.0                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │   CLASSIFY   │ → │   DISCOVER    │ → │   ANALYZE    │ → │  SYNTHESIZE │  │
│  │   + CONFIG   │   │   + ITERATE   │   │   + VALIDATE │   │  + REPORT   │  │
│  └──────────────┘   └───────────────┘   └──────────────┘   └─────────────┘  │
│         ↓                  ↓                   ↓                  ↓          │
│   • directory_path   • Auggie MCP        • Serena MCP      • Sequential     │
│   • --aggressiveness • Query Templates   • Hybrid Valid.   • write_memory   │
│   • Tier Detection   • Iterative Refine  • Quality Score   • Prog. Discl.   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │              ADAPTIVE TOKEN BUDGETING LAYER                             │ │
│  │   small: 100% base | medium: 150% | large: 200% | massive: 250%         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │          FALLBACK LAYER (Native Tools + Degradation Feedback)           │ │
│  │          Glob → Grep → Read → Write | "⚠️ Fallback mode active"         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AD-2: Phase-Based Pipeline Architecture (UPDATED)

**Decision**: Structure analysis as 5 distinct phases with clear boundaries, checkpoints, and v2.0 enhancements.

**Status**: Approved

**Phases (v2.0)**:

| Phase | Purpose | Primary Tools | NEW v2.0 Features | Checkpoint |
|-------|---------|---------------|-------------------|------------|
| 1. Classify | Determine scope, tier, aggressiveness | codebase-retrieval | Tier classification, adaptive budgeting | Scope confirmed |
| 2. Discover | Semantic code discovery | codebase-retrieval | Language-aware templates, iterative refinement | Candidates identified |
| 3. Analyze | Deep inspection | find_symbol, Grep | Hybrid validation pipeline, quality scoring | Findings validated |
| 4. Synthesize | Aggregate and prioritize | sequential-thinking | Cross-session memory, delta analysis | Synthesis complete |
| 5. Report | Generate output | Write, write_memory | Progressive disclosure (3 tiers) | Report delivered |

### AD-3: MCP Abstraction Layer (UPDATED)

**Decision**: Abstract MCP server interactions behind a common interface for testability and flexibility.

**Status**: Approved

**Interface Definition (v2.0)**:
```python
class AnalysisToolProvider(Protocol):
    """Abstract interface for analysis tools"""

    def discover(
        self,
        query: str,
        scope: str,
        directory_path: str,  # NEW: Required for Auggie
        language: str | None = None  # NEW: Language-aware
    ) -> list[CodeLocation]:
        """Discover code matching semantic query"""
        ...

    def analyze_symbol(self, location: CodeLocation) -> SymbolAnalysis:
        """Deep analysis of specific symbol"""
        ...

    def validate_finding(
        self,
        finding: Finding
    ) -> ValidationResult:  # NEW: Hybrid validation
        """3-stage validation pipeline"""
        ...

    def is_available(self) -> bool:
        """Check if provider is available"""
        ...

    def get_degradation_message(self) -> str | None:  # NEW
        """Get message for degraded operation mode"""
        ...
```

**Implementations**:
- `AuggieMCPProvider`: Semantic search via mcp__auggie-mcp__codebase-retrieval
- `SerenaMCPProvider`: Symbol analysis via find_symbol/find_referencing_symbols
- `NativeToolProvider`: Glob/Grep/Read fallback
- `MockProvider`: Testing mock

### AD-4: Progressive Disclosure Output (NEW)

**Decision**: Implement 3-tier progressive disclosure for analysis output.

**Status**: Approved (ROI 7.01 - Highest priority improvement)

**Tiers**:
- **Tier 1 (Summary)**: Always shown - finding count, top 3 issues, health score
- **Tier 2 (Details)**: On request (--verbose) - all findings with context and fix suggestions
- **Tier 3 (Evidence)**: On request (--evidence) - full audit trail with validation chain

**Rationale**:
- Reduces cognitive load for quick checks
- Preserves full evidence for audit requirements
- Aligns with different user needs (quick scan vs. compliance audit)

### AD-5: Hybrid Validation Pipeline (NEW)

**Decision**: Implement 3-stage validation to maximize confidence in findings.

**Status**: Approved (ROI 6.11)

**Pipeline**:
```
Stage 1: Auggie (Semantic)     → relevance_score >= 0.6
Stage 2: Serena (Structural)   → symbol_found AND references > 0
Stage 3: Grep (Syntactic)      → pattern_matched

Confidence Assignment:
  All 3 pass:     HIGH (0.9+)
  Stages 1+2:     MEDIUM (0.7-0.9)
  Stage 1 only:   LOW (0.5-0.7)
```

**Fallback Behavior**:
- Serena unavailable → Skip stage 2, use stages 1+3
- Grep timeout → Accept stages 1+2 results

---

## 4. MCP Integration Patterns

### 4.1 Server Configuration (UPDATED)

**Updated YAML Header**:
```yaml
---
name: analyze
description: "Semantic code analysis across quality, security, performance, and architecture domains"
category: utility
complexity: standard
mcp-servers: [mcp__auggie-mcp__codebase-retrieval, mcp__sequential-thinking__sequentialthinking]
mcp-optional: [serena]
personas: [analyzer, security, performance, architect]
fallback-enabled: true
tier-classification: auto
progressive-disclosure: true
---
```

**Server Roles (v2.0)**:

| Server | Role | Required Parameter | Fallback |
|--------|------|-------------------|----------|
| mcp__auggie-mcp__codebase-retrieval | Semantic discovery | **directory_path** | Glob + Grep |
| mcp__sequential-thinking__sequentialthinking | Multi-step reasoning | - | Native reasoning |
| serena (find_symbol, write_memory) | Symbol analysis, memory | - | Read + pattern match |

### 4.2 Circuit Breaker Configuration (UPDATED)

**Per-Server Settings with Degradation Feedback**:

```yaml
circuit_breaker:
  auggie_circuit:
    failure_threshold: 3
    timeout: 30s
    fallback: "Native Glob + Grep discovery"
    user_message: "⚠️ Semantic search circuit open - using pattern matching (reduced precision)"
    recovery: "Half-open after 60s"
    recovery_message: "✅ Testing semantic search recovery..."

  serena_circuit:
    failure_threshold: 4
    timeout: 45s
    fallback: "Read target files directly"
    user_message: "⚠️ Symbol analysis unavailable - using file-based analysis"
    recovery: "Half-open after 60s"

  sequential_circuit:
    failure_threshold: 3
    timeout: 30s
    fallback: "Native Claude reasoning"
    user_message: "⚠️ Advanced reasoning unavailable - using direct synthesis"
    recovery: "Half-open after 60s"
```

### 4.3 Tool Coordination Matrix (UPDATED)

| Phase | Primary Tool | Parameters | Validation | Fallback |
|-------|-------------|------------|------------|----------|
| Classify | mcp__auggie-mcp__codebase-retrieval | directory_path, "project structure" | - | Glob enumeration |
| Discover | mcp__auggie-mcp__codebase-retrieval | directory_path, language_aware_query | Quality scoring | Grep patterns |
| Analyze | find_symbol, find_referencing_symbols | - | Hybrid pipeline | Read + pattern |
| Synthesize | mcp__sequential-thinking__sequentialthinking | - | - | Native reasoning |
| Report | Write, write_memory | - | - | Write only |

### 4.4 Query Templates (UPDATED - Language-Aware)

**Python Security**:
```yaml
python_security_queries:
  - "SQL injection vulnerabilities including f-string formatting"
  - "Pickle deserialization and untrusted data loading"
  - "__import__, exec, eval usage patterns"
  - "Django/Flask security misconfigurations"
  - "YAML/JSON deserialization without safe loaders"
```

**JavaScript/TypeScript Security**:
```yaml
javascript_security_queries:
  - "XSS vulnerabilities in DOM manipulation"
  - "Prototype pollution attack vectors"
  - "Insecure use of innerHTML or dangerouslySetInnerHTML"
  - "JWT handling and token storage issues"
  - "eval() and Function() constructor usage"
```

**Go Security**:
```yaml
go_security_queries:
  - "SQL injection in database/sql queries"
  - "Path traversal in file operations"
  - "Insecure TLS configurations"
  - "Command injection via os/exec"
```

**Java Security**:
```yaml
java_security_queries:
  - "SQL injection in JDBC and JPA"
  - "XXE vulnerabilities in XML parsing"
  - "Insecure deserialization patterns"
  - "LDAP injection vulnerabilities"
```

---

## 5. Success Criteria

### 5.1 Performance Metrics (UPDATED)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Token consumption (quick) | 15-50K | 5-8K | Token counting |
| Token consumption (deep) | 50-200K | 15-25K | Token counting |
| Latency (quick) | 20-40s | 8-15s | Wall clock time |
| Latency (deep) | 60-180s | 30-60s | Wall clock time |
| MCP overhead | N/A | <15% | Protocol profiling |
| **NEW** Quality score threshold | N/A | ≥0.7 | Auggie result scoring |
| **NEW** Cross-session delta accuracy | N/A | ≥95% | Finding tracking |

### 5.2 Quality Metrics (UPDATED)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Analysis precision | ~40% | ≥85% | Hybrid validation |
| Analysis recall | ~60% | ≥90% | Known issue sets |
| False positive rate | ~50% | <10% | User dismissals |
| User override rate | N/A | <15% | --skip-analysis usage |
| **NEW** HIGH confidence findings | N/A | ≥60% | 3-stage validation |
| **NEW** Evidence completeness | N/A | 100% | Audit trail validation |

### 5.3 Acceptance Tests (UPDATED)

**AT-1: Basic Semantic Discovery (UPDATED)**
```gherkin
Given a codebase with authentication module
When /sc:analyze @auth --focus security --depth quick
Then findings include all auth-related security patterns
And execution completes within 30 seconds
And token usage is under 8K
And Auggie queries include directory_path parameter
```

**AT-2: Graceful Degradation with Feedback (UPDATED)**
```gherkin
Given Auggie MCP is unavailable
When /sc:analyze @src --focus quality --depth deep
Then analysis completes using native tools
And user receives degradation notification "⚠️ Semantic search unavailable"
And results include degradation impact note
And quality is marked as "reduced precision"
```

**AT-3: Evidence Chain Completeness with Progressive Disclosure (UPDATED)**
```gherkin
Given security analysis finds SQL injection
When default output is shown
Then finding shows summary tier only (location, severity, action required)

When user requests --verbose
Then finding shows details tier (context, impact, fix suggestion)

When user requests --evidence
Then finding shows evidence tier (code snippet, validation chain, cross-references)
And confidence score is provided
```

**AT-4: Large Codebase Handling with Adaptive Budgeting (UPDATED)**
```gherkin
Given a codebase with 500K+ LOC
When /sc:analyze --focus architecture --depth comprehensive
Then analysis detects "large" size tier
And token budget is multiplied by 2.0x
And analysis uses hierarchical narrowing
And completes within 5 minutes
```

**AT-5: Aggressiveness Control (NEW)**
```gherkin
Given a standard codebase
When /sc:analyze @src --focus security --depth deep --aggressiveness aggressive
Then Auggie queries are 1.5x the balanced baseline
And token budget is 1.3x the balanced baseline
And hybrid validation is mandatory
```

**AT-6: Tier Classification Integration (NEW)**
```gherkin
Given a file path containing "auth" in security-sensitive location
When /sc:analyze @src/auth --tier auto
Then tier classification detects STRICT
And auto-aggressiveness is set to aggressive
And auto-depth is set to deep minimum
And hybrid validation is mandatory
```

**AT-7: Iterative Query Refinement (NEW)**
```gherkin
Given an initial broad query with quality_score 0.45
When /sc:analyze --depth comprehensive
Then refinement strategy is triggered
And query is narrowed based on initial results
And second query achieves quality_score >= 0.7
And refinement trace is logged
```

**AT-8: Cross-Session Memory (NEW)**
```gherkin
Given a previous analysis exists in Serena memory
When /sc:analyze @src is run again
Then previous findings are loaded from memory
And delta is calculated (new/resolved/recurring)
And output shows "🆕 5 new | ✅ 3 resolved | 🔁 7 recurring"
And trend indicator shows health score change
```

### 5.4 Quality Gates (UPDATED)

```yaml
analysis_quality_gates:
  relevance:
    check: "Findings relate to specified --focus"
    threshold: 95%

  actionability:
    check: "Specific file:line references provided"
    threshold: 100%

  context:
    check: "Semantic context included in findings"
    threshold: 80%

  severity:
    check: "Impact-based severity ratings"
    threshold: "All critical and high findings"

  # NEW v2.0 gates
  validation_chain:
    check: "Hybrid validation completed for MEDIUM+ confidence findings"
    threshold: 100%

  progressive_disclosure:
    check: "All 3 tiers properly populated"
    threshold: 100%

  quality_scoring:
    check: "Auggie results scored before processing"
    threshold: 100%
```

---

## 6. Implementation Phases (REVISED by ROI)

### Phase 1: Critical Fixes + P1 Improvements (Week 1-2)
**Duration**: 2 sprints
**Dependencies**: None

**Deliverables**:
- [ ] Fix MCP tool name: "auggie-mcp" → "mcp__auggie-mcp__codebase-retrieval"
- [ ] Add required `directory_path` parameter to all Auggie calls
- [ ] Implement Progressive Disclosure output (ROI 7.01)
- [ ] Integrate Tier Classification from sc:task-unified (ROI 6.83)
- [ ] Implement Cross-Session Memory via Serena (ROI 6.71)
- [ ] Basic fallback with degradation feedback

**Acceptance Criteria**:
- All Auggie calls include directory_path
- Output shows correct tier based on user request
- Memory persists across sessions
- Degradation messages shown when MCP unavailable

### Phase 2: P2 Improvements (Week 3-4)
**Duration**: 2 sprints
**Dependencies**: Phase 1 complete

**Deliverables**:
- [ ] Implement Adaptive Token Budgeting (ROI 6.50)
- [ ] Add Language-Aware Query Templates (ROI 6.43)
- [ ] Implement Iterative Query Refinement (ROI 6.23)
- [ ] Build Hybrid Validation Pipeline (ROI 6.11)
- [ ] Add --aggressiveness flag (ROI 6.10)

**Acceptance Criteria**:
- Budget adapts to codebase size
- Language-specific queries execute correctly
- Refinement improves quality scores
- Hybrid validation produces confidence scores
- Aggressiveness modifies query intensity

### Phase 3: P3 Improvements + Hardening (Week 5-6)
**Duration**: 2 sprints
**Dependencies**: Phase 2 complete

**Deliverables**:
- [ ] Implement Auggie Quality Scoring (ROI 5.53)
- [ ] Add Real-Time Degradation Feedback (ROI 5.42)
- [ ] Performance monitoring and alerting
- [ ] Documentation and examples
- [ ] A/B testing framework for precision measurement

**Acceptance Criteria**:
- Quality scores logged for all queries
- Degradation feedback shown in real-time
- Monitoring dashboards operational
- Documentation complete for all features
- Token efficiency claims validated

### Implementation Timeline

```
Week 1-2:  [████████████████████] Phase 1: Critical Fixes + P1 (ROI 7.01, 6.83, 6.71)
Week 3-4:  [████████████████████] Phase 2: P2 Improvements (ROI 6.50→6.10)
Week 5-6:  [████████████████████] Phase 3: P3 + Hardening (ROI 5.53, 5.42)
           ─────────────────────────────────────────────→
           Week 1   Week 2   Week 3   Week 4   Week 5   Week 6
```

---

## 7. Risk Register (UPDATED)

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| R1 | Auggie MCP unavailable during analysis | Medium | High | Circuit breaker + fallback chain + degradation feedback | Architect |
| R2 | Query latency exceeds budget | Low | Medium | Adaptive budgeting + early termination + parallel execution | Performance |
| R3 | False positive rate unchanged | Low | High | Iterative refinement + hybrid validation pipeline | Analyzer |
| R4 | Large codebase performance | Medium | Medium | Adaptive token budgeting + hierarchical narrowing | Architect |
| R5 | User learning curve | Low | Low | Clear examples + progressive disclosure defaults | Scribe |
| R6 | Token efficiency claims unmet | Medium | Medium | A/B testing + adaptive budgeting + MCP overhead tracking | Performance |
| R7 | Evidence chain overhead too high | Medium | Low | Progressive disclosure + tier-specific requirements | Analyzer |
| R8 | Caching invalidation bugs | Low | Medium | Conservative TTL + explicit invalidation on git commit | QA |
| **R9** | **Missing directory_path causes failures** | **High** | **High** | **Auto-detect project root, validate before query** | **Architect** |
| **R10** | **Cross-session memory corruption** | **Low** | **Medium** | **Validation on load, backup previous state** | **QA** |
| **R11** | **User confusion with aggressiveness levels** | **Low** | **Low** | **Clear documentation, sensible defaults** | **Scribe** |

---

## 8. Appendices

### Appendix A: Glossary (UPDATED)

| Term | Definition |
|------|------------|
| Auggie MCP | Model Context Protocol server providing semantic code search via `mcp__auggie-mcp__codebase-retrieval` tool |
| Circuit Breaker | Pattern that prevents cascading failures by failing fast when service is unhealthy |
| Evidence Chain | Traceable path from finding to source code with supporting cross-references |
| Semantic Discovery | Code search using natural language understanding vs. pattern matching |
| Depth Tier | Execution mode controlling resource budget and analysis thoroughness |
| **Aggressiveness** | User-controllable query intensity level (minimal/balanced/aggressive/maximum) |
| **Progressive Disclosure** | 3-tier output system (Summary → Details → Evidence) |
| **Hybrid Validation** | 3-stage finding verification (Auggie → Serena → Grep) |
| **Tier Classification** | Task categorization (STRICT/STANDARD/LIGHT/EXEMPT) from sc:task-unified |
| **Quality Score** | Metric for Auggie result relevance and completeness (0.0-1.0) |

### Appendix B: Related Documents

- [Proposal Document v2.0](./sc-analyze-auggie-refactor-proposal.md)
- [Adversarial Debate Transcript](./sc-analyze-auggie-debate-transcript.md)
- [MCP.md Framework Reference](~/.claude/MCP.md)
- [PRINCIPLES.md](~/.claude/PRINCIPLES.md)
- [sc:task-unified Skill](/.claude/skills/sc-task-unified/)

### Appendix C: Expert Panel Credits

| Expert | Contribution |
|--------|--------------|
| Karl Wiegers | Requirements engineering, SMART criteria, acceptance criteria, FR-9→FR-15 specifications |
| Martin Fowler | Architecture patterns, interface design, dependency management, AD-4/AD-5 decisions |
| Michael Nygard | Reliability patterns, circuit breakers, operational concerns, degradation feedback |
| Gojko Adzic | Specification by example, Given/When/Then scenarios, AT-5→AT-8 tests |
| Lisa Crispin | Testing strategy, quality validation, coverage requirements, quality gate updates |

### Appendix D: ROI-Prioritized Improvement Summary

| Rank | Improvement | ROI Score | Verdict | Phase |
|------|-------------|-----------|---------|-------|
| 1 | Progressive Disclosure Evidence | 7.01 | STRONG_CANDIDATE | 1 |
| 2 | Tier Classification Integration | 6.83 | STRONG_CANDIDATE | 1 |
| 3 | Cross-Session Analysis Memory | 6.71 | STRONG_CANDIDATE | 1 |
| 4 | Adaptive Token Budgeting | 6.50 | STRONG_CANDIDATE | 2 |
| 5 | Language-Aware Query Templates | 6.43 | STRONG_CANDIDATE | 2 |
| 6 | Iterative Query Refinement | 6.23 | STRONG_CANDIDATE | 2 |
| 7 | Hybrid Validation Pipeline | 6.11 | STRONG_CANDIDATE | 2 |
| 8 | --aggressiveness Flag | 6.10 | STRONG_CANDIDATE | 2 |
| 9 | Auggie Result Quality Scoring | 5.53 | CONSIDER | 3 |
| 10 | Real-Time Degradation Feedback | 5.42 | CONSIDER | 3 |

---

*Specification Version 2.0.0 - Spec-Panel Reviewed*
*Incorporating 10 improvements prioritized by ROI score*
*Expert reviewers: Wiegers, Fowler, Nygard, Adzic, Crispin*
