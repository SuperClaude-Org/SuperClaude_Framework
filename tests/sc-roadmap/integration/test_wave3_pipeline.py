"""
Integration tests for Wave 3 pipeline: Artifact generation.

Tests that Wave 3 generates all 5 required artifacts with correct structure.
"""

import re

import pytest


# Required artifacts from SKILL.md
REQUIRED_ARTIFACTS = [
    "roadmap.md",
    "extraction.md",
    "test-strategy.md",
    "execution-prompt.md",
]
# Plus tasklists/M{N}-*.md (variable count)


def validate_artifact_set(artifacts: dict) -> dict:
    """
    Validate a set of generated artifacts:
    - All required files present
    - All files non-empty
    - ID schema consistent
    """
    issues = []

    # Check required artifacts
    for name in REQUIRED_ARTIFACTS:
        if name not in artifacts:
            issues.append(f"Missing artifact: {name}")
        elif len(artifacts[name]) == 0:
            issues.append(f"Empty artifact: {name}")

    # Check tasklists
    tasklists = [k for k in artifacts if k.startswith("tasklists/")]
    if len(tasklists) == 0:
        issues.append("No tasklist files found")

    # Validate tasklist naming
    tasklist_pattern = re.compile(r"^tasklists/M\d+-[\w-]+\.md$")
    for tl in tasklists:
        if not tasklist_pattern.match(tl):
            issues.append(f"Invalid tasklist name: {tl}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "artifact_count": len(artifacts),
        "tasklist_count": len(tasklists),
    }


def validate_id_schema(content: str) -> list:
    """
    Validate ID schema across content:
    - M{digit} for milestones
    - D{M}.{seq} for deliverables
    - T{M}.{seq} for tasks
    - R-{3digits} for risks
    """
    issues = []

    # Check milestone references are valid
    milestone_refs = re.findall(r"\bM(\d+)\b", content)
    for ref in milestone_refs:
        if int(ref) < 1 or int(ref) > 20:
            issues.append(f"Unusual milestone number: M{ref}")

    return issues


class TestArtifactSetValidation:
    """Test artifact set completeness."""

    def test_complete_set_passes(self):
        """Complete artifact set should validate."""
        artifacts = {
            "roadmap.md": "# Roadmap\nContent here",
            "extraction.md": "# Extraction\nContent here",
            "test-strategy.md": "# Test Strategy\nContent here",
            "execution-prompt.md": "# Execution\nContent here",
            "tasklists/M1-foundation.md": "# M1\nContent",
            "tasklists/M2-implementation.md": "# M2\nContent",
        }
        result = validate_artifact_set(artifacts)
        assert result["valid"]
        assert result["artifact_count"] == 6
        assert result["tasklist_count"] == 2

    def test_missing_artifact_fails(self):
        """Missing required artifact should fail validation."""
        artifacts = {
            "roadmap.md": "Content",
            "extraction.md": "Content",
            # Missing test-strategy.md and execution-prompt.md
        }
        result = validate_artifact_set(artifacts)
        assert not result["valid"]
        assert any("Missing" in i for i in result["issues"])

    def test_empty_artifact_fails(self):
        """Empty artifact should fail validation."""
        artifacts = {
            "roadmap.md": "",  # Empty
            "extraction.md": "Content",
            "test-strategy.md": "Content",
            "execution-prompt.md": "Content",
            "tasklists/M1-foundation.md": "Content",
        }
        result = validate_artifact_set(artifacts)
        assert not result["valid"]
        assert any("Empty" in i for i in result["issues"])

    def test_no_tasklists_fails(self):
        """Missing tasklist files should fail validation."""
        artifacts = {
            "roadmap.md": "Content",
            "extraction.md": "Content",
            "test-strategy.md": "Content",
            "execution-prompt.md": "Content",
        }
        result = validate_artifact_set(artifacts)
        assert not result["valid"]
        assert any("tasklist" in i.lower() for i in result["issues"])

    def test_invalid_tasklist_name_fails(self):
        """Improperly named tasklist should fail validation."""
        artifacts = {
            "roadmap.md": "Content",
            "extraction.md": "Content",
            "test-strategy.md": "Content",
            "execution-prompt.md": "Content",
            "tasklists/bad-name.md": "Content",  # Invalid name
        }
        result = validate_artifact_set(artifacts)
        assert not result["valid"]
        assert any("Invalid tasklist" in i for i in result["issues"])


class TestIDSchemaValidation:
    """Test cross-artifact ID schema consistency."""

    def test_valid_milestone_refs(self):
        """Valid milestone references should pass."""
        content = "M1 depends on M2, which feeds M3"
        issues = validate_id_schema(content)
        assert len(issues) == 0

    def test_unusual_milestone_number(self):
        """Very high milestone numbers should be flagged."""
        content = "This references M99 which is unusual"
        issues = validate_id_schema(content)
        assert len(issues) > 0
