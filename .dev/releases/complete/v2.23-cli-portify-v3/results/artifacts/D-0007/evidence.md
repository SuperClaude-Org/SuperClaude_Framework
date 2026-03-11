# D-0007: Conditional Section Markers

## Conditional Sections (FR-060.7)

All conditional sections are marked with `[CONDITIONAL: <spec_types>]` format:

| Section | Marker | Applicable Spec Types |
|---------|--------|----------------------|
| 4.3 Removed Files | `[CONDITIONAL: refactoring, portification]` | Refactoring, Portification |
| 4.5 Data Models | `[CONDITIONAL: new_feature, portification]` | New Feature, Portification |
| 5. Interface Contracts | `[CONDITIONAL: portification, new_feature]` | Portification, New Feature |
| 5.1 CLI Surface | `[CONDITIONAL: new_feature, portification]` | New Feature, Portification |
| 5.2 Gate Criteria | `[CONDITIONAL: portification]` | Portification |
| 5.3 Phase Contracts | `[CONDITIONAL: portification, infrastructure]` | Portification, Infrastructure |
| 8.3 Manual/E2E Tests | `[CONDITIONAL: infrastructure, portification]` | Infrastructure, Portification |
| 9. Migration & Rollout | `[CONDITIONAL: refactoring, portification]` | Refactoring, Portification |
| Appendix A: Glossary | `[CONDITIONAL: all types]` | All (if terminology used) |
| Appendix B: Reference Documents | `[CONDITIONAL: all types]` | All (if external refs needed) |

## Cross-Type Validation

| Spec Type | Mandatory Sections | Conditional Sections Included |
|-----------|-------------------|------------------------------|
| New Feature | 1-4, 6-8, 10-12 | 4.5, 5, 5.1 |
| Refactoring | 1-4, 6-8, 10-12 | 4.3, 9 |
| Portification | 1-4, 6-8, 10-12 | 4.3, 4.5, 5, 5.1, 5.2, 5.3, 8.3, 9 |
| Infrastructure | 1-4, 6-8, 10-12 | 5.3, 8.3 |

All 4 spec types validated. Mandatory sections (1-4, 6-8, 10-12) always present.
