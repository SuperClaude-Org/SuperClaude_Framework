"""Unit tests for integration_contracts.py.

Tests cover:
1. 7-category dispatch pattern detection (FR-MOD2.1)
2. Wiring task coverage check (FR-MOD2.3)
3. Mechanism deduplication (FR-MOD2.2)
4. cli-portify regression case SC-003

All tests use real content fixtures, no mocks.
"""

from superclaude.cli.roadmap.integration_contracts import (
    IntegrationAuditResult,
    check_roadmap_coverage,
    extract_integration_contracts,
)

# --- Real content fixtures ---

DISPATCH_TABLE_SPEC = """\
The executor uses a `PROGRAMMATIC_RUNNERS` dispatch table that maps step IDs
to Python callable functions. Each step type has a dedicated runner registered
in the DISPATCH_TABLE.

The HANDLERS dictionary routes command types to their handler functions.
"""

REGISTRY_SPEC = """\
Components register themselves via `plugin_registry.register()`. The system
populates the registry at startup. Each plugin registers its handlers.
"""

CALLBACK_INJECTION_SPEC = """\
The executor accepts a Callable for step processing. The factory
takes a Protocol-compliant argument for dependency injection.
"""

STRATEGY_SPEC = """\
Use the Strategy pattern: `Context(strategy=ConcreteStrategy())`.
The system calls `set_strategy` to configure behavior at runtime.
"""

MIDDLEWARE_SPEC = """\
Configure middleware chain: `app.use(auth_middleware)`.
The pipeline uses `add_middleware` for request processing.
"""

EVENT_BINDING_SPEC = """\
Events are bound via `emitter.on('change', handler)`.
Use `subscribe` for reactive updates and `add_listener` for DOM events.
"""

DI_CONTAINER_SPEC = """\
Dependencies registered with `container.bind(Service, impl)`.
The Injector resolves all Provider instances at startup.
"""

ALL_CATEGORIES_SPEC = (
    DISPATCH_TABLE_SPEC
    + "\n"
    + REGISTRY_SPEC
    + "\n"
    + CALLBACK_INJECTION_SPEC
    + "\n"
    + STRATEGY_SPEC
    + "\n"
    + MIDDLEWARE_SPEC
    + "\n"
    + EVENT_BINDING_SPEC
    + "\n"
    + DI_CONTAINER_SPEC
)

GOOD_ROADMAP = """\
## Phase 1: Setup

Create the dispatch table for step routing.
Populate the PROGRAMMATIC_RUNNERS with all step handlers.
Register implementations into the plugin registry.
Wire handlers into the middleware chain.
Configure the strategy pattern for runtime behavior.
Set up event binding for reactive updates.
Initialize DI container with all dependencies.
"""

BAD_ROADMAP = """\
## Phase 1: Setup

Set up project structure.

## Phase 2: Implementation

Implement the executor with sequential execution.
Add rich output formatting.
"""

CLI_PORTIFY_SPEC = """\
Three-way dispatch: `_run_programmatic_step()`, `_run_claude_step()`, `_run_convergence_step()`

The `PROGRAMMATIC_RUNNERS` dictionary maps step IDs to Python functions:

```python
PROGRAMMATIC_RUNNERS = {
    "validate_config": _run_validate_config,
    "parse_spec": _run_parse_spec,
}
```

Module dependency graph: `executor.py --> steps/validate_config.py`
Integration test: `test_programmatic_step_routing`
"""

CLI_PORTIFY_BAD_ROADMAP = """\
## Phase 1: Foundation

Set up project structure and configuration.

## Phase 2: Executor Shell

Implement executor: sequential execution only, `--dry-run`, `--resume <step-id>`, signal handling.

Milestone M2: Sequential pipeline runs end-to-end with mocked steps.

## Phase 3: CLI Polish

Add rich output formatting and progress display.
"""

# Synthetic fixture per RQ-1 Option A: TUIBBS-scp-inspired prose with shared
# UPPER_SNAKE token `FR-S10-02` in every hub-dispatch context window so
# `_signature_subsumed` fires deterministically (subset+overlap dedup).
TUIBBS_HUB_SPEC = """\
## S10. Message Hub

Goal: Route messages through the hub with strict priority semantics.

Requirements:
- FR-S10-02 specifies the dispatch order.
- The message hub uses class-priority dispatch — Interactive > Coalescible > Bulk.

Interactive messages are processed first, then Coalescible, then Bulk.

The hub dispatch table maps message-class to handler. See FR-S10-02
for the canonical ordering. Interactive class-priority dispatch order
is strict; subsequent classes wait their turn.

For severity-keyed dispatch see the related severity table. FR-S10-02
defines the priority lattice. Severity-keyed dispatch for hub messages
is layered on top of class-priority.

Default class-priority dispatch falls back to Bulk when no overrides
apply. FR-S10-02 governs the fallback semantics. The hub maintains
a single dispatch table keyed by class-priority.
"""

# Roadmap excerpt mimicking TUIBBS-scp v1-MVP roadmap.md hub block.
# Includes Layer 1 (class-priority dispatch), Layer 2 (populate the
# dispatch table — exercises new `populate` impl_verb), and Layer 3
# (FR-S10-02 identifier for overlap-guard) coverage paths.
TUIBBS_HUB_ROADMAP = """\
## Phase 1: Foundation

Set up the project structure.

## Phase 5: Message Hub

Implement the message hub with typed class-priority dispatch.

The executor populates the dispatch table for message routing.

FR-S10-02 messages take priority over later classes.
"""


class TestDispatchPatternDetection:
    """FR-MOD2.1: 7-category dispatch pattern detection."""

    def test_category1_dispatch_table(self):
        contracts = extract_integration_contracts(DISPATCH_TABLE_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "dispatch_table" in mechanisms

    def test_category2_plugin_registry(self):
        contracts = extract_integration_contracts(REGISTRY_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "registry" in mechanisms or "explicit_wiring" in mechanisms

    def test_category3_callback_injection(self):
        contracts = extract_integration_contracts(CALLBACK_INJECTION_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "dependency_injection" in mechanisms

    def test_category4_strategy_pattern(self):
        contracts = extract_integration_contracts(STRATEGY_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "strategy_pattern" in mechanisms

    def test_category5_middleware_chain(self):
        contracts = extract_integration_contracts(MIDDLEWARE_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "middleware_chain" in mechanisms

    def test_category6_event_binding(self):
        contracts = extract_integration_contracts(EVENT_BINDING_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "event_binding" in mechanisms

    def test_category7_di_container(self):
        contracts = extract_integration_contracts(DI_CONTAINER_SPEC)
        assert len(contracts) >= 1
        mechanisms = {c.mechanism for c in contracts}
        assert "di_container" in mechanisms or "dependency_injection" in mechanisms

    def test_all_categories_detected(self):
        contracts = extract_integration_contracts(ALL_CATEGORIES_SPEC)
        mechanisms = {c.mechanism for c in contracts}
        # Should detect at least 4 distinct mechanism types
        assert len(mechanisms) >= 4


class TestWiringCoverage:
    """FR-MOD2.3, FR-MOD2.5: Wiring task coverage check."""

    def test_covered_roadmap_passes(self):
        contracts = extract_integration_contracts(DISPATCH_TABLE_SPEC)
        result = check_roadmap_coverage(contracts, GOOD_ROADMAP)
        assert result.all_covered
        assert result.uncovered_count == 0

    def test_uncovered_roadmap_fails(self):
        contracts = extract_integration_contracts(DISPATCH_TABLE_SPEC)
        result = check_roadmap_coverage(contracts, BAD_ROADMAP)
        assert not result.all_covered
        assert result.uncovered_count > 0

    def test_empty_contracts_passes(self):
        result = check_roadmap_coverage([], BAD_ROADMAP)
        assert result.all_covered
        assert result.total_count == 0

    def test_coverage_evidence_recorded(self):
        contracts = extract_integration_contracts(DISPATCH_TABLE_SPEC)
        result = check_roadmap_coverage(contracts, GOOD_ROADMAP)
        covered = [c for c in result.coverage if c.covered]
        for c in covered:
            assert c.roadmap_evidence != ""
            assert c.roadmap_location != ""


class TestDeduplication:
    """FR-MOD2.2: Deduplication by evidence."""

    def test_duplicate_lines_deduplicated(self):
        spec = """\
The DISPATCH_TABLE maps steps.
The DISPATCH_TABLE maps steps.
The DISPATCH_TABLE maps steps.
"""
        contracts = extract_integration_contracts(spec)
        # Should have only 1 contract despite 3 identical lines
        assert len(contracts) == 1

    def test_sequential_id_assignment(self):
        contracts = extract_integration_contracts(ALL_CATEGORIES_SPEC)
        for i, c in enumerate(contracts):
            assert c.id == f"IC-{i + 1:03d}"


class TestNamedMechanismMatching:
    """FR-MOD2.4: Named mechanism identifier matching."""

    def test_upper_snake_case_detected(self):
        contracts = extract_integration_contracts(CLI_PORTIFY_SPEC)
        evidence_text = " ".join(c.spec_evidence for c in contracts)
        assert "PROGRAMMATIC_RUNNERS" in evidence_text

    def test_named_mechanism_in_roadmap_coverage(self):
        contracts = extract_integration_contracts(CLI_PORTIFY_SPEC)
        roadmap_with_name = "## Phase 1\nPopulate PROGRAMMATIC_RUNNERS dict."
        result = check_roadmap_coverage(contracts, roadmap_with_name)
        assert result.all_covered


class TestCliPortifyRegression:
    """SC-003: Detects PROGRAMMATIC_RUNNERS without wiring task at >= 90%."""

    def test_detects_programmatic_runners_without_wiring(self):
        contracts = extract_integration_contracts(CLI_PORTIFY_SPEC)
        result = check_roadmap_coverage(contracts, CLI_PORTIFY_BAD_ROADMAP)
        assert not result.all_covered
        assert result.uncovered_count >= 1
        # Verify PROGRAMMATIC_RUNNERS specifically is uncovered
        uncovered = [c for c in result.coverage if not c.covered]
        uncovered_evidence = " ".join(c.contract.spec_evidence for c in uncovered)
        assert "PROGRAMMATIC_RUNNERS" in uncovered_evidence

    def test_total_contracts_detected(self):
        contracts = extract_integration_contracts(CLI_PORTIFY_SPEC)
        assert len(contracts) >= 1


class TestIntegrationAuditResult:
    """FR-MOD2.6: IntegrationAuditResult properties."""

    def test_all_covered_true_when_zero_uncovered(self):
        result = IntegrationAuditResult(uncovered_count=0, total_count=3)
        assert result.all_covered

    def test_all_covered_false_when_uncovered(self):
        result = IntegrationAuditResult(uncovered_count=1, total_count=3)
        assert not result.all_covered

    def test_empty_result_is_covered(self):
        result = IntegrationAuditResult()
        assert result.all_covered


class TestHubDispatchRegression:
    """Anti-instinct gate must produce 1 hub-dispatch contract, not 4, AND must find it covered in the roadmap."""

    def test_t1_one_contract_per_hub_mechanism(self):
        """4 epic lines mentioning hub dispatch → 1 IntegrationContract."""
        contracts = extract_integration_contracts(TUIBBS_HUB_SPEC)
        hub_contracts = [
            c for c in contracts
            if c.mechanism == "dispatch_table"
            and "FR-S10-02" in c.spec_evidence
        ]
        assert len(hub_contracts) == 1

    def test_t2_class_priority_dispatch_covers_hub(self):
        """Roadmap phrase 'class-priority dispatch' covers hub contract."""
        contracts = extract_integration_contracts(TUIBBS_HUB_SPEC)
        result = check_roadmap_coverage(contracts, TUIBBS_HUB_ROADMAP)
        assert result.uncovered_count == 0

    def test_t3_prose_dispatch_not_extracted_alone(self):
        """'priority dispatch cannot be undermined' in isolation yields ≤1 contract."""
        prose = "So that priority dispatch cannot be undermined by mis-tagged messages."
        contracts = extract_integration_contracts(prose)
        assert len(contracts) <= 1

    def test_t4_existing_dispatch_table_test_still_passes(self):
        """DISPATCH_TABLE_SPEC still yields a dispatch_table contract."""
        contracts = extract_integration_contracts(DISPATCH_TABLE_SPEC)
        assert any(c.mechanism == "dispatch_table" for c in contracts)

    def test_t5_cli_portify_regression_still_blocks(self):
        """SC-003 regression: PROGRAMMATIC_RUNNERS without wiring still uncovered."""
        contracts = extract_integration_contracts(CLI_PORTIFY_SPEC)
        result = check_roadmap_coverage(contracts, CLI_PORTIFY_BAD_ROADMAP)
        assert result.uncovered_count >= 1

    def test_t6_stem_fallback_with_ident_overlap_covers(self):
        """Roadmap with 'Implement ... class-priority dispatch' + FR-S10-02 in window covers hub contract."""
        spec = (
            "The hub uses class-priority dispatch — FR-S10-02 is the relevant requirement.\n"
            "Default dispatch order is strict.\n"
        )
        roadmap = (
            "## M5\n"
            "Implement the message hub with typed class-priority dispatch.\n"
            "FR-S10-02 messages take priority over others.\n"
        )
        contracts = extract_integration_contracts(spec)
        result = check_roadmap_coverage(contracts, roadmap)
        assert result.uncovered_count == 0

    def test_t7_stem_fallback_without_ident_overlap_uncovers(self):
        """'Implement priority dispatch for logging' must NOT cover hub contract because no identifier overlap with the contract's signature."""
        spec = (
            "The hub uses class-priority dispatch — FR-S10-02 is the relevant requirement.\n"
        )
        roadmap = (
            "## M5\n"
            "Implement priority dispatch for logging events.\n"
            "Configure debug log levels and rotation.\n"
        )
        contracts = extract_integration_contracts(spec)
        result = check_roadmap_coverage(contracts, roadmap)
        # No FR-S10-02 in the roadmap → stem-fallback identifier-overlap guard rejects the match → contract uncovered.
        assert result.uncovered_count >= 1
