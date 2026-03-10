"""Tests for is_behavioral() -- T01.03 behavioral detection heuristic."""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.deliverables import is_behavioral


class TestIsBehavioral:
    def test_replace_boolean_with_int_offset_is_behavioral(self):
        assert is_behavioral("Replace boolean with int offset") is True

    def test_document_api_endpoint_is_not_behavioral(self):
        assert is_behavioral("Document API endpoint") is False

    def test_add_type_definition_is_not_behavioral(self):
        assert is_behavioral("Add type definition for GateResult") is False

    def test_implement_retry_with_bounded_attempts_is_behavioral(self):
        assert is_behavioral("Implement retry with bounded attempts") is True

    def test_update_readme_is_not_behavioral(self):
        assert is_behavioral("Update README") is False

    def test_empty_description_returns_false(self):
        assert is_behavioral("") is False

    def test_whitespace_only_returns_false(self):
        assert is_behavioral("   ") is False

    def test_none_like_empty(self):
        assert is_behavioral("") is False

    def test_compute_verb(self):
        assert is_behavioral("Compute hash of input file") is True

    def test_extract_verb(self):
        assert is_behavioral("Extract metadata from headers") is True

    def test_filter_verb(self):
        assert is_behavioral("Filter results by date range") is True

    def test_state_mutation_self(self):
        assert is_behavioral("Update self._counter on each call") is True

    def test_conditional_guard(self):
        assert is_behavioral("Add guard clause for empty input") is True

    def test_sentinel_pattern(self):
        assert is_behavioral("Use sentinel value to detect end") is True

    def test_describe_is_not_behavioral(self):
        assert is_behavioral("Describe the authentication flow") is False

    def test_explain_is_not_behavioral(self):
        assert is_behavioral("Explain how the routing works") is False

    def test_list_endpoints_is_not_behavioral(self):
        assert is_behavioral("List all API endpoints") is False

    def test_parse_verb_is_behavioral(self):
        assert is_behavioral("Parse configuration from YAML file") is True

    def test_validate_verb_is_behavioral(self):
        assert is_behavioral("Validate input against schema") is True

    def test_early_return_is_behavioral(self):
        assert is_behavioral("Add early return for invalid state") is True
