# Agent 3: QA Assessment -- Group A Schema Integrity

**Perspective**: Testability and validation
**Core question**: "Can we write acceptance tests for this change? Does it introduce untestable requirements?"
**Date**: 2026-02-26

---

## PROPOSAL-006: Add missing schema for `new-tests-manifest.json`

**Verdict**: ACCEPT

**Rationale**: A defined schema is the foundation of testability. Without a schema, there is nothing to validate against. With the proposed schema, we can write:

**Acceptance tests**:
1. **Schema conformance**: Agent 4b output validates against the JSON schema (automated, deterministic).
2. **Required field presence**: Every record has `file_path`, `test_type`, `related_hypothesis_ids`, `status`.
3. **Cross-reference integrity**: Every `related_hypothesis_id` in the manifest exists in `base-selection.md` surviving hypotheses.
4. **Phase 5 consumption**: Agent 5b can parse the manifest and correlate every entry with a test file on disk.
5. **Status values**: `status` field is constrained to `new` or `modified` (enum validation).

**Testability score**: 0.95 -- Schemas are inherently testable via JSON Schema validation. Cross-reference tests are straightforward.

**Untestable requirements introduced**: None.

---

## PROPOSAL-007: Align Risk Surface schema with prompts and requirements

**Verdict**: MODIFY

**Rationale**: The testability of the two sub-proposals differs significantly.

**`overall_risk_score` alignment**:
- Testable: YES. We can verify Agent 0c output contains `overall_risk_score` (schema validation). We can verify the calculation method is documented and the value is a weighted average of category scores within [0.0, 1.0].
- Acceptance test: `assert risk_surface["overall_risk_score"] == weighted_average(category_scores)`

**`secrets_exposure` addition**:
- Testable: PARTIALLY. We can validate the field exists, but testing that the agent *correctly detects* secrets exposure requires ground-truth test fixtures with known secrets. This is a detection quality problem, not a schema problem.
- The proposal introduces a requirement that is hard to write deterministic acceptance tests for. How do we define "correctly identified secrets_exposure"? False negatives are undetectable without oracle data.
- This shifts the testing burden from schema validation (easy) to detection accuracy (hard).

**Modification**: Accept `overall_risk_score` alignment (fully testable). Reject `secrets_exposure` as it introduces a testability gap -- we cannot write meaningful acceptance tests for detection correctness without a curated test corpus that does not yet exist.

**Testability score**: 0.85 for `overall_risk_score` alone; drops to 0.50 if `secrets_exposure` is included.

---

## PROPOSAL-008: Strengthen `progress.json` for reproducibility and resume safety

**Verdict**: MODIFY

**Rationale**: Resume safety is inherently testable -- we can create controlled resume scenarios and verify behavior. However, each new required field adds a test dimension. The question is which fields produce meaningful test coverage.

**Per-field testability**:

| Field | Test Scenario | Deterministic? | Value |
|-------|---------------|----------------|-------|
| `spec_version` | Resume with mismatched version | Yes | Low (no version exists yet) |
| `run_id` | Log correlation | Yes | Low (observability, not correctness) |
| `target_paths` | Resume after changing target directory | Yes | HIGH |
| `git_head_or_snapshot` | Resume after git commit | Yes (in git repos) | HIGH |
| `phase_status_map` | Resume with partial phase completion | Yes | LOW (covered by existing fields) |
| `flags` mandatory | Resume without flags field | Yes | HIGH |

**Key acceptance tests enabled by the valuable fields**:
1. `target_paths`: Start run on `/path/A`, interrupt, move to `/path/B`, resume -> system detects mismatch and warns.
2. `git_head_or_snapshot`: Start run, `git commit` a change, resume -> system detects stale state.
3. `flags` mandatory: Create `progress.json` without `flags`, attempt resume -> validation fails with clear error.

**Modification**: Accept `target_paths`, `git_head_or_snapshot` (as optional for non-git), and `flags` mandatory. These enable the three highest-value test scenarios. Reject `spec_version`, `run_id`, `phase_status_map` -- they add test surface area without proportional quality signal.

**Testability score**: 0.80 for the recommended subset; 0.60 for the full proposal (diluted by low-value test dimensions).

---

## PROPOSAL-009: Make domain IDs stable across retries/resume

**Verdict**: ACCEPT

**Rationale**: This proposal is exceptionally testable. The core invariant is: "domain IDs must be identical across independent runs on the same codebase."

**Acceptance tests**:
1. **Determinism test**: Run Phase 0 twice on the same codebase. Assert `domain_id` values are identical (even if array order differs).
2. **Resume integrity test**: Run through Phase 1, interrupt, re-run Phase 0, resume Phase 1. Assert all hypothesis references still resolve.
3. **Cross-phase reference test**: For every `hypothesis_id` in `fix-proposal-H-{N}.md`, assert the domain portion resolves to a valid domain in `investigation-domains.json`.
4. **Stability under concurrency test**: Run Phase 0 with `--concurrency 1` and `--concurrency 10`. Assert same domain IDs.

**Negative test for the current design** (proving the bug exists):
- Run Phase 0 twice with `--concurrency 10`. If domain order differs, hypothesis IDs from run 1 are invalid in run 2. This test WILL fail under the current index-based scheme, confirming the bug.

**Testability score**: 0.95 -- The invariant is precise, deterministic, and automatable. No oracle problem.

**Untestable requirements introduced**: None. Deterministic hashing is a well-understood primitive.

---

## PROPOSAL-010: Enforce exactly three fix tiers with uniqueness constraints

**Verdict**: MODIFY

**Rationale**: The two sub-proposals have opposite testability profiles.

**Uniqueness constraint**:
- Testable: YES. `assert len(set(tier["tier"] for tier in fix_options)) == len(fix_options)`
- This is a one-line validation check. Deterministic, no oracle problem.

**"Exactly 3" constraint**:
- Testable: YES, but the test is degenerate. `assert len(fix_options) == 3`
- The deeper concern: testing that all 3 tiers are *meaningful* is NOT testable with schema validation. We cannot distinguish a genuine `robust` tier from a padded filler tier. This creates a false-positive risk: the schema test passes but the content is garbage.
- This is the classic "testing the letter of the law, not the spirit" problem. The schema validates structure; quality requires human review.

**Additionally**: If we enforce "exactly 3", we need a test for the edge case where an agent legitimately cannot produce 3 distinct tiers. What is the expected behavior? Force generation? Skip the proposal? The spec does not define this, creating an untestable requirement.

**Modification**: Accept uniqueness constraint (trivially testable, prevents real bug). Reject "exactly 3" (creates untestable quality requirement and undefined edge case). Add a test for `--fix-tier` fallback behavior: `--fix-tier robust` on a 2-tier proposal -> select `moderate` + emit warning.

**Testability score**: 0.90 for uniqueness + fallback; 0.55 for "exactly 3" (tests pass but meaning is unverifiable).

---

## PROPOSAL-021: Add multi-root path provenance to schemas

**Verdict**: ACCEPT

**Rationale**: Multi-root path provenance is highly testable because path resolution is deterministic.

**Acceptance tests**:
1. **Single-root invariant**: With one target path, `root_id`/`target_root` is consistent across all records.
2. **Multi-root disambiguation**: With two target paths that both contain `src/main.py`, assert that each path record unambiguously resolves to exactly one file.
3. **Cross-schema consistency**: For every `file` in `changes-manifest.json`, the `root_id` matches a valid root in the original invocation.
4. **Report rendering**: Final report paths render correctly with root prefix when multiple roots are present.
5. **Round-trip test**: Emit path with provenance -> resolve back to absolute path -> verify file exists.

**Edge case tests**:
- Overlapping paths (e.g., `/repo` and `/repo/subdir`) -> verify no double-counting.
- Symlinked roots -> verify canonical resolution.

**Testability score**: 0.90 -- Path resolution is deterministic and automatable. Edge cases are well-defined.

**Untestable requirements introduced**: None. Path provenance is a data enrichment, not a behavioral change.

---

## Summary Table

| Proposal | Verdict | Testability | Key Test | Concern |
|----------|---------|-------------|----------|---------|
| P-006 | ACCEPT | 0.95 | Schema validation + cross-ref integrity | None |
| P-007 | MODIFY | 0.85/0.50 | Calculation verification; secrets detection is oracle-dependent | secrets_exposure untestable without fixtures |
| P-008 | MODIFY | 0.80 | Resume mismatch detection scenarios | Low-value fields dilute test coverage |
| P-009 | ACCEPT | 0.95 | Determinism across runs; negative test proves the bug | None |
| P-010 | MODIFY | 0.90/0.55 | Uniqueness is trivial; "exactly 3" quality is unverifiable | "Exactly 3" creates false-positive testing |
| P-021 | ACCEPT | 0.90 | Multi-root disambiguation; round-trip resolution | None |
