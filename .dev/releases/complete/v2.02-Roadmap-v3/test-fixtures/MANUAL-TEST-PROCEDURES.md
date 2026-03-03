# Manual Test Procedures — Fallback Protocol Cascade Paths

**Sprint**: v2.02-Roadmap-v3 (QA Remediation)
**Date**: 2026-03-03
**Status**: Reference document — execute manually when needed

---

## Overview

Three Fallback Protocol cascade paths (F1, F2/F3, F4/F5) cannot be tested via `--resume-from` fixtures because they operate in the **invocation failure domain** (Skill tool errors), not the **data corruption domain** (malformed return contracts). These paths require manual intervention to simulate infrastructure-level failures.

**Coverage context**: The DC-1 through DC-5 fixtures test 6/9 error paths (data corruption domain). These 3 manual procedures cover the remaining 3/9 error paths (invocation failure domain).

---

## F1 — Skill Tool Error (Retry Path)

**Fallback Protocol Reference**: SKILL.md Wave 2 Step 3, Fallback Protocol F1

**What it tests**: When `Skill sc:adversarial-protocol` returns a tool-level error (not a status response), sc:roadmap should log the error verbatim and retry once with reduced payload (omit `--interactive`, use `--depth quick`).

### Procedure

1. **Preparation**:
   - Locate `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`
   - Create a backup: `cp SKILL.md SKILL.md.bak`
   - Rename the original: `mv SKILL.md SKILL.md.disabled`

2. **Execution**:
   - Run: `/sc:roadmap <any-valid-spec> --multi-roadmap --agents opus,sonnet`
   - Observe Claude Code's behavior when Skill invocation fails

3. **Expected Behavior**:
   - First invocation fails (SKILL.md not found)
   - sc:roadmap logs the error verbatim
   - sc:roadmap retries once with `--depth quick` (no `--interactive`)
   - Retry also fails (SKILL.md still not found)
   - sc:roadmap proceeds to F2/F3 (see next procedure)

4. **Cleanup**:
   - `mv SKILL.md.disabled SKILL.md`
   - Verify: `ls src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

### Pass Criteria
- [ ] Error logged verbatim on first failure
- [ ] Retry attempted with reduced payload
- [ ] Retry failure logged

---

## F2/F3 — Template Fallback (Invocation Failure Cascade)

**Fallback Protocol Reference**: SKILL.md Wave 2 Step 3, Fallback Protocol F2/F3

**What it tests**: After F1 retry fails, sc:roadmap should abandon Skill invocation, emit a WARNING about falling back to template-based generation, set `fallback_mode: true`, and proceed to template-based milestone creation (Step 4) instead of using adversarial output.

### Procedure

1. **Preparation**:
   - Same as F1 — keep `SKILL.md.disabled` (do not restore yet)
   - This procedure continues from F1's failure state

2. **Execution**:
   - Continue observing from F1 procedure (same invocation)
   - After retry failure in F1, sc:roadmap should cascade to F2/F3

3. **Expected Behavior**:
   - WARNING emitted: `"Skill invocation failed after retry. Falling back to template-based roadmap generation."`
   - `fallback_mode: true` set in pipeline state
   - sc:roadmap proceeds to Step 4 (template-based milestone creation)
   - Roadmap is generated using templates instead of adversarial output
   - extraction.md includes `fallback_activated: true` in `pipeline_diagnostics`

4. **Cleanup**:
   - `mv SKILL.md.disabled SKILL.md`
   - Verify restoration

### Pass Criteria
- [ ] Fallback warning emitted with exact message text
- [ ] `fallback_mode: true` in pipeline state
- [ ] Template-based generation activates (Step 4)
- [ ] Roadmap artifacts produced (degraded quality acceptable)
- [ ] `pipeline_diagnostics.fallback_activated: true` in extraction.md

---

## F4/F5 — Terminal Abort (Both Paths Failed)

**Fallback Protocol Reference**: SKILL.md Wave 2 Step 3, Fallback Protocol F4/F5

**What it tests**: If template-based generation (Step 4) also encounters a critical error after adversarial invocation already failed, sc:roadmap should log full context and abort with terminal error message. This is the "both paths failed" scenario.

### Procedure

1. **Preparation**:
   - Rename SKILL.md: `mv SKILL.md SKILL.md.disabled` (breaks adversarial path)
   - Corrupt template directory: rename or empty the template discovery paths
     - `mv .dev/templates/roadmap/ .dev/templates/roadmap.disabled/` (if exists)
     - `mv ~/.claude/templates/roadmap/ ~/.claude/templates/roadmap.disabled/` (if exists)
   - Note: Tier 4 (inline generation) should still work, so this procedure may require additionally corrupting the spec file AFTER F2/F3 activates (to trigger a generation error during Step 4)

2. **Execution**:
   - Run: `/sc:roadmap <spec-that-will-cause-generation-error> --multi-roadmap --agents opus,sonnet`
   - Observe the full cascade: F1 → F2/F3 → F4/F5

3. **Expected Behavior**:
   - F1: Skill invocation fails, retry fails
   - F2/F3: Template fallback activates
   - F4/F5: Template generation encounters critical error
   - Terminal abort message: `"Both adversarial and template-based generation failed. Manual intervention required."`
   - `fallback_mode: true` written to any partial artifacts

4. **Cleanup**:
   - `mv SKILL.md.disabled SKILL.md`
   - Restore template directories if renamed
   - Verify all paths restored

### Pass Criteria
- [ ] Full cascade observed: F1 → F2/F3 → F4/F5
- [ ] Terminal abort message emitted with exact text
- [ ] `fallback_mode: true` in any partial artifacts
- [ ] No silent failures — all error states logged

---

## Notes

- These procedures are **destructive** (temporarily rename/remove files). Always create backups.
- Execute in a development environment only — never in production or shared branches.
- The F4/F5 path is difficult to trigger because Tier 4 inline generation is resilient by design. It may require creative corruption of the spec file mid-pipeline.
- All 3 procedures can be run in a single session by not restoring SKILL.md between F1 and F2/F3.
