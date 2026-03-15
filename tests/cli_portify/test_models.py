"""Unit tests for v2.24.1 model additions.

Covers:
- TargetInputType enum membership (5 values)
- ResolvedTarget construction
- CommandEntry/SkillEntry/AgentEntry tier assignments
- ComponentTree computed properties
- to_flat_inventory() round-trip (Path -> str boundary)
- to_manifest_markdown() output
- Error code constant values
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.models import (
    AgentEntry,
    AmbiguousPathError,
    CommandEntry,
    ComponentEntry,
    ComponentInventory,
    ComponentTree,
    ConvergenceState,
    DerivationFailedError,
    ERR_AMBIGUOUS_TARGET,
    ERR_BROKEN_ACTIVATION,
    ERR_TARGET_NOT_FOUND,
    InvalidPathError,
    MonitorState,
    NameCollisionError,
    OutputNotWritableError,
    PortifyOutcome,
    PortifyPhaseType,
    PortifyStep,
    PortifyStatus,
    PortifyValidationError,
    AMBIGUOUS_PATH,
    DERIVATION_FAILED,
    INVALID_PATH,
    NAME_COLLISION,
    OUTPUT_NOT_WRITABLE,
    ResolvedTarget,
    SkillEntry,
    TargetInputType,
    TurnLedger,
    WARN_MISSING_AGENTS,
)


# --- TargetInputType Enum ---


class TestTargetInputType:
    """Verify TargetInputType enum has exactly 5 spec-defined members."""

    @pytest.mark.parametrize(
        "member",
        ["COMMAND_NAME", "COMMAND_PATH", "SKILL_DIR", "SKILL_NAME", "SKILL_FILE"],
    )
    def test_enum_has_member(self, member: str) -> None:
        assert hasattr(TargetInputType, member)

    def test_enum_has_exactly_five_members(self) -> None:
        assert len(TargetInputType) == 5

    def test_enum_values_are_strings(self) -> None:
        for member in TargetInputType:
            assert isinstance(member.value, str)


# --- ResolvedTarget Dataclass ---


class TestResolvedTarget:
    """Verify ResolvedTarget construction and field types."""

    def test_construction_with_required_fields(self) -> None:
        rt = ResolvedTarget(
            input_form="roadmap",
            input_type=TargetInputType.COMMAND_NAME,
        )
        assert rt.input_form == "roadmap"
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path is None
        assert rt.skill_dir is None

    def test_construction_with_all_fields(self) -> None:
        rt = ResolvedTarget(
            input_form="roadmap",
            input_type=TargetInputType.COMMAND_NAME,
            command_path=Path("/tmp/roadmap.md"),
            skill_dir=Path("/tmp/sc-roadmap-protocol"),
            project_root=Path("/tmp"),
            commands_dir=Path("/tmp/commands"),
            skills_dir=Path("/tmp/skills"),
            agents_dir=Path("/tmp/agents"),
        )
        assert rt.command_path == Path("/tmp/roadmap.md")
        assert rt.agents_dir == Path("/tmp/agents")

    def test_has_eight_fields(self) -> None:
        assert len(ResolvedTarget.__dataclass_fields__) == 8


# --- Tiered Component Entries ---


class TestTieredEntries:
    """Verify CommandEntry, SkillEntry, AgentEntry tier assignments."""

    def test_command_entry_tier(self) -> None:
        assert CommandEntry().tier == 0

    def test_skill_entry_tier(self) -> None:
        assert SkillEntry().tier == 1

    def test_agent_entry_tier(self) -> None:
        assert AgentEntry().tier == 2


# --- ComponentTree ---


class TestComponentTree:
    """Verify ComponentTree computed properties."""

    def test_empty_tree(self) -> None:
        ct = ComponentTree()
        assert ct.component_count == 0
        assert ct.total_lines == 0
        assert ct.all_source_dirs == []

    def test_full_tree(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(
                name="roadmap",
                line_count=50,
                source_dir=Path("/commands"),
            ),
            skill=SkillEntry(
                name="sc-roadmap-protocol",
                line_count=200,
                source_dir=Path("/skills"),
            ),
            agents=[
                AgentEntry(name="architect", line_count=30, source_dir=Path("/agents")),
                AgentEntry(name="qa", line_count=20, source_dir=Path("/agents")),
            ],
        )
        assert ct.component_count == 4
        assert ct.total_lines == 300
        assert len(ct.all_source_dirs) == 3

    def test_all_source_dirs_deduplicates(self) -> None:
        shared = Path("/shared")
        ct = ComponentTree(
            command=CommandEntry(source_dir=shared),
            skill=SkillEntry(source_dir=shared),
        )
        assert ct.all_source_dirs == [shared]

    def test_command_only_tree(self) -> None:
        ct = ComponentTree(command=CommandEntry(name="solo", line_count=10))
        assert ct.component_count == 1
        assert ct.total_lines == 10

    def test_skill_only_tree(self) -> None:
        ct = ComponentTree(skill=SkillEntry(name="solo-skill", line_count=25))
        assert ct.component_count == 1
        assert ct.total_lines == 25


# --- to_flat_inventory() Round-trip ---


class TestToFlatInventory:
    """Verify ComponentTree -> ComponentInventory conversion."""

    def test_roundtrip_field_equivalence(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(
                name="roadmap",
                path=Path("/tmp/roadmap.md"),
                line_count=50,
            ),
            skill=SkillEntry(
                name="sc-roadmap-protocol",
                path=Path("/tmp/sc-roadmap-protocol"),
                line_count=200,
            ),
        )
        inv = ct.to_flat_inventory()
        assert isinstance(inv, ComponentInventory)
        assert inv.component_count == 2
        assert inv.source_skill == "sc-roadmap-protocol"

    def test_no_path_leakage(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(path=Path("/tmp/cmd.md"), line_count=10),
        )
        inv = ct.to_flat_inventory()
        for comp in inv.components:
            assert isinstance(comp.path, str), f"Path leakage: {type(comp.path)}"
            assert isinstance(comp.name, str)

    def test_empty_tree_inventory(self) -> None:
        ct = ComponentTree()
        inv = ct.to_flat_inventory()
        assert inv.component_count == 0
        assert inv.source_skill == ""

    def test_agents_included(self) -> None:
        ct = ComponentTree(
            agents=[
                AgentEntry(name="a1", path=Path("/tmp/a1.md"), line_count=10),
                AgentEntry(name="a2", path=Path("/tmp/a2.md"), line_count=20),
            ],
        )
        inv = ct.to_flat_inventory()
        assert inv.component_count == 2
        agent_types = [c.component_type for c in inv.components]
        assert all(t == "agent" for t in agent_types)


# --- to_manifest_markdown() ---


class TestToManifestMarkdown:
    """Verify Markdown manifest output."""

    def test_has_yaml_frontmatter(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(name="roadmap", line_count=50),
            skill=SkillEntry(name="sc-roadmap-protocol", line_count=200),
        )
        md = ct.to_manifest_markdown()
        assert md.startswith("---\n")
        assert "source_command: roadmap" in md
        assert "source_skill: sc-roadmap-protocol" in md
        assert "component_count: 2" in md

    def test_empty_tree_manifest(self) -> None:
        md = ComponentTree().to_manifest_markdown()
        assert "No components discovered." in md


# --- Error Code Constants ---


class TestErrorConstants:
    """Verify exact string values of all 4 error code constants."""

    def test_err_target_not_found(self) -> None:
        assert ERR_TARGET_NOT_FOUND == "ERR_TARGET_NOT_FOUND"

    def test_err_ambiguous_target(self) -> None:
        assert ERR_AMBIGUOUS_TARGET == "ERR_AMBIGUOUS_TARGET"

    def test_err_broken_activation(self) -> None:
        assert ERR_BROKEN_ACTIVATION == "ERR_BROKEN_ACTIVATION"

    def test_warn_missing_agents(self) -> None:
        assert WARN_MISSING_AGENTS == "WARN_MISSING_AGENTS"


# ---------------------------------------------------------------------------
# T02.07 acceptance criteria: test_error_codes
# ---------------------------------------------------------------------------


class TestErrorCodes:
    """T02.07 — All 5 Phase 2 error codes defined, importable, and raiseable.

    These tests satisfy the validation command:
        uv run pytest tests/ -k "test_error_codes"
    """

    def test_error_codes_name_collision_constant(self) -> None:
        """NAME_COLLISION constant has correct string value."""
        assert NAME_COLLISION == "NAME_COLLISION"

    def test_error_codes_output_not_writable_constant(self) -> None:
        """OUTPUT_NOT_WRITABLE constant has correct string value."""
        assert OUTPUT_NOT_WRITABLE == "OUTPUT_NOT_WRITABLE"

    def test_error_codes_ambiguous_path_constant(self) -> None:
        """AMBIGUOUS_PATH constant has correct string value."""
        assert AMBIGUOUS_PATH == "AMBIGUOUS_PATH"

    def test_error_codes_invalid_path_constant(self) -> None:
        """INVALID_PATH constant has correct string value."""
        assert INVALID_PATH == "INVALID_PATH"

    def test_error_codes_derivation_failed_constant(self) -> None:
        """DERIVATION_FAILED constant has correct string value."""
        assert DERIVATION_FAILED == "DERIVATION_FAILED"

    def test_error_codes_all_five_are_importable(self) -> None:
        """All 5 error codes are importable from models.py."""
        codes = [NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED]
        assert len(codes) == 5
        assert all(isinstance(c, str) for c in codes)

    def test_error_codes_name_collision_raises(self) -> None:
        """NameCollisionError is a PortifyValidationError with NAME_COLLISION code."""
        with pytest.raises(PortifyValidationError) as exc_info:
            raise NameCollisionError("my-module")
        assert exc_info.value.error_code == NAME_COLLISION

    def test_error_codes_output_not_writable_raises(self) -> None:
        """OutputNotWritableError is a PortifyValidationError with OUTPUT_NOT_WRITABLE code."""
        with pytest.raises(PortifyValidationError) as exc_info:
            raise OutputNotWritableError("/some/path")
        assert exc_info.value.error_code == OUTPUT_NOT_WRITABLE

    def test_error_codes_ambiguous_path_raises(self) -> None:
        """AmbiguousPathError is a PortifyValidationError with AMBIGUOUS_PATH code."""
        with pytest.raises(PortifyValidationError) as exc_info:
            raise AmbiguousPathError("my-skill", ["skill-a", "skill-b"])
        assert exc_info.value.error_code == AMBIGUOUS_PATH

    def test_error_codes_invalid_path_raises(self) -> None:
        """InvalidPathError is a PortifyValidationError with INVALID_PATH code."""
        with pytest.raises(PortifyValidationError) as exc_info:
            raise InvalidPathError("/not/a/skill")
        assert exc_info.value.error_code == INVALID_PATH

    def test_error_codes_derivation_failed_raises(self) -> None:
        """DerivationFailedError is a PortifyValidationError with DERIVATION_FAILED code."""
        with pytest.raises(PortifyValidationError) as exc_info:
            raise DerivationFailedError("---")
        assert exc_info.value.error_code == DERIVATION_FAILED

    def test_error_codes_all_are_subclasses_of_base(self) -> None:
        """All 5 error exception classes are subclasses of PortifyValidationError."""
        assert issubclass(NameCollisionError, PortifyValidationError)
        assert issubclass(OutputNotWritableError, PortifyValidationError)
        assert issubclass(AmbiguousPathError, PortifyValidationError)
        assert issubclass(InvalidPathError, PortifyValidationError)
        assert issubclass(DerivationFailedError, PortifyValidationError)

    def test_error_codes_caught_as_base_exception(self) -> None:
        """Any error code exception can be caught via the base PortifyValidationError."""
        for exc_cls, args in [
            (NameCollisionError, ("test",)),
            (OutputNotWritableError, ("/path",)),
            (AmbiguousPathError, ("x", ["a", "b"])),
            (InvalidPathError, ("/path",)),
            (DerivationFailedError, ("name",)),
        ]:
            with pytest.raises(PortifyValidationError):
                raise exc_cls(*args)


# ---------------------------------------------------------------------------
# T03.01 acceptance criteria: test_domain_models
# ---------------------------------------------------------------------------


class TestDomainModels:
    """T03.01 — All 9 domain models defined and importable.

    Validation command: uv run pytest tests/ -k "test_domain_models"
    """

    def test_domain_models_portify_phase_type_enum_exists(self) -> None:
        assert issubclass(PortifyPhaseType, type(PortifyPhaseType.PREREQUISITES).__mro__[0])

    def test_domain_models_portify_phase_type_members(self) -> None:
        expected = {"PREREQUISITES", "ANALYSIS", "USER_REVIEW", "SPECIFICATION", "SYNTHESIS", "CONVERGENCE"}
        actual = {m.name for m in PortifyPhaseType}
        assert actual == expected

    def test_domain_models_convergence_state_enum_exists(self) -> None:
        assert issubclass(ConvergenceState, type(ConvergenceState.NOT_STARTED).__mro__[0])

    def test_domain_models_convergence_state_members(self) -> None:
        expected = {"NOT_STARTED", "REVIEWING", "INCORPORATING", "SCORING", "CONVERGED", "ESCALATED"}
        actual = {m.name for m in ConvergenceState}
        assert actual == expected

    def test_domain_models_portify_outcome_enum_members(self) -> None:
        expected = {"SUCCESS", "FAILURE", "TIMEOUT", "INTERRUPTED", "HALTED", "DRY_RUN"}
        actual = {m.name for m in PortifyOutcome}
        assert actual == expected

    def test_domain_models_portify_step_instantiates(self) -> None:
        step = PortifyStep(step_id="s1", phase_type=PortifyPhaseType.ANALYSIS)
        assert step.step_id == "s1"
        assert step.phase_type == PortifyPhaseType.ANALYSIS
        assert step.status == PortifyStatus.PENDING

    def test_domain_models_portify_step_default_status_pending(self) -> None:
        step = PortifyStep()
        assert step.status == PortifyStatus.PENDING

    def test_domain_models_monitor_state_instantiates(self) -> None:
        ms = MonitorState()
        assert ms.output_bytes == 0
        assert ms.growth_rate_bps == 0.0
        assert ms.stall_seconds == 0.0
        assert ms.events == 0
        assert ms.line_count == 0
        assert ms.convergence_iteration == 0
        assert ms.findings_count == 0
        assert ms.placeholder_count == 0

    def test_domain_models_monitor_state_has_all_fields(self) -> None:
        fields = set(MonitorState.__dataclass_fields__.keys())
        expected = {
            "output_bytes", "growth_rate_bps", "stall_seconds", "events",
            "line_count", "convergence_iteration", "findings_count", "placeholder_count",
        }
        assert expected.issubset(fields)

    def test_domain_models_turn_ledger_instantiates(self) -> None:
        ledger = TurnLedger(total_budget=10)
        assert ledger.total_budget == 10
        assert ledger.consumed == 0
        assert ledger.remaining == 10

    def test_domain_models_turn_ledger_can_launch_true(self) -> None:
        ledger = TurnLedger(total_budget=5)
        assert ledger.can_launch() is True

    def test_domain_models_turn_ledger_can_launch_false_when_exhausted(self) -> None:
        ledger = TurnLedger(total_budget=2)
        ledger.consume(2)
        assert ledger.can_launch() is False

    def test_domain_models_nine_models_importable(self) -> None:
        """All 9 domain models are importable."""
        from superclaude.cli.cli_portify.models import PortifyConfig, PortifyStepResult
        models = [
            PortifyPhaseType, ConvergenceState, PortifyConfig, PortifyStep,
            PortifyStepResult, PortifyOutcome, PortifyStatus, MonitorState, TurnLedger,
        ]
        assert len(models) == 9
        for m in models:
            assert m is not None


# ---------------------------------------------------------------------------
# T03.03 acceptance criteria: test_step_order
# ---------------------------------------------------------------------------


class TestStepOrder:
    """T03.03 — Step registration in mandated order (NFR-006, AC-012).

    Validation command: uv run pytest tests/ -k "test_step_order"
    """

    def test_step_order_mandated_sequence(self) -> None:
        """MANDATED_STEP_ORDER matches the exact 13-step mandated sequence."""
        from superclaude.cli.cli_portify.registry import MANDATED_STEP_ORDER
        expected = [
            "models", "gates", "prompts", "config", "inventory", "monitor",
            "process", "executor", "tui", "logging_", "diagnostics", "commands", "__init__",
        ]
        assert list(MANDATED_STEP_ORDER) == expected

    def test_step_order_is_immutable_tuple(self) -> None:
        """MANDATED_STEP_ORDER is a tuple (immutable at runtime)."""
        from superclaude.cli.cli_portify.registry import MANDATED_STEP_ORDER
        assert isinstance(MANDATED_STEP_ORDER, tuple)

    def test_step_order_has_thirteen_entries(self) -> None:
        from superclaude.cli.cli_portify.registry import MANDATED_STEP_ORDER
        assert len(MANDATED_STEP_ORDER) == 13

    def test_step_order_get_step_order_returns_tuple(self) -> None:
        from superclaude.cli.cli_portify.registry import get_step_order
        order = get_step_order()
        assert isinstance(order, tuple)
        assert len(order) == 13

    def test_step_order_assert_step_order_passes_on_correct_order(self) -> None:
        from superclaude.cli.cli_portify.registry import assert_step_order, MANDATED_STEP_ORDER
        assert_step_order(list(MANDATED_STEP_ORDER))  # should not raise

    def test_step_order_assert_step_order_fails_on_wrong_order(self) -> None:
        from superclaude.cli.cli_portify.registry import assert_step_order
        with pytest.raises(AssertionError):
            assert_step_order(["executor", "models"])  # wrong order

    def test_step_order_models_is_first(self) -> None:
        from superclaude.cli.cli_portify.registry import MANDATED_STEP_ORDER
        assert MANDATED_STEP_ORDER[0] == "models"

    def test_step_order_init_is_last(self) -> None:
        from superclaude.cli.cli_portify.registry import MANDATED_STEP_ORDER
        assert MANDATED_STEP_ORDER[-1] == "__init__"
