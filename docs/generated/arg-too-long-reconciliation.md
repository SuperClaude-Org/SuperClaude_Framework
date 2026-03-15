# Reconciliation: Debate Verdicts & Primary Root Cause Nomination

**Issue**: `OSError: [Errno 7] Argument list too long: 'claude'` at `spec-fidelity`
**Date**: 2026-03-14

---

## Debate Verdict Summary

| Root Cause | Likelihood Score | Characterisation from Debate |
|------------|-----------------|------------------------------|
| **RC1**: `_EMBED_SIZE_LIMIT` miscalibrated above `MAX_ARG_STRLEN` | **72 / 100** | Direct causal link; changing one constant prevents this crash |
| **RC2**: spec-fidelity embeds unbounded user-supplied spec file | **45 / 100** | Correct structural diagnosis; describes the better durable fix design |
| **RC3**: Prompt delivery via `-p` CLI arg creates an ineliminable OS ceiling | **38 / 100** | Accurate architectural observation; correct long-term remediation target |

---

## Reconciliation

### Why RC1 Is Nominated as Primary Root Cause

RC1 carries the highest likelihood (72/100) and both the RC2 and RC3 debates independently
confirmed it as the more proximate causal agent. The convergent logic across all three debates:

> A correctly calibrated `_EMBED_SIZE_LIMIT` (≤ 120 KB with margin) would have triggered the
> existing `--file` fallback, reducing the `-p` argument to the base prompt template (~4 KB),
> preventing the crash — regardless of whether RC2 or RC3's structural gaps exist.

The stale comment (`# 100 KB` alongside `200 * 1024`) is forensic evidence of an unconsidered
change: the constant's original value was calibrated against `MAX_ARG_STRLEN`; the change to
200 KB was made without understanding that constraint relationship, creating a 72 KB "dead zone"
(128–200 KB) where content passes the guard but crashes `Popen`.

### Why RC2 and RC3 Are Not Dismissed

Both RC2 (45/100) and RC3 (38/100) were assessed as genuine structural concerns that RC1's
miscalibration exposed:

- **RC2** is the correct *design diagnosis*: per-file size awareness is absent; the spec file is
  the only unbounded user-controlled input; fixing only the constant leaves the design fragile.
- **RC3** is the correct *long-term architectural target*: passing variable-length prompts as CLI
  arguments creates a kernel-enforced ceiling that a guard can only proxy, not eliminate. The
  correct transport for large prompts is stdin or a temp file, not `-p`.

### Causal Hierarchy

```
RC1 (miscalibrated _EMBED_SIZE_LIMIT)      ← PRIMARY ROOT CAUSE of this crash
  └─ exposed by → RC2 (unbounded spec file as direct input)   ← structural design gap
       └─ enabled by → RC3 (CLI arg as prompt transport)       ← architectural debt
```

RC1 is the immediately actionable fix. RC2 is the better fix design. RC3 is the durable
architectural solution that eliminates the entire class.

---

## Nominated Primary Root Cause

> **RC1: `_EMBED_SIZE_LIMIT = 200 * 1024` is set 56% above `MAX_ARG_STRLEN` (128 KB), placing
> the guard 72 KB above the OS constraint it was designed to protect. The guard was changed from
> its original intent (proxied by the stale `# 100 KB` comment) without understanding or
> preserving its relationship to the kernel limit. Any combined embed between 128 KB and 200 KB
> passes the guard and crashes `subprocess.Popen`.**

---

## Solution Brainstorm

See `arg-too-long-solution-brainstorm.md` for the full solution space exploration covering
immediate fixes, structural improvements, and architectural hardening.
