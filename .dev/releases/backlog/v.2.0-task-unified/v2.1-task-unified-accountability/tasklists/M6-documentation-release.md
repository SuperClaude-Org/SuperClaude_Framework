# Tasklist: M6 - Documentation & Release

## Metadata
- **Milestone**: M6
- **Dependencies**: M5 (Testing & Quality)
- **Estimated Complexity**: Low
- **Primary Persona**: Scribe, Docs
- **Files to Modify/Create**: 4 documentation files, 1 changelog

---

## Tasks

### T6.1: SKILL.md Update - Section 6 Accountability Framework (DOC-001)
**Type**: DOC
**Priority**: P1-High
**Files Affected**:
- `skills/sc-task-unified/SKILL.md` (modify)

#### Steps
1. Read existing SKILL.md to understand structure
2. Add Section 6 "Accountability Framework" after Section 5
3. Document worklog behavior (silent, automatic)
4. Document verification behavior (STRICT tier only)
5. Document checkpoint behavior (tier-based)
6. Add tier accountability matrix
7. Include configuration reference

#### Content Structure
```markdown
## 6. Accountability Framework

### 6.1 Overview
The accountability framework provides automatic audit trails, verification, and progress tracking for task execution. It scales with task risk—STRICT tasks get full accountability while EXEMPT tasks incur zero overhead.

### 6.2 Components

#### Worklog
- **Purpose**: Audit trail of all tier-significant operations
- **Scope**: All tiers (scoped by significance)
- **Location**: `_worklog/{session_id}` memory
- **Default**: Enabled (silent, no user action required)

#### Verification (STRICT only)
- **Purpose**: Closed-loop status confirmation after TodoWrite
- **Behavior**: Automatic retry (1 attempt), circuit breaker (3 total)
- **Default**: Enabled for STRICT tier

#### Checkpoints
- **Purpose**: Progress summaries at phase boundaries
- **STRICT**: 3 checkpoints (planning, execution, verification)
- **STANDARD**: 1 checkpoint (execution)
- **LIGHT/EXEMPT**: 0 checkpoints

### 6.3 Tier Accountability Matrix

| Tier | Worklog | Verification | Checkpoints | Token Overhead |
|------|---------|--------------|-------------|----------------|
| STRICT | Full | Yes | 3 | ≤750 |
| STANDARD | Scoped | No | 1 | ≤300 |
| LIGHT | Minimal | No | 0 | ≤60 |
| EXEMPT | None | No | 0 | 0 |

### 6.4 User Escalation
When verification fails 3 times:
1. **Accept**: Accept current state, continue
2. **Abort**: Stop task, preserve worklog
3. **Continue**: Continue without verification (logged risk)

### 6.5 Fallback Behavior
If Serena MCP unavailable:
- Falls back to session-only logging
- User notification displayed
- Use `--retry-memory` to reconnect

### 6.6 Configuration
See `config/accountability.yaml` for all settings.
```

#### Acceptance Criteria
- [ ] Section 6 exists in SKILL.md after Section 5
- [ ] All three components documented (worklog, verification, checkpoints)
- [ ] Tier accountability matrix accurate
- [ ] User escalation options documented
- [ ] Fallback behavior documented
- [ ] Configuration reference included

#### Verification
```bash
# Check section exists
grep -n "## 6. Accountability Framework" skills/sc-task-unified/SKILL.md
```

---

### T6.2: Flag Reference Update (DOC-002)
**Type**: DOC
**Priority**: P1-High
**Files Affected**:
- `skills/sc-task-unified/SKILL.md` (modify - flag reference section)

#### Steps
1. Locate flag reference section in SKILL.md
2. Add 5 new accountability flags
3. Include descriptions, defaults, and recommendations
4. Add examples for each flag

#### Flag Documentation
```markdown
### Accountability Flags

| Flag | Effect | Default | Recommendation |
|------|--------|---------|----------------|
| `--no-worklog` | Disable all worklog functionality | OFF | Not recommended - breaks accountability |
| `--skip-verify` | Skip STRICT verification | OFF | Use for trusted environments |
| `--no-checkpoints` | Disable checkpoint summaries | OFF | Use for time-critical tasks |
| `--verbose-log` | Include full tool results in worklog | OFF | Use for debugging |
| `--retry-memory` | Retry Serena connection after fallback | N/A | Use after fallback notification |

#### Examples

```bash
# Skip verification for trusted dev environment
/sc:task "implement feature" --skip-verify

# Disable all accountability (not recommended)
/sc:task "quick fix" --no-worklog --skip-verify --no-checkpoints

# Debug mode with full logging
/sc:task "troubleshoot issue" --verbose-log

# Retry Serena after fallback
/sc:task "resume work" --retry-memory
```
```

#### Acceptance Criteria
- [ ] All 5 new flags documented
- [ ] Each flag has description, default, recommendation
- [ ] Examples provided for common use cases
- [ ] Flags integrated into existing flag reference section

#### Verification
```bash
# Check all flags documented
grep -E "\-\-no-worklog|\-\-skip-verify|\-\-no-checkpoints|\-\-verbose-log|\-\-retry-memory" skills/sc-task-unified/SKILL.md
```

---

### T6.3: Migration Guide (DOC-003)
**Type**: DOC
**Priority**: P2-Medium
**Files Affected**:
- `docs/migration/v1.3-accountability.md` (create)

#### Steps
1. Create migration guide directory if needed
2. Document changes for existing users
3. Document backward compatibility
4. Provide opt-out instructions
5. Document SKILL.md maintainer updates

#### Content Structure
```markdown
# Migration Guide: v1.3 Accountability Framework

## Overview
Version 1.3 introduces the Accountability Framework to `sc:task-unified`. This guide helps existing users and maintainers understand the changes.

## What's New
- **Worklog**: Automatic audit trail for task operations
- **Verification**: Closed-loop status confirmation for STRICT tasks
- **Checkpoints**: Progress summaries at phase boundaries

## For Existing Users

### Nothing Required
Accountability is enabled by default but requires no user action:
- Existing `/sc:task` commands work without modification
- New `_worklog/` memories will appear automatically
- No breaking changes to command syntax or behavior

### What You'll Notice
- `_worklog/` prefix memories in your memory list
- (STRICT tasks) Verification may pause briefly after TodoWrite
- (STRICT/STANDARD) Checkpoint summaries in output

### Opting Out
To disable accountability features:
```bash
# Disable worklog (not recommended)
/sc:task "description" --no-worklog

# Disable verification (STRICT only)
/sc:task "description" --skip-verify

# Disable checkpoints
/sc:task "description" --no-checkpoints

# Disable all accountability
/sc:task "description" --no-worklog --skip-verify --no-checkpoints
```

## For SKILL.md Maintainers

### Required Changes
1. Add Section 6 (Accountability Framework) after Section 5
2. Update flag reference with 5 new flags
3. Import accountability config

### Configuration Integration
```yaml
# In SKILL.md or referenced config
accountability:
  import: config/accountability.yaml
```

### Tier Enforcement Updates
Update tier enforcement logic to include worklog operations:

```yaml
# STRICT tier enforcement
strict_tier:
  worklog: full
  verification: required
  checkpoints: [planning, execution, verification]

# STANDARD tier enforcement
standard_tier:
  worklog: scoped
  verification: none
  checkpoints: [execution]

# LIGHT tier enforcement
light_tier:
  worklog: minimal
  verification: none
  checkpoints: []

# EXEMPT tier enforcement
exempt_tier:
  worklog: none
  verification: none
  checkpoints: []
```

## Backward Compatibility

### Unchanged
- Tier classification algorithm
- Verification routing
- Command syntax
- Task execution flow

### New Default Behaviors
- Worklog creation (silent)
- Checkpoint generation (silent)

Users will see new artifacts but no action is required.

## Troubleshooting

### "Memory system unavailable" notification
Serena MCP is not responding. Options:
1. Wait and retry: `--retry-memory`
2. Continue with session-only logging (automatic)
3. Check Serena MCP status

### Verification keeps failing
If you see repeated verification failures:
1. Check if todo state is actually changing
2. Use `--skip-verify` if in trusted environment
3. Select "Accept" to continue with current state

### Worklog taking too much space
Cleanup runs automatically on session start. To force:
1. Old worklogs (>24h) are archived to summaries
2. Max 50 active worklogs enforced
3. Summaries retained 30 days
```

#### Acceptance Criteria
- [ ] Migration guide created at correct path
- [ ] Existing user section complete (nothing required, what to notice, opt-out)
- [ ] SKILL.md maintainer section complete
- [ ] Backward compatibility documented
- [ ] Troubleshooting section included

#### Verification
```bash
# Check file exists and has key sections
ls docs/migration/v1.3-accountability.md
grep -n "For Existing Users\|For SKILL.md Maintainers\|Backward Compatibility" docs/migration/v1.3-accountability.md
```

---

### T6.4: Configuration Documentation (DOC-004)
**Type**: DOC
**Priority**: P2-Medium
**Files Affected**:
- `docs/reference/accountability-config.md` (create)

#### Steps
1. Create reference documentation for config schema
2. Document all configuration options
3. Provide default values and valid ranges
4. Include customization examples
5. Link to SPEC-REVISED.md for rationale

#### Content Structure
```markdown
# Accountability Configuration Reference

## Overview
This document describes all configuration options for the `sc:task-unified` Accountability Framework.

## Configuration File
Location: `config/accountability.yaml`

## Schema

### Worklog Configuration
```yaml
worklog:
  buffer_size: 10          # Entries before flush (1-100)
  buffer_time_seconds: 30  # Time-based flush interval (10-300)
  init_timeout_ms: 500     # Initialization timeout (100-2000)
  append_timeout_ms: 200   # Entry append timeout (50-500)
  flush_timeout_ms: 300    # Buffer flush timeout (100-1000)
```

### Verification Configuration
```yaml
verification:
  enabled_tiers: [STRICT]  # Tiers with verification
  max_automatic_retries: 1 # Auto retries on mismatch (0-3)
  max_total_attempts: 3    # Including user retries (1-10)
  timeout_ms: 1000         # Verification timeout (500-5000)
  retry_delay_ms: 100      # Delay between retries (50-500)
  circuit_breaker_cooldown_s: 300  # Cooldown period (60-600)
```

### Checkpoint Configuration
```yaml
checkpoints:
  STRICT: [planning_complete, execution_complete, verification_complete]
  STANDARD: [execution_complete]
  LIGHT: []
  EXEMPT: []
  timeout_ms: 2000         # Checkpoint generation timeout (500-5000)
```

### Retention Configuration
```yaml
retention:
  current_session: full    # Keep full worklog
  previous_session: summary  # Archive to summary
  older_sessions_ttl_hours: 24  # TTL for raw worklogs (12-168)
  max_active_worklogs: 50  # Maximum active (10-200)
```

### Aggregate Timeout
```yaml
aggregate_timeout_ms: 3000  # Total accountability phase budget (1000-10000)
```

## Default Configuration
```yaml
accountability_config:
  version: "1.0"

  worklog:
    buffer_size: 10
    buffer_time_seconds: 30
    init_timeout_ms: 500
    append_timeout_ms: 200
    flush_timeout_ms: 300

  verification:
    enabled_tiers: [STRICT]
    max_automatic_retries: 1
    max_total_attempts: 3
    timeout_ms: 1000
    retry_delay_ms: 100
    circuit_breaker_cooldown_s: 300

  checkpoints:
    STRICT: [planning_complete, execution_complete, verification_complete]
    STANDARD: [execution_complete]
    LIGHT: []
    EXEMPT: []
    timeout_ms: 2000

  retention:
    current_session: full
    previous_session: summary
    older_sessions_ttl_hours: 24
    max_active_worklogs: 50

  aggregate_timeout_ms: 3000
```

## Customization Examples

### High-Performance Environment
```yaml
# Reduce overhead for fast execution
worklog:
  buffer_size: 20           # Larger batches
  buffer_time_seconds: 60   # Less frequent flushes

verification:
  timeout_ms: 500           # Faster timeout
  retry_delay_ms: 50        # Faster retry

aggregate_timeout_ms: 2000  # Tighter budget
```

### High-Reliability Environment
```yaml
# Maximize accountability
worklog:
  buffer_size: 5            # More frequent flushes
  buffer_time_seconds: 15   # Shorter time threshold

verification:
  max_automatic_retries: 2  # More retries
  timeout_ms: 2000          # More patience

retention:
  older_sessions_ttl_hours: 72  # Keep longer
  max_active_worklogs: 100     # More history
```

### Development Environment
```yaml
# Disable for local development
verification:
  enabled_tiers: []         # No verification

checkpoints:
  STRICT: []
  STANDARD: []
```

## Related Documentation
- [SPEC-REVISED.md](../../.dev/releases/current/v1.3-task-unified-accountability/SPEC-REVISED.md) - Full specification
- [SKILL.md](../../skills/sc-task-unified/SKILL.md) - Skill documentation
- [Migration Guide](./v1.3-accountability.md) - Upgrade instructions
```

#### Acceptance Criteria
- [ ] Configuration reference created at correct path
- [ ] All configuration options documented
- [ ] Default values and valid ranges specified
- [ ] Customization examples provided (high-perf, high-reliability, dev)
- [ ] Links to related documentation

#### Verification
```bash
# Check file exists and has key sections
ls docs/reference/accountability-config.md
grep -n "worklog:\|verification:\|checkpoints:\|retention:" docs/reference/accountability-config.md
```

---

## Milestone Verification Checkpoint

### Pre-Completion Checklist
- [ ] All 4 deliverables complete
- [ ] SKILL.md Section 6 present and accurate
- [ ] All 5 new flags documented with examples
- [ ] Migration guide complete with all sections
- [ ] Configuration documentation complete
- [ ] All documentation reviewed for accuracy
- [ ] CHANGELOG.md updated

### Documentation Validation
```bash
# Verify SKILL.md structure
grep -n "## 6. Accountability" skills/sc-task-unified/SKILL.md

# Verify flags documented
grep -c "\-\-no-worklog\|\-\-skip-verify\|\-\-no-checkpoints\|\-\-verbose-log\|\-\-retry-memory" skills/sc-task-unified/SKILL.md

# Verify migration guide exists
ls docs/migration/v1.3-accountability.md

# Verify config reference exists
ls docs/reference/accountability-config.md
```

### CHANGELOG Update
```markdown
## [1.3.0] - 2026-XX-XX

### Added
- Accountability Framework for sc:task-unified
  - Worklog: Automatic audit trail for all tiers
  - Verification: Closed-loop status confirmation (STRICT tier)
  - Checkpoints: Progress summaries at phase boundaries
- New flags: --no-worklog, --skip-verify, --no-checkpoints, --verbose-log, --retry-memory
- Serena fallback mode for session-only logging

### Changed
- SKILL.md: Added Section 6 Accountability Framework
- Configuration: Added config/accountability.yaml

### Documentation
- Migration guide: docs/migration/v1.3-accountability.md
- Configuration reference: docs/reference/accountability-config.md
```

### Final Release Checklist
- [ ] All milestones (M1-M6) complete
- [ ] All tests passing (`uv run pytest tests/accountability/ -v`)
- [ ] Coverage ≥95% (`uv run pytest --cov=superclaude.accountability`)
- [ ] Documentation reviewed and accurate
- [ ] CHANGELOG updated
- [ ] No linting errors
- [ ] Ready for release

---

## File Summary

| File | Purpose | Status |
|------|---------|--------|
| `skills/sc-task-unified/SKILL.md` | Section 6 + flags | Modify |
| `docs/migration/v1.3-accountability.md` | Migration guide | Create |
| `docs/reference/accountability-config.md` | Config reference | Create |
| `CHANGELOG.md` | Release notes | Modify |
