# Validated Solution Plan: `OSError [Errno 7] Argument list too long`

**Date**: 2026-03-15
**Input**: 3 adversarial solution debates (L1, L2, L3) + root cause debates (RC1–RC3)
**Artifacts**: 9 documents in `docs/generated/arg-too-long-*`

---

## Debate Verdict Summary

| Level | Solutions | Confidence | Recommendation |
|-------|----------|------------|----------------|
| **L1** | 1A (derive limit) + 1B (guard full string) | **88/100** | Ship immediately — correct and sufficient |
| **L2** | 2A (per-file guard) + 2B (startup warning) | **58/100** | Optional — defer if time-constrained |
| **L3** | 3A (stdin delivery) | **45/100** | Defer to v2.26 spike — architecturally sound but unvalidated |

---

## Validated Immediate Fix: 1A + 1B

### Corrections from Debate

The L1 debate identified four corrections to the original brainstorm proposal:

| # | Issue Found | Correction |
|---|------------|------------|
| 1 | `import resource` in 1A snippet is dead code (unused import from discarded `getrlimit` approach) | **Remove** — only `_MAX_ARG_STRLEN`, `_PROMPT_TEMPLATE_OVERHEAD`, and `_EMBED_SIZE_LIMIT` are needed |
| 2 | Largest prompt template is **3.4 KB** (not 4.3 KB as originally stated) | 8 KB overhead is slightly more conservative than necessary but correct in intent |
| 3 | Test `test_100kb_guard_fallback` name becomes misleading | **Rename** to `test_embed_size_guard_fallback` and update docstring |
| 4 | No guard when `step.prompt` alone exceeds `MAX_ARG_STRLEN` | **Acknowledged gap** — deferred to L2 (currently impossible: largest template is 3.4 KB) |

### Validated Implementation

```python
# In executor.py — replace line 54
_MAX_ARG_STRLEN = 128 * 1024   # Linux kernel compile-time constant (non-negotiable)
_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024   # 2.3× headroom over largest template (3.4 KB)
_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD  # ~120 KB

# In roadmap_run_step() — replace lines 173-192
embedded = _embed_inputs(step.inputs)
composed = step.prompt + "\n\n" + embedded if embedded else step.prompt

if len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = composed
    extra_args: list[str] = []
elif embedded:
    _log.warning(
        "Step '%s': composed prompt (%d bytes) exceeds %d bytes, "
        "falling back to --file flags",
        step.id,
        len(composed.encode("utf-8")),
        _EMBED_SIZE_LIMIT,
    )
    effective_prompt = step.prompt
    extra_args = [
        arg
        for input_path in step.inputs
        for arg in ("--file", str(input_path))
    ]
else:
    effective_prompt = step.prompt
    extra_args = []
```

### Companion Changes

1. Rename `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`
2. Update test docstring to reference derived limit
3. Fix comment on line 54 (currently `# 100 KB` — remove stale comment since derivation is self-documenting)

### Expected Outcome

- spec-fidelity step: 152.1 KB combined > 120 KB limit → fallback to `--file` → no crash
- extract step: 117.9 KB spec + 4 KB template = ~122 KB > 120 KB limit → fallback → no crash
- test-strategy step: 69.5 KB inputs + 4 KB template = ~73.5 KB < 120 KB → inline embed (unchanged)
- All other steps: inputs < 120 KB → inline embed (unchanged)

---

## L2: Optional Defense-in-Depth

The L2 debate (58/100) concluded these are **genuine but non-essential** improvements.

### If Adopted (Phase 2):

**2A — Per-file guard**: Use derived constant, not hardcoded:
```python
_PER_FILE_EMBED_LIMIT = _EMBED_SIZE_LIMIT // 2  # No single file > 50% of budget (~60 KB)
```

**2B — Startup warning**: Raise threshold to match embed limit:
```python
_SPEC_FILE_WARN_THRESHOLD = _EMBED_SIZE_LIMIT  # Warning when spec size would trigger fallback
```

### Key Debate Findings on L2

- **TOCTOU concern**: `_should_embed_inputs()` uses `.stat().st_size` but `_embed_inputs()` uses `.read_text()` — file could change between checks. Document as approximation, not safety gate.
- **Per-file ratio (50%)** is a policy decision unrelated to the OS constraint. Must be documented as such.
- **Critic's strongest point**: If time is constrained, skip L2 and invest in L3 instead — eliminating the class beats adding more proxy guards.

---

## L3: Deferred to v2.26

The L3 debate (45/100) reached clear consensus on three points:

### 1. Only 3A (stdin) Is Viable

| Variant | Verdict | Reason |
|---------|---------|--------|
| **3A** (stdin) | Viable if validated | No dependency on `--file` semantics; fail-safe threshold |
| **3B** (`--file` for prompt) | Rejected | `--file` format is `file_id:relative_path`, not bare paths |
| **3C** (all prompts as files) | Rejected | Over-engineered; depends on unconfirmed `--file` semantics |

### 2. Critical Finding: `--file` Fallback May Be Broken

The L3 debate surfaced that the **existing** `--file` fallback passes `("--file", str(input_path))` but `claude --help` documents `--file` as expecting `file_id:relative_path` format. This means either:
- (a) The fallback silently fails (we've never noticed because it rarely triggers), or
- (b) `claude` accepts bare paths as undocumented behavior

**Action required**: Validate `--file` behavior independently, regardless of L3 decision. This is a correctness concern for L1+L2's fallback path.

### 3. Validation Spike (v2.26)

| # | Test | Pass Criteria | Time |
|---|------|---------------|------|
| V1 | Basic stdin delivery | `echo "test" \| claude --print` produces response | 5 min |
| V2 | Large prompt (>128 KB) via stdin | Response references late content | 10 min |
| V3 | `os.setpgrp` + stdin compatibility | No broken pipe in separate process group | 15 min |
| V4 | Unicode/special chars via stdin | No truncation or encoding errors | 10 min |
| V5 | Stdin closure timing | Full read before processing starts | 10 min |

**Also validate**: `--file` with bare path format (15 min). This blocks L1+L2 fallback correctness.

---

## Final Artifact Index

| Document | Purpose |
|----------|---------|
| `arg-too-long-root-causes.md` | 3 root causes with evidence |
| `arg-too-long-debate-rc1.md` | RC1 debate (72/100 — primary) |
| `arg-too-long-debate-rc2.md` | RC2 debate (45/100 — contributing) |
| `arg-too-long-debate-rc3.md` | RC3 debate (38/100 — architectural debt) |
| `arg-too-long-reconciliation.md` | Root cause verdict reconciliation |
| `arg-too-long-solution-brainstorm.md` | Full solution space (7 solutions, 3 levels) |
| `arg-too-long-debate-solutions-L1.md` | L1 solution debate (88/100) |
| `arg-too-long-debate-solutions-L2.md` | L2 solution debate (58/100) |
| `arg-too-long-debate-solutions-L3.md` | L3 solution debate (45/100) |
| `arg-too-long-solution-validation.md` | **This file** — final validated plan |

---

## Action Items

### This Sprint (unblock pipeline)
- [ ] Apply 1A + 1B in `executor.py` (remove dead `import resource`, use derived constants, guard full composed string)
- [ ] Rename test `test_100kb_guard_fallback` → `test_embed_size_guard_fallback`
- [ ] Validate `--file` with bare path format (15 min — blocks fallback correctness)

### Next Sprint (defense-in-depth, optional)
- [ ] Evaluate 2A (per-file guard with derived `_EMBED_SIZE_LIMIT // 2` constant)
- [ ] Evaluate 2B (startup warning at `_EMBED_SIZE_LIMIT` threshold)

### v2.26 (architectural hardening)
- [ ] Create spike ticket: "Validate stdin prompt delivery for ClaudeProcess"
- [ ] Execute V1–V5 validation tests
- [ ] If validated: implement 3A with `_PROMPT_FILE_THRESHOLD` approach
- [ ] Do NOT pursue 3B or 3C
