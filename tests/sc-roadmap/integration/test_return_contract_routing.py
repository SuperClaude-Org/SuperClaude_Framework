"""
Integration tests for return contract consumer routing (T04.01 / D-0022).

Validates the 3-status routing logic from sc:roadmap SKILL.md Wave 2 Step 3e:
- PASS: convergence_score >= 0.6 → use merged_output_path as roadmap source
- PARTIAL: convergence_score >= 0.5 → use merged_output_path with warning
- FAIL: convergence_score < 0.5 → abort roadmap generation

Also tests edge cases: missing contract, parse errors, boundary values,
malformed convergence_score, and consumer defaults.

Reference: D-0009 (Step 3e routing), D-0010 (fallback protocol),
SKILL.md §Return Contract, refs/adversarial-integration.md §Return Contract Consumption
"""

import math

import pytest


# -- Consumer defaults from SKILL.md §Return Contract --

CONSUMER_DEFAULTS = {
    "convergence_score": 0.5,
    "status": "failed",
    "merged_output_path": None,
    "fallback_mode": False,
    "invocation_method": None,
    "unresolved_conflicts": [],
}


# -- Return contract routing logic (reimplemented from SKILL.md Step 3e) --


def parse_return_contract(raw_response):
    """
    Parse return contract from inline Skill response.

    Implements the empty/malformed response guard from SKILL.md Step 3e:
    - Empty or unparseable → fallback convergence_score: 0.5 (Partial path)
    - Missing fields get consumer defaults

    Args:
        raw_response: Either a dict (parsed contract) or None/empty (missing).

    Returns:
        dict: Parsed contract with all fields populated (defaults applied).
    """
    if raw_response is None or raw_response == {}:
        # Missing contract → fallback
        return {**CONSUMER_DEFAULTS, "convergence_score": 0.5, "status": "partial"}

    if not isinstance(raw_response, dict):
        # Unparseable → fallback
        return {**CONSUMER_DEFAULTS, "convergence_score": 0.5, "status": "partial"}

    # Apply consumer defaults for missing fields
    result = {**CONSUMER_DEFAULTS, **raw_response}

    # Validate convergence_score is numeric
    score = result.get("convergence_score")
    if not isinstance(score, (int, float)) or (isinstance(score, float) and math.isnan(score)):
        result["convergence_score"] = 0.5

    return result


def route_contract(contract):
    """
    Route based on convergence_score per SKILL.md Step 3e.

    Routing thresholds:
    - >= 0.6 → PASS: use merged_output_path as roadmap source
    - >= 0.5 → PARTIAL: use merged_output_path with warning
    - < 0.5  → FAIL: abort roadmap generation

    Returns:
        dict: Routing decision with status, action, and metadata.
    """
    score = contract.get("convergence_score", 0.5)

    if score >= 0.6:
        return {
            "route": "PASS",
            "action": "use_merged_output",
            "merged_output_path": contract.get("merged_output_path"),
            "warning": None,
        }
    elif score >= 0.5:
        return {
            "route": "PARTIAL",
            "action": "use_merged_output_with_warning",
            "merged_output_path": contract.get("merged_output_path"),
            "warning": f"adversarial_status: partial (convergence: {score})",
        }
    else:
        return {
            "route": "FAIL",
            "action": "abort",
            "merged_output_path": None,
            "warning": f"Adversarial pipeline failed (convergence: {score:.2f}). "
            "Cannot produce reliable roadmap from divergent variants.",
        }


# -- Canonical field set from SKILL.md §Return Contract + adversarial-integration.md --

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


# -- Test fixtures --


def make_contract(
    status="success",
    convergence_score=0.7,
    merged_output_path="/output/merged.md",
    fallback_mode=False,
    invocation_method="skill-direct",
    unresolved_conflicts=None,
    artifacts_dir="/output/artifacts/",
    base_variant="opus:architect",
    debate_rounds=2,
    variant_count=3,
):
    """Build a valid return contract dict with canonical 10 fields."""
    return {
        "status": status,
        "convergence_score": convergence_score,
        "merged_output_path": merged_output_path,
        "fallback_mode": fallback_mode,
        "invocation_method": invocation_method,
        "unresolved_conflicts": unresolved_conflicts or [],
        "artifacts_dir": artifacts_dir,
        "base_variant": base_variant,
        "debate_rounds": debate_rounds,
        "variant_count": variant_count,
    }


# == Test Classes ==


class TestPassRouting:
    """Tests for PASS routing path (convergence_score >= 0.6)."""

    def test_high_convergence_routes_to_pass(self):
        """Score 0.9 should route to PASS."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.9, status="success")
        )
        result = route_contract(contract)
        assert result["route"] == "PASS"
        assert result["action"] == "use_merged_output"
        assert result["warning"] is None

    def test_exact_0_6_routes_to_pass(self):
        """Boundary: exact 0.6 should route to PASS (>= 0.6)."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.6, status="success")
        )
        result = route_contract(contract)
        assert result["route"] == "PASS"
        assert result["action"] == "use_merged_output"

    def test_pass_preserves_merged_output_path(self):
        """PASS should provide merged_output_path for downstream consumption."""
        contract = parse_return_contract(
            make_contract(
                convergence_score=0.8,
                merged_output_path="/output/roadmap-merged.md",
            )
        )
        result = route_contract(contract)
        assert result["merged_output_path"] == "/output/roadmap-merged.md"

    def test_perfect_convergence(self):
        """Score 1.0 should route to PASS."""
        contract = parse_return_contract(
            make_contract(convergence_score=1.0, status="success")
        )
        result = route_contract(contract)
        assert result["route"] == "PASS"


class TestPartialRouting:
    """Tests for PARTIAL routing path (0.5 <= convergence_score < 0.6)."""

    def test_mid_partial_routes_correctly(self):
        """Score 0.55 should route to PARTIAL."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.55, status="partial")
        )
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"
        assert result["action"] == "use_merged_output_with_warning"
        assert "partial" in result["warning"].lower()

    def test_exact_0_5_routes_to_partial(self):
        """Boundary: exact 0.5 should route to PARTIAL (>= 0.5)."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.5, status="partial")
        )
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"

    def test_just_below_0_6_routes_to_partial(self):
        """Score 0.599 should route to PARTIAL (not PASS)."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.599, status="partial")
        )
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"

    def test_partial_includes_warning(self):
        """PARTIAL should include adversarial_status warning."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.55, status="partial")
        )
        result = route_contract(contract)
        assert result["warning"] is not None
        assert "adversarial_status" in result["warning"]

    def test_partial_preserves_merged_output_path(self):
        """PARTIAL should still provide merged_output_path."""
        contract = parse_return_contract(
            make_contract(
                convergence_score=0.52,
                merged_output_path="/output/partial-merge.md",
            )
        )
        result = route_contract(contract)
        assert result["merged_output_path"] == "/output/partial-merge.md"


class TestFailRouting:
    """Tests for FAIL routing path (convergence_score < 0.5)."""

    def test_low_convergence_routes_to_fail(self):
        """Score 0.3 should route to FAIL."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.3, status="failed")
        )
        result = route_contract(contract)
        assert result["route"] == "FAIL"
        assert result["action"] == "abort"

    def test_just_below_0_5_routes_to_fail(self):
        """Score 0.499 should route to FAIL (< 0.5)."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.499, status="failed")
        )
        result = route_contract(contract)
        assert result["route"] == "FAIL"

    def test_zero_convergence_routes_to_fail(self):
        """Score 0.0 should route to FAIL."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.0, status="failed")
        )
        result = route_contract(contract)
        assert result["route"] == "FAIL"

    def test_fail_nullifies_merged_output(self):
        """FAIL should set merged_output_path to None (no output consumed)."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.2, status="failed")
        )
        result = route_contract(contract)
        assert result["merged_output_path"] is None

    def test_fail_includes_abort_message(self):
        """FAIL should include descriptive abort message with convergence score."""
        contract = parse_return_contract(
            make_contract(convergence_score=0.3, status="failed")
        )
        result = route_contract(contract)
        assert "failed" in result["warning"].lower()
        assert "0.30" in result["warning"]


class TestEdgeCases:
    """Edge case tests: missing contract, parse errors, malformed data."""

    def test_none_response_uses_fallback(self):
        """None response → fallback convergence_score 0.5."""
        contract = parse_return_contract(None)
        assert contract["convergence_score"] == 0.5
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"

    def test_empty_dict_uses_fallback(self):
        """Empty dict → fallback convergence_score 0.5."""
        contract = parse_return_contract({})
        assert contract["convergence_score"] == 0.5
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"

    def test_non_dict_response_uses_fallback(self):
        """Non-dict response (e.g., list) → fallback."""
        contract = parse_return_contract(["not", "a", "dict"])
        assert contract["convergence_score"] == 0.5
        result = route_contract(contract)
        assert result["route"] == "PARTIAL"

    def test_string_response_uses_fallback(self):
        """String response (unparseable) → fallback."""
        contract = parse_return_contract("just a string")
        assert contract["convergence_score"] == 0.5

    def test_malformed_convergence_score_string(self):
        """String convergence_score → fallback 0.5."""
        contract = parse_return_contract(
            {"convergence_score": "not-a-number", "status": "partial"}
        )
        assert contract["convergence_score"] == 0.5

    def test_malformed_convergence_score_nan(self):
        """NaN convergence_score → fallback 0.5."""
        contract = parse_return_contract(
            {"convergence_score": float("nan"), "status": "partial"}
        )
        assert contract["convergence_score"] == 0.5

    def test_missing_convergence_score_uses_default(self):
        """Missing convergence_score field → consumer default 0.5."""
        contract = parse_return_contract(
            {"status": "partial", "merged_output_path": "/output/merged.md"}
        )
        assert contract["convergence_score"] == 0.5

    def test_missing_status_uses_default(self):
        """Missing status field → consumer default 'failed'."""
        contract = parse_return_contract(
            {"convergence_score": 0.7, "merged_output_path": "/output/merged.md"}
        )
        assert contract["status"] == "failed"

    def test_missing_merged_output_path_uses_default(self):
        """Missing merged_output_path → consumer default None."""
        contract = parse_return_contract(
            {"status": "success", "convergence_score": 0.8}
        )
        assert contract["merged_output_path"] is None

    def test_consumer_defaults_all_fields(self):
        """All consumer defaults applied when response has unrelated fields only."""
        contract = parse_return_contract({"some_unrelated_key": True})
        assert contract["convergence_score"] == 0.5
        assert contract["status"] == "failed"
        assert contract["merged_output_path"] is None
        assert contract["fallback_mode"] is False
        assert contract["invocation_method"] is None
        assert contract["unresolved_conflicts"] == []


class TestCanonicalSchema:
    """Validate contract fixtures use the canonical 10-field schema."""

    def test_full_contract_has_10_fields(self):
        """A fully-specified contract should contain all 10 canonical fields."""
        contract = make_contract()
        contract_fields = set(contract.keys())
        assert contract_fields == CANONICAL_RETURN_CONTRACT_FIELDS

    def test_all_fields_present_in_pass_fixture(self):
        """PASS fixture uses canonical schema."""
        contract = make_contract(convergence_score=0.8, status="success")
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - set(contract.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_all_fields_present_in_partial_fixture(self):
        """PARTIAL fixture uses canonical schema."""
        contract = make_contract(convergence_score=0.55, status="partial")
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - set(contract.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_all_fields_present_in_fail_fixture(self):
        """FAIL fixture uses canonical schema."""
        contract = make_contract(convergence_score=0.3, status="failed")
        missing = CANONICAL_RETURN_CONTRACT_FIELDS - set(contract.keys())
        assert not missing, f"Missing fields: {missing}"


class TestBoundaryValues:
    """Boundary value tests for convergence_score thresholds."""

    @pytest.mark.parametrize(
        "score,expected_route",
        [
            (0.0, "FAIL"),
            (0.1, "FAIL"),
            (0.49, "FAIL"),
            (0.499, "FAIL"),
            (0.5, "PARTIAL"),
            (0.501, "PARTIAL"),
            (0.55, "PARTIAL"),
            (0.599, "PARTIAL"),
            (0.6, "PASS"),
            (0.601, "PASS"),
            (0.7, "PASS"),
            (0.8, "PASS"),
            (0.9, "PASS"),
            (1.0, "PASS"),
        ],
    )
    def test_convergence_threshold_boundary(self, score, expected_route):
        """Parametrized boundary test for convergence thresholds."""
        contract = parse_return_contract(make_contract(convergence_score=score))
        result = route_contract(contract)
        assert result["route"] == expected_route, (
            f"Score {score} expected {expected_route}, got {result['route']}"
        )

    def test_negative_score_routes_to_fail(self):
        """Negative convergence_score should route to FAIL."""
        contract = parse_return_contract(make_contract(convergence_score=-0.1))
        result = route_contract(contract)
        assert result["route"] == "FAIL"

    def test_score_above_1_routes_to_pass(self):
        """Score > 1.0 (out of range) still routes to PASS."""
        contract = parse_return_contract(make_contract(convergence_score=1.5))
        result = route_contract(contract)
        assert result["route"] == "PASS"
