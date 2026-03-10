"""
Unit tests for Wave 1 complexity scoring system (T2.4).

Tests the complexity scoring formula defined in SKILL.md:
- 5 complexity factors with weights
- Factor scoring lookup tables
- Final score calculation (0.0-1.0)
- Classification thresholds (LOW/MEDIUM/HIGH)
"""

import pytest


def score_factor(value: int, scoring: dict) -> float:
    """Look up score for a value in a range-based scoring table."""
    for (low, high), score in scoring.items():
        if low <= value <= high:
            return score
    return 0.0


def calculate_complexity(
    req_count: int,
    dep_depth: int,
    domain_spread: int,
    risk_severity: str,
    scope_size: str,
    factors: dict,
) -> float:
    """
    Reimplements complexity formula from SKILL.md T2.4:
    score = (req_count_score * 0.25) + (dep_depth_score * 0.25) +
            (domain_spread_score * 0.20) + (risk_sev_score * 0.15) +
            (scope_size_score * 0.15)
    """
    req_score = score_factor(req_count, factors["requirement_count"]["scoring"])
    dep_score = score_factor(dep_depth, factors["dependency_depth"]["scoring"])
    dom_score = score_factor(domain_spread, factors["domain_spread"]["scoring"])
    risk_score = factors["risk_severity"]["scoring_labels"][risk_severity]
    scope_score = factors["scope_size"]["scoring_labels"][scope_size]

    return (
        req_score * 0.25
        + dep_score * 0.25
        + dom_score * 0.20
        + risk_score * 0.15
        + scope_score * 0.15
    )


def classify_complexity(score: float) -> str:
    """Classify score as LOW/MEDIUM/HIGH per SKILL.md."""
    if score < 0.4:
        return "LOW"
    elif score <= 0.7:
        return "MEDIUM"
    else:
        return "HIGH"


class TestComplexityWeights:
    """Verify factor weights sum to 1.0."""

    def test_weights_sum_to_one(self, complexity_factors):
        """All factor weights should sum to 1.0."""
        weights = [
            complexity_factors["requirement_count"]["weight"],
            complexity_factors["dependency_depth"]["weight"],
            complexity_factors["domain_spread"]["weight"],
            complexity_factors["risk_severity"]["weight"],
            complexity_factors["scope_size"]["weight"],
        ]
        assert abs(sum(weights) - 1.0) < 0.001

    def test_five_factors_defined(self, complexity_factors):
        """Should have exactly 5 complexity factors."""
        assert len(complexity_factors) == 5


class TestFactorScoring:
    """Test individual factor score lookups."""

    def test_requirement_count_scoring(self, complexity_factors):
        """Verify requirement count ranges."""
        scoring = complexity_factors["requirement_count"]["scoring"]
        assert score_factor(3, scoring) == 0.2   # 1-5 range
        assert score_factor(8, scoring) == 0.4   # 6-10 range
        assert score_factor(15, scoring) == 0.6  # 11-20 range
        assert score_factor(25, scoring) == 0.8  # 21-35 range
        assert score_factor(50, scoring) == 1.0  # 36+ range

    def test_dependency_depth_scoring(self, complexity_factors):
        """Verify dependency depth ranges."""
        scoring = complexity_factors["dependency_depth"]["scoring"]
        assert score_factor(0, scoring) == 0.1   # none
        assert score_factor(2, scoring) == 0.3   # 1-2
        assert score_factor(4, scoring) == 0.5   # 3-5
        assert score_factor(7, scoring) == 0.7   # 6-10
        assert score_factor(15, scoring) == 1.0  # 11+

    def test_domain_spread_scoring(self, complexity_factors):
        """Verify domain spread ranges."""
        scoring = complexity_factors["domain_spread"]["scoring"]
        assert score_factor(1, scoring) == 0.2
        assert score_factor(3, scoring) == 0.6
        assert score_factor(5, scoring) == 1.0


class TestComplexityClassification:
    """Test complexity classification thresholds."""

    def test_low_classification(self):
        """Score < 0.4 should be LOW."""
        assert classify_complexity(0.0) == "LOW"
        assert classify_complexity(0.2) == "LOW"
        assert classify_complexity(0.39) == "LOW"

    def test_medium_classification(self):
        """Score 0.4-0.7 should be MEDIUM."""
        assert classify_complexity(0.4) == "MEDIUM"
        assert classify_complexity(0.55) == "MEDIUM"
        assert classify_complexity(0.7) == "MEDIUM"

    def test_high_classification(self):
        """Score > 0.7 should be HIGH."""
        assert classify_complexity(0.71) == "HIGH"
        assert classify_complexity(0.85) == "HIGH"
        assert classify_complexity(1.0) == "HIGH"


class TestComplexityCalculation:
    """Test full complexity calculation."""

    def test_sample_auth_spec(self, complexity_factors):
        """Auth system with 18 reqs, 4 deps, 3 domains, high risk, large scope."""
        score = calculate_complexity(
            req_count=18,      # 11-20 → 0.6
            dep_depth=4,       # 3-5 → 0.5
            domain_spread=3,   # 3 → 0.6
            risk_severity="high_risks",  # 0.7
            scope_size="large",          # 0.6
            factors=complexity_factors,
        )
        # 0.6*0.25 + 0.5*0.25 + 0.6*0.20 + 0.7*0.15 + 0.6*0.15
        # = 0.15 + 0.125 + 0.12 + 0.105 + 0.09 = 0.59
        expected = 0.59
        assert abs(score - expected) < 0.01, f"Expected ~{expected}, got {score}"
        assert classify_complexity(score) == "MEDIUM"

    def test_minimal_spec(self, complexity_factors):
        """Minimal spec with 2 reqs, no deps, 1 domain, no risk, small scope."""
        score = calculate_complexity(
            req_count=2,
            dep_depth=0,
            domain_spread=1,
            risk_severity="no_risks",
            scope_size="small",
            factors=complexity_factors,
        )
        # 0.2*0.25 + 0.1*0.25 + 0.2*0.20 + 0.1*0.15 + 0.2*0.15
        # = 0.05 + 0.025 + 0.04 + 0.015 + 0.03 = 0.16
        expected = 0.16
        assert abs(score - expected) < 0.01, f"Expected ~{expected}, got {score}"
        assert classify_complexity(score) == "LOW"

    def test_massive_enterprise(self, complexity_factors):
        """Enterprise spec with 50 reqs, 15 deps, 5 domains, critical, massive."""
        score = calculate_complexity(
            req_count=50,
            dep_depth=15,
            domain_spread=5,
            risk_severity="critical_risks",
            scope_size="massive",
            factors=complexity_factors,
        )
        # 1.0*0.25 + 1.0*0.25 + 1.0*0.20 + 1.0*0.15 + 1.0*0.15
        # = 0.25 + 0.25 + 0.20 + 0.15 + 0.15 = 1.0
        assert score == 1.0
        assert classify_complexity(score) == "HIGH"

    def test_score_always_in_range(self, complexity_factors):
        """Score should always be between 0.0 and 1.0."""
        for req in [1, 10, 50]:
            for dep in [0, 5, 15]:
                for dom in [1, 3, 5]:
                    score = calculate_complexity(
                        req, dep, dom, "medium_risks", "medium",
                        complexity_factors,
                    )
                    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
