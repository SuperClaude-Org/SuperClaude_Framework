# Unified /sc:task Command Implementation Workflow

**Generated**: 2026-01-23
**Source**: UNIFIED-TASK-COMMAND-SPEC.md v1.2.0
**Strategy**: Systematic
**Estimated Effort**: 15-20 development days

---

## Overview

This workflow implements the unified `/sc:task` command that merges orchestration capabilities with MCP compliance enforcement into a single coherent interface.

### Success Criteria
- Tier classification accuracy ≥80%
- User confusion rate <10%
- Skip rate <12%
- Regression prevention ≥85%
- STRICT tier overhead <25%

---

## Phase 1: Foundation & Core Infrastructure
**Duration**: 3-4 days | **Priority**: Critical | **Dependencies**: None

### 1.1 Protocol Classes & Interfaces
- [ ] **P1.1.1** Create `TierClassifierProtocol` interface (§10.1)
  - Define `classify()` method signature
  - Define `ClassificationResult` dataclass
  - Add type hints and docstrings

- [ ] **P1.1.2** Create `VerificationEngineProtocol` interface (§10.1)
  - Define `verify()` method signature
  - Define `VerificationPlan` and `VerificationResult` dataclasses

- [ ] **P1.1.3** Create `FeedbackCollectorProtocol` interface (§10.1)
  - Define `collect()` and `analyze()` method signatures
  - Define feedback event types

- [ ] **P1.1.4** Create `CircuitBreakerProtocol` interface (§10.1)
  - Define circuit state management
  - Define failure/success recording methods

### 1.2 Observability Infrastructure
- [ ] **P1.2.1** Implement `ObservabilityEventType` enum (§10.2)
  - TASK_STARTED, TASK_COMPLETED, TASK_FAILED
  - CLASSIFICATION_STARTED, CLASSIFICATION_COMPLETE
  - VERIFICATION_STARTED, VERIFICATION_COMPLETE
  - CIRCUIT_OPENED, CIRCUIT_CLOSED
  - OVERRIDE_APPLIED, FEEDBACK_COLLECTED

- [ ] **P1.2.2** Implement `TaskObservability` class (§10.2)
  - Event emission methods
  - Handler registration
  - Prometheus metrics integration

- [ ] **P1.2.3** Create metrics dashboard schema (Appendix C)
  - Classification metrics
  - Override metrics
  - System health metrics

### 1.3 Configuration System
- [ ] **P1.3.1** Define configuration dataclasses
  - `CircuitBreakerConfig` (§4.4)
  - `BatchVerificationLimits` (§4.5)
  - `TrustThresholds` (§5.5)

- [ ] **P1.3.2** Implement smart defaults (§2.3)
  - Strategy: auto
  - Compliance: auto
  - Verify: auto
  - Parallel: false
  - Delegate: false

---

## Phase 2: Tier Classification System
**Duration**: 3-4 days | **Priority**: Critical | **Dependencies**: Phase 1

### 2.1 Keyword Detection Engine
- [ ] **P2.1.1** Implement STRICT keyword detection (§3.4)
  - Security domain keywords
  - Data integrity keywords
  - Scope indicator keywords
  - Experimentation keywords
  - API contract keywords

- [ ] **P2.1.2** Implement EXEMPT keyword detection (§3.4)
  - Question keywords
  - Planning keywords
  - Git operation keywords

- [ ] **P2.1.3** Implement LIGHT keyword detection (§3.4)
  - Trivial change keywords
  - Formatting keywords

- [ ] **P2.1.4** Implement STANDARD keyword detection (§3.4)
  - Standard development action keywords

### 2.2 Compound Phrase Handling
- [ ] **P2.2.1** Implement LIGHT compound phrase overrides (§3.5)
  - "quick fix", "minor change", "fix typo", etc.

- [ ] **P2.2.2** Implement STRICT compound phrase overrides (§3.5)
  - "fix security", "add authentication", etc.

- [ ] **P2.2.3** Add compound phrase detection priority logic

### 2.3 TierClassifier Implementation
- [ ] **P2.3.1** Implement `TierClassifier.classify()` (§3.2)
  - Compound phrase check (highest priority)
  - Priority-ordered keyword scoring
  - Pattern matching for EXEMPT
  - Context boosters

- [ ] **P2.3.2** Implement `_apply_context_boosters()` (§3.2)
  - File count boosting
  - Security-sensitive path detection
  - Test file detection
  - Documentation-only detection

- [ ] **P2.3.3** Implement `_resolve_with_priority()` (§3.2)
  - Priority order: STRICT > EXEMPT > LIGHT > STANDARD
  - Ambiguity escalation (within 0.1)

- [ ] **P2.3.4** Implement confidence scoring (§3.6)
  - Score calculation: min(0.95, 0.5 + max_score)
  - requires_confirmation threshold (<0.7)

### 2.4 Classification Display
- [ ] **P2.4.1** Implement `ConfidenceDisplay.render()` (§3.6)
  - Confidence bar visualization
  - Rationale display
  - Alternatives display
  - Override prompt for low confidence

---

## Phase 3: Verification System
**Duration**: 3-4 days | **Priority**: Critical | **Dependencies**: Phase 2

### 3.1 Verification Router
- [ ] **P3.1.1** Define critical path patterns (§4.2)
  - security/, auth/, crypto/, models/, migrations/, etc.

- [ ] **P3.1.2** Define trivial path patterns (§4.2)
  - *.md, *test*.py, *.txt, etc.

- [ ] **P3.1.3** Implement `VerificationRouter.route()` (§4.2)
  - EXEMPT → skip
  - Critical patterns → CRITICAL tier
  - Trivial patterns → skip
  - Match to compliance tier

### 3.2 Batch Verification
- [ ] **P3.2.1** Implement `BatchVerifier` class (§4.3)
  - Pending changes queue
  - Batch threshold (default: 3)

- [ ] **P3.2.2** Implement `add_change()` method (§4.3)
  - Immediate verification triggers
  - Batch threshold check

- [ ] **P3.2.3** Implement `flush()` method (§4.3)
  - Path aggregation
  - Max tier determination
  - Batch execution

### 3.3 Bounded Batch Verification
- [ ] **P3.3.1** Implement `BatchVerificationLimits` (§4.5)
  - max_changes_per_batch: 15
  - min_changes_per_batch: 1
  - max_verification_subagents: 3
  - max_active_subagents: 5
  - max_delegated_tasks: 10
  - Timeout limits

- [ ] **P3.3.2** Implement `BoundedBatchVerifier` (§4.5)
  - Resource bounds enforcement
  - Timeout handling
  - Batch splitting logic

### 3.4 Circuit Breakers
- [ ] **P3.4.1** Implement `CircuitState` enum (§4.4)
  - CLOSED, OPEN, HALF_OPEN

- [ ] **P3.4.2** Implement `MCPCircuitBreaker` class (§4.4)
  - State transitions
  - Failure/success recording
  - Timeout handling

- [ ] **P3.4.3** Configure per-server circuit breakers (§4.4)
  - Sequential: failure_threshold=3, timeout=30s
  - Context7: failure_threshold=5, timeout=60s
  - Serena: failure_threshold=4, timeout=45s
  - Playwright: failure_threshold=2, timeout=120s

### 3.5 Verification Caching
- [ ] **P3.5.1** Implement verification result caching (§4.6)
  - Cache key generation
  - TTL management
  - Cache invalidation

---

## Phase 4: Feedback & Learning System
**Duration**: 2-3 days | **Priority**: High | **Dependencies**: Phase 3

### 4.1 User Feedback Collection
- [ ] **P4.1.1** Implement `FeedbackEvent` dataclass (§5.1)
  - task_id, tier_classified, user_override
  - feedback_type, timestamp, context_hash

- [ ] **P4.1.2** Implement feedback UI integration (§5.1)
  - Tier appropriateness question
  - Override reason capture

- [ ] **P4.1.3** Implement feedback storage

### 4.2 Override Tracking
- [ ] **P4.2.1** Implement `OverrideTracker` class (§5.2)
  - Override pattern collection
  - Pattern weight calculation

- [ ] **P4.2.2** Implement `OverrideType` enum (§5.2)
  - TIER_UPGRADE, TIER_DOWNGRADE, SKIP_COMPLIANCE
  - VERIFICATION_SKIP, FORCE_STRICT, FORCE_EXEMPT

### 4.3 Implicit Feedback Collection
- [ ] **P4.3.1** Implement implicit feedback detection (§5.4)
  - Immediate override signal
  - Regression detection signal
  - Smooth completion signal
  - Re-execution signal

- [ ] **P4.3.2** Implement `ImplicitFeedbackCollector` (§5.4)
  - Signal detection methods
  - Feedback synthesis

### 4.4 Team Trust Context
- [ ] **P4.4.1** Implement `TeamTrustContext` (§5.5)
  - user_accuracy_history
  - domain_expertise
  - override_calibration

- [ ] **P4.4.2** Implement trust-based tier adjustment (§5.5)
  - High trust → reduce tier
  - Low trust → maintain tier

- [ ] **P4.4.3** Implement `TrustBasedTierAdjuster` (§5.6)
  - Trust threshold configuration
  - Tier adjustment logic

### 4.5 Calibration Process
- [ ] **P4.5.1** Implement `CalibrationEngine` (§5.3)
  - Pattern analysis
  - Threshold adjustment
  - Keyword weight updates

---

## Phase 5: MCP Server Integration
**Duration**: 2-3 days | **Priority**: High | **Dependencies**: Phase 3

### 5.1 Server Selection
- [ ] **P5.1.1** Implement server selection matrix (§6.1)
  - Always active: Sequential, Context7, Serena
  - Conditional: Playwright, Magic, Morphllm

- [ ] **P5.1.2** Implement `should_activate_playwright()` (§6.2)
  - UI indicators detection
  - Tier requirement check

### 5.2 Persona Coordination
- [ ] **P5.2.1** Implement persona matrix (§6.3)
  - Core personas: architect, analyzer, qa, refactorer
  - Domain personas: backend, frontend, infrastructure, security
  - Verification persona: quality-engineer

- [ ] **P5.2.2** Implement persona activation triggers

### 5.3 Tool Coordination
- [ ] **P5.3.1** Implement tool-MCP coordination patterns (§6.4)
  - Planning phase sequence
  - Execution phase sequence
  - Verification phase sequence
  - Completion phase sequence

- [ ] **P5.3.2** Implement tier-specific tool usage rules (§6.4)
  - STRICT: all tools
  - STANDARD: no Task (verification agents)
  - LIGHT: limited tools
  - EXEMPT: minimal tools

---

## Phase 6: Command Interface & Integration
**Duration**: 2-3 days | **Priority**: High | **Dependencies**: Phases 2-5

### 6.1 Command Parser
- [ ] **P6.1.1** Implement flag parsing (§2.2)
  - Strategy flags
  - Compliance flags
  - Execution control flags
  - Verification flags

- [ ] **P6.1.2** Implement smart defaults application (§2.3)

### 6.2 Auto-Activation
- [ ] **P6.2.1** Implement trigger detection (§1.5)
  - Complexity score triggers
  - Multi-file scope triggers
  - Security domain triggers
  - Keyword triggers

- [ ] **P6.2.2** Implement context signal detection (§1.5)

### 6.3 Main Orchestrator
- [ ] **P6.3.1** Implement `/sc:task` main entry point
  - Parse arguments and flags
  - Classify tier
  - Execute with compliance
  - Verify results
  - Collect feedback

- [ ] **P6.3.2** Integrate observability hooks

---

## Phase 7: Testing & Validation
**Duration**: 2-3 days | **Priority**: High | **Dependencies**: Phase 6

### 7.1 Golden Dataset Tests
- [ ] **P7.1.1** Create 100-example golden dataset (§9.5)
  - STRICT examples (25)
  - STANDARD examples (25)
  - LIGHT examples (25)
  - EXEMPT examples (25)

- [ ] **P7.1.2** Implement boundary value tests (§9.5)
  - Threshold boundaries
  - Edge cases

- [ ] **P7.1.3** Implement ambiguous case tests
  - Conflicting signals
  - Low confidence scenarios

### 7.2 Given/When/Then Scenarios
- [ ] **P7.2.1** Implement STRICT tier scenarios (§9.2)
  - Security change scenario
  - Multi-file refactoring scenario

- [ ] **P7.2.2** Implement STANDARD tier scenarios (§9.2)
  - Single-file update scenario
  - API modification scenario

- [ ] **P7.2.3** Implement LIGHT tier scenarios (§9.2)
  - Typo fix scenario
  - Comment update scenario

- [ ] **P7.2.4** Implement EXEMPT tier scenarios (§9.2)
  - Question scenario
  - Exploration scenario

### 7.3 Integration Tests
- [ ] **P7.3.1** MCP server integration tests
- [ ] **P7.3.2** Circuit breaker behavior tests
- [ ] **P7.3.3** Batch verification tests
- [ ] **P7.3.4** Feedback loop tests

---

## Phase 8: Migration & Deprecation
**Duration**: 1-2 days | **Priority**: Medium | **Dependencies**: Phase 7

### 8.1 Migration Helpers
- [ ] **P8.1.1** Create migration guide documentation (§8)
- [ ] **P8.1.2** Implement command aliasing
  - `sc:task-mcp` → `sc:task --compliance strict`

- [ ] **P8.1.3** Add deprecation warnings

### 8.2 Backward Compatibility
- [ ] **P8.2.1** Ensure existing `sc:task` behavior preserved
- [ ] **P8.2.2** Ensure existing `sc:task-mcp` behavior preserved
- [ ] **P8.2.3** Document breaking changes (if any)

---

## Phase 9: Documentation & Finalization
**Duration**: 1 day | **Priority**: Medium | **Dependencies**: Phase 8

### 9.1 User Documentation
- [ ] **P9.1.1** Update command help text
- [ ] **P9.1.2** Create usage examples (§7)
- [ ] **P9.1.3** Document flag combinations (§7.2)

### 9.2 Developer Documentation
- [ ] **P9.2.1** Document protocol classes
- [ ] **P9.2.2** Document observability hooks
- [ ] **P9.2.3** Document extension points

### 9.3 Final Validation
- [ ] **P9.3.1** Run full test suite
- [ ] **P9.3.2** Validate success criteria met
- [ ] **P9.3.3** Update specification status to APPROVED

---

## Dependency Graph

```
Phase 1 (Foundation)
    │
    ├──▶ Phase 2 (Classification)
    │       │
    │       └──▶ Phase 3 (Verification)
    │               │
    │               ├──▶ Phase 4 (Feedback)
    │               │
    │               └──▶ Phase 5 (MCP Integration)
    │                       │
    │                       └──▶ Phase 6 (Command Interface)
    │                               │
    │                               └──▶ Phase 7 (Testing)
    │                                       │
    │                                       └──▶ Phase 8 (Migration)
    │                                               │
    │                                               └──▶ Phase 9 (Documentation)
```

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Classification accuracy <80% | High | Medium | Golden dataset expansion, user feedback loop |
| Circuit breaker too aggressive | Medium | Low | Conservative thresholds, monitoring |
| Performance overhead >25% | High | Low | Caching, batch verification, parallel execution |
| MCP server unavailability | Medium | Medium | Circuit breakers, graceful degradation |
| User resistance to unified command | Medium | Low | Clear migration guide, backward compatibility |

---

## Acceptance Checklist

- [ ] All protocol classes implemented and tested
- [ ] Tier classification accuracy ≥80% on golden dataset
- [ ] Circuit breakers prevent cascading failures
- [ ] Bounded batch verification enforces resource limits
- [ ] Feedback loop collecting and learning from usage
- [ ] All MCP servers properly integrated
- [ ] Migration path documented and tested
- [ ] Success criteria validated with telemetry
