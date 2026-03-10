# D-0008: Parser Unit Test Evidence

## Test Execution

```
uv run pytest tests/roadmap/test_remediate_parser.py -v
38 passed in 0.14s
```

## Coverage

```
uv run pytest tests/roadmap/test_remediate_parser.py --cov=superclaude.cli.roadmap.remediate_parser --cov=superclaude.cli.roadmap.models --cov-report=term-missing

models.py:       89% (45 stmts, 5 missed -- ValidateConfig class, outside scope)
remediate_parser: 93% (182 stmts, 13 missed -- edge-case fallback paths)
TOTAL:           92% (227 stmts, 18 missed)
```

Finding dataclass + parser-specific coverage: 93%

## Format Variants Covered

1. **reflect-merged.md** (11 tests): Agreement Table with Remediation Status column, Consolidated Findings with severity sections
2. **merged-validation-report.md** (8 tests): Agreement Table without Remediation Status column, Consolidated Findings
3. **Individual reflect-*.md** (7 tests): Flat Findings sections, fallback deduplication path

## Test Breakdown

| Class | Tests | Focus |
|-------|-------|-------|
| TestFindingDataclass | 6 | Dataclass fields, defaults, status validation |
| TestPrimaryParserReflectMerged | 11 | Format 1: remediation status overlay, agreement extraction |
| TestPrimaryParserMergedValidation | 8 | Format 2: all pending, file extraction, evidence |
| TestFallbackParserDedup | 7 | Format 3: dedup, severity resolution, guidance merge |
| TestParserNegativeCases | 4 | Empty/malformed input, ValueError, purity |
| TestParserPurityGuarantee | 2 | Determinism, no side effects |

## Regression Check

```
uv run pytest tests/roadmap/ -v
358 passed in 0.33s
```

All existing roadmap tests pass with zero regressions.
