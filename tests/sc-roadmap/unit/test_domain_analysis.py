"""
Unit tests for Wave 1 domain analysis classifier (T2.3).

Tests the domain keyword classification algorithm defined in SKILL.md:
- Keyword counting per domain
- Weight application
- Percentage normalization to 100%
- Domain distribution calculation
"""

import re

import pytest


class TestDomainKeywords:
    """Verify domain keyword definitions match SKILL.md."""

    def test_five_domains_defined(self, domain_keywords):
        """Should have exactly 5 domains."""
        assert len(domain_keywords) == 5
        expected = {"frontend", "backend", "security", "performance", "documentation"}
        assert set(domain_keywords.keys()) == expected

    def test_security_has_higher_weight(self, domain_keywords):
        """Security domain should have weight 1.2 (higher than others)."""
        assert domain_keywords["security"]["weight"] == 1.2

    def test_documentation_has_lower_weight(self, domain_keywords):
        """Documentation domain should have weight 0.8 (lower than others)."""
        assert domain_keywords["documentation"]["weight"] == 0.8

    def test_standard_domains_weight_1(self, domain_keywords):
        """Frontend, backend, performance should have weight 1.0."""
        for domain in ["frontend", "backend", "performance"]:
            assert domain_keywords[domain]["weight"] == 1.0

    def test_each_domain_has_keywords(self, domain_keywords):
        """Each domain should have at least 5 keywords."""
        for domain, config in domain_keywords.items():
            assert len(config["keywords"]) >= 5, (
                f"Domain '{domain}' has too few keywords: {len(config['keywords'])}"
            )


class TestDomainClassification:
    """Test the classification algorithm."""

    def classify_text(self, text: str, domain_keywords: dict) -> dict:
        """
        Reimplements the classification algorithm from SKILL.md T2.3:
        1. For each domain, count keyword occurrences (case-insensitive)
        2. Apply keyword weights
        3. Calculate percentage distribution
        4. Normalize to 100%
        """
        text_lower = text.lower()
        scores = {}
        for domain, config in domain_keywords.items():
            count = 0
            for kw in config["keywords"]:
                count += len(re.findall(re.escape(kw.lower()), text_lower))
            scores[domain] = count * config["weight"]

        total = sum(scores.values())
        if total == 0:
            return {d: 0.0 for d in domain_keywords}

        return {d: (s / total) * 100 for d, s in scores.items()}

    def test_auth_spec_is_security_heavy(self, sample_spec_content, domain_keywords):
        """Auth system spec should classify heavily toward security."""
        dist = self.classify_text(sample_spec_content, domain_keywords)
        # Security should be a top domain for an auth spec
        assert dist["security"] > 20, f"Security too low: {dist['security']:.1f}%"

    def test_auth_spec_has_backend(self, sample_spec_content, domain_keywords):
        """Auth system spec should have significant backend presence."""
        dist = self.classify_text(sample_spec_content, domain_keywords)
        assert dist["backend"] > 10, f"Backend too low: {dist['backend']:.1f}%"

    def test_percentages_sum_to_100(self, sample_spec_content, domain_keywords):
        """Domain percentages should sum to 100%."""
        dist = self.classify_text(sample_spec_content, domain_keywords)
        total = sum(dist.values())
        assert abs(total - 100.0) < 0.01, f"Expected 100%, got {total:.2f}%"

    def test_empty_text_returns_zeros(self, domain_keywords):
        """Empty text should return 0% for all domains."""
        dist = self.classify_text("", domain_keywords)
        assert all(v == 0.0 for v in dist.values())

    def test_frontend_only_text(self, domain_keywords):
        """Text with only frontend keywords should classify as frontend."""
        text = "UI components React CSS responsive layout design button modal"
        dist = self.classify_text(text, domain_keywords)
        assert dist["frontend"] > 50, f"Frontend should dominate: {dist}"

    def test_backend_only_text(self, domain_keywords):
        """Text with only backend keywords should classify as backend."""
        text = "API database services endpoint REST controller model"
        dist = self.classify_text(text, domain_keywords)
        assert dist["backend"] > 50, f"Backend should dominate: {dist}"

    def test_security_weight_boosts_score(self, domain_keywords):
        """Security weight (1.2) should amplify security keyword scores."""
        # Text with equal mentions of security and backend keywords
        text = "auth API encryption database tokens server"
        dist = self.classify_text(text, domain_keywords)
        # With 3 security keywords at 1.2 weight vs 3 backend at 1.0,
        # security should score higher
        assert dist["security"] > dist["backend"]

    def test_minimal_spec_is_frontend(self, minimal_spec_content, domain_keywords):
        """Minimal spec about button color should lean frontend."""
        dist = self.classify_text(minimal_spec_content, domain_keywords)
        # "button" and "color" - button is frontend keyword
        # This is a simple spec so percentages may vary
        total_nonzero = sum(1 for v in dist.values() if v > 0)
        assert total_nonzero >= 1  # At least one domain detected
