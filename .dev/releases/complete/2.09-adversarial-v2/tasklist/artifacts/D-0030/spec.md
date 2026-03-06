# D-0030: invariant-probe.md Artifact Assembly

## Overview

The `invariant-probe.md` artifact captures Round 2.5 fault-finder output as a structured markdown table. Each finding has a unique `INV-NNN` identifier and required columns: ID, Category, Assumption, Status, Severity, Evidence.

## Table Schema

| Column | Values | Constraint |
|--------|--------|------------|
| ID | INV-NNN | Sequential from INV-001 |
| Category | state_variables, guard_conditions, count_divergence, collection_boundaries, interaction_effects | Exactly one of 5 |
| Assumption | Free text | Non-empty |
| Status | ADDRESSED, UNADDRESSED | Exactly one of 2 |
| Severity | HIGH, MEDIUM, LOW | Exactly one of 3 |
| Evidence | Free text reference | Non-empty |

## Assembly Algorithm

1. Parse fault-finder output
2. Validate all 6 fields present per finding
3. Normalize IDs to sequential INV-NNN
4. Validate Status enum (ADDRESSED/UNADDRESSED)
5. Validate Severity enum (HIGH/MEDIUM/LOW)
6. Assemble markdown table
7. Append summary counts

## Output Location

`<output-dir>/adversarial/invariant-probe.md`

## Acceptance Criteria

- Table contains all 6 required columns: ID, Category, Assumption, Status, Severity, Evidence
- IDs are unique INV-NNN, assigned sequentially
- Status values are exactly ADDRESSED or UNADDRESSED
- Severity values are exactly HIGH, MEDIUM, or LOW
- Empty probe (zero findings) produces valid table with header only
