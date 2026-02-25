# D-0001 — Skill Tool Probe Result

**Task**: T01.01 — Skill Tool Probe Re-Run
**Roadmap Item**: R-001
**Date**: 2026-02-24
**Environment**: Claude Code 2.1.52, Linux 6.8.0-90-generic
**Branch**: `feature/v2.01-Architecture-Refactor`

---

## Probe Results

### Probe 1: Skill Tool Availability

**Command**: `Skill sc-adversarial-protocol`
**Result**: **AVAILABLE** — Skill tool successfully loaded `sc-adversarial-protocol/SKILL.md`
**Evidence**: Full SKILL.md content was loaded into conversation context without error.

**Prior Result**: `TOOL_NOT_AVAILABLE` (prior sprint, different environment)
**Delta**: **RESULT CHANGED** — Skill tool is now available.

### Probe 2: `claude -p` Subprocess Viability

**Command**: `which claude && claude --version`
**Result**: **AVAILABLE** — Claude CLI v2.1.52 found at `/config/.local/bin/claude`
**Note**: Viability of `claude -p` with `--append-system-prompt` for SKILL.md injection was NOT empirically tested (requires subprocess execution which may be sandboxed). The binary exists and reports a version, but runtime behavior under `claude -p` with large SKILL.md payloads remains unverified.

---

## Variant Decision

**Prior Decision (D-0001/D-0002 from prior sprint)**: FALLBACK-ONLY
**Updated Decision**: **SKILL-AVAILABLE**

The Skill tool is available in the current environment. This means:
1. The primary invocation path (`Skill sc:<name>-protocol`) is viable
2. The FALLBACK-ONLY variant is **no longer the sole option**
3. Task agent dispatch remains available as a fallback mechanism
4. `claude -p` script strategy remains unverified but the binary exists

### Invocation Hierarchy (Updated)

| Priority | Mechanism | Status | Use Case |
|----------|-----------|--------|----------|
| 1 (Primary) | Skill tool | **AVAILABLE** | Direct skill invocation in current context |
| 2 (Fallback) | Task tool | AVAILABLE | Cross-skill invocation (avoids re-entry block) |
| 3 (Deferred) | `claude -p` script | UNVERIFIED | Headless sub-agent with ref injection |

---

## Downstream Impact Analysis

The change from FALLBACK-ONLY to SKILL-AVAILABLE affects:

1. **T02.03 (Wave 2 Step 3 decomposition)**: Step 3f ("Skip primary template") is no longer a no-op. The primary Skill tool path should be documented as the preferred invocation mechanism.
2. **T02.04 (roadmap.md Activation)**: The `## Activation` section can use `Skill sc:roadmap-protocol` as the primary mechanism with confidence.
3. **Sprint-spec §9 (Fallback Protocol)**: The fallback protocol F1/F2-3/F4-5 is still needed but now as a true fallback, not the only path.
4. **Decision D-0002**: Must be updated from "Sprint variant: FALLBACK-ONLY" to "Sprint variant: SKILL-AVAILABLE with Task agent fallback".

**Critical caveat**: Skill-to-skill chaining (one skill invoking another via Skill tool) may still trigger the re-entry block described in §6. The Task agent wrapper remains necessary for cross-skill invocation (e.g., `sc:roadmap-protocol` invoking `sc:adversarial-protocol`).

---

## Probe Methodology (for future re-runs)

```bash
# Probe 1: Skill tool
# From within Claude Code session, invoke:
#   Skill sc-adversarial-protocol
# Expected: SKILL.md content loads into conversation
# If error: Record exact error message

# Probe 2: claude -p binary
which claude && claude --version
# Expected: Path and version number
# If not found: FALLBACK-ONLY variant applies

# Probe 3 (future): claude -p runtime test
# claude -p --append-system-prompt "$(cat SKILL.md)" "Test prompt"
# Expected: Successful execution with output
# If error: Record error, fall back to Task agent only
```

---

*Artifact produced by T01.01 — Skill Tool Probe Re-Run*
*Variant decision: SKILL-AVAILABLE (changed from FALLBACK-ONLY)*
