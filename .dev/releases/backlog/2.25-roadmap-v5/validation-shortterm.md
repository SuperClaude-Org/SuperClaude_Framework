STATUS: FAIL
TOTAL_ISSUES_SOURCE: 7
TOTAL_ISSUES_EXTRACTED: 6

MISSES: ## Consolidated FR/NFR List
TRUNCATIONS: NONE
PHANTOMS: NONE
CONTAMINATIONS: NONE

=== CORRECTION FOR: ## Consolidated FR/NFR List ===

This section contains no "Recommended Approach" or "Draft Spec Language" subsections.
The entire section was absent from the extracted file. Verbatim content from source follows.

## Consolidated FR/NFR List

| ID | Section | Issue | Type | Summary |
|----|---------|-------|------|---------|
| FR-016a | §4.3 | ISSUE 1 | FR | spec-fidelity prompt SHALL produce `## Deviations Found` markdown table with 6-column header |
| FR-056 | §7.2a | ISSUE 1 | FR | Specify `_extract_fidelity_deviations()` — markdown table parser, edge cases, failure behavior |
| FR-057 | §7.2a | ISSUE 1 | FR | Specify `_parse_routing_list()` — comma-separated frontmatter parser, edge cases, ID validation |
| FR-058 | §7.2a | ISSUE 1 | FR | Specify `_extract_deviation_classes()` — deviation classification table parser, edge cases |
| FR-034 (amended) | §7.2 | ISSUE 4 | FR | LOW deviations excluded from `deviations_to_findings()`; remove LOW→INFO mapping; `severity_map` is `{"HIGH": "BLOCKING", "MEDIUM": "WARNING"}` only |
| FR-021 (amended) | §5.3 | ISSUE 4 | FR | Explicitly exclude LOW deviations from `deviation-analysis` classification and routing tables |
| FR-020 (amended) | §5.2 | ISSUE 5 | FR | Replace §5.2 snippet with corrected version using real variable names and keyword arguments matching §5.3 signature |
| FR-059 | §8.3 | ISSUE 2 | FR | On `ambiguous_count > 0` gate failure, write `AMBIGUOUS_ITEMS.md` before halting |
| FR-060 | §8.3 | ISSUE 2 | FR | Specify `_write_ambiguous_items_report()` — extraction of AMBIGUOUS entries, template stubs, failure behavior |
| FR-061 | §8.3 | ISSUE 2 | FR | `_write_ambiguous_items_report()` SHALL still write summary + instructions if body parsing fails |
| FR-062 | §8.5 (amended) | ISSUE 3 | FR | Specify `_extract_unfixed_findings(content: str) -> list[dict]` — FAILED row extraction from certification table |
| FR-063 | §8.5 (amended) | ISSUE 3 | FR | Update `build_certify_metadata()` signature with `unfixed_details: list[dict] | None = None` |
| FR-064 | §8.5 (amended) | ISSUE 3 | FR | Specify `.roadmap-state.json` `certify.unfixed_details` schema — `[{"id": str, "description": str}]` |
| FR-065 | §8.2 (amended) | ISSUE 6 | FR | `_apply_resume()` mtime check: force re-run of `annotate-deviations` if `mtime(roadmap.md) > mtime(spec-deviations.md)` |
| NFR-011 | §8.5 (amended) | ISSUE 3 | NFR | `unfixed_details` entries contain exactly `"id"` and `"description"` string fields; description truncated at 500 chars |
| NFR-012 | §14 | ISSUE 4 | NFR | LOW exclusion is a clarification, not behavior change; `low_severity_count` in spec-fidelity frontmatter retained |
| NFR-013 | §8.2 (amended) | ISSUE 6 | NFR | mtime comparison uses `st_mtime` float; 1-second resolution limitation accepted; workaround documented |

### Phase Assignment for New FRs/NFRs

| Phase | New IDs |
|-------|---------|
| Phase 1 (Scope 2 — Annotation) | FR-016a |
| Phase 2 (Scope 1 — Classification) | FR-021(amended), FR-034(amended), FR-020(amended), FR-056, FR-057, FR-058, FR-059, FR-060, FR-061, FR-065, NFR-012, NFR-013 |
| Phase 3 (Certify Hardening) | FR-042(amended), FR-062, FR-063, FR-064, NFR-011 |
