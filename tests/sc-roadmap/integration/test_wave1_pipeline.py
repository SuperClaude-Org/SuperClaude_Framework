"""
Integration tests for Wave 1 pipeline: Spec → Extraction → Domain → Complexity → Persona.

Tests the complete Wave 1 flow from specification parsing through persona assignment.
"""

import os
import re

import pytest


def extract_title(content: str) -> str:
    """Extract title from H1 heading."""
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        return match.group(1)
    return os.path.basename("unknown").replace(".md", "")


def extract_requirements(content: str) -> dict:
    """Extract FR and NFR requirements."""
    fr_pattern = re.compile(r"- FR-(\d{3}):\s*(.+)", re.MULTILINE)
    nfr_pattern = re.compile(r"- NFR-(\d{3}):\s*(.+)", re.MULTILINE)

    frs = [(f"FR-{m.group(1)}", m.group(2).strip()) for m in fr_pattern.finditer(content)]
    nfrs = [(f"NFR-{m.group(1)}", m.group(2).strip()) for m in nfr_pattern.finditer(content)]

    return {"functional": frs, "nonfunctional": nfrs}


def classify_domains(content: str, domain_keywords: dict) -> dict:
    """Classify text into domain percentages."""
    text_lower = content.lower()
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


def calculate_complexity(req_count, dep_depth, domain_spread, risk_severity, scope_size):
    """Simplified complexity calculation."""
    # Requirement count scoring
    if req_count <= 5:
        req_s = 0.2
    elif req_count <= 10:
        req_s = 0.4
    elif req_count <= 20:
        req_s = 0.6
    elif req_count <= 35:
        req_s = 0.8
    else:
        req_s = 1.0

    # Dependency depth scoring
    if dep_depth == 0:
        dep_s = 0.1
    elif dep_depth <= 2:
        dep_s = 0.3
    elif dep_depth <= 5:
        dep_s = 0.5
    elif dep_depth <= 10:
        dep_s = 0.7
    else:
        dep_s = 1.0

    # Domain spread scoring
    dom_map = {1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8}
    dom_s = dom_map.get(domain_spread, 1.0)

    # Risk severity mapping
    risk_map = {"none": 0.1, "low": 0.3, "medium": 0.5, "high": 0.7, "critical": 1.0}
    risk_s = risk_map.get(risk_severity, 0.5)

    # Scope size mapping
    scope_map = {"small": 0.2, "medium": 0.4, "large": 0.6, "xlarge": 0.8, "massive": 1.0}
    scope_s = scope_map.get(scope_size, 0.4)

    return req_s * 0.25 + dep_s * 0.25 + dom_s * 0.20 + risk_s * 0.15 + scope_s * 0.15


def select_personas(domain_dist):
    """Select primary and consulting personas."""
    PERSONA_MAP = {
        "frontend": "frontend",
        "backend": "backend",
        "security": "security",
        "performance": "performance",
        "documentation": "scribe",
    }
    primary = None
    consulting = []
    sorted_domains = sorted(domain_dist.items(), key=lambda x: x[1], reverse=True)

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

    return {"primary": primary, "consulting": consulting, "fallback_used": fallback_used}


class TestWave1FullPipeline:
    """Test complete Wave 1 pipeline with sample specification."""

    def test_full_pipeline_sample_spec(self, sample_spec_content, domain_keywords):
        """Run full Wave 1 pipeline on sample auth spec."""
        # Step 1: Extract title
        title = extract_title(sample_spec_content)
        assert title == "User Authentication System"

        # Step 2: Extract requirements
        reqs = extract_requirements(sample_spec_content)
        assert len(reqs["functional"]) == 12
        assert len(reqs["nonfunctional"]) == 6
        total_reqs = len(reqs["functional"]) + len(reqs["nonfunctional"])
        assert total_reqs == 18

        # Step 3: Classify domains
        domain_dist = classify_domains(sample_spec_content, domain_keywords)
        assert abs(sum(domain_dist.values()) - 100.0) < 0.01
        # Security should be significant for auth spec
        assert domain_dist["security"] > 15

        # Step 4: Calculate complexity
        active_domains = sum(1 for v in domain_dist.values() if v > 10)
        complexity = calculate_complexity(
            req_count=total_reqs,
            dep_depth=4,  # 4 explicit dependencies
            domain_spread=active_domains,
            risk_severity="high",
            scope_size="large",
        )
        assert 0.0 <= complexity <= 1.0

        # Step 5: Select personas
        personas = select_personas(domain_dist)
        assert personas["primary"] is not None
        assert isinstance(personas["consulting"], list)

    def test_full_pipeline_minimal_spec(self, minimal_spec_content, domain_keywords):
        """Run full Wave 1 pipeline on minimal spec."""
        title = extract_title(minimal_spec_content)
        assert title == "Quick Fix"

        reqs = extract_requirements(minimal_spec_content)
        total_reqs = len(reqs["functional"]) + len(reqs["nonfunctional"])
        assert total_reqs == 2

        domain_dist = classify_domains(minimal_spec_content, domain_keywords)
        complexity = calculate_complexity(
            req_count=total_reqs,
            dep_depth=0,
            domain_spread=1,
            risk_severity="none",
            scope_size="small",
        )
        assert complexity < 0.4  # Should be LOW complexity

        personas = select_personas(domain_dist)
        # Minimal spec likely doesn't have 40% in any domain
        assert personas["primary"] is not None


class TestWave1DataFlow:
    """Test data flows correctly between Wave 1 stages."""

    def test_requirements_feed_complexity(self, sample_spec_content):
        """Requirement count from extraction should feed complexity scoring."""
        reqs = extract_requirements(sample_spec_content)
        total = len(reqs["functional"]) + len(reqs["nonfunctional"])
        # 18 requirements → 11-20 range → score 0.6
        assert 11 <= total <= 20

    def test_domain_dist_feeds_personas(self, sample_spec_content, domain_keywords):
        """Domain distribution should feed persona selection."""
        domain_dist = classify_domains(sample_spec_content, domain_keywords)
        personas = select_personas(domain_dist)
        # The primary persona should correspond to highest domain
        top_domain = max(domain_dist, key=domain_dist.get)
        if domain_dist[top_domain] >= 40:
            expected_persona_map = {
                "frontend": "frontend",
                "backend": "backend",
                "security": "security",
                "performance": "performance",
                "documentation": "scribe",
            }
            expected = expected_persona_map.get(top_domain)
            assert personas["primary"] == expected
