"""Tests for remediate_parser.py -- fixture-based, 3+ format variants.

Format variants tested:
1. reflect-merged.md (with Remediation Status column)
2. merged-validation-report.md (without Remediation Status column)
3. Individual reflect-*.md reports (fallback dedup path)
"""

import pytest

from superclaude.cli.roadmap.models import Finding, VALID_FINDING_STATUSES
from superclaude.cli.roadmap.remediate_parser import (
    parse_validation_report,
    parse_individual_reports,
)


# ── Fixtures: Format Variant 1 -- reflect-merged.md ─────────────────────

REFLECT_MERGED_FIXTURE = """\
---
blocking_issues_count: 2
warnings_count: 1
tasklist_ready: false
validation_mode: adversarial
validation_agents: 'opus-architect, haiku-analyzer'
remediation_pass: true
findings_fixed: 2
findings_out_of_scope: 1
---

## Agreement Table

| Finding ID | Agent A (Opus) | Agent B (Haiku) | Agreement Category | Remediation Status |
|---|---|---|---|---|
| F-01: interleave_ratio type mismatch | INFO | BLOCKING | CONFLICT | **FIXED** — replaced string with numeric |
| F-02: milestone model mismatch | -- | BLOCKING | ONLY_B | **FIXED** — Phase 5 added |
| F-03: pre-impl no code deliverables | WARNING | -- | ONLY_A | **OUT_OF_SCOPE** — acceptable by design |

## Consolidated Findings

### BLOCKING

**F-01 [BLOCKING] Schema: `interleave_ratio` frontmatter is wrong type**
- Location: `test-strategy.md:1-4`
- Evidence: Frontmatter uses string '1:2', but spec defines numeric ratio in [0.1, 1.0].
- Agreement: CONFLICT (Agent A: INFO, Agent B: BLOCKING). Escalated to BLOCKING.
- Fix guidance: Replace the string with the computed numeric value (0.80 or 1.0).

**F-02 [BLOCKING] Cross-file consistency: milestone model mismatch**
- Location: `roadmap.md:23, 359-363` vs `test-strategy.md:2, 10-80`
- Evidence: Roadmap has 5 phases, test-strategy has 6 milestones.
- Agreement: ONLY_B.
- Fix guidance: Add Release Readiness phase to roadmap or remove Milestone 5.

### WARNING

**F-03 [WARNING] Interleave: Pre-impl phase has no code deliverables**
- Location: `roadmap.md:§2`
- Evidence: Pre-impl contains decisions but no testable code.
- Agreement: ONLY_A. Flagged for awareness.
- Fix guidance: Acceptable by design. No action required.
"""


# ── Fixtures: Format Variant 2 -- merged-validation-report.md ───────────

MERGED_VALIDATION_FIXTURE = """\
---
blocking_issues_count: 1
warnings_count: 2
tasklist_ready: false
validation_mode: adversarial
validation_agents: 'opus-architect, haiku-analyzer'
---

## Agreement Table

| Finding ID | Description | Agent A (opus) | Agent B (haiku) | Agreement Category |
|---|---|---|---|---|
| F-01 | Timeline contradiction | FOUND (BLOCKING) | FOUND (INFO) | CONFLICT |
| F-02 | NFR-001 allocation mismatch | FOUND (WARNING) | -- | ONLY_A |
| F-03 | P4.1 compound deliverable | FOUND (WARNING) | -- | ONLY_A |

## Consolidated Findings

### BLOCKING

- **[F-01] [BLOCKING] Structure: Internal timeline/effort contradiction**
  - Location: `roadmap.md:Executive Summary` vs `roadmap.md:Timeline Summary`
  - Evidence: Executive Summary states 11 sprints, Timeline Summary states 10 sprints.
  - Fix guidance: Update Executive Summary to match Timeline Summary.

### WARNING

- **[F-02] [WARNING] Cross-file consistency: NFR-001 requirement-to-phase allocation mismatch**
  - Location: `roadmap.md:Phase 1` vs `test-strategy.md:Milestone B`
  - Evidence: Roadmap allocates NFR-001 to Phase 1, but Phase 1 has no semantic gates.
  - Fix guidance: Move NFR-001 from Phase 1 to Phase 2 requirements.

- **[F-03] [WARNING] Decomposition: P4.1 is compound (3 distinct pipeline stages)**
  - Location: `roadmap.md:P4.1 Retrospective-to-Spec Pipeline`
  - Evidence: Three separate actions: extraction, conversion, injection.
  - Fix guidance: Split into P4.1a/b/c.
"""


# ── Fixtures: Format Variant 3 -- Individual reflect-*.md reports ───────

INDIVIDUAL_REPORT_A = """\
---
blocking_issues_count: 1
warnings_count: 1
tasklist_ready: false
---

## Findings

- **[BLOCKING] Schema**: `interleave_ratio` wrong type for a ratio field.
  - Location: `test-strategy.md:2-3`
  - Evidence: Stores string '1:2', should be numeric 1.0.
  - Fix guidance: Change to numeric value.

- **[WARNING] Traceability**: P1.3 lacks requirement citation.
  - Location: `roadmap.md:64-65`
  - Evidence: P1.3 cites only SC-006 but no FR/NFR.
  - Fix guidance: Add FR-006 to P1.3.
"""

INDIVIDUAL_REPORT_B = """\
---
blocking_issues_count: 1
warnings_count: 1
tasklist_ready: false
---

## Findings

- **[BLOCKING] Schema**: interleave_ratio stored with wrong type.
  - Location: `test-strategy.md:2-3`
  - Evidence: Validation spec defines numeric ratio but frontmatter uses string.
  - Fix guidance: Replace with numeric 1.0 in frontmatter.

- **[WARNING] Decomposition**: P0.3 is compound.
  - Location: `roadmap.md:51-58`
  - Evidence: Bundles seam mapping, validator classification, architecture evaluation.
  - Fix guidance: Split P0.3 into separate deliverables.
"""


# ── Fixtures: Negative test cases ───────────────────────────────────────

EMPTY_REPORT = """\
---
blocking_issues_count: 0
warnings_count: 0
---

## Summary

No issues found.
"""

MISSING_FIELDS_REPORT = """\
## Consolidated Findings

### BLOCKING

**[BLOCKING] : **
- Location: somewhere
"""

MALFORMED_REPORT = """\
This is not a validation report at all.
Just some random markdown text.
"""


# ═══════════════════════════════════════════════════════════════
# Test classes
# ═══════════════════════════════════════════════════════════════


class TestFindingDataclass:
    """Tests for the Finding dataclass itself."""

    def test_default_status_is_pending(self):
        f = Finding(
            id="F-01", severity="BLOCKING", dimension="Schema",
            description="test", location="file:1", evidence="ev",
            fix_guidance="fix",
        )
        assert f.status == "PENDING"

    def test_all_valid_statuses(self):
        for status in VALID_FINDING_STATUSES:
            f = Finding(
                id="F-01", severity="BLOCKING", dimension="d",
                description="d", location="l", evidence="e",
                fix_guidance="fg", status=status,
            )
            assert f.status == status

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="Invalid Finding status"):
            Finding(
                id="F-01", severity="BLOCKING", dimension="d",
                description="d", location="l", evidence="e",
                fix_guidance="fg", status="INVALID",
            )

    def test_default_files_affected_empty(self):
        f = Finding(
            id="F-01", severity="BLOCKING", dimension="d",
            description="d", location="l", evidence="e",
            fix_guidance="fg",
        )
        assert f.files_affected == []

    def test_default_agreement_category_empty(self):
        f = Finding(
            id="F-01", severity="BLOCKING", dimension="d",
            description="d", location="l", evidence="e",
            fix_guidance="fg",
        )
        assert f.agreement_category == ""

    def test_all_ten_fields_present(self):
        f = Finding(
            id="F-01", severity="BLOCKING", dimension="Schema",
            description="desc", location="file.py:1",
            evidence="evidence text", fix_guidance="fix it",
            files_affected=["file.py"], status="PENDING",
            agreement_category="BOTH_AGREE",
        )
        assert f.id == "F-01"
        assert f.severity == "BLOCKING"
        assert f.dimension == "Schema"
        assert f.description == "desc"
        assert f.location == "file.py:1"
        assert f.evidence == "evidence text"
        assert f.fix_guidance == "fix it"
        assert f.files_affected == ["file.py"]
        assert f.status == "PENDING"
        assert f.agreement_category == "BOTH_AGREE"


class TestPrimaryParserReflectMerged:
    """Format variant 1: reflect-merged.md with Remediation Status column."""

    def test_extracts_correct_count(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        assert len(findings) == 3

    def test_blocking_findings(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        blocking = [f for f in findings if f.severity == "BLOCKING"]
        assert len(blocking) == 2

    def test_warning_findings(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        warnings = [f for f in findings if f.severity == "WARNING"]
        assert len(warnings) == 1

    def test_finding_ids(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        ids = {f.id for f in findings}
        assert ids == {"F-01", "F-02", "F-03"}

    def test_dimensions_extracted(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "Schema" in by_id["F-01"].dimension
        assert "Cross-file" in by_id["F-02"].dimension
        assert "Interleave" in by_id["F-03"].dimension

    def test_location_extracted(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "test-strategy.md" in by_id["F-01"].location

    def test_fix_guidance_extracted(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "Replace" in by_id["F-01"].fix_guidance

    def test_files_affected_extracted(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "test-strategy.md" in by_id["F-01"].files_affected

    def test_remediation_status_overlay_fixed(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-01"].status == "FIXED"
        assert by_id["F-02"].status == "FIXED"

    def test_remediation_status_overlay_skipped(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-03"].status == "SKIPPED"

    def test_agreement_category_from_table(self):
        findings = parse_validation_report(REFLECT_MERGED_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-01"].agreement_category == "CONFLICT"
        assert by_id["F-02"].agreement_category == "ONLY_B"
        assert by_id["F-03"].agreement_category == "ONLY_A"


class TestPrimaryParserMergedValidation:
    """Format variant 2: merged-validation-report.md without Remediation Status."""

    def test_extracts_correct_count(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        assert len(findings) == 3

    def test_finding_ids(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        ids = {f.id for f in findings}
        assert ids == {"F-01", "F-02", "F-03"}

    def test_all_status_pending(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        for f in findings:
            assert f.status == "PENDING"

    def test_blocking_severity(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-01"].severity == "BLOCKING"

    def test_warning_severity(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-02"].severity == "WARNING"
        assert by_id["F-03"].severity == "WARNING"

    def test_agreement_categories(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert by_id["F-01"].agreement_category == "CONFLICT"
        assert by_id["F-02"].agreement_category == "ONLY_A"

    def test_files_from_location(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "roadmap.md" in by_id["F-01"].files_affected

    def test_evidence_extracted(self):
        findings = parse_validation_report(MERGED_VALIDATION_FIXTURE)
        by_id = {f.id: f for f in findings}
        assert "11 sprints" in by_id["F-01"].evidence


class TestFallbackParserDedup:
    """Format variant 3: Individual reflect-*.md with fallback dedup."""

    def test_dedup_reduces_duplicates(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        # 2 unique findings from A + 2 from B, but Schema findings overlap
        # -> Should produce 3 findings (1 merged Schema + 1 Traceability + 1 Decomposition)
        assert len(findings) == 3

    def test_dedup_keeps_higher_severity(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        schema_findings = [f for f in findings if "Schema" in f.dimension]
        assert len(schema_findings) == 1
        assert schema_findings[0].severity == "BLOCKING"

    def test_dedup_merges_guidance(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        schema_findings = [f for f in findings if "Schema" in f.dimension]
        assert len(schema_findings) == 1
        # Guidance should contain text from both reports
        guidance = schema_findings[0].fix_guidance
        assert "numeric" in guidance.lower()

    def test_non_matching_kept(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        dims = {f.dimension for f in findings}
        assert "Traceability" in dims
        assert "Decomposition" in dims

    def test_single_report_no_dedup(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A])
        assert len(findings) == 2

    def test_empty_reports_list(self):
        findings = parse_individual_reports([])
        assert findings == []

    def test_all_statuses_pending(self):
        findings = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        for f in findings:
            assert f.status == "PENDING"


class TestParserNegativeCases:
    """Negative tests: missing fields, malformed input, empty reports."""

    def test_empty_report_raises(self):
        with pytest.raises(ValueError, match="No findings extracted"):
            parse_validation_report(EMPTY_REPORT)

    def test_malformed_report_raises(self):
        with pytest.raises(ValueError, match="No findings extracted"):
            parse_validation_report(MALFORMED_REPORT)

    def test_fallback_empty_reports_returns_empty(self):
        result = parse_individual_reports([EMPTY_REPORT, MALFORMED_REPORT])
        assert result == []

    def test_pure_function_no_side_effects(self):
        """Parser should not modify its input or produce side effects."""
        text = REFLECT_MERGED_FIXTURE
        original = text[:]
        parse_validation_report(text)
        assert text == original


class TestParserPurityGuarantee:
    """Verify parser functions are pure (NFR-004)."""

    def test_parse_validation_report_is_deterministic(self):
        r1 = parse_validation_report(REFLECT_MERGED_FIXTURE)
        r2 = parse_validation_report(REFLECT_MERGED_FIXTURE)
        assert len(r1) == len(r2)
        for f1, f2 in zip(r1, r2):
            assert f1.id == f2.id
            assert f1.severity == f2.severity

    def test_parse_individual_reports_is_deterministic(self):
        r1 = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        r2 = parse_individual_reports([INDIVIDUAL_REPORT_A, INDIVIDUAL_REPORT_B])
        assert len(r1) == len(r2)
