# D-0008: Sentinel Self-Validation Check (SC-003)

## Check Specification

**ID**: SC-003
**Purpose**: Scan generated spec output for remaining `{{SC_PLACEHOLDER:name}}` sentinels to ensure all placeholders were resolved during content population.

## Regex Pattern

```
\{\{SC_PLACEHOLDER:[^}]+\}\}
```

**Matches**: Any string of the form `{{SC_PLACEHOLDER:...}}` where `...` is one or more non-`}` characters.

## Pass/Fail Logic

- **PASS**: Zero matches -- all sentinels resolved
- **FAIL**: N > 0 matches -- report count and list unresolved sentinel names

## Instruction Block (for SKILL.md Phase 3, after step 3b)

```markdown
#### Self-Validation: Sentinel Check (SC-003)

After step 3b (content population), before proceeding to step 3c (brainstorm):

1. Scan `{work_dir}/portify-release-spec.md` for remaining sentinels using pattern `\{\{SC_PLACEHOLDER:[^}]+\}\}`
2. Count matches
3. If count > 0:
   - List each unresolved sentinel with its line number
   - Re-attempt population for the affected sections
   - Re-scan after remediation
   - If sentinels still remain after one retry, record them in the return contract `warnings` array and continue (non-blocking for brainstorm phase)
4. If count == 0: Proceed to step 3c

Record sentinel check result in Phase 3 contract:
```yaml
sentinel_check:
  remaining_count: <int>  # 0 = pass
  unresolved: [<list of sentinel names>]  # empty on pass
```
```

## Integration Point

- **Position**: After Phase 3 step 3b (content population), before step 3c (automated brainstorm)
- **Blocking**: Non-blocking (warns but does not halt pipeline)
- **Retry**: One automatic retry before accepting remaining sentinels as warnings
- **Target file**: `SKILL.md` new Phase 3 section (to be written in sprint Phase 2)

## Verification

The regex `\{\{SC_PLACEHOLDER:[^}]+\}\}` was tested against the template:
- Template file: 57 intentional matches (correct -- template has unresolved placeholders by design)
- A populated spec should have 0 matches
- The pattern produces zero false positives on prose containing `{{` or `}}` separately
