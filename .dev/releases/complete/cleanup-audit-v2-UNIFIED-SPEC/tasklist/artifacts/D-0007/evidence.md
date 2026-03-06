# D-0007 Evidence: Gitignore Inconsistency Detection

## Test Results (8/8 passed)
- TestParseGitignore: parses_patterns, no_gitignore_returns_empty
- TestCheckConsistency: detects_inconsistencies, no_inconsistencies, glob_pattern_match, no_gitignore_no_crash, output_includes_matching_pattern, serialization

## AC Verification
- [x] AC8: Tracked-but-ignored files detected
- [x] Output lists each file with matching pattern
- [x] No crash on missing .gitignore
