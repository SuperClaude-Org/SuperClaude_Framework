# Unified Task Command Specification

**Version**: 1.2.0
**Status**: DRAFT - Framework Compliance Update
**Created**: 2026-01-23
**Revised**: 2026-01-23
**Authors**: Claude Code + Adversarial Debate Panel

### Revision Summary (v1.2.0)

This revision addresses SuperClaude framework compliance gaps:

| Gap | Issue | Resolution |
|-----|-------|------------|
| **G1** | Missing Triggers section | ✅ Added Section 1.5 with auto-activation patterns, keyword triggers, context signals |
| **G2** | Missing Boundaries section | ✅ Added Section 12 with Will/Will Not format and escape hatches |
| **G3** | Scattered NFRs | ✅ Consolidated into Section 11 with performance, reliability, UX, and resource requirements |
| **G4** | No Tool Coordination table | ✅ Added Section 6.4 with tool-MCP coordination patterns and tier-specific usage |

### Revision Summary (v1.1.0)

This revision addressed critical issues identified by three expert panels:

| Panel | Critical Issues Addressed |
|-------|--------------------------|
| **Wiegers + Adzic** | ✅ SMART criteria for all tiers (Section 3.1), ✅ Golden dataset expanded to 100 examples (Section 9.5), ✅ Given/When/Then scenarios complete |
| **Fowler + Nygard** | ✅ Circuit breakers (Section 4.4), ✅ Bounded batch size (Section 4.5), ✅ Interface/protocol classes (Section 10.1), ✅ Observability hooks (Section 10.2) |
| **Crispin + Gregory** | ✅ Implicit feedback collection (Section 5.4), ✅ Team trust context (Section 5.5), ✅ Boundary value tests (Section 9.5) |

---

## 1. Executive Summary

### 1.1 Purpose

This specification defines a **unified `/sc:task` command** that merges the orchestration capabilities of the original `sc:task` with the MCP compliance enforcement of `sc:task-mcp` into a single, coherent interface.

### 1.2 Problem Statement

The current dual-command system (`sc:task` + `sc:task-mcp`) creates:
- **User confusion**: 5-1 verdict in adversarial debate that distinction is unclear
- **Naming collision**: Both use "task" prefix
- **Capability gaps**: Compliance enforcement unavailable for frontend/devops domains
- **Decision paralysis**: Users cannot reliably choose the correct command

### 1.3 Solution Overview

A unified command with **orthogonal dimensions**:

```
/sc:task [operation] --strategy [systematic|agile|enterprise] --compliance [strict|standard|light|exempt]
```

| Dimension | Purpose | Options |
|-----------|---------|---------|
| **Strategy** | HOW to coordinate work | systematic, agile, enterprise |
| **Compliance** | HOW strictly to enforce quality | strict, standard, light, exempt |

### 1.4 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tier classification accuracy | ≥80% | User feedback on tier appropriateness |
| User confusion rate | <10% | "Which command?" questions eliminated |
| Skip rate (--skip-compliance) | <12% | Override tracking |
| Regression prevention | 85%+ | Post-verification bug detection rate |
| Time overhead for STRICT | <25% of task time | Execution telemetry |

### 1.5 Triggers

This section defines when `/sc:task` should be used and when it auto-activates.

#### Auto-Activation Patterns

| Trigger Type | Condition | Confidence |
|--------------|-----------|------------|
| **Complexity Score** | Task complexity >0.6 with code modifications | 90% |
| **Multi-file Scope** | Estimated affected files >2 | 85% |
| **Security Domain** | Paths contain `auth/`, `security/`, `crypto/` | 95% |
| **Refactoring Scope** | Keywords: refactor, remediate, multi-file | 90% |
| **Test Remediation** | Keywords: fix tests, test failures | 88% |

#### Keyword Triggers

```yaml
explicit_invocation:
  - "/sc:task [description]"
  - "/sc:task [operation] --strategy [type]"
  - "/sc:task [operation] --compliance [tier]"

auto_suggest_keywords:
  high_confidence:
    - "implement feature"
    - "refactor system"
    - "fix security"
    - "add authentication"
    - "update database schema"

  moderate_confidence:
    - "add new"
    - "create component"
    - "update service"
    - "modify API"
```

#### Context Signals

The command should be suggested when:
- User describes a multi-step implementation task
- Task involves code modifications with downstream impacts
- Security or data integrity domains are involved
- User explicitly requests compliance workflow
- Previous similar tasks benefited from structured execution

#### Manual Invocation

Users can always invoke directly:
```bash
/sc:task "description"                    # Auto-detect all dimensions
/sc:task "description" --compliance auto  # Explicit auto-detection
/sc:task "description" --skip-compliance  # Bypass compliance (escape hatch)
```

---

## 2. Command Interface

### 2.1 Usage Syntax

```bash
/sc:task [operation] [target] [flags]
```

### 2.2 Flag Taxonomy

#### Strategy Flags (Orchestration Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

#### Compliance Flags (Quality Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) | Most tasks |

#### Execution Control Flags

| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--reason "..."` | Required justification for tier override |

#### Verification Flags

| Flag | Description |
|------|-------------|
| `--verify critical` | Full sub-agent verification |
| `--verify standard` | Direct test execution only |
| `--verify skip` | Skip verification (use with caution) |
| `--verify auto` | Auto-select based on compliance tier (default) |

### 2.3 Smart Defaults

When flags are omitted, the system applies intelligent defaults:

```yaml
defaults:
  strategy: auto  # Detected from task scope
  compliance: auto  # Detected from task characteristics
  verify: auto  # Matched to compliance tier
  parallel: false
  delegate: false
```

**Auto-Detection Principle**: "Better false positives than false negatives" - when uncertain, escalate to higher compliance tier.

---

## 3. Tier Classification System

### 3.1 Compliance Tier Definitions

#### TIER 1: STRICT

**Definition**: Maximum compliance enforcement for high-risk changes.

**Characteristics**:
- Full pre-work checklist required
- Complete task execution template
- Mandatory verification agent spawn
- Adversarial review questions
- "Did I?" post-task checklist

**Acceptance Criteria** (SMART):
- **S**pecific: All 6 checklist categories completed
- **M**easurable: 100% checklist completion rate
- **A**chievable: <25% overhead relative to task time
- **R**elevant: Prevents regressions in high-impact changes
- **T**ime-bound: Verification completes within 60 seconds

#### TIER 2: STANDARD

**Definition**: Core rules enforcement for typical code changes.

**Characteristics**:
- Context loading before edit required
- Downstream impact check required
- Manual or automated verification acceptable

**Acceptance Criteria** (SMART):
- **S**pecific: Context loaded, impacts checked, basic verification performed
- **M**easurable:
  - ≥1 codebase-retrieval call before editing
  - ≥1 downstream impact search (grep/find_referencing_symbols)
  - Test execution OR manual confirmation documented
- **A**chievable: <15% overhead relative to task time
- **R**elevant: Prevents common regressions in typical code changes
- **T**ime-bound: Verification completes within 30 seconds

**Checklist**:
- [ ] Context loaded via codebase-retrieval
- [ ] Downstream impacts searched (find_referencing_symbols OR grep)
- [ ] Tests run OR manual verification documented

#### TIER 3: LIGHT

**Definition**: Awareness-level guidance for minor changes.

**Characteristics**:
- MCP principles acknowledged
- Judgment-based verification
- Formal process skipped

**Acceptance Criteria** (SMART):
- **S**pecific: Change made, no unexpected side effects, scope matches intent
- **M**easurable:
  - Modified files ≤2
  - Changed lines ≤50
  - No new test failures introduced
- **A**chievable: <5% overhead (essentially no process overhead)
- **R**elevant: Appropriate for truly trivial changes
- **T**ime-bound: No verification delay

**Checklist**:
- [ ] Change scope as expected (files/lines within bounds)
- [ ] Quick sanity check (syntax valid, no obvious errors)
- [ ] Proceed with judgment

#### TIER 4: EXEMPT

**Definition**: No compliance enforcement for non-code activities.

**Triggers**: Questions, exploration, brainstorming, documentation-only

**Acceptance Criteria** (SMART):
- **S**pecific: Task is read-only OR documentation-only
- **M**easurable:
  - Zero code files modified
  - Zero test executions required
  - Zero verification steps needed
- **A**chievable: 0% overhead
- **R**elevant: No compliance needed for non-modification activities
- **T**ime-bound: Immediate execution

**Checklist**: None - proceed normally

### 3.2 Classification Algorithm

```python
class TierClassifier:
    """
    Determines compliance tier based on task characteristics.

    Priority Order: STRICT > EXEMPT > LIGHT > STANDARD > FALLBACK

    This ordering ensures:
    - Safety-critical triggers always win (STRICT)
    - Explicit non-code work is recognized (EXEMPT)
    - Trivial work is appropriately light-touch (LIGHT)
    - Unknown tasks default to moderate enforcement (STANDARD)
    """

    # Priority 1: STRICT triggers (safety-critical)
    STRICT_KEYWORDS = [
        # Security domain
        "security", "auth", "authentication", "authorization",
        "password", "credential", "token", "session", "encrypt",

        # Data integrity domain
        "database", "migration", "schema", "model",

        # Scope indicators
        "refactor", "remediate", "fix tests", "multi-file",
        "across all", "throughout", "system-wide",

        # Exploratory coding (intentional experimentation)
        "exploratory", "try this", "experiment",

        # API contracts
        "api contract", "breaking change", "public interface"
    ]

    STRICT_COMPOUND_PHRASES = [
        "fix security",
        "add authentication",
        "update database",
        "change api",
        "modify schema"
    ]

    # Priority 2: EXEMPT triggers (non-code work)
    EXEMPT_KEYWORDS = [
        # Questions
        "what", "how", "why", "explain", "understand",

        # Exploration (read-only)
        "explore", "investigate", "analyze", "review",

        # Planning
        "brainstorm", "plan", "design", "think about",

        # Git operations
        "git status", "git diff", "git log"
    ]

    EXEMPT_PATTERNS = [
        r"^what (is|are|does)",
        r"^how (do|does|can|should)",
        r"^explain",
        r"^show me"
    ]

    # Priority 3: LIGHT triggers (trivial changes)
    LIGHT_KEYWORDS = [
        "typo", "typos", "spelling",
        "format", "formatting", "indent",
        "comment", "comments", "documentation",
        "minor", "trivial", "simple",
        "rename", "spacing", "whitespace", "lint"
    ]

    LIGHT_COMPOUND_PHRASES = [
        "quick fix",           # Overrides "fix" → STANDARD
        "minor change",        # Overrides "change" → STANDARD
        "small update",        # Overrides "update" → STANDARD
        "refactor comment",    # Overrides "refactor" → STRICT
        "fix typo"             # Overrides "fix" → STANDARD
    ]

    # Priority 4: STANDARD triggers (typical code work)
    STANDARD_KEYWORDS = [
        "add", "create", "implement", "build",
        "update", "modify", "change", "edit",
        "fix", "remove", "delete"
    ]

    def classify(self, task_description: str, context: TaskContext) -> ClassificationResult:
        """
        Main classification entry point.

        Returns:
            ClassificationResult with tier, confidence, rationale, and alternatives
        """
        task_lower = task_description.lower()

        # Step 1: Check compound phrases first (highest specificity)
        compound_result = self._check_compound_phrases(task_lower)
        if compound_result:
            return compound_result

        # Step 2: Apply priority-ordered keyword detection
        scores = {
            "STRICT": self._score_keywords(task_lower, self.STRICT_KEYWORDS),
            "EXEMPT": self._score_keywords(task_lower, self.EXEMPT_KEYWORDS),
            "LIGHT": self._score_keywords(task_lower, self.LIGHT_KEYWORDS),
            "STANDARD": self._score_keywords(task_lower, self.STANDARD_KEYWORDS)
        }

        # Step 3: Apply pattern matching for EXEMPT
        if self._matches_exempt_patterns(task_lower):
            scores["EXEMPT"] += 0.5

        # Step 4: Apply context boosters
        scores = self._apply_context_boosters(scores, context)

        # Step 5: Resolve conflicts using priority ordering
        tier, confidence = self._resolve_with_priority(scores)

        # Step 6: Generate rationale and alternatives
        rationale = self._generate_rationale(task_lower, tier, scores)
        alternatives = self._generate_alternatives(scores, tier)

        return ClassificationResult(
            tier=tier,
            confidence=confidence,
            rationale=rationale,
            alternatives=alternatives,
            keyword_matches=self._get_matches(task_lower),
            requires_confirmation=confidence < 0.7
        )

    def _check_compound_phrases(self, task: str) -> Optional[ClassificationResult]:
        """Check for compound phrases that override individual keywords."""
        for phrase in self.LIGHT_COMPOUND_PHRASES:
            if phrase in task:
                return ClassificationResult(
                    tier="LIGHT",
                    confidence=0.9,
                    rationale=f"Compound phrase '{phrase}' detected - LIGHT override",
                    alternatives=[]
                )

        for phrase in self.STRICT_COMPOUND_PHRASES:
            if phrase in task:
                return ClassificationResult(
                    tier="STRICT",
                    confidence=0.9,
                    rationale=f"Compound phrase '{phrase}' detected - STRICT override",
                    alternatives=[]
                )

        return None

    def _apply_context_boosters(self, scores: dict, context: TaskContext) -> dict:
        """Apply contextual signals to boost/reduce tier scores."""

        # File count booster
        if context.estimated_files > 2:
            scores["STRICT"] += 0.3
        elif context.estimated_files == 1:
            scores["LIGHT"] += 0.1

        # Security-sensitive path detection
        if any(p in context.affected_paths for p in ["auth", "security", "crypto"]):
            scores["STRICT"] += 0.4

        # Test file detection
        if all("test" in p for p in context.affected_paths):
            scores["STANDARD"] += 0.2  # Test changes are moderate risk

        # Documentation-only detection
        if all(p.endswith((".md", ".txt", ".rst")) for p in context.affected_paths):
            scores["EXEMPT"] += 0.5

        return scores

    def _resolve_with_priority(self, scores: dict) -> Tuple[str, float]:
        """
        Resolve tier using priority ordering.

        Priority: STRICT > EXEMPT > LIGHT > STANDARD

        If highest score is ambiguous (within 0.1), escalate to higher priority tier.
        """
        priority_order = ["STRICT", "EXEMPT", "LIGHT", "STANDARD"]

        # Get tier with highest score
        max_tier = max(scores, key=scores.get)
        max_score = scores[max_tier]

        # Check for close competitors
        close_competitors = [
            t for t, s in scores.items()
            if t != max_tier and abs(s - max_score) < 0.1
        ]

        if close_competitors:
            # Escalate to highest priority among competitors
            all_candidates = [max_tier] + close_competitors
            for priority_tier in priority_order:
                if priority_tier in all_candidates:
                    confidence = 0.6  # Lower confidence due to ambiguity
                    return priority_tier, confidence

        # Clear winner
        confidence = min(0.95, 0.5 + max_score)
        return max_tier, confidence

    def _generate_rationale(self, task: str, tier: str, scores: dict) -> str:
        """Generate human-readable rationale for classification."""
        matches = self._get_matches(task)

        rationale_parts = [f"Classified as {tier}:"]

        if matches.get(tier):
            rationale_parts.append(f"  - Keywords matched: {', '.join(matches[tier])}")

        if scores[tier] > 0.5:
            rationale_parts.append(f"  - Confidence score: {scores[tier]:.2f}")

        competing = [(t, s) for t, s in scores.items() if t != tier and s > 0.2]
        if competing:
            rationale_parts.append(f"  - Considered alternatives: {competing}")

        return "\n".join(rationale_parts)
```

### 3.3 Priority Resolution Rules

```yaml
priority_resolution:
  principle: "Safety-critical tiers win over convenience tiers"

  order:
    1: STRICT   # Security, multi-file, breaking changes
    2: EXEMPT   # Non-code work recognized early
    3: LIGHT    # Trivial work gets light treatment
    4: STANDARD # Fallback for unknown tasks

  conflict_resolution:
    - rule: "STRICT keyword + LIGHT keyword → STRICT"
      example: "'quick security fix' → STRICT (security wins over quick)"

    - rule: "EXEMPT pattern + any code keyword → Examine context"
      example: "'explain how to refactor' → EXEMPT (explain pattern wins)"

    - rule: "Compound phrase overrides individual keywords"
      example: "'fix typo' → LIGHT (compound wins over 'fix' → STANDARD)"

    - rule: "Context boosters break ties"
      example: "Ambiguous task + auth/ path → STRICT"

    - rule: "When truly uncertain, default to STANDARD"
      rationale: "Moderate enforcement is safe middle ground"
```

### 3.4 Keyword Detection Matrix

| Category | Keywords | Tier | Priority |
|----------|----------|------|----------|
| Security | security, auth, password, token, encrypt, credential | STRICT | 1 |
| Data | database, migration, schema, model | STRICT | 1 |
| Scope | refactor, multi-file, system-wide, across all | STRICT | 1 |
| Exploration | exploratory, experiment, try this | STRICT | 1 |
| Questions | what, how, why, explain | EXEMPT | 2 |
| Planning | brainstorm, plan, design, think | EXEMPT | 2 |
| Git | git status, git diff, git log | EXEMPT | 2 |
| Trivial | typo, format, comment, minor, rename | LIGHT | 3 |
| Standard | add, create, implement, update, fix, remove | STANDARD | 4 |

### 3.5 Compound Phrase Handling

```yaml
compound_phrases:
  # LIGHT overrides (trivial patterns)
  light_overrides:
    - phrase: "quick fix"
      overrides: ["fix → STANDARD"]
      result: LIGHT

    - phrase: "minor change"
      overrides: ["change → STANDARD"]
      result: LIGHT

    - phrase: "fix typo"
      overrides: ["fix → STANDARD"]
      result: LIGHT

    - phrase: "refactor comment"
      overrides: ["refactor → STRICT"]
      result: LIGHT

    - phrase: "simple update"
      overrides: ["update → STANDARD"]
      result: LIGHT

  # STRICT overrides (safety patterns)
  strict_overrides:
    - phrase: "fix security"
      overrides: ["fix → STANDARD"]
      result: STRICT

    - phrase: "add authentication"
      overrides: ["add → STANDARD"]
      result: STRICT

    - phrase: "update database"
      overrides: ["update → STANDARD"]
      result: STRICT

    - phrase: "quick security"
      overrides: ["quick → suggests LIGHT"]
      result: STRICT
      rationale: "Security always wins"

    - phrase: "minor auth change"
      overrides: ["minor → LIGHT"]
      result: STRICT
      rationale: "Auth changes are never minor"
```

### 3.6 Confidence Scoring

```python
@dataclass
class ClassificationResult:
    tier: str                    # STRICT, STANDARD, LIGHT, EXEMPT
    confidence: float            # 0.0 - 1.0
    rationale: str               # Human-readable explanation
    alternatives: List[Tuple[str, float]]  # [(tier, score), ...]
    keyword_matches: Dict[str, List[str]]  # {tier: [matched_keywords]}
    requires_confirmation: bool  # True if confidence < 0.7

class ConfidenceDisplay:
    """
    User-visible confidence display with tier recommendation.
    """

    @staticmethod
    def render(result: ClassificationResult) -> str:
        output = []

        # Header with tier and confidence
        confidence_bar = "█" * int(result.confidence * 10) + "░" * (10 - int(result.confidence * 10))
        output.append(f"Tier: {result.tier} [{confidence_bar}] {result.confidence:.0%}")

        # Rationale
        output.append(f"\nRationale: {result.rationale}")

        # Alternatives if confidence is low
        if result.alternatives:
            output.append("\nAlternatives considered:")
            for alt_tier, alt_score in result.alternatives:
                output.append(f"  - {alt_tier}: {alt_score:.0%}")

        # Confirmation prompt if needed
        if result.requires_confirmation:
            output.append("\n⚠️ Low confidence classification.")
            output.append("Override with: --compliance [strict|standard|light|exempt]")

        return "\n".join(output)

# Example output:
# Tier: STANDARD [████████░░] 78%
#
# Rationale: Classified as STANDARD:
#   - Keywords matched: add, implement
#   - Confidence score: 0.78
#   - Considered alternatives: [('STRICT', 0.35)]
```

---

## 4. Verification System

### 4.1 Verification Tier Definitions

| Verification Tier | Compliance Tier Match | Method | Token Cost | Time |
|-------------------|----------------------|--------|------------|------|
| **CRITICAL** | STRICT | Full sub-agent spawn | 3-5K | 45-60s |
| **STANDARD** | STANDARD | Direct test execution | 300-500 | 10-20s |
| **TRIVIAL** | LIGHT, EXEMPT | Skip verification | 0 | 0s |

### 4.2 Verification Routing Algorithm

```python
class VerificationRouter:
    """
    Routes verification requests to appropriate verification tier.
    """

    # Critical verification triggers
    CRITICAL_PATH_PATTERNS = [
        r"security/",
        r"auth/",
        r"crypto/",
        r"models/",      # Database models
        r"migrations/",
        r"api/.*endpoint",
        r"services/payment",
    ]

    CRITICAL_CHANGE_TYPES = [
        "security_sensitive",
        "database_schema",
        "api_contract",
        "authentication_flow",
        "multi_file_refactor"
    ]

    # Trivial verification triggers (skip)
    TRIVIAL_PATH_PATTERNS = [
        r".*\.md$",           # Documentation
        r".*test.*\.py$",     # Test files (they ARE verification)
        r".*\.txt$",
        r".*\.rst$",
        r"comments?/",
    ]

    TRIVIAL_CHANGE_TYPES = [
        "comment_only",
        "formatting_only",
        "documentation_only",
        "test_file_only"
    ]

    def route(self, change: ChangeSet, compliance_tier: str) -> VerificationPlan:
        """
        Determine verification tier and create execution plan.

        Args:
            change: The changeset to verify
            compliance_tier: The compliance tier (STRICT, STANDARD, etc.)

        Returns:
            VerificationPlan with tier, method, and execution steps
        """

        # Rule 1: EXEMPT compliance → no verification
        if compliance_tier == "EXEMPT":
            return VerificationPlan(tier="TRIVIAL", method="skip")

        # Rule 2: Check for critical patterns
        if self._is_critical(change):
            return VerificationPlan(
                tier="CRITICAL",
                method="sub_agent",
                sub_agent_type="quality-engineer",
                steps=[
                    "codebase-retrieval for context",
                    "run affected tests",
                    "check for regressions",
                    "adversarial review"
                ]
            )

        # Rule 3: Check for trivial patterns
        if self._is_trivial(change):
            return VerificationPlan(tier="TRIVIAL", method="skip")

        # Rule 4: Match to compliance tier
        if compliance_tier == "STRICT":
            return VerificationPlan(
                tier="CRITICAL",
                method="sub_agent",
                sub_agent_type="quality-engineer",
                steps=["full verification workflow"]
            )

        if compliance_tier == "STANDARD":
            return VerificationPlan(
                tier="STANDARD",
                method="direct_test",
                test_command="pytest {affected_paths} -v --tb=short"
            )

        if compliance_tier == "LIGHT":
            return VerificationPlan(tier="TRIVIAL", method="skip")

        # Fallback
        return VerificationPlan(tier="STANDARD", method="direct_test")

    def _is_critical(self, change: ChangeSet) -> bool:
        """Check if change requires critical verification."""
        # Path-based detection
        for path in change.affected_paths:
            for pattern in self.CRITICAL_PATH_PATTERNS:
                if re.match(pattern, path):
                    return True

        # Change type detection
        if change.change_type in self.CRITICAL_CHANGE_TYPES:
            return True

        # Multi-file threshold
        if len(change.affected_paths) >= 3:
            return True

        return False

    def _is_trivial(self, change: ChangeSet) -> bool:
        """Check if change can skip verification."""
        # All paths must match trivial patterns
        for path in change.affected_paths:
            if not any(re.match(p, path) for p in self.TRIVIAL_PATH_PATTERNS):
                return False

        # Or explicit trivial change type
        return change.change_type in self.TRIVIAL_CHANGE_TYPES
```

### 4.3 Batch Verification Pattern

```python
class BatchVerifier:
    """
    Batches related changes for efficient verification.

    Instead of: Task1 → Verify → Task2 → Verify → Task3 → Verify
    Uses:       Task1 → Task2 → Task3 → BatchVerify

    Benefits:
    - 60% reduction in context loading overhead
    - Holistic verification catches cross-task issues
    - Single sub-agent spawn for multiple changes
    """

    def __init__(self, batch_threshold: int = 3):
        self.pending_changes: List[ChangeSet] = []
        self.batch_threshold = batch_threshold

    def add_change(self, change: ChangeSet) -> Optional[VerificationResult]:
        """
        Add change to batch. Returns result if batch is ready.
        """
        self.pending_changes.append(change)

        # Check if any change requires immediate verification
        if self._requires_immediate(change):
            return self.flush()

        # Check batch threshold
        if len(self.pending_changes) >= self.batch_threshold:
            return self.flush()

        return None  # Batch not ready

    def flush(self) -> VerificationResult:
        """Execute batch verification for all pending changes."""
        if not self.pending_changes:
            return VerificationResult(status="no_changes")

        # Aggregate affected paths
        all_paths = set()
        for change in self.pending_changes:
            all_paths.update(change.affected_paths)

        # Determine highest verification tier needed
        max_tier = self._determine_max_tier()

        # Execute verification
        result = self._execute_verification(max_tier, list(all_paths))

        # Clear batch
        self.pending_changes = []

        return result

    def _requires_immediate(self, change: ChangeSet) -> bool:
        """Some changes require immediate verification."""
        return change.change_type in [
            "security_sensitive",
            "breaking_change",
            "production_deployment"
        ]

    def _determine_max_tier(self) -> str:
        """Get the highest verification tier from all pending changes."""
        tier_priority = {"CRITICAL": 3, "STANDARD": 2, "TRIVIAL": 1}
        max_priority = 0
        max_tier = "TRIVIAL"

        for change in self.pending_changes:
            tier = VerificationRouter().route(change, "STANDARD").tier
            if tier_priority.get(tier, 0) > max_priority:
                max_priority = tier_priority[tier]
                max_tier = tier

        return max_tier
```

### 4.4 Circuit Breakers for MCP Server Calls

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, TypeVar, Optional
import asyncio

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 3        # Failures before opening
    success_threshold: int = 2        # Successes to close from half-open
    timeout_seconds: float = 30.0     # Time before trying half-open
    call_timeout_seconds: float = 10.0  # Timeout per MCP call
    max_consecutive_timeouts: int = 2   # Timeouts count as failures

class MCPCircuitBreaker:
    """
    Circuit breaker for MCP server calls with automatic recovery.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Server failing, calls rejected immediately with fallback
    - HALF_OPEN: Testing if server recovered, limited calls allowed

    Usage:
        circuit = MCPCircuitBreaker("sequential", fallback=native_reasoning)
        result = await circuit.call(mcp__sequential__sequentialthinking, args)
    """

    def __init__(
        self,
        server_name: str,
        config: CircuitBreakerConfig = None,
        fallback: Optional[Callable] = None
    ):
        self.server_name = server_name
        self.config = config or CircuitBreakerConfig()
        self.fallback = fallback

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.consecutive_timeouts = 0

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute MCP call with circuit breaker protection."""

        # Check if circuit should transition
        self._check_state_transition()

        if self.state == CircuitState.OPEN:
            return await self._handle_open_circuit(func, *args, **kwargs)

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.call_timeout_seconds
            )

            self._record_success()
            return result

        except asyncio.TimeoutError:
            self._record_timeout()
            return await self._handle_failure(func, *args, **kwargs)

        except Exception as e:
            self._record_failure(e)
            return await self._handle_failure(func, *args, **kwargs)

    def _check_state_transition(self) -> None:
        """Check if circuit should transition between states."""
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = datetime.now() - self.last_failure_time
                if elapsed.total_seconds() >= self.config.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0

    def _record_success(self) -> None:
        """Record successful call."""
        self.failure_count = 0
        self.consecutive_timeouts = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED

    def _record_failure(self, error: Exception) -> None:
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def _record_timeout(self) -> None:
        """Record timeout (counts toward failures)."""
        self.consecutive_timeouts += 1
        if self.consecutive_timeouts >= self.config.max_consecutive_timeouts:
            self._record_failure(TimeoutError("Max consecutive timeouts"))

    async def _handle_open_circuit(self, func, *args, **kwargs):
        """Handle call when circuit is open."""
        if self.fallback:
            return await self.fallback(*args, **kwargs)
        raise CircuitOpenError(f"Circuit breaker open for {self.server_name}")

    async def _handle_failure(self, func, *args, **kwargs):
        """Handle failure with fallback if available."""
        if self.fallback:
            return await self.fallback(*args, **kwargs)
        raise MCPServerError(f"MCP server {self.server_name} failed")

class CircuitOpenError(Exception):
    """Raised when circuit is open and no fallback available."""
    pass

class MCPServerError(Exception):
    """Raised when MCP server fails and no fallback available."""
    pass

# Pre-configured circuit breakers for each MCP server
MCP_CIRCUIT_BREAKERS = {
    "sequential": MCPCircuitBreaker(
        "sequential",
        config=CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=30,
            call_timeout_seconds=15
        ),
        fallback=native_reasoning_fallback
    ),
    "context7": MCPCircuitBreaker(
        "context7",
        config=CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=60,
            call_timeout_seconds=10
        ),
        fallback=websearch_fallback
    ),
    "serena": MCPCircuitBreaker(
        "serena",
        config=CircuitBreakerConfig(
            failure_threshold=2,  # More strict - memory is critical
            timeout_seconds=45,
            call_timeout_seconds=8
        ),
        fallback=session_only_memory_fallback
    ),
    "playwright": MCPCircuitBreaker(
        "playwright",
        config=CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=120,  # Browser operations need recovery time
            call_timeout_seconds=30
        ),
        fallback=manual_testing_fallback
    )
}
```

### 4.5 Bounded Batch Size and Timeout Limits

```python
@dataclass
class BatchLimits:
    """
    Bounded limits for batch verification to prevent resource exhaustion.

    All limits are configurable but have safe defaults.
    """
    # Batch size limits
    max_batch_size: int = 5              # Maximum changes per batch
    min_batch_size: int = 1              # Minimum to trigger batch mode
    optimal_batch_size: int = 3          # Target for best efficiency

    # Timeout limits
    batch_timeout_seconds: float = 120.0  # Total batch verification timeout
    per_change_timeout_seconds: float = 30.0  # Timeout per change in batch
    sub_agent_timeout_seconds: float = 90.0   # Sub-agent spawn timeout

    # Resource limits
    max_affected_files_per_batch: int = 20   # Cap on files to verify
    max_token_budget_per_batch: int = 8000   # Token limit for batch
    max_concurrent_verifications: int = 2    # Parallel verification limit

    # Safety limits
    max_retries: int = 2                     # Retries before fallback
    circuit_breaker_threshold: int = 3       # Failures before circuit opens

class BoundedBatchVerifier:
    """
    Batch verifier with strict resource bounds and timeouts.

    Prevents:
    - Unbounded batch growth
    - Resource exhaustion
    - Hanging verification operations
    - Cascading failures
    """

    def __init__(self, limits: BatchLimits = None):
        self.limits = limits or BatchLimits()
        self.pending_changes: List[ChangeSet] = []
        self.circuit_breaker = MCP_CIRCUIT_BREAKERS.get("sequential")

    def add_change(self, change: ChangeSet) -> Optional[VerificationResult]:
        """
        Add change to batch with bounds checking.

        Returns result if:
        - Batch reaches max size
        - Change requires immediate verification
        - Timeout approaching
        """
        # Check file limit
        total_files = sum(len(c.affected_paths) for c in self.pending_changes)
        if total_files + len(change.affected_paths) > self.limits.max_affected_files_per_batch:
            # Flush current batch before adding
            result = self.flush()
            self.pending_changes.append(change)
            return result

        self.pending_changes.append(change)

        # Check batch size limit
        if len(self.pending_changes) >= self.limits.max_batch_size:
            return self.flush()

        # Check immediate verification triggers
        if self._requires_immediate(change):
            return self.flush()

        return None

    async def flush(self) -> VerificationResult:
        """Execute batch verification with timeout and bounds."""
        if not self.pending_changes:
            return VerificationResult(status="no_changes")

        try:
            # Execute with overall batch timeout
            result = await asyncio.wait_for(
                self._execute_bounded_verification(),
                timeout=self.limits.batch_timeout_seconds
            )
            return result

        except asyncio.TimeoutError:
            return VerificationResult(
                status="timeout",
                message=f"Batch verification timed out after {self.limits.batch_timeout_seconds}s",
                fallback_required=True,
                pending_changes=self.pending_changes
            )

        finally:
            self.pending_changes = []

    async def _execute_bounded_verification(self) -> VerificationResult:
        """Execute verification within bounds."""
        # Aggregate paths with limit
        all_paths = set()
        for change in self.pending_changes:
            all_paths.update(change.affected_paths)
            if len(all_paths) >= self.limits.max_affected_files_per_batch:
                break

        # Determine verification tier
        max_tier = self._determine_max_tier()

        # Execute via circuit breaker
        if max_tier == "CRITICAL":
            return await self.circuit_breaker.call(
                self._spawn_verification_agent,
                list(all_paths)[:self.limits.max_affected_files_per_batch]
            )
        else:
            return await self._execute_direct_test(list(all_paths))

    def _requires_immediate(self, change: ChangeSet) -> bool:
        """Check if change requires immediate (unbatched) verification."""
        immediate_triggers = [
            "security_sensitive",
            "breaking_change",
            "production_deployment",
            "database_migration"
        ]
        return change.change_type in immediate_triggers
```

### 4.6 Verification Caching Strategy

```yaml
verification_cache:
  purpose: "Reduce redundant verification overhead within a workflow"

  cache_layers:
    # Layer 1: Context cache
    context_cache:
      scope: "Workflow session"
      contents: "codebase-retrieval results"
      ttl: "Until workflow completion"
      invalidation: "New file modifications"

    # Layer 2: Test result cache
    test_cache:
      scope: "Per-file"
      contents: "Test execution results"
      ttl: "Until file modified"
      invalidation: "File content change"

    # Layer 3: Verification decision cache
    decision_cache:
      scope: "Per-changeset hash"
      contents: "Verification tier decision"
      ttl: "Session duration"
      invalidation: "Algorithm update"

  cache_hits:
    expected_rate: "40-60% for typical workflows"
    token_savings: "1-2K tokens per cache hit"
    time_savings: "10-20s per cache hit"

  implementation:
    storage: "In-memory dictionary with LRU eviction"
    key_format: "{workflow_id}:{file_hash}:{verification_type}"
    max_entries: 100
```

---

## 5. Feedback & Learning System

### 5.1 User Feedback Collection

```python
class TierFeedbackCollector:
    """
    Collects user feedback on tier classification accuracy.
    """

    def collect_feedback(self, task_id: str, classification: ClassificationResult) -> None:
        """
        Prompt user for feedback after task completion.
        """
        prompt = f"""
Task completed with {classification.tier} compliance tier.

Was this tier appropriate for your task?
  [1] Too much process - should have been lower tier
  [2] About right
  [3] Too little process - should have been higher tier
  [4] Skip feedback

Your choice: """

        response = get_user_input(prompt)

        feedback = TierFeedback(
            task_id=task_id,
            task_description=classification.original_task,
            assigned_tier=classification.tier,
            confidence=classification.confidence,
            user_rating=response,
            timestamp=datetime.now()
        )

        self._store_feedback(feedback)

    def _store_feedback(self, feedback: TierFeedback) -> None:
        """Store feedback for analysis."""
        # Store in Serena memory for persistence
        memory_key = f"tier_feedback_{feedback.task_id}"
        mcp__serena__write_memory(
            memory_file_name=memory_key,
            content=feedback.to_json()
        )

@dataclass
class TierFeedback:
    task_id: str
    task_description: str
    assigned_tier: str
    confidence: float
    user_rating: int  # 1=too strict, 2=right, 3=too loose, 4=skipped
    timestamp: datetime

    # Optional fields populated on override
    user_override_tier: Optional[str] = None
    override_reason: Optional[str] = None
```

### 5.2 Override Tracking

```python
class OverrideTracker:
    """
    Tracks when users override tier classification.

    Purpose:
    - Identify systematic classification errors
    - Detect keywords/phrases needing adjustment
    - Measure algorithm accuracy
    """

    def record_override(
        self,
        original_tier: str,
        user_tier: str,
        task_description: str,
        reason: str
    ) -> None:
        """Record a user tier override."""
        override = TierOverride(
            original_tier=original_tier,
            user_tier=user_tier,
            task_description=task_description,
            reason=reason,
            keywords_detected=self._extract_keywords(task_description),
            timestamp=datetime.now()
        )

        self._store_override(override)

        # Check for pattern
        if self._should_alert_pattern(override):
            self._alert_calibration_needed(override)

    def get_override_report(self, days: int = 30) -> OverrideReport:
        """Generate report of override patterns."""
        overrides = self._get_recent_overrides(days)

        return OverrideReport(
            total_overrides=len(overrides),
            override_rate=self._calculate_rate(overrides),
            common_patterns=self._identify_patterns(overrides),
            suggested_adjustments=self._suggest_adjustments(overrides)
        )

    def _identify_patterns(self, overrides: List[TierOverride]) -> List[OverridePattern]:
        """Identify recurring override patterns."""
        patterns = []

        # Group by direction (escalation vs de-escalation)
        escalations = [o for o in overrides if self._is_escalation(o)]
        deescalations = [o for o in overrides if not self._is_escalation(o)]

        # Find common keywords in each group
        if escalations:
            common_keywords = self._find_common_keywords(escalations)
            if common_keywords:
                patterns.append(OverridePattern(
                    direction="escalation",
                    keywords=common_keywords,
                    frequency=len(escalations),
                    suggestion=f"Consider adding {common_keywords} to STRICT triggers"
                ))

        if deescalations:
            common_keywords = self._find_common_keywords(deescalations)
            if common_keywords:
                patterns.append(OverridePattern(
                    direction="de-escalation",
                    keywords=common_keywords,
                    frequency=len(deescalations),
                    suggestion=f"Consider adding {common_keywords} to LIGHT triggers"
                ))

        return patterns
```

### 5.3 Calibration Process

```yaml
calibration_process:
  frequency: "Monthly or after 100 tasks"

  inputs:
    - user_feedback: "Tier appropriateness ratings"
    - override_data: "Manual tier overrides with reasons"
    - regression_data: "Bugs introduced by tier level"
    - skip_data: "--skip-compliance usage patterns"

  analysis_steps:
    1_accuracy_calculation:
      formula: "(tasks rated 'about right') / (total rated tasks)"
      target: "≥80%"

    2_pattern_identification:
      method: "Cluster override reasons by keyword"
      output: "Keywords needing tier reassignment"

    3_false_positive_analysis:
      definition: "Tasks rated 'too strict'"
      action: "Identify keywords causing over-classification"

    4_false_negative_analysis:
      definition: "Tasks rated 'too loose' OR regressions at that tier"
      action: "Identify keywords needing escalation"

    5_compound_phrase_discovery:
      method: "Find keyword combinations frequently overridden"
      action: "Add as compound phrase with appropriate tier"

  output:
    - adjusted_keyword_matrix: "Updated STRICT/STANDARD/LIGHT keywords"
    - new_compound_phrases: "Discovered phrase patterns"
    - accuracy_trend: "Historical accuracy over time"
    - recommended_threshold_changes: "Confidence threshold adjustments"

  implementation:
    storage: ".serena/memories/tier_calibration_history.md"
    automation: "Monthly Serena memory update with calibration results"
```

### 5.4 Implicit Feedback Collection

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

class ImplicitSignalType(Enum):
    """Types of implicit feedback signals."""
    # Override signals
    TIER_OVERRIDE = "tier_override"          # User manually changed tier
    SKIP_COMPLIANCE = "skip_compliance"       # Used --skip-compliance flag
    FORCE_STRICT = "force_strict"             # Used --force-strict flag

    # Behavioral signals
    IMMEDIATE_RETRY = "immediate_retry"       # Retried within 30 seconds
    ABANDONED_TASK = "abandoned_task"         # Started but didn't complete
    RAPID_COMPLETION = "rapid_completion"     # Completed very quickly
    EXTENDED_COMPLETION = "extended_completion"  # Took much longer than expected

    # Quality signals
    REGRESSION_DETECTED = "regression_detected"  # Bug found post-verification
    TEST_FAILURES = "test_failures"              # Tests failed after change
    ROLLBACK_PERFORMED = "rollback_performed"    # Git revert after task

    # Engagement signals
    CONFIRMATION_SKIPPED = "confirmation_skipped"   # Dismissed confirmation prompt
    RATIONALE_VIEWED = "rationale_viewed"           # Expanded rationale details
    ALTERNATIVES_VIEWED = "alternatives_viewed"     # Viewed alternative tiers

@dataclass
class ImplicitFeedbackSignals:
    """Collection of implicit feedback signals for a task."""
    task_id: str
    session_id: str
    signals: List[ImplicitSignalType] = field(default_factory=list)
    timestamps: Dict[ImplicitSignalType, datetime] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Computed signals
    time_to_completion: Optional[timedelta] = None
    expected_completion_time: Optional[timedelta] = None
    retry_count: int = 0

    def add_signal(self, signal: ImplicitSignalType, metadata: Dict = None) -> None:
        """Add an implicit signal with timestamp."""
        self.signals.append(signal)
        self.timestamps[signal] = datetime.now()
        if metadata:
            self.metadata.update(metadata)

    def has_signal(self, signal: ImplicitSignalType) -> bool:
        """Check if a signal was recorded."""
        return signal in self.signals

@dataclass
class ImplicitFeedbackAnalysis:
    """Analysis of implicit feedback for calibration."""
    task_id: str
    assigned_tier: str

    # Inferred tier appropriateness
    inferred_too_strict: bool = False
    inferred_too_loose: bool = False
    inferred_appropriate: bool = False

    # Contributing signals
    contributing_signals: List[ImplicitSignalType] = field(default_factory=list)

    # Confidence in inference
    inference_confidence: float = 0.0

class ImplicitFeedbackCollector:
    """
    Collects and analyzes implicit feedback signals.

    Unlike explicit feedback (user ratings), implicit feedback is collected
    automatically from user behavior without prompting.

    Signals indicating tier was TOO STRICT:
    - Skip compliance used
    - Rapid completion (finished much faster than expected)
    - Confirmation skipped quickly
    - Light changes in what was classified as STRICT

    Signals indicating tier was TOO LOOSE:
    - Regression detected after task
    - Force strict used
    - Test failures after task
    - Rollback performed after task
    - Extended completion time (struggled with inadequate process)

    Signals indicating tier was APPROPRIATE:
    - Normal completion time
    - No overrides used
    - No regressions detected
    - Rationale viewed (engaged with the classification)
    """

    # Signal weights for inference
    SIGNAL_WEIGHTS = {
        # TOO_STRICT indicators (negative = too strict)
        ImplicitSignalType.SKIP_COMPLIANCE: -0.8,
        ImplicitSignalType.RAPID_COMPLETION: -0.4,
        ImplicitSignalType.CONFIRMATION_SKIPPED: -0.3,

        # TOO_LOOSE indicators (positive = too loose)
        ImplicitSignalType.REGRESSION_DETECTED: 0.9,
        ImplicitSignalType.FORCE_STRICT: 0.6,
        ImplicitSignalType.TEST_FAILURES: 0.7,
        ImplicitSignalType.ROLLBACK_PERFORMED: 0.9,
        ImplicitSignalType.EXTENDED_COMPLETION: 0.3,
        ImplicitSignalType.IMMEDIATE_RETRY: 0.4,

        # NEUTRAL indicators
        ImplicitSignalType.RATIONALE_VIEWED: 0.0,
        ImplicitSignalType.ALTERNATIVES_VIEWED: 0.0,
    }

    def __init__(self, observability: ObservabilityHooks = None):
        self.observability = observability or OBSERVABILITY
        self.active_signals: Dict[str, ImplicitFeedbackSignals] = {}

    def start_tracking(self, task_id: str, session_id: str) -> ImplicitFeedbackSignals:
        """Start tracking implicit signals for a task."""
        signals = ImplicitFeedbackSignals(task_id=task_id, session_id=session_id)
        self.active_signals[task_id] = signals
        return signals

    def record_signal(
        self,
        task_id: str,
        signal: ImplicitSignalType,
        metadata: Dict = None
    ) -> None:
        """Record an implicit signal for a task."""
        if task_id not in self.active_signals:
            return

        self.active_signals[task_id].add_signal(signal, metadata)

        # Emit observability event
        self.observability.emit(ObservabilityEvent(
            event_type=ObservabilityEventType.FEEDBACK_COLLECTED,
            timestamp=datetime.now(),
            task_id=task_id,
            session_id=self.active_signals[task_id].session_id,
            data={
                "feedback_type": "implicit",
                "signal": signal.value,
                "metadata": metadata
            }
        ))

    def analyze_signals(self, task_id: str, assigned_tier: str) -> ImplicitFeedbackAnalysis:
        """Analyze collected signals to infer tier appropriateness."""
        if task_id not in self.active_signals:
            return ImplicitFeedbackAnalysis(task_id=task_id, assigned_tier=assigned_tier)

        signals = self.active_signals[task_id]
        analysis = ImplicitFeedbackAnalysis(task_id=task_id, assigned_tier=assigned_tier)

        # Calculate weighted score
        weighted_score = 0.0
        for signal in signals.signals:
            weight = self.SIGNAL_WEIGHTS.get(signal, 0.0)
            weighted_score += weight
            if abs(weight) > 0.3:
                analysis.contributing_signals.append(signal)

        # Determine inference
        if weighted_score < -0.5:
            analysis.inferred_too_strict = True
            analysis.inference_confidence = min(1.0, abs(weighted_score))
        elif weighted_score > 0.5:
            analysis.inferred_too_loose = True
            analysis.inference_confidence = min(1.0, weighted_score)
        else:
            analysis.inferred_appropriate = True
            analysis.inference_confidence = 1.0 - abs(weighted_score)

        return analysis

    def complete_tracking(self, task_id: str) -> Optional[ImplicitFeedbackAnalysis]:
        """Complete tracking and return analysis."""
        if task_id not in self.active_signals:
            return None

        signals = self.active_signals[task_id]
        analysis = self.analyze_signals(task_id, signals.metadata.get("assigned_tier", "UNKNOWN"))

        # Store for calibration
        self._store_for_calibration(analysis)

        # Clean up
        del self.active_signals[task_id]

        return analysis

    def _store_for_calibration(self, analysis: ImplicitFeedbackAnalysis) -> None:
        """Store analysis for monthly calibration."""
        # Store in Serena memory
        memory_key = f"implicit_feedback_{analysis.task_id}"
        mcp__serena__write_memory(
            memory_file_name=memory_key,
            content=json.dumps({
                "task_id": analysis.task_id,
                "assigned_tier": analysis.assigned_tier,
                "inferred_too_strict": analysis.inferred_too_strict,
                "inferred_too_loose": analysis.inferred_too_loose,
                "inferred_appropriate": analysis.inferred_appropriate,
                "confidence": analysis.inference_confidence,
                "contributing_signals": [s.value for s in analysis.contributing_signals],
                "timestamp": datetime.now().isoformat()
            })
        )
```

### 5.5 Team Trust Context

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class TeamRole(Enum):
    """Roles within a team context."""
    OWNER = "owner"           # Project owner, highest trust
    MAINTAINER = "maintainer"  # Core team member
    CONTRIBUTOR = "contributor"  # Regular contributor
    REVIEWER = "reviewer"        # Code reviewer only
    OBSERVER = "observer"        # Read-only access

@dataclass
class TeamContext:
    """
    Team-level context for trust and compliance decisions.

    Addresses expert panel concern about individual vs team trust.
    A new team member should inherit some team baseline trust.
    """
    team_id: str
    team_name: str

    # Team-level metrics
    team_success_rate: float = 0.85       # Team's overall success rate
    team_regression_rate: float = 0.05    # Team's regression rate
    team_active_members: int = 1
    team_maturity_score: float = 0.5      # 0-1 based on project history

    # User's role in team
    user_role: TeamRole = TeamRole.CONTRIBUTOR

    # Team norms and overrides
    team_default_tier: Optional[str] = None  # Team can set default tier
    team_require_review: bool = False         # Team requires peer review
    team_critical_paths: List[str] = field(default_factory=list)  # Extra-strict paths

class TeamAwareTrustSystem:
    """
    Trust system that considers both individual and team context.

    Trust Calculation:
    1. Individual trust level (from ProgressiveTrustSystem)
    2. Team baseline trust (new members start with team average * 0.8)
    3. Role-based adjustments (owners/maintainers get expedited trust)
    4. Project maturity influence (mature projects have tighter standards)

    This prevents:
    - New team members being stuck in NOVICE on mature projects
    - Overly strict enforcement on well-established teams
    - Insufficient rigor from high-trust individuals on critical paths
    """

    # Role trust multipliers
    ROLE_MULTIPLIERS = {
        TeamRole.OWNER: 1.2,        # Owners get trust boost
        TeamRole.MAINTAINER: 1.1,   # Maintainers get slight boost
        TeamRole.CONTRIBUTOR: 1.0,  # Contributors use calculated trust
        TeamRole.REVIEWER: 0.9,     # Reviewers get slightly less (read-focused)
        TeamRole.OBSERVER: 0.5,     # Observers get minimal trust
    }

    # Team maturity thresholds
    MATURITY_THRESHOLDS = {
        "startup": (0.0, 0.3),    # New project, looser standards OK
        "growth": (0.3, 0.7),     # Growing project, moderate standards
        "mature": (0.7, 1.0),     # Mature project, tighter standards
    }

    def __init__(self, individual_trust: ProgressiveTrustSystem):
        self.individual_trust = individual_trust

    def calculate_effective_trust(
        self,
        user_id: str,
        team_context: Optional[TeamContext] = None
    ) -> TrustLevel:
        """Calculate effective trust considering team context."""
        # Get individual trust
        individual_level = self.individual_trust.get_user_trust_level(user_id)

        if not team_context:
            return individual_level

        # Calculate team baseline for new members
        if individual_level.name == "NOVICE":
            team_baseline_trust = self._calculate_team_baseline(team_context)
            if team_baseline_trust > 0.5:  # Team has good track record
                return TrustLevel(
                    "TEAM_BASELINE",
                    {
                        "min_tasks": 0,
                        "required_success_rate": team_context.team_success_rate * 0.8,
                        "skip_allowed": team_context.team_success_rate > 0.9,
                        "expedited_tiers": ["LIGHT"] if team_context.team_success_rate > 0.85 else [],
                        "description": f"Team baseline (inherited from {team_context.team_name})"
                    }
                )

        # Apply role multiplier
        role_multiplier = self.ROLE_MULTIPLIERS.get(team_context.user_role, 1.0)

        # Apply maturity adjustment
        maturity_adjustment = self._get_maturity_adjustment(team_context.team_maturity_score)

        # Calculate effective trust
        effective_success_rate = (
            individual_level.config["required_success_rate"] *
            role_multiplier *
            maturity_adjustment
        )

        # Return adjusted trust level
        return self._determine_level_from_rate(effective_success_rate, individual_level)

    def _calculate_team_baseline(self, team_context: TeamContext) -> float:
        """Calculate team baseline trust score."""
        return (
            team_context.team_success_rate * 0.5 +
            (1 - team_context.team_regression_rate) * 0.3 +
            team_context.team_maturity_score * 0.2
        )

    def _get_maturity_adjustment(self, maturity_score: float) -> float:
        """Get trust adjustment based on project maturity."""
        if maturity_score >= 0.7:
            # Mature projects: stricter standards (lower multiplier)
            return 0.9
        elif maturity_score >= 0.3:
            # Growth projects: standard
            return 1.0
        else:
            # Startup projects: more lenient
            return 1.1

    def should_apply_team_critical_path(
        self,
        team_context: TeamContext,
        affected_paths: List[str]
    ) -> bool:
        """Check if any affected path is in team's critical paths."""
        for path in affected_paths:
            for critical in team_context.team_critical_paths:
                if critical in path:
                    return True
        return False

    def get_team_tier_override(
        self,
        team_context: TeamContext,
        detected_tier: str,
        affected_paths: List[str]
    ) -> Optional[str]:
        """Get team-level tier override if applicable."""
        # Critical paths always get STRICT
        if self.should_apply_team_critical_path(team_context, affected_paths):
            return "STRICT"

        # Team default tier (if set and higher than detected)
        if team_context.team_default_tier:
            tier_priority = {"STRICT": 4, "STANDARD": 3, "LIGHT": 2, "EXEMPT": 1}
            if tier_priority.get(team_context.team_default_tier, 0) > tier_priority.get(detected_tier, 0):
                return team_context.team_default_tier

        return None
```

### 5.6 Progressive Trust Model

```python
class ProgressiveTrustSystem:
    """
    Adjusts process overhead based on user's historical accuracy.

    Trust Levels:
    - NOVICE (first 20 tasks): Full process, no skips allowed
    - COMPETENT (80%+ success): Partial skip allowed with justification
    - EXPERT (95%+ success): Auto-skip for LIGHT, expedited STANDARD

    Trust degrades after bugs introduced via skipped process.
    """

    TRUST_LEVELS = {
        "NOVICE": {
            "min_tasks": 0,
            "required_success_rate": 0.0,
            "skip_allowed": False,
            "expedited_tiers": [],
            "description": "Full process, learning mode"
        },
        "COMPETENT": {
            "min_tasks": 20,
            "required_success_rate": 0.80,
            "skip_allowed": True,
            "expedited_tiers": ["LIGHT"],
            "description": "Partial skip with justification"
        },
        "EXPERT": {
            "min_tasks": 50,
            "required_success_rate": 0.95,
            "skip_allowed": True,
            "expedited_tiers": ["LIGHT", "STANDARD"],
            "description": "Auto-skip LIGHT, expedited STANDARD"
        }
    }

    def get_user_trust_level(self, user_id: str) -> TrustLevel:
        """Determine user's current trust level."""
        history = self._get_user_history(user_id)

        if history.total_tasks < 20:
            return TrustLevel("NOVICE", self.TRUST_LEVELS["NOVICE"])

        success_rate = history.successful_tasks / history.total_tasks

        if history.total_tasks >= 50 and success_rate >= 0.95:
            return TrustLevel("EXPERT", self.TRUST_LEVELS["EXPERT"])

        if success_rate >= 0.80:
            return TrustLevel("COMPETENT", self.TRUST_LEVELS["COMPETENT"])

        return TrustLevel("NOVICE", self.TRUST_LEVELS["NOVICE"])

    def record_outcome(self, user_id: str, task_id: str, had_regression: bool) -> None:
        """Record task outcome and update trust level."""
        history = self._get_user_history(user_id)

        history.total_tasks += 1
        if not had_regression:
            history.successful_tasks += 1
        else:
            # Regression degrades trust faster
            history.regression_count += 1
            if history.regression_count >= 3:
                self._demote_trust_level(user_id, history)

        self._save_user_history(user_id, history)

    def _demote_trust_level(self, user_id: str, history: UserHistory) -> None:
        """Demote trust level after repeated regressions."""
        current_level = self.get_user_trust_level(user_id)

        if current_level.name == "EXPERT":
            # Reset success rate calculation
            history.successful_tasks = int(history.total_tasks * 0.85)
        elif current_level.name == "COMPETENT":
            history.successful_tasks = int(history.total_tasks * 0.70)

        # Notify user
        notify_user(f"Trust level adjusted due to regressions. Current level: {current_level.name}")
```

---

## 6. MCP Server Integration

### 6.1 Server Selection Matrix

| Server | Always Active | Conditional Activation | Purpose |
|--------|---------------|----------------------|---------|
| Sequential | Yes | - | Reasoning, analysis, tier classification |
| Context7 | Yes | - | Patterns, best practices, documentation |
| Serena | Yes | - | Memory persistence, project context |
| Playwright | No | STRICT + (UI or E2E tasks) | Browser verification |
| Magic | No | --with-ui flag | UI component generation |
| Morphllm | No | --with-bulk-edit flag | Large-scale transformations |

### 6.2 Conditional Playwright Activation

```python
def should_activate_playwright(
    compliance_tier: str,
    task_context: TaskContext
) -> bool:
    """
    Determine if Playwright MCP should be activated.

    Playwright is needed for STRICT tier verification when:
    - Task involves UI components
    - Task requires E2E validation
    - Task affects user-facing functionality
    """
    if compliance_tier != "STRICT":
        return False

    ui_indicators = [
        "component" in task_context.description.lower(),
        "ui" in task_context.description.lower(),
        "frontend" in task_context.description.lower(),
        any(p.endswith((".jsx", ".tsx", ".vue")) for p in task_context.affected_paths),
        "e2e" in task_context.description.lower(),
        "browser" in task_context.description.lower()
    ]

    return any(ui_indicators)
```

### 6.3 Persona Coordination

```yaml
persona_matrix:
  # Core personas (always available)
  core:
    - architect      # System design, dependencies
    - analyzer       # Root cause, investigation
    - qa             # Quality, verification
    - refactorer     # Code quality, cleanup

  # Domain personas (activated by context)
  domain:
    backend:
      personas: [python-expert, backend-architect]
      triggers: [".py files", "api/", "services/", "backend/"]

    frontend:
      personas: [frontend]
      triggers: [".jsx", ".tsx", ".vue", "components/", "ui/"]
      requires: "--with-ui flag or auto-detection"

    infrastructure:
      personas: [devops]
      triggers: ["Dockerfile", ".yml", "kubernetes/", "terraform/"]
      requires: "--with-infra flag or auto-detection"

    security:
      personas: [security-engineer]
      triggers: ["auth/", "security/", "crypto/", STRICT tier]

  # Verification persona (STRICT tier only)
  verification:
    personas: [quality-engineer]
    triggers: [STRICT compliance tier, CRITICAL verification tier]
```

### 6.4 Tool Coordination

This section defines how `/sc:task` coordinates native Claude Code tools with MCP servers.

| Tool | Purpose | Usage Pattern | Integration Notes |
|------|---------|---------------|-------------------|
| **TodoWrite** | Task tracking and progress | Create tasks at planning, update during execution | Always active; reflects compliance tier requirements |
| **Read** | File inspection | Pre-work analysis, context gathering | Parallel reads for multi-file tasks |
| **Edit/Write** | Code modification | Execute planned changes | Followed by verification in STRICT |
| **Glob** | File discovery | Identify affected files for tier classification | Feeds into scope estimation |
| **Grep** | Pattern search | Find references, dependencies | Informs impact analysis |
| **Bash** | Command execution | Run tests, linters, build commands | Verification phase execution |
| **Task** | Sub-agent delegation | Spawn verification agents, parallel processing | STRICT tier verification |

#### Tool-MCP Coordination Patterns

```yaml
tool_mcp_patterns:
  planning_phase:
    sequence:
      - Glob: "Identify affected files"
      - Read: "Analyze current state (parallel)"
      - Sequential: "Classify tier, plan approach"
      - Context7: "Fetch relevant patterns"
      - Serena: "Load project context from memory"
    parallel_opportunities:
      - Read calls for independent files
      - Context7 + Serena initial loads

  execution_phase:
    sequence:
      - TodoWrite: "Track task start"
      - Edit/Write: "Apply changes"
      - TodoWrite: "Update progress"
    parallel_opportunities:
      - Independent file edits (when no cross-dependencies)

  verification_phase:
    sequence:
      - Bash: "Run tests, linters"
      - Task: "Spawn verification agent (STRICT only)"
      - Playwright: "Browser verification (UI tasks)"
      - Serena: "Persist outcomes to memory"
    parallel_opportunities:
      - Test execution + static analysis
      - Multiple verification sub-agents

  completion_phase:
    sequence:
      - TodoWrite: "Mark complete"
      - Serena: "Store task context and learnings"
      - Sequential: "Generate summary"
```

#### Tier-Specific Tool Usage

| Tier | Required Tools | Optional Tools | Prohibited |
|------|----------------|----------------|------------|
| **STRICT** | TodoWrite, Read, Edit, Bash, Task, Sequential, Serena | Playwright, Magic, Morphllm | None |
| **STANDARD** | TodoWrite, Read, Edit, Bash, Sequential | Context7, Serena | Task (verification agents) |
| **LIGHT** | Read, Edit | TodoWrite, Bash | Task, extensive Grep |
| **EXEMPT** | Read | Any | Heavy tool orchestration |

---

## 7. Examples & Usage Patterns

### 7.1 Typical Usage Scenarios

```bash
# Scenario 1: Multi-file security refactoring
# Auto-detects: strategy=systematic, compliance=STRICT
/sc:task "refactor authentication to use JWT tokens"

# Output:
# Strategy: systematic (multi-file, security domain)
# Compliance: STRICT [██████████] 95%
#   Rationale: Keywords matched: refactor, authentication, tokens
# Verification: CRITICAL (sub-agent)
# Personas: architect, security-engineer, backend-architect
# MCP: Sequential, Context7, Serena, Playwright

# Scenario 2: Single file feature addition
# Auto-detects: strategy=agile, compliance=STANDARD
/sc:task "add input validation to registration form"

# Output:
# Strategy: agile (single component)
# Compliance: STANDARD [████████░░] 78%
#   Rationale: Keywords matched: add, validation
# Verification: STANDARD (direct test)
# Personas: backend-architect, qa

# Scenario 3: Documentation question
# Auto-detects: compliance=EXEMPT
/sc:task "explain how the authentication flow works"

# Output:
# Compliance: EXEMPT [██████████] 92%
#   Rationale: Pattern matched: "explain how"
# Verification: TRIVIAL (skip)
# Proceeding without compliance workflow...

# Scenario 4: Typo fix with explicit tier
/sc:task "fix typo in error message" --compliance light

# Output:
# Compliance: LIGHT (user specified)
# Verification: TRIVIAL (skip)
# Proceeding with light-touch workflow...

# Scenario 5: Override with justification
/sc:task "quick database migration" --compliance strict --reason "Production database"

# Output:
# Compliance: STRICT (user override)
#   Override recorded: "Production database"
# Full STRICT workflow activated...
```

### 7.2 Flag Combinations

```bash
# Enterprise feature with full compliance
/sc:task "implement payment processing" --strategy enterprise --compliance strict --parallel

# Agile iteration with standard compliance
/sc:task "update user profile API" --strategy agile --compliance standard

# Quick exploration (skip compliance)
/sc:task "test different caching strategies" --skip-compliance --reason "Prototype only"

# Force strict for seemingly simple task
/sc:task "update logging format" --force-strict --reason "Affects all services"
```

---

## 8. Migration Guide

### 8.1 From sc:task

```bash
# Old
/sc:task create "feature" --strategy systematic --parallel --delegate

# New (identical - full backward compatibility)
/sc:task create "feature" --strategy systematic --parallel --delegate

# New with compliance (optional enhancement)
/sc:task create "feature" --strategy systematic --compliance strict --parallel
```

### 8.2 From sc:task-mcp

```bash
# Old
/sc:task-mcp "fix tests" --tier strict

# New
/sc:task "fix tests" --compliance strict

# Old
/sc:task-mcp "update config" --tier light

# New
/sc:task "update config" --compliance light

# Old
/sc:task-mcp "change" --skip-mcp

# New
/sc:task "change" --skip-compliance --reason "..."
```

### 8.3 Deprecation Timeline

```yaml
deprecation:
  phase_1:
    duration: "30 days"
    action: "sc:task-mcp shows deprecation warning, continues working"
    message: "DEPRECATED: Use /sc:task --compliance [tier] instead"

  phase_2:
    duration: "60 days"
    action: "sc:task-mcp auto-redirects to sc:task with tier mapping"
    message: "Redirecting to: /sc:task --compliance {tier}"

  phase_3:
    duration: "90 days"
    action: "sc:task-mcp removed"
    message: "Command not found. Use /sc:task --compliance [tier]"
```

---

## 9. Expert Panel Review Anticipation

### 9.1 Karl Wiegers (Requirements) Anticipated Concerns

**Concern**: "How do you validate the 80% accuracy target?"

**Response**:
- User feedback collection after each task (Section 5.1)
- Override tracking measures implicit accuracy (Section 5.2)
- Monthly calibration calculates explicit accuracy (Section 5.3)

**Concern**: "Acceptance criteria for tiers need SMART format"

**Response**: Each tier has explicit acceptance criteria in Section 3.1

### 9.2 Gojko Adzic (Specification by Example) Anticipated Concerns

**Concern**: "Need Given/When/Then scenarios for tier detection"

**Response**: Adding executable examples:

```gherkin
Feature: Tier Classification

  Scenario: Security keyword triggers STRICT
    Given a task description "fix security vulnerability in auth"
    When the classifier analyzes the task
    Then the tier should be STRICT
    And the confidence should be >= 0.9
    And the rationale should mention "security"

  Scenario: Compound phrase overrides keyword
    Given a task description "quick fix for the typo"
    When the classifier analyzes the task
    Then the tier should be LIGHT
    And the rationale should mention "compound phrase 'quick fix'"

  Scenario: Ambiguous task defaults to STANDARD
    Given a task description "make the code better"
    When the classifier analyzes the task
    Then the tier should be STANDARD
    And the confidence should be < 0.7
    And requires_confirmation should be true
```

### 9.3 Martin Fowler (Architecture) Anticipated Concerns

**Concern**: "Separation of concerns between classification and verification"

**Response**:
- `TierClassifier` handles classification only (Section 3.2)
- `VerificationRouter` handles verification routing only (Section 4.2)
- `BatchVerifier` handles execution batching only (Section 4.3)
- Clear interfaces between components

**Concern**: "Extensibility for custom keywords"

**Response**: Adding extension point:

```python
class TierClassifier:
    def __init__(self, custom_keywords: Optional[CustomKeywords] = None):
        self.custom_keywords = custom_keywords or CustomKeywords()
        self._merge_keywords()

    def _merge_keywords(self):
        """Merge custom keywords with defaults."""
        self.STRICT_KEYWORDS = list(set(
            self.STRICT_KEYWORDS +
            self.custom_keywords.strict
        ))
        # ... repeat for other tiers
```

### 9.4 Michael Nygard (Production Systems) Anticipated Concerns

**Concern**: "What happens when verification agent fails?"

**Response**: Adding failure handling:

```python
class VerificationExecutor:
    MAX_RETRIES = 2
    TIMEOUT_SECONDS = 90

    def execute_with_fallback(self, plan: VerificationPlan) -> VerificationResult:
        """Execute verification with retry and fallback."""
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                return self._execute(plan, timeout=self.TIMEOUT_SECONDS)
            except VerificationTimeout:
                if attempt < self.MAX_RETRIES:
                    continue
                return self._fallback_to_manual(plan)
            except SubAgentFailure as e:
                return self._fallback_to_direct_test(plan, error=e)

        return VerificationResult(
            status="fallback",
            message="Verification agent unavailable. Manual verification required.",
            manual_steps=plan.steps
        )
```

### 9.5 Lisa Crispin (Testing) Anticipated Concerns

**Concern**: "How do you test the classification algorithm itself?"

**Response**: Adding comprehensive test strategy with complete golden dataset:

```python
class TierClassifierTests:
    """
    Test suite for tier classification accuracy.

    Test Categories:
    1. Keyword detection (unit tests)
    2. Compound phrase handling (unit tests)
    3. Priority resolution (integration tests)
    4. Confidence scoring (property-based tests)
    5. End-to-end classification (regression tests)
    6. Boundary value tests (edge cases)
    """

    # Golden dataset: 100 tasks with expected classifications
    # Format: (task_description, expected_tier, min_confidence, test_category)
    GOLDEN_DATASET = [
        # === STRICT TIER (25 examples) ===
        # Security domain
        ("fix security vulnerability in auth module", "STRICT", 0.9, "security"),
        ("add authentication to API endpoint", "STRICT", 0.9, "security"),
        ("update password hashing algorithm", "STRICT", 0.9, "security"),
        ("implement OAuth2 authorization flow", "STRICT", 0.9, "security"),
        ("fix JWT token validation bug", "STRICT", 0.85, "security"),
        ("add encryption to user data storage", "STRICT", 0.9, "security"),
        ("update session management logic", "STRICT", 0.85, "security"),

        # Data integrity domain
        ("create database migration for users table", "STRICT", 0.9, "data"),
        ("modify schema to add new column", "STRICT", 0.9, "data"),
        ("refactor model relationships", "STRICT", 0.85, "data"),
        ("update database connection pooling", "STRICT", 0.8, "data"),

        # Scope indicators
        ("refactor entire authentication system", "STRICT", 0.9, "scope"),
        ("fix tests across all modules", "STRICT", 0.85, "scope"),
        ("update API contract for v2 release", "STRICT", 0.9, "scope"),
        ("system-wide logging improvements", "STRICT", 0.85, "scope"),
        ("remediate technical debt in core services", "STRICT", 0.85, "scope"),

        # Exploratory coding
        ("exploratory implementation of new caching strategy", "STRICT", 0.85, "exploratory"),
        ("try this approach for the payment flow", "STRICT", 0.8, "exploratory"),
        ("experiment with different sorting algorithms", "STRICT", 0.8, "exploratory"),

        # API contracts
        ("breaking change to REST API response format", "STRICT", 0.9, "api"),
        ("modify public interface of SDK", "STRICT", 0.9, "api"),

        # Compound phrases that stay STRICT
        ("quick security audit of auth endpoints", "STRICT", 0.9, "compound"),
        ("minor auth flow adjustment", "STRICT", 0.85, "compound"),
        ("simple database migration", "STRICT", 0.85, "compound"),
        ("fix security issue quickly", "STRICT", 0.9, "compound"),

        # === STANDARD TIER (30 examples) ===
        # Creation verbs
        ("add input validation to form", "STANDARD", 0.75, "creation"),
        ("create new utility function for date formatting", "STANDARD", 0.75, "creation"),
        ("implement user profile page", "STANDARD", 0.75, "creation"),
        ("build notification service", "STANDARD", 0.75, "creation"),
        ("develop search functionality", "STANDARD", 0.75, "creation"),

        # Modification verbs
        ("update error handling in API", "STANDARD", 0.75, "modification"),
        ("modify response format for better UX", "STANDARD", 0.75, "modification"),
        ("change button color to match brand", "STANDARD", 0.7, "modification"),
        ("edit configuration for production", "STANDARD", 0.75, "modification"),
        ("adjust rate limiting parameters", "STANDARD", 0.75, "modification"),

        # Fix verbs (non-security)
        ("fix bug in user registration flow", "STANDARD", 0.75, "fix"),
        ("fix null pointer exception in service", "STANDARD", 0.75, "fix"),
        ("fix race condition in async handler", "STANDARD", 0.75, "fix"),
        ("fix memory leak in event listener", "STANDARD", 0.75, "fix"),
        ("fix pagination bug on listing page", "STANDARD", 0.75, "fix"),

        # Removal verbs
        ("remove deprecated API endpoint", "STANDARD", 0.75, "removal"),
        ("delete unused helper functions", "STANDARD", 0.75, "removal"),
        ("clean up old feature flags", "STANDARD", 0.75, "removal"),

        # Single file/component work
        ("add loading spinner to dashboard", "STANDARD", 0.7, "single"),
        ("implement retry logic for HTTP client", "STANDARD", 0.75, "single"),
        ("add caching layer to repository", "STANDARD", 0.75, "single"),
        ("create unit tests for calculator service", "STANDARD", 0.75, "single"),
        ("update logging in payment processor", "STANDARD", 0.75, "single"),

        # Ambiguous but should default to STANDARD
        ("make the code better", "STANDARD", 0.5, "ambiguous"),
        ("improve this function", "STANDARD", 0.6, "ambiguous"),
        ("enhance user experience", "STANDARD", 0.6, "ambiguous"),
        ("optimize query performance", "STANDARD", 0.7, "ambiguous"),
        ("work on the checkout flow", "STANDARD", 0.5, "ambiguous"),
        ("handle the edge case", "STANDARD", 0.6, "ambiguous"),

        # === LIGHT TIER (25 examples) ===
        # Trivial keywords
        ("fix typo in error message", "LIGHT", 0.85, "trivial"),
        ("fix typos throughout readme", "LIGHT", 0.85, "trivial"),
        ("correct spelling in user guide", "LIGHT", 0.85, "trivial"),
        ("fix formatting in config file", "LIGHT", 0.85, "trivial"),
        ("adjust indentation in service.py", "LIGHT", 0.8, "trivial"),

        # Documentation
        ("update comment explaining algorithm", "LIGHT", 0.8, "documentation"),
        ("add comments to complex function", "LIGHT", 0.8, "documentation"),
        ("update docstring for API method", "LIGHT", 0.8, "documentation"),
        ("improve inline documentation", "LIGHT", 0.8, "documentation"),

        # Minimal scope
        ("minor tweak to error message text", "LIGHT", 0.85, "minimal"),
        ("trivial change to log level", "LIGHT", 0.85, "minimal"),
        ("simple rename of internal variable", "LIGHT", 0.85, "minimal"),
        ("small adjustment to timeout value", "LIGHT", 0.8, "minimal"),

        # Cosmetic
        ("rename function to follow convention", "LIGHT", 0.8, "cosmetic"),
        ("fix spacing in template file", "LIGHT", 0.85, "cosmetic"),
        ("remove trailing whitespace", "LIGHT", 0.9, "cosmetic"),
        ("apply lint fixes", "LIGHT", 0.85, "cosmetic"),
        ("fix style issues flagged by linter", "LIGHT", 0.85, "cosmetic"),

        # Compound phrases that trigger LIGHT
        ("quick fix for the display issue", "LIGHT", 0.85, "compound"),
        ("minor change to validation message", "LIGHT", 0.85, "compound"),
        ("small update to help text", "LIGHT", 0.85, "compound"),
        ("simple add of constant value", "LIGHT", 0.8, "compound"),
        ("refactor comment to be clearer", "LIGHT", 0.85, "compound"),
        ("fix formatting only", "LIGHT", 0.9, "compound"),
        ("update comment for clarity", "LIGHT", 0.85, "compound"),

        # === EXEMPT TIER (20 examples) ===
        # Questions
        ("what does this function do", "EXEMPT", 0.9, "question"),
        ("how does the authentication flow work", "EXEMPT", 0.9, "question"),
        ("why is this pattern used here", "EXEMPT", 0.9, "question"),
        ("explain the caching strategy", "EXEMPT", 0.9, "question"),
        ("understand the event system", "EXEMPT", 0.85, "question"),
        ("describe the architecture", "EXEMPT", 0.9, "question"),
        ("show me the API endpoints", "EXEMPT", 0.85, "question"),

        # Exploration
        ("explore the codebase structure", "EXEMPT", 0.85, "exploration"),
        ("investigate the memory usage issue", "EXEMPT", 0.85, "exploration"),
        ("analyze the performance metrics", "EXEMPT", 0.85, "exploration"),
        ("review the current implementation", "EXEMPT", 0.85, "exploration"),
        ("look at the test coverage report", "EXEMPT", 0.85, "exploration"),
        ("check the dependency graph", "EXEMPT", 0.85, "exploration"),

        # Planning
        ("brainstorm solutions for scaling", "EXEMPT", 0.85, "planning"),
        ("plan the migration strategy", "EXEMPT", 0.85, "planning"),
        ("design the new feature architecture", "EXEMPT", 0.85, "planning"),
        ("think about the best approach", "EXEMPT", 0.85, "planning"),
        ("consider different options", "EXEMPT", 0.8, "planning"),

        # Git operations
        ("git status to check changes", "EXEMPT", 0.9, "git"),
        ("git diff to see modifications", "EXEMPT", 0.9, "git"),
        ("git log to review history", "EXEMPT", 0.9, "git"),
    ]

    # === BOUNDARY VALUE TESTS ===
    BOUNDARY_TESTS = [
        # Empty/minimal input
        ("", "STANDARD", 0.3, "boundary_empty"),
        ("x", "STANDARD", 0.3, "boundary_minimal"),

        # Conflicting keywords (STRICT should win per priority)
        ("quick security fix", "STRICT", 0.85, "boundary_conflict"),
        ("minor database change", "STRICT", 0.8, "boundary_conflict"),
        ("simple auth update", "STRICT", 0.85, "boundary_conflict"),

        # Multiple tier keywords (priority resolution)
        ("explain how to refactor the authentication", "EXEMPT", 0.8, "boundary_multi"),
        ("what security improvements should we make", "EXEMPT", 0.85, "boundary_multi"),

        # Near-threshold confidence
        ("update something in the code", "STANDARD", 0.5, "boundary_confidence"),
        ("do the thing", "STANDARD", 0.3, "boundary_confidence"),

        # Very long descriptions
        ("add a new feature that allows users to " * 10, "STANDARD", 0.6, "boundary_long"),

        # Special characters
        ("fix bug #1234 in auth-service", "STANDARD", 0.7, "boundary_special"),
        ("update config.yaml values", "STANDARD", 0.7, "boundary_special"),

        # Case sensitivity
        ("FIX SECURITY VULNERABILITY", "STRICT", 0.9, "boundary_case"),
        ("Fix Typo In README", "LIGHT", 0.85, "boundary_case"),
    ]

    def test_golden_dataset_accuracy(self):
        """Classification must achieve 80% accuracy on golden dataset."""
        classifier = TierClassifier()
        correct = 0
        failures = []

        for task, expected_tier, min_conf, category in self.GOLDEN_DATASET:
            result = classifier.classify(task, MockContext())
            if result.tier == expected_tier:
                correct += 1
            else:
                failures.append({
                    "task": task,
                    "expected": expected_tier,
                    "got": result.tier,
                    "category": category
                })

        accuracy = correct / len(self.GOLDEN_DATASET)
        assert accuracy >= 0.80, f"Accuracy {accuracy:.1%} below 80% target. Failures: {failures}"

    def test_boundary_values(self):
        """Boundary cases must be handled gracefully."""
        classifier = TierClassifier()

        for task, expected_tier, min_conf, category in self.BOUNDARY_TESTS:
            result = classifier.classify(task, MockContext())

            # Boundary tests should not crash
            assert result is not None, f"Null result for boundary case: {task}"

            # Should return valid tier
            assert result.tier in ["STRICT", "STANDARD", "LIGHT", "EXEMPT"]

            # Confidence should be between 0 and 1
            assert 0.0 <= result.confidence <= 1.0

    def test_confidence_boundaries(self):
        """Confidence scores should trigger confirmation at correct thresholds."""
        classifier = TierClassifier()

        # Tasks that should require confirmation (low confidence)
        low_confidence_tasks = [
            "do the thing",
            "update something",
            "work on it"
        ]

        for task in low_confidence_tasks:
            result = classifier.classify(task, MockContext())
            assert result.confidence < 0.7, f"Expected low confidence for: {task}"
            assert result.requires_confirmation, f"Should require confirmation: {task}"

    def test_tier_distribution(self):
        """Golden dataset should have reasonable tier distribution."""
        tier_counts = {"STRICT": 0, "STANDARD": 0, "LIGHT": 0, "EXEMPT": 0}

        for _, expected_tier, _, _ in self.GOLDEN_DATASET:
            tier_counts[expected_tier] += 1

        # Sanity check distribution
        assert tier_counts["STRICT"] >= 20, "Need sufficient STRICT examples"
        assert tier_counts["STANDARD"] >= 25, "Need sufficient STANDARD examples"
        assert tier_counts["LIGHT"] >= 20, "Need sufficient LIGHT examples"
        assert tier_counts["EXEMPT"] >= 15, "Need sufficient EXEMPT examples"
```

### 9.6 Janet Gregory (Agile Testing) Anticipated Concerns

**Concern**: "Need implicit feedback collection, not just explicit prompts"

**Response**: See Section 5.5 for implicit feedback design

---

## 10. Interface Definitions

### 10.1 Protocol Classes (Dependency Injection)

```python
from abc import ABC, abstractmethod
from typing import Protocol, List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# === CORE DATA CLASSES ===

@dataclass
class TaskContext:
    """Context information for task classification."""
    description: str
    affected_paths: List[str] = field(default_factory=list)
    estimated_files: int = 0
    user_trust_level: str = "NOVICE"
    team_context: Optional["TeamContext"] = None
    session_id: Optional[str] = None

@dataclass
class ClassificationResult:
    """Result of tier classification."""
    tier: str                              # STRICT, STANDARD, LIGHT, EXEMPT
    confidence: float                      # 0.0 - 1.0
    rationale: str                         # Human-readable explanation
    alternatives: List[Tuple[str, float]]  # [(tier, score), ...]
    keyword_matches: Dict[str, List[str]]  # {tier: [keywords]}
    requires_confirmation: bool            # True if confidence < 0.7
    original_task: str = ""                # Original task description

@dataclass
class ChangeSet:
    """Set of changes to be verified."""
    affected_paths: List[str]
    change_type: str
    description: str
    diff_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VerificationPlan:
    """Plan for verification execution."""
    tier: str                              # CRITICAL, STANDARD, TRIVIAL
    method: str                            # sub_agent, direct_test, skip
    sub_agent_type: Optional[str] = None
    test_command: Optional[str] = None
    steps: List[str] = field(default_factory=list)
    timeout_seconds: float = 60.0

@dataclass
class VerificationResult:
    """Result of verification execution."""
    status: str                            # passed, failed, timeout, fallback
    message: str = ""
    test_output: Optional[str] = None
    duration_seconds: float = 0.0
    fallback_required: bool = False
    pending_changes: List[ChangeSet] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


# === PROTOCOL INTERFACES ===

class IClassifier(Protocol):
    """Interface for tier classification implementations."""

    def classify(self, task_description: str, context: TaskContext) -> ClassificationResult:
        """Classify task into compliance tier."""
        ...

class IVerificationRouter(Protocol):
    """Interface for verification routing implementations."""

    def route(self, change: ChangeSet, compliance_tier: str) -> VerificationPlan:
        """Route changeset to appropriate verification method."""
        ...

class IBatchVerifier(Protocol):
    """Interface for batch verification implementations."""

    def add_change(self, change: ChangeSet) -> Optional[VerificationResult]:
        """Add change to batch, return result if batch is ready."""
        ...

    async def flush(self) -> VerificationResult:
        """Execute verification for all pending changes."""
        ...

class IFeedbackCollector(Protocol):
    """Interface for feedback collection implementations."""

    def collect_explicit_feedback(
        self, task_id: str, classification: ClassificationResult
    ) -> None:
        """Collect explicit user feedback."""
        ...

    def collect_implicit_feedback(
        self, task_id: str, signals: "ImplicitFeedbackSignals"
    ) -> None:
        """Collect implicit behavioral signals."""
        ...

class ITrustSystem(Protocol):
    """Interface for progressive trust implementations."""

    def get_user_trust_level(self, user_id: str) -> "TrustLevel":
        """Get current trust level for user."""
        ...

    def record_outcome(self, user_id: str, task_id: str, had_regression: bool) -> None:
        """Record task outcome and update trust."""
        ...

class ICircuitBreaker(Protocol):
    """Interface for circuit breaker implementations."""

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        ...

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute call with circuit breaker protection."""
        ...


# === DEPENDENCY INJECTION CONTAINER ===

class TaskCommandContainer:
    """
    Dependency injection container for /sc:task command.

    Allows swapping implementations for testing and customization.
    """

    def __init__(
        self,
        classifier: IClassifier = None,
        verification_router: IVerificationRouter = None,
        batch_verifier: IBatchVerifier = None,
        feedback_collector: IFeedbackCollector = None,
        trust_system: ITrustSystem = None,
        circuit_breakers: Dict[str, ICircuitBreaker] = None
    ):
        self.classifier = classifier or TierClassifier()
        self.verification_router = verification_router or VerificationRouter()
        self.batch_verifier = batch_verifier or BoundedBatchVerifier()
        self.feedback_collector = feedback_collector or TierFeedbackCollector()
        self.trust_system = trust_system or ProgressiveTrustSystem()
        self.circuit_breakers = circuit_breakers or MCP_CIRCUIT_BREAKERS

    @classmethod
    def create_testing_container(cls) -> "TaskCommandContainer":
        """Create container with mock implementations for testing."""
        return cls(
            classifier=MockClassifier(),
            verification_router=MockVerificationRouter(),
            batch_verifier=MockBatchVerifier(),
            feedback_collector=NoOpFeedbackCollector(),
            trust_system=MockTrustSystem()
        )
```

### 10.2 Observability Hooks

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, Any, List, Optional
import logging

class ObservabilityEventType(Enum):
    """Types of observable events in the task workflow."""
    # Classification events
    CLASSIFICATION_START = "classification_start"
    CLASSIFICATION_COMPLETE = "classification_complete"
    CLASSIFICATION_OVERRIDE = "classification_override"

    # Verification events
    VERIFICATION_START = "verification_start"
    VERIFICATION_COMPLETE = "verification_complete"
    VERIFICATION_FAILURE = "verification_failure"
    VERIFICATION_TIMEOUT = "verification_timeout"

    # Circuit breaker events
    CIRCUIT_OPENED = "circuit_opened"
    CIRCUIT_HALF_OPEN = "circuit_half_open"
    CIRCUIT_CLOSED = "circuit_closed"
    CIRCUIT_FALLBACK_USED = "circuit_fallback_used"

    # Feedback events
    FEEDBACK_COLLECTED = "feedback_collected"
    TRUST_LEVEL_CHANGED = "trust_level_changed"

    # Resource events
    BATCH_THRESHOLD_REACHED = "batch_threshold_reached"
    TOKEN_BUDGET_WARNING = "token_budget_warning"
    TIMEOUT_WARNING = "timeout_warning"

@dataclass
class ObservabilityEvent:
    """Event for observability tracking."""
    event_type: ObservabilityEventType
    timestamp: datetime
    task_id: str
    session_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    error: Optional[str] = None

# Type alias for event handlers
EventHandler = Callable[[ObservabilityEvent], None]

class ObservabilityHooks:
    """
    Central observability system for task workflow monitoring.

    Supports:
    - Real-time event streaming
    - Metrics aggregation
    - Structured logging
    - Custom handler registration
    - Prometheus/OpenTelemetry integration points
    """

    def __init__(self):
        self._handlers: Dict[ObservabilityEventType, List[EventHandler]] = {}
        self._metrics: Dict[str, Any] = {}
        self._logger = logging.getLogger("sc_task_observability")

    def register_handler(
        self,
        event_type: ObservabilityEventType,
        handler: EventHandler
    ) -> None:
        """Register handler for specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def emit(self, event: ObservabilityEvent) -> None:
        """Emit event to all registered handlers."""
        # Always log
        self._logger.info(
            f"{event.event_type.value}",
            extra={
                "task_id": event.task_id,
                "session_id": event.session_id,
                "data": event.data,
                "duration_ms": event.duration_ms
            }
        )

        # Update metrics
        self._update_metrics(event)

        # Call registered handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self._logger.error(f"Handler error: {e}")

    def _update_metrics(self, event: ObservabilityEvent) -> None:
        """Update internal metrics based on event."""
        # Counter metrics
        counter_key = f"count_{event.event_type.value}"
        self._metrics[counter_key] = self._metrics.get(counter_key, 0) + 1

        # Duration metrics (histogram-like)
        if event.duration_ms:
            duration_key = f"duration_{event.event_type.value}"
            if duration_key not in self._metrics:
                self._metrics[duration_key] = []
            self._metrics[duration_key].append(event.duration_ms)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        return self._metrics.copy()

    # === CONVENIENCE EMIT METHODS ===

    def emit_classification_start(self, task_id: str, session_id: str, task: str) -> None:
        """Emit classification start event."""
        self.emit(ObservabilityEvent(
            event_type=ObservabilityEventType.CLASSIFICATION_START,
            timestamp=datetime.now(),
            task_id=task_id,
            session_id=session_id,
            data={"task_description": task[:200]}  # Truncate for privacy
        ))

    def emit_classification_complete(
        self,
        task_id: str,
        session_id: str,
        result: ClassificationResult,
        duration_ms: float
    ) -> None:
        """Emit classification complete event."""
        self.emit(ObservabilityEvent(
            event_type=ObservabilityEventType.CLASSIFICATION_COMPLETE,
            timestamp=datetime.now(),
            task_id=task_id,
            session_id=session_id,
            data={
                "tier": result.tier,
                "confidence": result.confidence,
                "requires_confirmation": result.requires_confirmation
            },
            duration_ms=duration_ms
        ))

    def emit_circuit_event(
        self,
        server_name: str,
        new_state: CircuitState,
        session_id: str
    ) -> None:
        """Emit circuit breaker state change event."""
        event_type = {
            CircuitState.OPEN: ObservabilityEventType.CIRCUIT_OPENED,
            CircuitState.HALF_OPEN: ObservabilityEventType.CIRCUIT_HALF_OPEN,
            CircuitState.CLOSED: ObservabilityEventType.CIRCUIT_CLOSED
        }[new_state]

        self.emit(ObservabilityEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            task_id="",
            session_id=session_id,
            data={"server_name": server_name, "new_state": new_state.value}
        ))

# Global observability instance
OBSERVABILITY = ObservabilityHooks()

# === PROMETHEUS INTEGRATION EXAMPLE ===

def setup_prometheus_handlers():
    """Setup Prometheus metrics export handlers."""
    from prometheus_client import Counter, Histogram, Gauge

    classification_counter = Counter(
        'sc_task_classifications_total',
        'Total task classifications',
        ['tier', 'required_confirmation']
    )

    classification_duration = Histogram(
        'sc_task_classification_duration_seconds',
        'Classification duration'
    )

    verification_counter = Counter(
        'sc_task_verifications_total',
        'Total verifications',
        ['tier', 'status']
    )

    circuit_state_gauge = Gauge(
        'sc_task_circuit_state',
        'Circuit breaker state',
        ['server_name']
    )

    def on_classification_complete(event: ObservabilityEvent):
        classification_counter.labels(
            tier=event.data.get('tier', 'unknown'),
            required_confirmation=str(event.data.get('requires_confirmation', False))
        ).inc()
        if event.duration_ms:
            classification_duration.observe(event.duration_ms / 1000)

    def on_circuit_event(event: ObservabilityEvent):
        state_value = {'open': 0, 'half_open': 0.5, 'closed': 1}
        circuit_state_gauge.labels(
            server_name=event.data.get('server_name', 'unknown')
        ).set(state_value.get(event.data.get('new_state', 'closed'), 0))

    OBSERVABILITY.register_handler(
        ObservabilityEventType.CLASSIFICATION_COMPLETE,
        on_classification_complete
    )
    OBSERVABILITY.register_handler(
        ObservabilityEventType.CIRCUIT_OPENED,
        on_circuit_event
    )
    OBSERVABILITY.register_handler(
        ObservabilityEventType.CIRCUIT_CLOSED,
        on_circuit_event
    )
```

---

## 11. Non-Functional Requirements

This section consolidates performance, reliability, and operational requirements scattered throughout the specification.

### 11.1 Performance Requirements

| Requirement | Target | Measurement | Section Reference |
|-------------|--------|-------------|-------------------|
| **Classification Latency** | <500ms | Time from input to tier determination | §3 |
| **STRICT Tier Overhead** | <25% of task time | Additional time for full compliance | §1.4, §3.1 |
| **STANDARD Tier Overhead** | <15% of task time | Additional time for core compliance | §3.1 |
| **LIGHT Tier Overhead** | <5% of task time | Minimal process overhead | §3.1 |
| **EXEMPT Tier Overhead** | 0% | No compliance overhead | §3.1 |
| **Verification Timeout (STRICT)** | 60 seconds | Max verification duration | §3.1, §4.5 |
| **Verification Timeout (STANDARD)** | 30 seconds | Max verification duration | §3.1 |
| **Batch Verification Timeout** | 120 seconds | Total batch processing time | §4.5 |
| **Per-Change Timeout** | 30 seconds | Individual change verification | §4.5 |
| **Sub-Agent Spawn Timeout** | 90 seconds | Verification agent creation | §4.5 |
| **MCP Call Timeout** | 8-30 seconds | Per-server call limits | §4.4 |

### 11.2 Reliability Requirements

| Requirement | Target | Measurement | Section Reference |
|-------------|--------|-------------|-------------------|
| **Tier Classification Accuracy** | ≥80% | User feedback validation | §1.4 |
| **Regression Prevention Rate** | ≥85% | Post-verification bug detection | §1.4 |
| **Circuit Breaker Recovery** | 30-120 seconds | Per-server timeout before retry | §4.4 |
| **Max Consecutive Timeouts** | 2 | Before circuit opens | §4.4 |
| **Failure Threshold** | 3-5 failures | Before circuit opens (per server) | §4.4 |

### 11.3 User Experience Requirements

| Requirement | Target | Measurement | Section Reference |
|-------------|--------|-------------|-------------------|
| **User Confusion Rate** | <10% | "Which command?" questions | §1.4 |
| **Skip Rate** | <12% | Override tracking (--skip-compliance) | §1.4 |
| **Trust Threshold Adjustment** | ±0.1 per validation | Progressive trust building | §5.5 |
| **Context Loading Overhead** | 60% reduction | With memory persistence | §6 |

### 11.4 Resource Constraints

| Resource | Limit | Purpose | Section Reference |
|----------|-------|---------|-------------------|
| **Max Batch Size** | 15 changes | Bounded verification scope | §4.5 |
| **Min Batch Size** | 1 change | Minimum granularity | §4.5 |
| **Max Verification Sub-Agents** | 3 | Parallel verification agents | §4.5 |
| **Max Active Sub-Agents** | 5 | Total concurrent agents | §4.5 |
| **Max Delegated Tasks** | 10 | Concurrent delegated tasks | §4.5 |

---

## 12. Boundaries

This section defines explicit boundaries for `/sc:task` command behavior.

### 12.1 Will

The `/sc:task` command **WILL**:

| Capability | Description | Applicable Tiers |
|------------|-------------|------------------|
| **Classify Tasks** | Automatically determine appropriate compliance tier | All |
| **Enforce Checklists** | Execute pre-work and post-work verification checklists | STRICT, STANDARD |
| **Spawn Verification Agents** | Create sub-agents for independent verification | STRICT |
| **Track Decisions** | Persist task context and decisions to memory | All |
| **Generate Documentation** | Auto-document changes and rationale | STRICT, STANDARD |
| **Coordinate MCP Servers** | Orchestrate Sequential, Context7, Serena, Playwright | All |
| **Escalate Uncertainty** | Escalate to higher tier when classification confidence <0.7 | All |
| **Support Overrides** | Allow tier overrides with required justification | All |
| **Provide Feedback Loops** | Collect implicit/explicit feedback for learning | All |
| **Maintain Context** | Preserve conversation and project context across sessions | All |

### 12.2 Will Not

The `/sc:task` command **WILL NOT**:

| Restriction | Rationale |
|-------------|-----------|
| **Modify Code Without Verification** | STRICT tier requires verification before marking complete |
| **Skip Security Checks** | Security domains always trigger STRICT compliance |
| **Execute Destructive Operations Silently** | Database migrations, deletions require explicit confirmation |
| **Override User Tier Selection Without Consent** | User can always force tier with `--force-strict` or `--skip-compliance` |
| **Store Sensitive Data in Memory** | Passwords, tokens, secrets excluded from persistence |
| **Bypass Circuit Breakers** | MCP server failures respect circuit breaker state |
| **Execute Unbounded Batches** | Max 15 changes per verification batch |
| **Spawn Unlimited Sub-Agents** | Max 3 verification, 5 total active agents |
| **Ignore Timeout Limits** | Hard timeouts prevent runaway processes |
| **Learn from Overridden Decisions** | `--skip-compliance` actions excluded from learning dataset |

### 12.3 Escape Hatches

Users can bypass normal behavior when necessary:

| Escape Hatch | Usage | Requirements |
|--------------|-------|--------------|
| `--skip-compliance` | Bypass all compliance enforcement | Reason automatically logged |
| `--force-strict` | Force STRICT tier regardless of classification | None |
| `--verify skip` | Skip verification phase | Only valid for LIGHT/EXEMPT |
| Manual override | User explicitly requests different tier | `--reason` flag required |

---

## 13. Appendices

### Appendix A: Complete Keyword Lists

```yaml
strict_keywords:
  security:
    - security
    - auth
    - authentication
    - authorization
    - password
    - credential
    - token
    - session
    - encrypt
    - decrypt
    - certificate
    - oauth
    - jwt
    - api key
    - secret

  data_integrity:
    - database
    - migration
    - schema
    - model
    - transaction
    - rollback
    - backup
    - restore

  scope:
    - refactor
    - remediate
    - fix tests
    - multi-file
    - across all
    - throughout
    - system-wide
    - breaking change

  experimentation:
    - exploratory
    - try this
    - experiment

  api:
    - api contract
    - public interface
    - breaking change
    - endpoint

exempt_keywords:
  questions:
    - what
    - how
    - why
    - explain
    - understand
    - describe
    - show me

  exploration:
    - explore
    - investigate
    - analyze
    - review
    - look at
    - check

  planning:
    - brainstorm
    - plan
    - design
    - think about
    - consider

  git:
    - git status
    - git diff
    - git log
    - git branch

light_keywords:
  trivial:
    - typo
    - typos
    - spelling
    - format
    - formatting
    - indent
    - indentation

  documentation:
    - comment
    - comments
    - documentation
    - readme
    - docs

  minimal:
    - minor
    - trivial
    - simple
    - small
    - quick

  cosmetic:
    - rename
    - spacing
    - whitespace
    - lint
    - style

standard_keywords:
  creation:
    - add
    - create
    - implement
    - build
    - develop

  modification:
    - update
    - modify
    - change
    - edit
    - adjust

  removal:
    - fix
    - remove
    - delete
    - clean up
```

### Appendix B: Compound Phrase Matrix

```yaml
compound_phrases:
  light_overrides:
    "quick fix": { overrides: [fix], result: LIGHT }
    "minor change": { overrides: [change], result: LIGHT }
    "small update": { overrides: [update], result: LIGHT }
    "simple add": { overrides: [add], result: LIGHT }
    "fix typo": { overrides: [fix], result: LIGHT }
    "fix comment": { overrides: [fix], result: LIGHT }
    "fix formatting": { overrides: [fix], result: LIGHT }
    "refactor comment": { overrides: [refactor], result: LIGHT }
    "rename variable": { overrides: [], result: LIGHT }
    "update comment": { overrides: [update], result: LIGHT }

  strict_overrides:
    "fix security": { overrides: [fix], result: STRICT }
    "add authentication": { overrides: [add], result: STRICT }
    "add authorization": { overrides: [add], result: STRICT }
    "update database": { overrides: [update], result: STRICT }
    "modify schema": { overrides: [modify], result: STRICT }
    "change api": { overrides: [change], result: STRICT }
    "quick security": { overrides: [], result: STRICT, note: "security always wins" }
    "minor auth": { overrides: [minor], result: STRICT, note: "auth never minor" }
    "simple migration": { overrides: [simple], result: STRICT, note: "migrations never simple" }
```

### Appendix C: Metrics Dashboard Schema

```yaml
metrics_dashboard:
  accuracy_metrics:
    - name: "Classification Accuracy"
      formula: "tasks_rated_appropriate / total_rated_tasks"
      target: "≥80%"
      visualization: "Line chart over time"

    - name: "Override Rate"
      formula: "manual_overrides / total_classifications"
      target: "<20%"
      visualization: "Bar chart by tier"

    - name: "Skip Rate"
      formula: "skip_compliance_uses / total_tasks"
      target: "<12%"
      visualization: "Line chart with warning threshold"

  quality_metrics:
    - name: "Regression Prevention"
      formula: "regressions_caught / (regressions_caught + regressions_missed)"
      target: "≥85%"
      visualization: "Gauge"

    - name: "Verification ROI"
      formula: "(debugging_cost_saved - verification_cost) / verification_cost"
      target: "≥2:1"
      visualization: "Ratio display"

  efficiency_metrics:
    - name: "STRICT Overhead"
      formula: "strict_workflow_time / task_execution_time"
      target: "<25%"
      visualization: "Box plot by task type"

    - name: "Cache Hit Rate"
      formula: "cache_hits / (cache_hits + cache_misses)"
      target: "≥40%"
      visualization: "Pie chart"
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-23 | Claude Code | Initial specification |
| 1.1.0 | 2026-01-23 | Claude Code | Revised based on expert panel feedback: Added SMART criteria for all tiers, complete 100-example golden dataset, circuit breakers, bounded batching, interface definitions, observability hooks, implicit feedback collection, team trust context, boundary value tests |

---

## Approval

### Expert Panel Review Status

| Panel | Verdict | Critical Issues | Status |
|-------|---------|-----------------|--------|
| Wiegers + Adzic (Requirements & Testability) | REVISE | SMART criteria, Golden dataset, NFR section | ✅ ADDRESSED |
| Fowler + Nygard (Architecture & Production) | REVISE | Circuit breakers, Bounded batching, Interfaces, Observability | ✅ ADDRESSED |
| Crispin + Gregory (Testing & Quality) | REVISE | Golden dataset, Implicit feedback, Team trust, Boundary tests | ✅ ADDRESSED |

### Approval Checklist

- [x] Expert Panel Critical Issues Addressed (v1.1.0)
- [ ] Expert Panel Re-Review Complete
- [ ] Implementation Plan Approved
- [ ] Migration Plan Approved
- [ ] Documentation Updated
- [ ] Golden Dataset Validated
- [ ] Interface Contracts Finalized
