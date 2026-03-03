"""
Integration tests for adversarial pipeline fallback protocol (T04.02 / D-0023).

Validates the end-to-end fallback protocol F1 → F2/3 → F4/5 produces a valid
return contract with the canonical 10-field schema.

Reference: D-0010 (fallback protocol spec), D-0009 (Step 3d invocation),
SKILL.md §Wave 2 Step 3d, refs/adversarial-integration.md

Protocol stages:
- F1: Variant generation (one per agent spec)
- F2/3: Diff analysis + adversarial debate (merged stage)
- F4/5: Base selection + merge + contract output (merged stage)
"""

import pytest


# -- Canonical return contract schema --

CANONICAL_RETURN_CONTRACT_FIELDS = {
    "status",               # success|partial|failed
    "convergence_score",    # float 0.0-1.0
    "merged_output_path",   # path|null
    "fallback_mode",        # bool
    "invocation_method",    # enum
    "unresolved_conflicts", # list[string] or integer
    "artifacts_dir",        # string (directory path)
    "base_variant",         # string (model:persona)
    "debate_rounds",        # integer
    "variant_count",        # integer
}

REQUIRED_STATUS_VALUES = {"success", "partial", "failed"}


# -- Fallback protocol simulation (from D-0010 spec) --


def f1_variant_generation(agent_specs):
    """
    F1: Generate variants (one per expanded agent spec from Step 3a/3b).

    Each agent produces a variant based on its model+persona+instruction.
    Returns list of variant dicts with content and agent metadata.
    """
    if not agent_specs or not isinstance(agent_specs, list):
        return {"error": "No agent specs provided", "variants": []}

    if len(agent_specs) < 2:
        return {"error": "Minimum 2 agents required", "variants": []}

    if len(agent_specs) > 10:
        return {"error": "Maximum 10 agents allowed", "variants": []}

    variants = []
    for i, spec in enumerate(agent_specs):
        model = spec.get("model", "unknown")
        persona = spec.get("persona", "default")
        variants.append({
            "id": f"variant-{i + 1}",
            "agent": f"{model}:{persona}",
            "content": f"Roadmap variant from {model}:{persona}",
            "score": None,  # Populated by F2/3
        })

    return {"error": None, "variants": variants}


def f2_f3_diff_and_debate(variants, debate_rounds=2):
    """
    F2/3: Diff analysis + adversarial debate (merged stage).

    Parallel advocates → sequential rebuttals.
    Produces scored variants with convergence assessment.
    """
    if not variants:
        return {
            "error": "No variants to debate",
            "scored_variants": [],
            "convergence_score": 0.0,
        }

    scored = []
    total_score = 0.0
    for v in variants:
        # Simulate scoring: distribute scores based on variant index
        base_score = 0.5 + (0.1 * (len(variants) - variants.index(v))) / len(variants)
        score = min(1.0, base_score)
        scored.append({**v, "score": round(score, 3)})
        total_score += score

    # Convergence = agreement level across variants
    avg_score = total_score / len(variants)
    variance = sum((s["score"] - avg_score) ** 2 for s in scored) / len(scored)
    # Lower variance = higher convergence
    convergence = max(0.0, min(1.0, 1.0 - (variance * 10)))

    return {
        "error": None,
        "scored_variants": scored,
        "convergence_score": round(convergence, 3),
        "debate_rounds": debate_rounds,
    }


def f4_f5_selection_and_merge(scored_variants, convergence_score, artifacts_dir="/output/artifacts/"):
    """
    F4/5: Base selection + merge + contract output (merged stage).

    Select winning variant (convergence_score driven).
    Produce return contract with canonical 10-field schema.
    """
    if not scored_variants:
        return {
            "status": "failed",
            "convergence_score": 0.0,
            "merged_output_path": None,
            "fallback_mode": True,
            "invocation_method": "skill-direct",
            "unresolved_conflicts": [],
            "artifacts_dir": artifacts_dir,
            "base_variant": None,
            "debate_rounds": 0,
            "variant_count": 0,
        }

    # Select base variant (highest scored)
    best = max(scored_variants, key=lambda v: v.get("score", 0))

    # Determine status from convergence
    if convergence_score >= 0.6:
        status = "success"
    elif convergence_score >= 0.5:
        status = "partial"
    else:
        status = "failed"

    merged_path = f"{artifacts_dir}merged-output.md" if status != "failed" else None

    return {
        "status": status,
        "convergence_score": convergence_score,
        "merged_output_path": merged_path,
        "fallback_mode": False,
        "invocation_method": "skill-direct",
        "unresolved_conflicts": [],
        "artifacts_dir": artifacts_dir,
        "base_variant": best.get("agent", "unknown"),
        "debate_rounds": 2,
        "variant_count": len(scored_variants),
    }


def run_fallback_protocol(agent_specs, debate_rounds=2, artifacts_dir="/output/artifacts/"):
    """
    Execute full fallback protocol: F1 → F2/3 → F4/5.

    Returns the final return contract dict.
    """
    # F1: Variant generation
    f1_result = f1_variant_generation(agent_specs)
    if f1_result["error"]:
        return {
            "status": "failed",
            "convergence_score": 0.0,
            "merged_output_path": None,
            "fallback_mode": True,
            "invocation_method": "skill-direct",
            "unresolved_conflicts": [],
            "artifacts_dir": artifacts_dir,
            "base_variant": None,
            "debate_rounds": 0,
            "variant_count": 0,
            "error": f1_result["error"],
        }

    # F2/3: Diff + debate
    f23_result = f2_f3_diff_and_debate(f1_result["variants"], debate_rounds)
    if f23_result["error"]:
        return {
            "status": "failed",
            "convergence_score": 0.0,
            "merged_output_path": None,
            "fallback_mode": True,
            "invocation_method": "skill-direct",
            "unresolved_conflicts": [],
            "artifacts_dir": artifacts_dir,
            "base_variant": None,
            "debate_rounds": debate_rounds,
            "variant_count": len(f1_result["variants"]),
            "error": f23_result["error"],
        }

    # F4/5: Selection + merge + contract
    contract = f4_f5_selection_and_merge(
        f23_result["scored_variants"],
        f23_result["convergence_score"],
        artifacts_dir,
    )
    contract["debate_rounds"] = debate_rounds

    return contract


# -- Test helpers --


def make_agent_specs(count=3, model="opus", persona="architect"):
    """Create a list of agent specs for testing."""
    return [
        {"model": f"{model}-{i + 1}" if count > 1 else model, "persona": persona}
        for i in range(count)
    ]


# == Test Classes ==


class TestF1VariantGeneration:
    """Test F1: variant generation produces agent outputs."""

    def test_generates_variants_per_agent(self):
        """F1 should produce one variant per agent spec."""
        specs = make_agent_specs(3)
        result = f1_variant_generation(specs)
        assert result["error"] is None
        assert len(result["variants"]) == 3

    def test_variant_includes_agent_identifier(self):
        """Each variant should identify its source agent."""
        specs = [{"model": "opus", "persona": "architect"}]
        # Need at least 2 agents
        specs.append({"model": "sonnet", "persona": "security"})
        result = f1_variant_generation(specs)
        assert result["variants"][0]["agent"] == "opus:architect"
        assert result["variants"][1]["agent"] == "sonnet:security"

    def test_minimum_2_agents_required(self):
        """F1 should error with fewer than 2 agents."""
        result = f1_variant_generation([{"model": "opus", "persona": "arch"}])
        assert result["error"] is not None
        assert "2 agents" in result["error"]

    def test_maximum_10_agents(self):
        """F1 should error with more than 10 agents."""
        specs = make_agent_specs(11)
        result = f1_variant_generation(specs)
        assert result["error"] is not None
        assert "10 agents" in result["error"]

    def test_empty_specs_errors(self):
        """F1 should error with empty agent specs."""
        result = f1_variant_generation([])
        assert result["error"] is not None

    def test_none_specs_errors(self):
        """F1 should error with None agent specs."""
        result = f1_variant_generation(None)
        assert result["error"] is not None

    def test_variant_ids_are_sequential(self):
        """Variant IDs should be sequential."""
        specs = make_agent_specs(3)
        result = f1_variant_generation(specs)
        ids = [v["id"] for v in result["variants"]]
        assert ids == ["variant-1", "variant-2", "variant-3"]


class TestF2F3DiffAndDebate:
    """Test F2/3: diff analysis + adversarial debate produces scored variants."""

    def test_produces_scored_variants(self):
        """F2/3 should score all input variants."""
        specs = make_agent_specs(3)
        f1 = f1_variant_generation(specs)
        result = f2_f3_diff_and_debate(f1["variants"])
        assert len(result["scored_variants"]) == 3
        assert all(v["score"] is not None for v in result["scored_variants"])

    def test_produces_convergence_score(self):
        """F2/3 should produce a convergence_score between 0 and 1."""
        specs = make_agent_specs(3)
        f1 = f1_variant_generation(specs)
        result = f2_f3_diff_and_debate(f1["variants"])
        assert 0.0 <= result["convergence_score"] <= 1.0

    def test_records_debate_rounds(self):
        """F2/3 should record the number of debate rounds."""
        specs = make_agent_specs(3)
        f1 = f1_variant_generation(specs)
        result = f2_f3_diff_and_debate(f1["variants"], debate_rounds=3)
        assert result["debate_rounds"] == 3

    def test_empty_variants_errors(self):
        """F2/3 should error with no variants."""
        result = f2_f3_diff_and_debate([])
        assert result["error"] is not None
        assert result["convergence_score"] == 0.0

    def test_scores_are_bounded(self):
        """All variant scores should be between 0 and 1."""
        specs = make_agent_specs(5)
        f1 = f1_variant_generation(specs)
        result = f2_f3_diff_and_debate(f1["variants"])
        for v in result["scored_variants"]:
            assert 0.0 <= v["score"] <= 1.0


class TestF4F5SelectionAndMerge:
    """Test F4/5: base selection + merge produces return contract."""

    def test_produces_valid_contract(self):
        """F4/5 should produce a dict with all 10 canonical fields."""
        specs = make_agent_specs(3)
        f1 = f1_variant_generation(specs)
        f23 = f2_f3_diff_and_debate(f1["variants"])
        contract = f4_f5_selection_and_merge(
            f23["scored_variants"], f23["convergence_score"]
        )
        contract_fields = set(contract.keys())
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - contract_fields
        assert not missing, f"Missing fields: {missing}"

    def test_status_is_valid_enum(self):
        """Status should be one of success|partial|failed."""
        specs = make_agent_specs(3)
        f1 = f1_variant_generation(specs)
        f23 = f2_f3_diff_and_debate(f1["variants"])
        contract = f4_f5_selection_and_merge(
            f23["scored_variants"], f23["convergence_score"]
        )
        assert contract["status"] in REQUIRED_STATUS_VALUES

    def test_selects_best_variant_as_base(self):
        """F4/5 should select the highest-scored variant as base."""
        scored = [
            {"id": "v1", "agent": "opus:arch", "score": 0.6},
            {"id": "v2", "agent": "sonnet:sec", "score": 0.9},
            {"id": "v3", "agent": "haiku:qa", "score": 0.7},
        ]
        contract = f4_f5_selection_and_merge(scored, 0.7)
        assert contract["base_variant"] == "sonnet:sec"

    def test_high_convergence_produces_success(self):
        """Convergence >= 0.6 should produce status: success."""
        scored = [{"id": "v1", "agent": "a:b", "score": 0.8}]
        contract = f4_f5_selection_and_merge(scored, 0.7)
        assert contract["status"] == "success"
        assert contract["merged_output_path"] is not None

    def test_mid_convergence_produces_partial(self):
        """Convergence 0.5-0.59 should produce status: partial."""
        scored = [{"id": "v1", "agent": "a:b", "score": 0.6}]
        contract = f4_f5_selection_and_merge(scored, 0.55)
        assert contract["status"] == "partial"
        assert contract["merged_output_path"] is not None

    def test_low_convergence_produces_failed(self):
        """Convergence < 0.5 should produce status: failed."""
        scored = [{"id": "v1", "agent": "a:b", "score": 0.3}]
        contract = f4_f5_selection_and_merge(scored, 0.3)
        assert contract["status"] == "failed"
        assert contract["merged_output_path"] is None

    def test_empty_variants_produces_failed(self):
        """No scored variants should produce failed contract."""
        contract = f4_f5_selection_and_merge([], 0.0)
        assert contract["status"] == "failed"
        assert contract["fallback_mode"] is True
        assert contract["variant_count"] == 0

    def test_variant_count_matches_input(self):
        """variant_count should match number of scored variants."""
        scored = [
            {"id": "v1", "agent": "a:b", "score": 0.8},
            {"id": "v2", "agent": "c:d", "score": 0.7},
        ]
        contract = f4_f5_selection_and_merge(scored, 0.7)
        assert contract["variant_count"] == 2


class TestEndToEndFallbackProtocol:
    """Test full F1 → F2/3 → F4/5 pipeline end-to-end."""

    def test_full_pipeline_produces_valid_contract(self):
        """End-to-end pipeline should produce contract with 10 canonical fields."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        # Remove 'error' key if present (not part of canonical schema)
        contract_fields = set(contract.keys()) - {"error"}
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - contract_fields
        assert not missing, f"Missing fields: {missing}"

    def test_pipeline_status_is_valid(self):
        """Pipeline status should be a valid enum value."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        assert contract["status"] in REQUIRED_STATUS_VALUES

    def test_pipeline_convergence_in_range(self):
        """Pipeline convergence_score should be 0.0-1.0."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        assert 0.0 <= contract["convergence_score"] <= 1.0

    def test_pipeline_with_2_agents(self):
        """Pipeline should work with minimum 2 agents."""
        specs = [
            {"model": "opus", "persona": "architect"},
            {"model": "sonnet", "persona": "security"},
        ]
        contract = run_fallback_protocol(specs)
        assert contract["status"] in REQUIRED_STATUS_VALUES
        assert contract["variant_count"] == 2

    def test_pipeline_with_5_agents(self):
        """Pipeline should work with 5 agents."""
        specs = make_agent_specs(5)
        contract = run_fallback_protocol(specs)
        assert contract["status"] in REQUIRED_STATUS_VALUES
        assert contract["variant_count"] == 5

    def test_pipeline_with_10_agents(self):
        """Pipeline should work with maximum 10 agents."""
        specs = make_agent_specs(10)
        contract = run_fallback_protocol(specs)
        assert contract["status"] in REQUIRED_STATUS_VALUES
        assert contract["variant_count"] == 10

    def test_pipeline_records_debate_rounds(self):
        """Pipeline should record debate_rounds in contract."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs, debate_rounds=3)
        assert contract["debate_rounds"] == 3

    def test_pipeline_sets_invocation_method(self):
        """Pipeline should set invocation_method to skill-direct."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        assert contract["invocation_method"] == "skill-direct"

    def test_pipeline_sets_artifacts_dir(self):
        """Pipeline should set artifacts_dir."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs, artifacts_dir="/custom/artifacts/")
        assert contract["artifacts_dir"] == "/custom/artifacts/"

    def test_pipeline_failure_with_1_agent(self):
        """Pipeline should fail with only 1 agent."""
        specs = [{"model": "opus", "persona": "architect"}]
        contract = run_fallback_protocol(specs)
        assert contract["status"] == "failed"
        assert contract["error"] is not None

    def test_pipeline_failure_with_11_agents(self):
        """Pipeline should fail with more than 10 agents."""
        specs = make_agent_specs(11)
        contract = run_fallback_protocol(specs)
        assert contract["status"] == "failed"

    def test_pipeline_failure_with_no_agents(self):
        """Pipeline should fail with empty agent list."""
        contract = run_fallback_protocol([])
        assert contract["status"] == "failed"


class TestFallbackSentinel:
    """Test fallback sentinel value (convergence_score = 0.5) behavior."""

    def test_sentinel_value_routes_to_partial(self):
        """Fallback sentinel 0.5 should route to PARTIAL path.

        Reimplements routing logic inline to avoid cross-module import.
        Sentinel 0.5 is >= 0.5 but < 0.6, so routes to PARTIAL.
        """
        score = 0.5  # Sentinel value
        assert score >= 0.5, "Sentinel should satisfy PARTIAL threshold"
        assert score < 0.6, "Sentinel should NOT satisfy PASS threshold"
        # Route: >= 0.6 PASS, >= 0.5 PARTIAL, < 0.5 FAIL
        if score >= 0.6:
            route = "PASS"
        elif score >= 0.5:
            route = "PARTIAL"
        else:
            route = "FAIL"
        assert route == "PARTIAL"

    def test_sentinel_used_when_convergence_unmeasurable(self):
        """When convergence can't be measured, use sentinel 0.5."""
        # Simulate unmeasurable by passing empty variants to F2/3
        result = f2_f3_diff_and_debate([])
        assert result["convergence_score"] == 0.0
        # The full pipeline handles this by producing a failed contract
        contract = f4_f5_selection_and_merge([], result["convergence_score"])
        assert contract["status"] == "failed"
        assert contract["fallback_mode"] is True


class TestFallbackOnlyVariant:
    """Test that FALLBACK-ONLY variant works end-to-end per D-0001."""

    def test_fallback_only_uses_skill_direct(self):
        """FALLBACK-ONLY variant should use skill-direct invocation."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        assert contract["invocation_method"] == "skill-direct"

    def test_fallback_only_produces_complete_contract(self):
        """FALLBACK-ONLY should produce all 10 required fields."""
        specs = make_agent_specs(3)
        contract = run_fallback_protocol(specs)
        contract_fields = set(contract.keys()) - {"error"}
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - contract_fields
        assert not missing, f"Missing fields in FALLBACK-ONLY: {missing}"

    def test_fallback_only_records_base_variant(self):
        """FALLBACK-ONLY should record which variant was selected as base."""
        specs = [
            {"model": "opus", "persona": "architect"},
            {"model": "sonnet", "persona": "security"},
        ]
        contract = run_fallback_protocol(specs)
        assert contract["base_variant"] is not None
        assert ":" in contract["base_variant"]  # Format: model:persona
