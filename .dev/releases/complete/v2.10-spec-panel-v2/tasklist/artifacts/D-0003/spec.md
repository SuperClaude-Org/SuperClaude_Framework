# D-0003 Evidence: Output Format Template

## Deliverable
Output format template added to Whittaker persona per FR-3 specification.

## Template Format
```
"I can break this specification by [attack methodology name].
The invariant at [section/requirement location] fails when [specific triggering condition].
Concrete attack: [step-by-step scenario with before/after state trace]."
```

## Severity Classification
- **CRITICAL**: Specification is provably wrong
- **MAJOR**: Specification is ambiguous or incomplete under attack
- **MINOR**: Specification could be clearer but behavior is inferrable

## Verification
- Template matches FR-3 structure: attack identification, invariant location, failure condition, concrete state trace
- Severity uses existing panel classification system (CRITICAL, MAJOR, MINOR)
- Located in Output Format field of Whittaker persona block

## Traceability
- Roadmap Item: R-003
- Task: T01.02
- Deliverable: D-0003
