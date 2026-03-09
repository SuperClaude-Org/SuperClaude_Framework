---
deliverable: D-0043
task: T05.07
status: PASS
date: 2026-03-09
---

# D-0043: Historical Artifact Replay Results

## Summary

70 artifacts from `.dev/releases/complete/` were replayed against v2.20 stricter
gates. **44 passed, 26 failed**.

All failures are **expected** (artifact quality issues from pre-frontmatter era),
not gate bugs.

## Failure Analysis

### Category: Missing YAML Frontmatter (25 failures)

Releases prior to v2.17 used markdown `## Metadata` sections instead of YAML
frontmatter. The STRICT and STANDARD gates require `---` delimited frontmatter.

| Affected Releases | Affected Gate | Count |
|-------------------|---------------|-------|
| v1.0-mcp-installer | EXTRACT, MERGE, TEST_STRATEGY | 3 |
| v1.4-roadmap-gen | EXTRACT, MERGE, TEST_STRATEGY | 3 |
| v1.7-adversarial | MERGE | 1 |
| v2.0-roadmap-v2 | MERGE, TEST_STRATEGY | 2 |
| v2.01 through v2.13 (roadmap.md only) | MERGE | 10+ |
| v2.10-spec-panel-v2 | EXTRACT, MERGE | 2 |

**Classification**: Expected — pre-frontmatter format artifacts

### Category: Missing Frontmatter Fields (3 failures)

- `v2.0-roadmap-v2/extraction.md`: Missing `generated` field
- `v2.05-sprint-cli-specification/extraction.md`: Missing `nonfunctional_requirements`
- `v2.0-roadmap-v2/test-strategy.md`: Missing `validation_milestones`

**Classification**: Expected — early extraction format used fewer fields

### Category: Zero Unexpected Failures

No gate bugs found. All 26 failures trace to artifact quality issues from
before the current frontmatter protocol was established.

## Pass Results

All artifacts from v2.17+ (when frontmatter protocol was adopted) pass all gates:

| Release | Artifacts | Status |
|---------|-----------|--------|
| v2.17-roadmap-reliability (pipeline-output/) | 6/6 | All PASS |
| v2.18-cli-portify-v2 | 6/6 | All PASS |
| v2.19-roadmap-validate | 6/6 | All PASS (1 cross-ref warning) |

## Migration Planning Recommendations

1. **No migration needed for v2.17+ artifacts** — all pass current gates
2. **Pre-v2.17 artifacts**: Historical record only; no migration recommended
   since they predate the frontmatter protocol
3. **Cross-reference warnings**: Warning-only mode correctly avoids blocking
   on "See section 6" style references in v2.19 roadmap
4. **Gate strictness is backward-compatible** with all artifacts produced
   under the current frontmatter protocol
