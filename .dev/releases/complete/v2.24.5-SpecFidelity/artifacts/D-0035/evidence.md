# D-0035 — Release Tag Evidence

**Task:** T07.06
**Date:** 2026-03-15

## Tag Details

```
Tag: v2.24.5
Points-at: 8b70fd58f83b58eb401c46494855553ed63490e6
Commit: fix(executors): replace --file fallback with inline embedding
```

## Verification

```
$ git tag | grep v2.24.5
v2.24.5

$ git tag --points-at HEAD
v2.24.5
```

## Commit History at Tag

```
8b70fd5 fix(executors): replace --file fallback with inline embedding      ← HEAD (tagged)
697a5af fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string
6240efa feat(pipeline): add --tools default to ClaudeProcess.build_command()
```

## Acceptance Criteria

- [x] Git tag `v2.24.5` created
- [x] Tag points to HEAD (after all fix commits)
- [x] `git tag | grep v2.24.5` returns `v2.24.5`
- [x] `git tag --points-at HEAD` returns `v2.24.5`
- [x] Version confirmed from T07.05 (D-0034/notes.md)
