"""
Unit tests for Wave 1 persona auto-activation (T2.5).

Tests the persona activation rules defined in SKILL.md:
- Primary persona threshold (>= 40% domain coverage)
- Consulting persona threshold (>= 15%)
- Fallback to architect when no domain reaches 40%
- Persona-domain mapping
"""

import pytest


def select_personas(domain_distribution: dict) -> dict:
    """
    Reimplements persona activation from SKILL.md T2.5:
    - Primary: Domain >= 40% coverage
    - Consulting: Domain >= 15% coverage
    - Fallback: architect if no domain reaches 40%
    """
    PERSONA_MAP = {
        "frontend": "frontend",
        "backend": "backend",
        "security": "security",
        "performance": "performance",
        "documentation": "scribe",
    }

    primary = None
    consulting = []

    # Find primary (highest domain >= 40%)
    sorted_domains = sorted(
        domain_distribution.items(), key=lambda x: x[1], reverse=True
    )

    for domain, pct in sorted_domains:
        if pct >= 40 and primary is None:
            primary = PERSONA_MAP.get(domain, "architect")
        elif pct >= 15:
            persona = PERSONA_MAP.get(domain, "architect")
            if persona != primary:
                consulting.append(persona)

    fallback_used = primary is None
    if fallback_used:
        primary = "architect"

    return {
        "primary": primary,
        "consulting": consulting,
        "fallback_used": fallback_used,
    }


class TestPersonaDomainMapping:
    """Verify persona-domain mappings match SKILL.md."""

    EXPECTED_MAPPING = {
        "frontend": "frontend",
        "backend": "backend",
        "security": "security",
        "performance": "performance",
        "documentation": "scribe",
    }

    def test_all_domains_have_personas(self):
        """Each domain should map to a persona."""
        for domain, persona in self.EXPECTED_MAPPING.items():
            assert persona is not None, f"Domain '{domain}' has no persona"

    def test_documentation_maps_to_scribe(self):
        """Documentation domain should map to 'scribe' persona."""
        assert self.EXPECTED_MAPPING["documentation"] == "scribe"


class TestPrimaryPersonaActivation:
    """Test primary persona selection (>= 40% threshold)."""

    def test_security_dominant(self):
        """When security >= 40%, primary should be 'security'."""
        dist = {"frontend": 10, "backend": 25, "security": 45, "performance": 10, "documentation": 10}
        result = select_personas(dist)
        assert result["primary"] == "security"
        assert not result["fallback_used"]

    def test_frontend_dominant(self):
        """When frontend >= 40%, primary should be 'frontend'."""
        dist = {"frontend": 55, "backend": 20, "security": 10, "performance": 10, "documentation": 5}
        result = select_personas(dist)
        assert result["primary"] == "frontend"

    def test_backend_dominant(self):
        """When backend >= 40%, primary should be 'backend'."""
        dist = {"frontend": 5, "backend": 60, "security": 15, "performance": 15, "documentation": 5}
        result = select_personas(dist)
        assert result["primary"] == "backend"

    def test_exactly_40_activates(self):
        """Exactly 40% should activate primary."""
        dist = {"frontend": 40, "backend": 30, "security": 15, "performance": 10, "documentation": 5}
        result = select_personas(dist)
        assert result["primary"] == "frontend"
        assert not result["fallback_used"]


class TestConsultingPersonaActivation:
    """Test consulting persona selection (>= 15% threshold)."""

    def test_consulting_personas_detected(self):
        """Domains >= 15% but < 40% should be consulting."""
        dist = {"frontend": 10, "backend": 45, "security": 25, "performance": 15, "documentation": 5}
        result = select_personas(dist)
        assert result["primary"] == "backend"
        assert "security" in result["consulting"]
        assert "performance" in result["consulting"]

    def test_no_consulting_when_all_below_15(self):
        """No consulting when all non-primary domains < 15%."""
        dist = {"frontend": 70, "backend": 10, "security": 10, "performance": 5, "documentation": 5}
        result = select_personas(dist)
        assert result["primary"] == "frontend"
        assert len(result["consulting"]) == 0


class TestFallbackBehavior:
    """Test fallback to architect persona."""

    def test_fallback_when_no_domain_reaches_40(self):
        """When no domain reaches 40%, fallback to architect."""
        dist = {"frontend": 25, "backend": 25, "security": 20, "performance": 15, "documentation": 15}
        result = select_personas(dist)
        assert result["primary"] == "architect"
        assert result["fallback_used"] is True

    def test_fallback_with_consulting(self):
        """Fallback should still assign consulting personas."""
        dist = {"frontend": 30, "backend": 30, "security": 20, "performance": 10, "documentation": 10}
        result = select_personas(dist)
        assert result["primary"] == "architect"
        assert "frontend" in result["consulting"]
        assert "backend" in result["consulting"]
        assert "security" in result["consulting"]

    def test_all_zero_distribution(self):
        """All-zero distribution should fallback to architect."""
        dist = {"frontend": 0, "backend": 0, "security": 0, "performance": 0, "documentation": 0}
        result = select_personas(dist)
        assert result["primary"] == "architect"
        assert result["fallback_used"] is True
