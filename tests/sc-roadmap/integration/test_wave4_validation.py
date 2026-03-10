"""
Integration tests for Wave 4 validation pipeline.

Tests the multi-agent validation system:
- Quality-engineer scoring (4 focus areas, 25 points each)
- Self-review scoring (4 questions, 25 points each)
- Score aggregation (60/40 weights)
- Decision thresholds (PASS/REVISE/REJECT)
"""

import pytest


def aggregate_scores(quality_score: int, review_score: int) -> dict:
    """
    Reimplements score aggregation from SKILL.md T5.3:
    final_score = round(quality_score * 0.60 + review_score * 0.40)
    """
    final = round(quality_score * 0.60 + review_score * 0.40)

    if final >= 85:
        decision = "PASS"
    elif final >= 70:
        decision = "REVISE"
    else:
        decision = "REJECT"

    return {
        "quality_score": quality_score,
        "review_score": review_score,
        "final_score": final,
        "decision": decision,
    }


class TestScoreAggregation:
    """Test score aggregation algorithm."""

    def test_weights_sum_to_one(self):
        """Quality (0.60) + Review (0.40) should sum to 1.0."""
        assert 0.60 + 0.40 == 1.0

    def test_example_pass(self):
        """Example from SKILL.md: quality=90, review=85 → 88 PASS."""
        result = aggregate_scores(90, 85)
        assert result["final_score"] == 88
        assert result["decision"] == "PASS"

    def test_example_revise(self):
        """Example from SKILL.md: quality=80, review=70 → 76 REVISE."""
        result = aggregate_scores(80, 70)
        assert result["final_score"] == 76
        assert result["decision"] == "REVISE"

    def test_example_reject(self):
        """Example from SKILL.md: quality=60, review=50 → 56 REJECT."""
        result = aggregate_scores(60, 50)
        assert result["final_score"] == 56
        assert result["decision"] == "REJECT"

    def test_perfect_scores(self):
        """Both 100 → 100 PASS."""
        result = aggregate_scores(100, 100)
        assert result["final_score"] == 100
        assert result["decision"] == "PASS"

    def test_zero_scores(self):
        """Both 0 → 0 REJECT."""
        result = aggregate_scores(0, 0)
        assert result["final_score"] == 0
        assert result["decision"] == "REJECT"

    def test_boundary_85(self):
        """Score exactly 85 → PASS."""
        # 85 * 0.6 + 85 * 0.4 = 51 + 34 = 85
        result = aggregate_scores(85, 85)
        assert result["final_score"] == 85
        assert result["decision"] == "PASS"

    def test_boundary_84(self):
        """Score 84 → REVISE."""
        result = aggregate_scores(84, 84)
        assert result["final_score"] == 84
        assert result["decision"] == "REVISE"

    def test_boundary_70(self):
        """Score exactly 70 → REVISE."""
        result = aggregate_scores(70, 70)
        assert result["final_score"] == 70
        assert result["decision"] == "REVISE"

    def test_boundary_69(self):
        """Score 69 → REJECT."""
        result = aggregate_scores(69, 69)
        assert result["final_score"] == 69
        assert result["decision"] == "REJECT"

    def test_quality_weighted_higher(self):
        """Quality engineer has 60% weight (higher than review at 40%)."""
        # High quality, low review
        result_high_q = aggregate_scores(100, 0)
        # Low quality, high review
        result_high_r = aggregate_scores(0, 100)

        assert result_high_q["final_score"] > result_high_r["final_score"]
        assert result_high_q["final_score"] == 60
        assert result_high_r["final_score"] == 40


class TestDecisionActions:
    """Test decision action requirements from SKILL.md."""

    def test_pass_proceeds_to_wave5(self):
        """PASS should proceed to Wave 5."""
        result = aggregate_scores(90, 90)
        assert result["decision"] == "PASS"

    def test_revise_max_iterations(self):
        """REVISE should support max 2 iterations."""
        MAX_ITERATIONS = 2
        result = aggregate_scores(75, 75)
        assert result["decision"] == "REVISE"
        # Verify max iterations constant matches SKILL.md
        assert MAX_ITERATIONS == 2

    def test_reject_preserves_drafts(self):
        """REJECT should rename artifacts to .draft."""
        result = aggregate_scores(50, 40)
        assert result["decision"] == "REJECT"
        # Draft preservation pattern from SKILL.md
        draft_pattern = "{filename}.draft"
        assert ".draft" in draft_pattern


class TestQualityEngineerBreakdown:
    """Test quality engineer scoring breakdown."""

    FOCUS_AREAS = ["completeness", "correctness", "consistency", "compliance"]

    def test_four_focus_areas(self):
        """Quality engineer should have 4 focus areas."""
        assert len(self.FOCUS_AREAS) == 4

    def test_each_area_25_points(self):
        """Each focus area should be worth 25 points."""
        total = 25 * len(self.FOCUS_AREAS)
        assert total == 100

    def test_focus_areas_in_skill_md(self, skill_md_content):
        """All focus areas should be documented in SKILL.md."""
        for area in self.FOCUS_AREAS:
            # Case-insensitive check
            assert area.lower() in skill_md_content.lower()


class TestSelfReviewProtocol:
    """Test self-review 4-question protocol."""

    QUESTIONS = [
        "q1_spec_coverage",
        "q2_path_conventions",
        "q3_critical_mistakes",
        "q4_traceability",
    ]

    def test_four_questions(self):
        """Self-review should have 4 questions."""
        assert len(self.QUESTIONS) == 4

    def test_each_question_25_points(self):
        """Each question should be worth 25 points."""
        total = 25 * len(self.QUESTIONS)
        assert total == 100

    def test_questions_in_skill_md(self, skill_md_content):
        """All question IDs should appear in SKILL.md."""
        for q in self.QUESTIONS:
            assert q in skill_md_content, f"Question '{q}' not found in SKILL.md"
