---
deliverable: D-0035
task: T05.01
status: PASS
date: 2026-03-09
---

# D-0035: build_extract_prompt() accepts retrospective_content

## Evidence

`build_extract_prompt()` in `src/superclaude/cli/roadmap/prompts.py` now accepts
`retrospective_content: str | None = None`.

When provided, the content is framed as:

> "Advisory: Areas to Watch (from prior retrospective)"
> "These are areas to watch during extraction -- they are NOT additional requirements"

### Test Output

```
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_accepts_retrospective_content_none PASSED
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_accepts_retrospective_content_explicit_none PASSED
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_retrospective_content_framed_as_advisory PASSED
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_retrospective_not_framed_as_requirements PASSED
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_retrospective_empty_string_treated_as_absent PASSED
tests/roadmap/test_retrospective.py::TestBuildExtractPromptRetrospective::test_prompt_still_valid_with_retrospective PASSED
```

All 6 prompt tests pass (SC-006 satisfied).
