"""Tests for user review gates with --skip-review bypass."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from superclaude.cli.cli_portify.review import (
    REVIEW_GATE_STEPS,
    ReviewDecision,
    is_review_step,
    prompt_review,
    review_gate,
)


class TestReviewDecision:
    """Tests for ReviewDecision enum."""

    def test_values(self):
        assert ReviewDecision.ACCEPTED.value == "accepted"
        assert ReviewDecision.REJECTED.value == "rejected"
        assert ReviewDecision.SKIPPED.value == "skipped"


class TestIsReviewStep:
    """Tests for review step identification."""

    def test_design_pipeline_is_review_step(self):
        assert is_review_step("design-pipeline") is True

    def test_panel_review_is_review_step(self):
        assert is_review_step("panel-review") is True

    def test_other_steps_are_not_review(self):
        assert is_review_step("validate-config") is False
        assert is_review_step("discover-components") is False
        assert is_review_step("analyze-workflow") is False
        assert is_review_step("synthesize-spec") is False
        assert is_review_step("brainstorm-gaps") is False


class TestPromptReview:
    """Tests for prompt_review function."""

    def test_skip_review_returns_skipped(self):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=True
        )
        assert decision == ReviewDecision.SKIPPED

    @patch("builtins.input", return_value="y")
    def test_y_response_returns_accepted(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.ACCEPTED

    @patch("builtins.input", return_value="yes")
    def test_yes_response_returns_accepted(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.ACCEPTED

    @patch("builtins.input", return_value="Y")
    def test_uppercase_y_returns_accepted(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.ACCEPTED

    @patch("builtins.input", return_value="n")
    def test_n_response_returns_rejected(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.REJECTED

    @patch("builtins.input", return_value="")
    def test_empty_response_returns_rejected(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.REJECTED

    @patch("builtins.input", return_value="maybe")
    def test_arbitrary_response_returns_rejected(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.REJECTED

    @patch("builtins.input", side_effect=EOFError)
    def test_eof_returns_rejected(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.REJECTED

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_rejected(self, mock_input):
        decision = prompt_review(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert decision == ReviewDecision.REJECTED


class TestReviewGate:
    """Tests for the combined review_gate function."""

    def test_non_review_step_returns_continue_skipped(self):
        should_continue, decision = review_gate(
            "validate-config", "/path/to/artifact.md"
        )
        assert should_continue is True
        assert decision == ReviewDecision.SKIPPED

    def test_skip_review_returns_continue_skipped(self):
        should_continue, decision = review_gate(
            "design-pipeline", "/path/to/artifact.md", skip_review=True
        )
        assert should_continue is True
        assert decision == ReviewDecision.SKIPPED

    @patch("builtins.input", return_value="y")
    def test_accepted_returns_continue(self, mock_input):
        should_continue, decision = review_gate(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert should_continue is True
        assert decision == ReviewDecision.ACCEPTED

    @patch("builtins.input", return_value="n")
    def test_rejected_returns_halt(self, mock_input):
        should_continue, decision = review_gate(
            "design-pipeline", "/path/to/artifact.md", skip_review=False
        )
        assert should_continue is False
        assert decision == ReviewDecision.REJECTED

    @patch("builtins.input", return_value="y")
    def test_panel_review_gate(self, mock_input):
        should_continue, decision = review_gate(
            "panel-review", "/path/to/artifact.md", skip_review=False
        )
        assert should_continue is True
        assert decision == ReviewDecision.ACCEPTED

    @patch("builtins.input", return_value="n")
    def test_panel_review_rejected(self, mock_input):
        should_continue, decision = review_gate(
            "panel-review", "/path/to/artifact.md", skip_review=False
        )
        assert should_continue is False
        assert decision == ReviewDecision.REJECTED
