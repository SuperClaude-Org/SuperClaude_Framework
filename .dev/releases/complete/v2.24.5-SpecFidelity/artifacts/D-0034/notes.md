# D-0034 — Version Number Decision

**Task:** T07.05
**Date:** 2026-03-15

## Decision

**Confirmed version: `v2.24.5`**

## Evidence

### pyproject.toml version
```
version = "4.2.0"
```
The Python package uses a separate `v4.x.x` versioning scheme. The `v2.x.x` scheme is the internal SuperClaude framework/sprint release versioning.

### Existing tags
```
v4.2.0  (most recent)
v4.1.9
v4.1.8
...
checkpoint-pre-phase-1
checkpoint-post-m5
checkpoint-post-m4
```
No `v2.24.5` or `v2.25.1` tag exists. Neither conflicts with existing tags.

### Roadmap evidence
- `target_release: v2.24.5` in roadmap.md YAML frontmatter
- Sprint directory: `.dev/releases/current/v2.24.5/`
- Roadmap explicitly states: "merged roadmap uses v2.24.5 as working title pending confirmation"
- Spec file named `v2.25.1-release-spec.md` is the prior draft name, superseded by roadmap decision

### Rationale
The authoritative source is the roadmap's own `target_release` field and the sprint directory name. The spec filename `v2.25.1` was an earlier draft artifact. The roadmap consolidation explicitly chose `v2.24.5` as the working (and final) release title.

## Tag to Create

`v2.24.5`

## Conflict Check

`git tag | grep v2.24.5` → no output → no conflict
