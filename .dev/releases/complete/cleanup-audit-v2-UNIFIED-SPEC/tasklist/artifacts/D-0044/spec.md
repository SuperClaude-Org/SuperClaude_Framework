# D-0044 Spec: AC1-AC20 Automated Validation Suite

## Task Reference
- Task: T05.05
- Roadmap Item: R-044
- AC: Final acceptance (all ACs)

## AC-to-Test Mapping

| AC | Description | Test Class | Test Count |
|----|-------------|------------|------------|
| AC1 | 5-category classification | TestAC1Classification | 3 |
| AC2 | Coverage tracking | TestAC2Coverage | 1 |
| AC3 | Checkpointing + resume | TestAC3Checkpointing | 2 |
| AC4 | Evidence for DELETE | TestAC4EvidenceDelete | 2 |
| AC5 | Evidence for KEEP | TestAC5EvidenceKeep | 2 |
| AC6 | Spot-check validation | TestAC6SpotCheck | 2 |
| AC7 | Credential scanning | TestAC7CredentialScanning | 2 |
| AC8 | Gitignore consistency | TestAC8Gitignore | 2 |
| AC9 | Budget control | TestAC9Budget | 2 |
| AC10 | Report depth modes | TestAC10ReportDepth | 2 |
| AC11 | Scanner schema | TestAC11ScannerSchema | 2 |
| AC12 | Dependency graph | TestAC12DependencyGraph | 2 |
| AC13 | Cold-start auto-config | TestAC13ColdStart | 2 |
| AC14 | Docs audit (broken refs + full) | TestAC14DocsAudit | 2 |
| AC15 | Backward compat (v1 mapping) | TestAC15BackwardCompat | 2 |
| AC16 | Directory assessment | TestAC16DirectoryAssessment | 2 |
| AC17 | INVESTIGATE cap / escalation | TestAC17InvestigateCap | 2 |
| AC18 | Anti-lazy distribution guard | TestAC18FailureHandling | 2 |
| AC19 | Dry-run estimation | TestAC19DryRun | 2 |
| AC20 | Run isolation | TestAC20RunIsolation | 2 |

**Total:** 40 tests covering all 20 ACs (minimum 1 per AC, most have 2).

## Test Fixtures

All fixtures are self-contained and do not require external repositories:
- Classification fixtures use inline `ConsolidatedFinding` objects
- File-system fixtures use `tmp_path` (pytest built-in)
- No external network dependencies

## Run Command

```bash
uv run pytest tests/audit/test_ac_validation.py -v
```
