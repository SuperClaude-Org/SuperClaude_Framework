# D-0023: Evidence - Dead Code Detector

## Test Results

8 tests passed (0 failures):
- TestCandidateIdentification: 3/3 passed (file with exports + 0 importers detected, file with importers excluded, file with no exports excluded)
- TestExclusionRules: 3/3 passed (main.py excluded as entry_point, conftest.py excluded as framework_hook, pytest_ prefix excluded)
- TestEvidenceAttachment: 2/2 passed (export_location populated with line numbers, boundary_search_scope lists searched directories)

## Candidate Detection Verification

Test fixture with 5 files:
- `utils.py` (2 exports, 0 importers): correctly flagged as dead-code candidate
- `helpers.py` (1 export, 1 Tier-A importer): correctly excluded
- `main.py` (1 export, 0 importers): correctly excluded by entry_point rule
- `conftest.py` (3 exports, 0 importers): correctly excluded by framework_hook rule

## Evidence Quality Verification

Each candidate includes:
- `export_location` with file path and specific line numbers of detected exports
- `boundary_search_scope` listing the directories and glob patterns searched for potential importers
