# Spec Panel Review: FR-PORTIFY-WORKFLOW

**Spec**: `portify-release-spec.md`
**Date**: 2026-03-13
**Mode**: Critique | **Focus**: Correctness, Architecture
**Panel**: Nygard (lead), Fowler, Adzic, Crispin, Whittaker, Newman, Hohpe

---

## Quality Scores

| Dimension | Score | Rationale |
|---|---|---|
| Clarity | 8.5 | Excellent structure, well-organized sections, clear decision tables. Minor deductions for unspecified edge cases (empty input, dedup rules). |
| Completeness | 7.5 | All template sections present with substantive content. 1 CRITICAL gap (R3 on None skill), 7 MAJOR gaps (mostly boundary conditions and underspecified algorithms). |
| Testability | 8.0 | 32 tests planned with clear coverage matrix. Acceptance criteria on all 3 FRs are checkbox-formatted and verifiable. 5 missing boundary test cases. |
| Consistency | 8.0 | Internal consistency strong. Deductions for `str` vs `Path` type inconsistency and `to_dict()` serialization gap. |
| Overall | 8.0 | Strong spec with clean backward-compatible architecture. CRITICAL finding is easily fixable. Most MAJORs are boundary clarifications. |

---

## State Variable Registry

| Variable Name | Type | Initial Value | Invariant | Read Operations | Write Operations |
|---|---|---|---|---|---|
| `ResolvedTarget.command_path` | `Path \| None` | `None` | If not None, file must exist and be `.md` | `build_component_tree()`, `derive_cli_name()`, `to_flat_inventory()` | `resolve_target()` R1 |
| `ResolvedTarget.skill_dir` | `Path \| None` | `None` | If not None, dir must exist and contain `SKILL.md` | `build_component_tree()`, `to_flat_inventory()` | `resolve_target()` R2 |
| `ComponentTree.agents` | `list[AgentEntry]` | `[]` | Deduplicated by name; `found` reflects filesystem | `all_source_dirs`, `to_flat_inventory()`, `to_manifest_markdown()`, `component_count`, `total_lines` | `build_component_tree()` R3, `--include-agent` |
| `ComponentTree.warnings` | `list[str]` | `[]` | Append-only during resolution | `to_manifest_markdown()` | R1, R3, R5 |
| `PortifyConfig.component_tree` | `ComponentTree \| None` | `None` | Must be populated before Step 2 completes | `PortifyProcess` construction, artifact generation | `run_discover_component_tree()` |
| `ValidateConfigResult.warnings` | `list[dict]` | `[]` | NEW field -- not in current codebase | Callers of `validate_portify_config()` | Validation checks 5, 6 |
| `PortifyProcess._additional_dirs` | `list[Path]` | `[]` | All paths resolved; count <= 10 (or consolidated) | `_build_add_dir_args()` | `__init__()` |

---

## Guard Condition Boundary Table

| Guard | Location | Input Condition | Variable Value | Guard Result | Specified Behavior | Status |
|---|---|---|---|---|---|---|
| `resolve_target()` input | FR-1, Sec 4.5 R1 | Zero/Empty | `""` | Unspecified | Not specified | **GAP** |
| `resolve_target()` input | FR-1, Sec 4.5 R1 | One/Minimal | `"a"` | COMMAND_NAME | Searches `commands/a.md` -> ERR_TARGET_NOT_FOUND | OK |
| `resolve_target()` input | FR-1, Sec 4.5 R1 | Typical | `"roadmap"` | COMMAND_NAME | Search, resolve, extract skill | OK |
| `resolve_target()` input | FR-1, Sec 4.5 R1 | Sentinel: `"sc:"` | Empty after strip | Unspecified | Strip yields empty string | **GAP** |
| `resolve_target()` input | FR-1, Sec 4.5 R1 | Trailing slash | `"src/.../protocol/"` | SKILL_DIR | Path resolution handles it | OK |
| `resolve_target()` input | FR-1, Sec 4.5 R1 | Symlink | Symlink to skill dir | Unspecified | `resolve()` behavior undefined | **GAP** |
| Agent extraction | FR-2, Sec 4.5 R3 | Zero/Empty | Empty SKILL.md | No matches | Empty agents list | OK |
| Agent extraction | FR-2, Sec 4.5 R3 | Reserved word | `"self"`, `"None"` | Matches regex | No name validation | **GAP** |
| Agent extraction | FR-2, Sec 4.5 R3 | Typical | Multiple refs | All matched | Deduplicate, resolve | OK |
| `--include-agent` | FR-2, Sec 5.1 | Zero/Empty | `""` | Resolves empty name | Not specified | **GAP** |
| `--include-agent` | FR-2, Sec 5.1 | Duplicate of auto | Same agent name | Dedup? | Not specified | **GAP** |
| Dir cap guard | FR-3, NFR-5 | Zero | 0 dirs | No extra dirs | Works | OK |
| Dir cap guard | FR-3, NFR-5 | At threshold | 10 dirs | No warning | ">10" means 10 is OK | OK |
| Dir cap guard | FR-3, NFR-5 | Above threshold | 11 dirs | Warning + consolidation | Algorithm unspecified | **GAP** |
| `derive_cli_name()` | Sec 4.5 | Empty command file | `Path("empty.md")` | exists=True | Returns `"empty"` | OK |
| `to_dict()` | Sec 4.5 | New fields | `warnings=[{...}]` | Unspecified | Not serialized | **GAP** |

**GAP Count**: 8 entries with GAP status.

---

## Findings

### Critical (1)

| ID | Expert | Finding | Section |
|---|---|---|---|
| C-1 | Whittaker | **R3 (agent extraction) runs on None skill_dir when command has no paired skill.** Steps R3 and R4 read SKILL.md and scan subdirectories, but spec doesn't guard against `skill_dir = None`. Standalone commands (help.md, sc.md) would crash at R3. | FR-2, Sec 4.5 R3 |

**Recommendation**: Add explicit guard: "If `skill_dir is None`, skip R3 and R4. Set `agents = []`, `refs = []`, `rules = []`, `templates = []`, `scripts = []`."

### Major (7)

| ID | Expert | Finding | Section | Recommendation |
|---|---|---|---|---|
| M-1 | Whittaker | Empty string TARGET input behavior undefined | FR-1, Sec 5.1 | Add validation: reject empty/whitespace TARGET with clear error message before classification |
| M-2 | Whittaker | `"sc:"` prefix stripping yields empty string -- undefined | Sec 4.5 R1 | Add post-strip validation: if stripped name is empty, return ERR_TARGET_NOT_FOUND |
| M-3 | Whittaker | `--include-agent` dedup against auto-discovered agents unclear | FR-2 | State explicitly: "All agents (auto + manual) are deduplicated by name. Manual agents override auto-discovered `referenced_in` field." |
| M-4 | Nygard | Consolidation algorithm for >10 dirs unspecified | FR-3, NFR-5 | Define algorithm: common-prefix clustering with exposure-limit guard. E.g., "consolidated dir must not contain >3x the files of its constituent dirs" |
| M-5 | Nygard | Ambiguity rules for command-name vs skill-name collision undefined | FR-1 | Clarify: "Ambiguity only applies within the same input type class. A bare name matching both command and skill is NOT ambiguous -- command wins per command-first policy." |
| M-6 | Fowler | `ComponentEntry.path: str` vs new models using `Path` -- type inconsistency undocumented | Sec 4.5 | Acknowledge: "Existing `ComponentEntry` retains `path: str` for backward compat. New dataclasses use `Path`. `to_flat_inventory()` converts via `str()`." |
| M-7 | Newman/Crispin | `ValidateConfigResult.to_dict()` doesn't serialize new fields or `warnings` | Sec 4.5 | State whether new fields are included in `to_dict()` serialization. If yes, update the method spec. |

### Minor (3)

| ID | Expert | Finding | Section | Recommendation |
|---|---|---|---|---|
| m-1 | Whittaker | `resolution_log` has no size bound (accumulation risk) | Sec 4.5 | Low risk for single-target usage. Document assumption: "resolution_log is per-invocation, not accumulated across calls." |
| m-2 | Nygard | No timeout enforcement on NFR-1 (<1s resolution) | NFR-1 | Aspirational target is acceptable for pure-Python filesystem ops. Add monitoring note. |
| m-3 | Fowler | `PipelineConfig` base class omitted from dependency graph | Sec 4.4 | Add `models.py --> PipelineConfig (base)` to graph |

---

## Missing Test Cases (Crispin)

These 5 test cases should be added to Section 8.1:

| Test | File | Validates |
|---|---|---|
| `resolve_target()`: empty/whitespace input | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND for `""`, `" "`, `None` |
| `resolve_target()`: `"sc:"` prefix with empty name | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND after stripping |
| `resolve_target()`: standalone command (no skill) | `test_resolution.py` | R3/R4 skipped, agents=[], skill=None |
| `--include-agent` dedup against auto-discovered | `test_resolution.py` | Manual agent replaces auto-discovered, no duplicates |
| `ValidateConfigResult.to_dict()` new fields | `test_validate_config.py` | New fields and `warnings` present in dict output |

---

## Quantity Flow Diagram

```
[1 TARGET input] --> [resolve_target(): 1 ResolvedTarget]
                          |
                          v
                    [build_component_tree(): 1 ComponentTree]
                          |
                          +---> [to_flat_inventory(): 1 ComponentInventory]  (1:1)
                          +---> [to_manifest_markdown(): 1 manifest.md]      (1:1, optional)
                          +---> [all_source_dirs: N dirs (N <= 10)]           (1:N, capped)
                                      |
                                      v
                                [_build_add_dir_args(): N --add-dir args]    (N:N)
```

No dimensional mismatches. All stages preserve count or have explicit caps.

---

## Downstream Integration Points

| Source | Target | Data Flow |
|---|---|---|
| Guard Boundary Table (8 GAPs) | `sc:adversarial` AD-1 | GAP entries as priority invariant candidates |
| Whittaker Findings (C-1, M-1..M-3) | `sc:adversarial` AD-2 | Attack findings feed assumption challenges |
| Correctness findings | `sc:roadmap` RM-3 | C-1 informs risk-weighted prioritization |

---

## Panel Consensus

1. **Architecture is sound**: Single new module, backward-compatible wrappers, no step renumbering -- correct approach.
2. **Critical fix needed**: R3/R4 must guard against `skill_dir = None` before implementation begins.
3. **Boundary conditions need specification**: Empty input, prefix stripping edge cases, dedup rules, and consolidation algorithm should be defined to prevent implementation ambiguity.
4. **Type consistency should be documented**: The `str` vs `Path` convention difference between old and new models needs explicit acknowledgment.
5. **Spec is implementation-ready** after addressing C-1 and the M-1 through M-3 input validation gaps.
