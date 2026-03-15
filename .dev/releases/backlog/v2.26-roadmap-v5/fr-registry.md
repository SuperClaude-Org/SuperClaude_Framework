---
title: "v2.25 FR/NFR Registry — Canonical Sequence"
version: "1.0"
created: 2026-03-14
sources:
  - approved-immediate.md   (5 issues: W-1, W-ADV-1, W-3, W-2, W-4+W-5)
  - approved-shortterm.md   (6 issues: Y-2, N-1, N-4, Y-3, Y-1, W-ADV-2)
  - approved-longterm.md    (4 issues: W-ADV-2 ext, W-ADV-4, W-ADV-3, N-2 ext)
---

# v2.25 FR/NFR Registry — Canonical Sequence

## 1. Pre-existing spec numbers (do not reassign)

These FR/NFR numbers are defined in `v2.25-spec-merged.md` and must be preserved exactly as-is.
They are listed here as reference anchors so new assignments do not collide.

| Number | Status | Known Location | Notes |
|--------|--------|----------------|-------|
| FR-001 … FR-015 | EXISTING | Various §§ | Do not touch |
| FR-016 | EXISTING | §4.3 | spec-fidelity prompt base FR |
| FR-017 … FR-019 | EXISTING | Various §§ | Do not touch |
| FR-020 | EXISTING (amended) | §5.2 | deviation-analysis step insertion in `_build_steps()` |
| FR-021 | EXISTING (amended) | §5.3 | deviation-analysis prompt classification |
| FR-022 | EXISTING | §5.x | SLIPs always routed to fix_roadmap (invariant) |
| FR-023 … FR-033 | EXISTING | Various §§ | Do not touch |
| FR-034 | EXISTING (amended) | §7.2 | `deviations_to_findings()` severity map |
| FR-035 … FR-037 | EXISTING | Various §§ | Do not touch |
| FR-038 | EXISTING | §x | `_get_all_step_ids()` step ID list |
| FR-039 | EXISTING | §x | `_save_state()` remediation counter |
| FR-040 | EXISTING | §x | `_check_remediation_budget()` |
| FR-041 | EXISTING | §8.4 | remediation cycle bounding (predecessor to FR-041 prose) |
| FR-042 | EXISTING (amended) | §8.5 | `_print_terminal_halt()` |
| FR-043 … FR-053 | EXISTING | Various §§ | Do not touch |
| FR-054 | EXISTING | §3.5 | ALL_GATES registry update (primary assignment) |
| FR-055 | EXISTING | §3.5 | Possible second ALL_GATES entry — **VERIFY IN MERGED SPEC** |
| NFR-001 … NFR-005 | EXISTING | Various §§ | Do not touch |
| NFR-006 | EXISTING (full replacement) | §14.2 | spec-fidelity gate downgrade behavioral consequences |
| NFR-007 … NFR-010 | EXISTING | Various §§ | Do not touch |

> **CRITICAL**: Before assigning any new FR numbers, verify the actual highest FR number
> in `v2.25-spec-merged.md`. The provisional assignments below assume **FR-054 is the
> current maximum** (per the Immediate amendments FR Number Collision Note). If FR-055
> is also used in the merged spec, shift all new FRs below by +1.

---

## 2. Conflict Map: Raw assignments from each source file

The three brainstorm files independently assigned FR/NFR numbers in the range FR-055–FR-065
and NFR-011–NFR-014. These assignments **conflict** — the same number is used for different
purposes across files.

### FR-055

| Source | Assignment |
|--------|-----------|
| approved-immediate.md (ISSUE 1 body text) | Spec-patch auto-resume cycle retirement (`_apply_resume_after_spec_patch()` deletion) |
| approved-immediate.md (ISSUE 5 correction) | **Retracts the above** — FR-055 is already taken by ALL_GATES; retirement FR should be FR-059 |
| approved-longterm.md (ISSUE 1) | `roadmap_hash` injection into `spec-deviations.md` frontmatter by executor |
| approved-immediate.md FR/NFR table | FR-059 (retirement) — FR-055 not listed as a new FR |
| approved-longterm.md FR/NFR table | FR-055 = roadmap_hash injection |

**CONFLICT**: Long-term assigns FR-055 to `roadmap_hash` injection. Immediate documents
acknowledge FR-055 may already be taken by ALL_GATES in the spec. Resolution: **defer to
pre-existing spec scan** (see §1 note). If FR-055 is free, long-term's assignment wins.
If occupied, long-term's FR-055 shifts to next available number.

### FR-056

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | `_routing_consistent_with_slip_count()` semantic check function (gates.py) |
| approved-shortterm.md | `_extract_fidelity_deviations()` — markdown table parser spec |
| approved-longterm.md | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` |

**3-WAY CONFLICT** — all three assign FR-056 to completely different functions.

### FR-057

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | `DEVIATION_ANALYSIS_GATE` gains third semantic check (`routing_consistent_with_slip_count`) |
| approved-shortterm.md | `_parse_routing_list()` — comma-separated frontmatter parser spec |
| approved-longterm.md | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping annotate-deviations |

**3-WAY CONFLICT**

### FR-058

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | `deviations_to_findings()` secondary ValueError guard (defense-in-depth) |
| approved-shortterm.md | `_extract_deviation_classes()` — deviation classification table parser spec |
| approved-longterm.md | `_check_remediation_budget()` coerces `remediation_attempts` to int |

**3-WAY CONFLICT**

### FR-059

| Source | Assignment |
|--------|-----------|
| approved-immediate.md (FR/NFR table) | Spec-patch auto-resume cycle retirement (corrected from FR-055) |
| approved-shortterm.md | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` |
| approved-longterm.md | Deviation IDs SHALL match `DEV-\d+` pattern; prompt constraint |

**3-WAY CONFLICT**

### FR-060

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `_write_ambiguous_items_report()` — extraction of AMBIGUOUS entries |
| approved-longterm.md | `_routing_ids_valid(content: str) -> bool` — validates routing field tokens against `^DEV-\d+$` |

**2-WAY CONFLICT** (immediate does not use this number)

### FR-061

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `_write_ambiguous_items_report()` writes summary even if body parsing fails |
| approved-longterm.md | `_parse_routing_list()` validates tokens against `^DEV-\d+$`; cross-checks len vs total_analyzed |

**2-WAY CONFLICT**

### FR-062

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `_extract_unfixed_findings(content: str) -> list[dict]` |
| approved-longterm.md | Spec-patch cycle and remediation budget remain independent; no global counter |

**2-WAY CONFLICT**

### FR-063

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `build_certify_metadata()` signature extended with `unfixed_details` param |
| approved-longterm.md | `_print_terminal_halt()` includes spec-patch-also-fired note (v2.26 impl) |

**2-WAY CONFLICT**

### FR-064

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `.roadmap-state.json` `certify.unfixed_details` schema specification |
| approved-longterm.md | (not assigned) |

**No conflict** — shortterm only.

### FR-065

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | `_apply_resume()` mtime check: force re-run of `annotate-deviations` if `mtime(roadmap.md) > mtime(spec-deviations.md)` |
| approved-longterm.md | (not assigned) |

**No conflict** — shortterm only.

### FR-016a

| Source | Assignment |
|--------|-----------|
| approved-shortterm.md | spec-fidelity prompt SHALL produce `## Deviations Found` markdown table |
| approved-immediate.md | (not assigned — this is a §4.3 amendment) |
| approved-longterm.md | (not assigned) |

**No conflict** — shortterm only. Note: uses letter suffix `a` to amend existing FR-016.

---

### NFR-011

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | Spec-patch auto-resume cycle not present in v2.25; operators use explicit --resume (§14.7) |
| approved-shortterm.md | `unfixed_details` entries contain exactly `"id"` and `"description"` string fields; 500-char truncation |
| approved-longterm.md | `_check_annotate_deviations_freshness()` is fail-closed; missing file/field/error returns False |

**3-WAY CONFLICT**

### NFR-012

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | No v2.25 pipeline step reads `dev-*-accepted-deviation.md`; consumed only by accept-spec-change CLI |
| approved-shortterm.md | LOW exclusion is a clarification, not behavior change; `low_severity_count` retained |
| approved-longterm.md | `_save_state()` coerces `existing_attempts` to int before incrementing |

**3-WAY CONFLICT**

### NFR-013

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | mtime comparison uses `st_mtime` float; 1-second resolution limitation accepted |
| approved-longterm.md | Combined max recovery attempts SHALL NOT exceed 3; enforced by independent caps |

**2-WAY CONFLICT**

### NFR-014

| Source | Assignment |
|--------|-----------|
| approved-immediate.md | (not assigned) |
| approved-shortterm.md | (not assigned) |
| approved-longterm.md | `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5 |

**No conflict** — longterm only.

---

## 3. Canonical Sequence Assignment

**Baseline assumption**: FR-054 is the highest existing FR number in the merged spec.
If this is wrong, shift all new FR numbers below starting from the actual max + 1.

**Ordering principle**: Immediate (critical blockers) → Short-term (Phase 2 delivery) →
Long-term (robustness). Within each tier, issues are ordered by their issue number.
Amended existing FRs keep their existing numbers; only the definitions change.

### New FR assignments (canonical)

| Canonical # | Source Tier | Source Issue | Original # in Source | Scope / Function |
|-------------|-------------|--------------|----------------------|------------------|
| **FR-016a** | Short-term | ISSUE 1 (Y-2) | FR-016a | spec-fidelity prompt SHALL produce `## Deviations Found` markdown table with 6-column header (§4.3 amendment) |
| **FR-055** | Long-term | ISSUE 1 (W-ADV-2) | FR-055 | Executor injects `roadmap_hash` into `spec-deviations.md` frontmatter after subprocess completes (§3.2) — **VERIFY: may conflict with existing spec FR-055** |
| **FR-056** | Immediate | ISSUE 2 (W-ADV-1) | FR-056 | `_routing_consistent_with_slip_count()` semantic check function added to `gates.py` (§5.5) |
| **FR-057** | Immediate | ISSUE 2 (W-ADV-1) | FR-057 | `DEVIATION_ANALYSIS_GATE` gains third semantic check `routing_consistent_with_slip_count` (§5.5) |
| **FR-058** | Immediate | ISSUE 2 (W-ADV-1) | FR-058 | `deviations_to_findings()` secondary ValueError guard when routing empty and slip_count > 0 (§7.2) |
| **FR-059** | Immediate | ISSUE 1 (W-1) | FR-059 (corrected from FR-055 draft) | Spec-patch auto-resume cycle retirement: delete `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, local vars, `auto_accept` param (§8.7 new) |
| **FR-060** | Short-term | ISSUE 1 (Y-2) | FR-056 | `_extract_fidelity_deviations()` — markdown table parser, edge cases, failure behavior (§7.2a) |
| **FR-061** | Short-term | ISSUE 1 (Y-2) | FR-057 | `_parse_routing_list()` — comma-separated frontmatter parser, edge cases, ID validation (§7.2a) |
| **FR-062** | Short-term | ISSUE 1 (Y-2) | FR-058 | `_extract_deviation_classes()` — deviation classification table parser, edge cases (§7.2a) |
| **FR-063** | Short-term | ISSUE 2 (N-1) | FR-059 | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` before halting (§8.3 new) |
| **FR-064** | Short-term | ISSUE 2 (N-1) | FR-060 | `_write_ambiguous_items_report()` — extraction of AMBIGUOUS entries, template stubs, failure behavior (§8.3 new) |
| **FR-065** | Short-term | ISSUE 2 (N-1) | FR-061 | `_write_ambiguous_items_report()` SHALL still write summary + instructions if body parsing fails (§8.3 new) |
| **FR-066** | Short-term | ISSUE 3 (N-4) | FR-062 | `_extract_unfixed_findings(content: str) -> list[dict]` — FAILED row extraction from certification table (§8.5 amended) |
| **FR-067** | Short-term | ISSUE 3 (N-4) | FR-063 | `build_certify_metadata()` signature extended with `unfixed_details: list[dict] \| None = None` (§8.5 amended) |
| **FR-068** | Short-term | ISSUE 3 (N-4) | FR-064 | `.roadmap-state.json` `certify.unfixed_details` schema specification (§8.5 amended) |
| **FR-069** | Short-term | ISSUE 6 (W-ADV-2) | FR-065 | `_apply_resume()` mtime check: force re-run of `annotate-deviations` if `mtime(roadmap.md) > mtime(spec-deviations.md)` (§8.2 amended) |
| **FR-070** | Long-term | ISSUE 1 (W-ADV-2) | FR-056 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` (§3.5) |
| **FR-071** | Long-term | ISSUE 1 (W-ADV-2) | FR-057 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` before skipping `annotate-deviations`; fail-closed (§8.2) |
| **FR-072** | Long-term | ISSUE 2 (W-ADV-4) | FR-058 | `_check_remediation_budget()` coerces `remediation_attempts` to int; logs WARNING on corrupt value; treats as 0 (§8.4) |
| **FR-073** | Long-term | ISSUE 3 (W-ADV-3) | FR-059 | Deviation IDs SHALL match `DEV-\d+`; prompt instructs agent to use only IDs as they appear in `spec-fidelity.md` (§5.4) |
| **FR-074** | Long-term | ISSUE 3 (W-ADV-3) | FR-060 | `_routing_ids_valid(content: str) -> bool` added to `gates.py`; validates routing field tokens; registered as STRICT check on `DEVIATION_ANALYSIS_GATE` (§5.5) |
| **FR-075** | Long-term | ISSUE 3 (W-ADV-3) | FR-061 | `_parse_routing_list()` validates tokens against `^DEV-\d+$`; cross-checks len vs `total_analyzed` (§7.2) |
| **FR-076** | Long-term | ISSUE 4 (N-2 ext) | FR-062 | Spec-patch cycle and remediation budget remain independent; no global budget counter introduced (§8.7 new, doc-only) |
| **FR-077** | Long-term | ISSUE 4 (N-2 ext) | FR-063 | `_print_terminal_halt()` SHALL include spec-patch-also-fired note when both mechanisms exhausted; state mechanism deferred to v2.26 (§8.7 new) |

### Amended existing FR assignments (canonical)

These keep their existing numbers but have modified definitions:

| Number | Source Tier | Original Location | Amendment Summary |
|--------|-------------|-------------------|-------------------|
| **FR-016** | Short-term ISSUE 1 | §4.3 | Amended by FR-016a (new subsection requirement for `## Deviations Found` table) |
| **FR-020** | Short-term ISSUE 5 | §5.2 | Replace §5.2 code stub with corrected version using real variable names and keyword args |
| **FR-021** | Short-term ISSUE 4 | §5.3 | Explicitly exclude LOW deviations from deviation-analysis classification and routing |
| **FR-034** | Short-term ISSUE 4 | §7.2 | Remove LOW→INFO mapping; severity_map is `{"HIGH": "BLOCKING", "MEDIUM": "WARNING"}` only |
| **FR-042** | Short-term ISSUE 3 | §8.5 | `_print_terminal_halt()` outputs per-finding details from `unfixed_details` in state |
| **NFR-006** | Immediate ISSUE 5 | §14.2 | Full replacement: forward compat, behavioral flip, dormancy, state file compat |

### New NFR assignments (canonical)

| Canonical # | Source Tier | Source Issue | Original # in Source | Scope |
|-------------|-------------|--------------|----------------------|-------|
| **NFR-011** | Immediate | ISSUE 1 (W-1) | NFR-011 | Spec-patch auto-resume cycle not present in v2.25; operators use explicit --resume (§14.7 new) |
| **NFR-012** | Immediate | ISSUE 3 (W-3) | NFR-012 | No v2.25 pipeline step reads `dev-*-accepted-deviation.md`; consumed only by accept-spec-change CLI (§14.8 new) |
| **NFR-013** | Short-term | ISSUE 3 (N-4) | NFR-011 | `unfixed_details` entries contain exactly `"id"` and `"description"` fields; description truncated at 500 chars (§8.5 amended) |
| **NFR-014** | Short-term | ISSUE 4 (Y-3) | NFR-012 | LOW exclusion is a clarification, not behavior change; `low_severity_count` in spec-fidelity frontmatter retained (§14) |
| **NFR-015** | Short-term | ISSUE 6 (W-ADV-2) | NFR-013 | mtime comparison uses `st_mtime` float; 1-second resolution limitation accepted; workaround documented (§8.2 amended) |
| **NFR-016** | Long-term | ISSUE 1 (W-ADV-2) | NFR-011 | `_check_annotate_deviations_freshness()` is fail-closed; missing file/field/error returns False, never raises (§8.2) |
| **NFR-017** | Long-term | ISSUE 2 (W-ADV-4) | NFR-012 | `_save_state()` coerces `existing_attempts` to int before incrementing; always writes Python int (§8.4) |
| **NFR-018** | Long-term | ISSUE 4 (N-2 ext) | NFR-013 | Combined max recovery attempts SHALL NOT exceed 3; enforced by independent caps (§8.7 new, doc-only) |
| **NFR-019** | Long-term | ISSUE 4 (N-2 ext) | NFR-014 | `_apply_resume_after_spec_patch()` and `_spec_patch_cycle_count` SHALL be retained unchanged in v5; not removed (§14.7 new) |

---

## 4. Before/After Mapping Table

For each FR/NFR number used in an approved file, this table shows the number as written in
the source file and the canonical replacement number to use in the merged spec.

### approved-immediate.md

| # As Written | Canonical # | Change Needed? | Notes |
|-------------|-------------|----------------|-------|
| FR-055 (ISSUE 1 body §8.7 draft) | **FR-059** | YES — replace throughout §8.7 and §14.7 draft language | ISSUE 5 explicitly corrects this; all "FR-055" in §8.7 and §14.7 draft text must become FR-059 |
| FR-055 (ISSUE 4 §11.5 table, FR Reference column for 6 RETIRED rows) | **FR-059** | YES | Same correction as above |
| FR-055 (ISSUE 5 cross-reference body) | **FR-059** | YES — "FR-055 (new, §8.7)" should read FR-059 | Already noted in ISSUE 5 but the header still says FR-055 |
| FR-056 (ISSUE 2) | **FR-056** | No change | Canonical assignment confirmed |
| FR-057 (ISSUE 2) | **FR-057** | No change | Canonical assignment confirmed |
| FR-058 (ISSUE 2) | **FR-058** | No change | Canonical assignment confirmed |
| FR-059 (FR/NFR table — retirement) | **FR-059** | No change | Canonical assignment confirmed (this is the corrected number) |
| NFR-006 | **NFR-006** | No change (existing, full replacement) | Canonical |
| NFR-011 | **NFR-011** | No change | Canonical |
| NFR-012 | **NFR-012** | No change | Canonical |

### approved-shortterm.md

| # As Written | Canonical # | Change Needed? | Notes |
|-------------|-------------|----------------|-------|
| FR-016a | **FR-016a** | No change | Unique suffix notation; no conflict |
| FR-020 (amended) | **FR-020** | No change | Amended existing |
| FR-021 (amended) | **FR-021** | No change | Amended existing |
| FR-034 (amended) | **FR-034** | No change | Amended existing |
| FR-042 (amended) | **FR-042** | No change | Amended existing |
| FR-056 (ISSUE 1 — `_extract_fidelity_deviations`) | **FR-060** | YES | Conflicts with immediate FR-056 |
| FR-057 (ISSUE 1 — `_parse_routing_list` spec) | **FR-061** | YES | Conflicts with immediate FR-057 |
| FR-058 (ISSUE 1 — `_extract_deviation_classes`) | **FR-062** | YES | Conflicts with immediate FR-058 |
| FR-059 (ISSUE 2 — AMBIGUOUS_ITEMS.md write) | **FR-063** | YES | Conflicts with immediate FR-059 |
| FR-060 (ISSUE 2 — `_write_ambiguous_items_report`) | **FR-064** | YES | Conflicts with longterm FR-060 |
| FR-061 (ISSUE 2 — fallback summary write) | **FR-065** | YES | Conflicts with longterm FR-061 |
| FR-062 (ISSUE 3 — `_extract_unfixed_findings`) | **FR-066** | YES | Conflicts with longterm FR-062 |
| FR-063 (ISSUE 3 — `build_certify_metadata` sig) | **FR-067** | YES | Conflicts with longterm FR-063 |
| FR-064 (ISSUE 3 — unfixed_details schema) | **FR-068** | No renumber needed (unique in shortterm) | But assign FR-068 for sequential clarity |
| FR-065 (ISSUE 6 — mtime check) | **FR-069** | YES — renumber for sequential clarity | |
| NFR-011 (ISSUE 3 — unfixed_details entry schema) | **NFR-013** | YES | Conflicts with immediate NFR-011 |
| NFR-012 (ISSUE 4 — LOW exclusion clarification) | **NFR-014** | YES | Conflicts with immediate NFR-012 |
| NFR-013 (ISSUE 6 — mtime limitation) | **NFR-015** | YES | Conflicts with longterm NFR-013 |

### approved-longterm.md

| # As Written | Canonical # | Change Needed? | Notes |
|-------------|-------------|----------------|-------|
| FR-055 (ISSUE 1 — roadmap_hash injection) | **FR-055** | Conditional — verify existing spec | If FR-055 is already used in spec, shift to next available after FR-077 |
| FR-056 (ISSUE 1 — ANNOTATE_DEVIATIONS_GATE field) | **FR-070** | YES | Conflicts with immediate FR-056 |
| FR-057 (ISSUE 1 — `_apply_resume` freshness check) | **FR-071** | YES | Conflicts with immediate FR-057 |
| FR-058 (ISSUE 2 — int coercion in budget check) | **FR-072** | YES | Conflicts with immediate FR-058 |
| FR-059 (ISSUE 3 — DEV-\d+ ID constraint) | **FR-073** | YES | Conflicts with immediate FR-059 |
| FR-060 (ISSUE 3 — `_routing_ids_valid`) | **FR-074** | YES | Conflicts with shortterm FR-060 |
| FR-061 (ISSUE 3 — `_parse_routing_list` token validation) | **FR-075** | YES | Conflicts with shortterm FR-061 |
| FR-062 (ISSUE 4 — independent counters doc) | **FR-076** | YES | Conflicts with shortterm FR-062 |
| FR-063 (ISSUE 4 — terminal halt dual-mechanism note) | **FR-077** | YES | Conflicts with shortterm FR-063 |
| NFR-011 (ISSUE 1 — fail-closed freshness check) | **NFR-016** | YES | Conflicts with immediate NFR-011 |
| NFR-012 (ISSUE 2 — _save_state int coercion) | **NFR-017** | YES | Conflicts with immediate NFR-012 |
| NFR-013 (ISSUE 4 — max 3 attempts cap) | **NFR-018** | YES | Conflicts with shortterm NFR-013 |
| NFR-014 (ISSUE 4 — spec-patch cycle retained) | **NFR-019** | YES — renumber for sequential clarity | |

---

## 5. Canonical FR/NFR List (complete, ordered)

All numbers that must appear in `v2.25-spec-merged.md` after amendment merging.

### Amended existing FRs

| Number | Section | Summary |
|--------|---------|---------|
| FR-016 (amended via FR-016a) | §4.3 | spec-fidelity prompt adds `## Deviations Found` table requirement |
| FR-020 (amended) | §5.2 | Replace code stub with corrected variable names and keyword args |
| FR-021 (amended) | §5.3 | Explicitly exclude LOW deviations from classification and routing |
| FR-034 (amended) | §7.2 | severity_map = `{"HIGH": "BLOCKING", "MEDIUM": "WARNING"}` only |
| FR-042 (amended) | §8.5 | `_print_terminal_halt()` outputs per-finding details from unfixed_details |
| NFR-006 (full replacement) | §14.2 | Spec-fidelity gate downgrade: behavioral consequences (a)–(d) |

### New FRs (canonical sequence)

| Number | Section | Tier | v2.25/v2.26 | Summary |
|--------|---------|------|-------------|---------|
| FR-016a | §4.3 | Short-term | v2.25 | spec-fidelity prompt SHALL produce `## Deviations Found` 6-column markdown table |
| FR-055 | §3.2 | Long-term | v2.25 | Executor injects `roadmap_hash` into `spec-deviations.md` frontmatter (**conditional on spec scan**) |
| FR-056 | §5.5 | Immediate | v2.25 | `_routing_consistent_with_slip_count()` semantic check function in `gates.py` |
| FR-057 | §5.5 | Immediate | v2.25 | `DEVIATION_ANALYSIS_GATE` gains third semantic check |
| FR-058 | §7.2 | Immediate | v2.25 | `deviations_to_findings()` secondary ValueError guard |
| FR-059 | §8.7 (new) | Immediate | v2.25 | Spec-patch auto-resume cycle retirement |
| FR-060 | §7.2a | Short-term | v2.25 | `_extract_fidelity_deviations()` — markdown table parser spec |
| FR-061 | §7.2a | Short-term | v2.25 | `_parse_routing_list()` — comma-separated parser, edge cases, ID validation |
| FR-062 | §7.2a | Short-term | v2.25 | `_extract_deviation_classes()` — deviation classification table parser |
| FR-063 | §8.3 (new) | Short-term | v2.25 | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` |
| FR-064 | §8.3 (new) | Short-term | v2.25 | `_write_ambiguous_items_report()` spec |
| FR-065 | §8.3 (new) | Short-term | v2.25 | `_write_ambiguous_items_report()` fallback behavior |
| FR-066 | §8.5 (amended) | Short-term | v2.25 | `_extract_unfixed_findings(content: str) -> list[dict]` |
| FR-067 | §8.5 (amended) | Short-term | v2.25 | `build_certify_metadata()` extended with `unfixed_details` param |
| FR-068 | §8.5 (amended) | Short-term | v2.25 | `.roadmap-state.json` `certify.unfixed_details` JSON schema |
| FR-069 | §8.2 (amended) | Short-term | v2.25 | `_apply_resume()` mtime staleness check for `spec-deviations.md` |
| FR-070 | §3.5 | Long-term | v2.25 | `ANNOTATE_DEVIATIONS_GATE` required fields include `roadmap_hash` |
| FR-071 | §8.2 | Long-term | v2.25 | `_apply_resume()` calls `_check_annotate_deviations_freshness()` |
| FR-072 | §8.4 | Long-term | v2.25 | `_check_remediation_budget()` int coercion for `remediation_attempts` |
| FR-073 | §5.4 | Long-term | v2.25 | Deviation IDs SHALL match `DEV-\d+` pattern |
| FR-074 | §5.5 | Long-term | v2.25 | `_routing_ids_valid(content: str) -> bool` in `gates.py`, STRICT check on DEVIATION_ANALYSIS_GATE |
| FR-075 | §7.2 | Long-term | v2.25 | `_parse_routing_list()` token validation against `^DEV-\d+$`; cross-check vs total_analyzed |
| FR-076 | §8.7 (new) | Long-term | v2.25 (doc) | Spec-patch cycle and remediation budget remain independent |
| FR-077 | §8.7 (new) | Long-term | v2.26 (impl) | `_print_terminal_halt()` dual-mechanism exhaustion note |

### New NFRs (canonical sequence)

| Number | Section | Tier | v2.25/v2.26 | Summary |
|--------|---------|------|-------------|---------|
| NFR-011 | §14.7 (new) | Immediate | v2.25 | Spec-patch auto-resume not present in v2.25; operators use explicit --resume |
| NFR-012 | §14.8 (new) | Immediate | v2.25 | No v2.25 pipeline step reads `dev-*-accepted-deviation.md` |
| NFR-013 | §8.5 (amended) | Short-term | v2.25 | `unfixed_details` entries: exactly `"id"` + `"description"` fields; 500-char truncation |
| NFR-014 | §14 | Short-term | v2.25 | LOW exclusion is a clarification; `low_severity_count` retained in spec-fidelity frontmatter |
| NFR-015 | §8.2 (amended) | Short-term | v2.25 | mtime comparison: `st_mtime` float; 1-second resolution limitation accepted |
| NFR-016 | §8.2 | Long-term | v2.25 | `_check_annotate_deviations_freshness()` fail-closed behavior |
| NFR-017 | §8.4 | Long-term | v2.25 | `_save_state()` int coercion; `remediation_attempts` always written as Python int |
| NFR-018 | §8.7 (new) | Long-term | v2.25 (doc) | Combined max 3 automatic recovery attempts; enforced by independent caps |
| NFR-019 | §14.7 (new) | Long-term | v2.25 (doc) | `_apply_resume_after_spec_patch()` retained unchanged in v5 |

---

## 6. Action Checklist Before Spec Merge

1. **VERIFY FR-054/FR-055 in merged spec**: Run `grep -n "FR-05[45]" v2.25-spec-merged.md`.
   - If FR-055 is unused: long-term ISSUE 1's `roadmap_hash` injection takes FR-055 as canonical.
   - If FR-055 is already defined: shift the roadmap_hash injection to FR-078 and all subsequent
     long-term FRs shift by +1 accordingly.

2. **Fix approved-immediate.md before applying to spec**:
   - Replace every occurrence of `FR-055` in ISSUE 1's §8.7 draft text → `FR-059`
   - Replace every occurrence of `FR-055` in ISSUE 1's §14.7 draft text → `FR-059`
   - Replace every `FR-055` in ISSUE 4's §11.5 table FR Reference column → `FR-059`
   - Replace the `FR-055 (new, §8.7)` cross-reference header in ISSUE 5 → `FR-059 (new, §8.7)`

3. **Renumber approved-shortterm.md before applying to spec** (per Before/After table above):
   FR-056→FR-060, FR-057→FR-061, FR-058→FR-062, FR-059→FR-063, FR-060→FR-064,
   FR-061→FR-065, FR-062→FR-066, FR-063→FR-067, FR-064→FR-068, FR-065→FR-069,
   NFR-011→NFR-013, NFR-012→NFR-014, NFR-013→NFR-015

4. **Renumber approved-longterm.md before applying to spec** (per Before/After table above):
   FR-056→FR-070, FR-057→FR-071, FR-058→FR-072, FR-059→FR-073, FR-060→FR-074,
   FR-061→FR-075, FR-062→FR-076, FR-063→FR-077,
   NFR-011→NFR-016, NFR-012→NFR-017, NFR-013→NFR-018, NFR-014→NFR-019

5. **Verify no gap or duplicate** in the sequence FR-055 through FR-077 (and NFR-011 through NFR-019)
   after applying all renumbers.

6. **Update shortterm Consolidated FR/NFR List** and **longterm Consolidated FR/NFR List** with
   canonical numbers before any implementation begins.

7. **Confirm v2.26 deferrals**: FR-077 and NFR-019 are spec-only in v2.25; implementation deferred.
   Add a `<!-- v2.26-impl -->` marker or equivalent when inserting these into the spec.
