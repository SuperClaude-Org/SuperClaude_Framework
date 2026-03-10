"""
Pytest configuration and shared fixtures for sc-roadmap tests.

These tests validate the sc-roadmap SKILL.md content — verifying that
the algorithms, patterns, and conventions documented in the skill
definition are correct and consistent.
"""

import os
import re

import pytest

# Path to the SKILL.md file (source of truth)
SKILL_MD_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "src",
    "superclaude",
    "skills",
    "sc-roadmap",
    "SKILL.md",
)

# Alternate installed path
INSTALLED_SKILL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    ".claude",
    "skills",
    "sc-roadmap",
    "SKILL.md",
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture(scope="session")
def skill_md_content():
    """Load SKILL.md content once for all tests."""
    path = SKILL_MD_PATH
    if not os.path.exists(path):
        path = INSTALLED_SKILL_PATH
    if not os.path.exists(path):
        pytest.skip("SKILL.md not found at source or installed path")
    with open(path, "r") as f:
        return f.read()


@pytest.fixture(scope="session")
def skill_md_path():
    """Return the resolved path to SKILL.md."""
    path = SKILL_MD_PATH
    if not os.path.exists(path):
        path = INSTALLED_SKILL_PATH
    return path


@pytest.fixture
def sample_spec_path():
    """Path to the sample specification fixture."""
    return os.path.join(FIXTURES_DIR, "sample_spec.md")


@pytest.fixture
def minimal_spec_path():
    """Path to the minimal specification fixture."""
    return os.path.join(FIXTURES_DIR, "minimal_spec.md")


@pytest.fixture
def invalid_spec_path():
    """Path to the invalid specification fixture."""
    return os.path.join(FIXTURES_DIR, "invalid_spec.md")


@pytest.fixture
def sample_spec_content(sample_spec_path):
    """Load sample spec content."""
    with open(sample_spec_path, "r") as f:
        return f.read()


@pytest.fixture
def minimal_spec_content(minimal_spec_path):
    """Load minimal spec content."""
    with open(minimal_spec_path, "r") as f:
        return f.read()


@pytest.fixture
def invalid_spec_content(invalid_spec_path):
    """Load invalid spec content."""
    with open(invalid_spec_path, "r") as f:
        return f.read()


# -- Algorithm reimplementations from SKILL.md for testing --


@pytest.fixture
def domain_keywords():
    """Domain keyword definitions from SKILL.md T2.3."""
    return {
        "frontend": {
            "keywords": [
                "UI", "components", "UX", "accessibility", "responsive",
                "React", "Vue", "Angular", "CSS", "HTML", "component",
                "layout", "design", "user interface", "form", "button", "modal",
            ],
            "weight": 1.0,
        },
        "backend": {
            "keywords": [
                "API", "database", "services", "infrastructure", "server",
                "endpoint", "REST", "GraphQL", "microservices", "authentication",
                "middleware", "controller", "model", "repository",
            ],
            "weight": 1.0,
        },
        "security": {
            "keywords": [
                "auth", "encryption", "compliance", "vulnerabilities", "tokens",
                "OAuth", "JWT", "RBAC", "permissions", "audit", "penetration",
                "OWASP", "security", "authorization", "credentials",
            ],
            "weight": 1.2,
        },
        "performance": {
            "keywords": [
                "optimization", "caching", "scaling", "latency", "throughput",
                "CDN", "load balancing", "profiling", "benchmark", "memory",
                "CPU", "response time",
            ],
            "weight": 1.0,
        },
        "documentation": {
            "keywords": [
                "guides", "references", "migration", "docs", "README", "wiki",
                "tutorial", "manual", "specification", "documentation",
            ],
            "weight": 0.8,
        },
    }


@pytest.fixture
def complexity_factors():
    """Complexity factor definitions from SKILL.md T2.4."""
    return {
        "requirement_count": {
            "weight": 0.25,
            "scoring": {
                (1, 5): 0.2,
                (6, 10): 0.4,
                (11, 20): 0.6,
                (21, 35): 0.8,
                (36, float("inf")): 1.0,
            },
        },
        "dependency_depth": {
            "weight": 0.25,
            "scoring": {
                (0, 0): 0.1,
                (1, 2): 0.3,
                (3, 5): 0.5,
                (6, 10): 0.7,
                (11, float("inf")): 1.0,
            },
        },
        "domain_spread": {
            "weight": 0.20,
            "scoring": {
                (1, 1): 0.2,
                (2, 2): 0.4,
                (3, 3): 0.6,
                (4, 4): 0.8,
                (5, float("inf")): 1.0,
            },
        },
        "risk_severity": {
            "weight": 0.15,
            "scoring_labels": {
                "no_risks": 0.1,
                "low_risks_only": 0.3,
                "medium_risks": 0.5,
                "high_risks": 0.7,
                "critical_risks": 1.0,
            },
        },
        "scope_size": {
            "weight": 0.15,
            "scoring_labels": {
                "small": 0.2,
                "medium": 0.4,
                "large": 0.6,
                "xlarge": 0.8,
                "massive": 1.0,
            },
        },
    }
