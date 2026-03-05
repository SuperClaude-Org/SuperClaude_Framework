# Refactor Plan — Strategy 3: Self-Contained Task Item Quality Gate

**Pipeline**: sc:adversarial — Step 4 of 5
**Date**: 2026-03-04
**Verdict**: MODIFY (with M1-M4 modifications)
**Target spec**: `sc-tasklist-command-spec-v1.0.md`
**Target skill**: `sc-tasklist-protocol/SKILL.md` (the v3.0 generator reformatted as a skill)

---

## Integration Points

### IP-1: §7 Style Rules — Add Standalone Task Rule
**Risk**: Low
**Type**: Additive (new rule in existing section)
**Target section**: SKILL.md → `## Style Rules` (verbatim from v3.0 §7)

The existing §7 Style Rules govern formatting (checkbox syntax, ID format, metadata field order). This rule adds a content quality constraint.

**Patch text to add** (add as the last rule in §7 or as a new sub-section §7.N):

```markdown
### §7.N Standalone Task Requirement

Each generated task description must be standalone and action-oriented.
A task is standalone when it satisfies ALL of the following:

1. **Named artifact or target**: The description names the specific file,
   function, endpoint, or component being operated on. Generic phrases
   like "implement the feature" or "update the system" are prohibited.

2. **Session-start executable**: An agent beginning a fresh session
   with only the phase file can begin execution without external
   conversational context. The task must not rely on "as discussed",
   "the above approach", or implicit references from prior messages.

3. **Action verb + explicit object**: Imperative verb + specific target.
   Acceptable: "Add `rateLimit()` middleware to `src/middleware/auth.ts`".
   Prohibited: "Add the middleware we talked about".

4. **No cross-task prose dependency**: The task description must not
   reference information available only in another task's description.
   Shared context belongs in a roadmap-referenced file, not in task prose.

**Enforcement**: Before emitting each task, confirm it satisfies all four
criteria. If it does not, revise the description until it does.
Do NOT emit non-standalone tasks.
```

---

### IP-2: §8 Sprint Compatibility Self-Check — Add Standalone Gate
**Risk**: Low
**Type**: Additive (new check in existing self-check section)
**Target section**: SKILL.md → `## Sprint Compatibility Self-Check`

The existing §8 checks are structural (file existence, heading regex, ID format, contiguous numbering). This adds a generation-discipline check.

**Patch text to add** (add as a new check item in §8):

```markdown
### §8.N Task Standalone Check (Generation-Time)

During task emission (not post-hoc), verify for each task:

- [ ] Description names at least one specific artifact, file, function,
      or component (not generic "the feature" or "the component")
- [ ] No pronoun/reference to external conversation ("as discussed",
      "the above", "we agreed", "from our earlier session")
- [ ] Description contains an imperative verb with an explicit direct object

**If any check fails**: revise the task description before proceeding
to the next task. Do not accumulate violations.

Note: This check is generation-discipline (enforced during generation),
not a structural parse check. It cannot be automated by `make lint-architecture`.
```

---

### IP-3: §9 Acceptance Criteria — Add Content Quality Criterion
**Risk**: Low
**Type**: Additive (new criterion in existing list)
**Target section**: `sc-tasklist-command-spec-v1.0.md` → `## 9. Acceptance Criteria`

Add as criterion 8 (after the existing 7):

```markdown
8. Every generated task description is standalone per §7.N: names a
   specific artifact or target, contains no external-context references,
   and is executable by an agent starting a fresh session using only
   the generated phase file.
```

---

### IP-4: §9 Parity Criterion — Add Clarifying Note
**Risk**: Low
**Type**: Clarifying annotation (does not change functional behavior)
**Target section**: `sc-tasklist-command-spec-v1.0.md` → `## 9. Acceptance Criteria` → criterion 7

Current text:
```
7. Functional parity: output is identical to running the v3.0 generator prompt manually
```

Modified text:
```
7. Functional parity: output is structurally and schematically identical to running
   the v3.0 generator prompt manually (same file format, task ID scheme, metadata
   fields, and phase file structure). Note: §7.N standalone quality rules may produce
   improved task description prose versus a raw v3.0 run; this is intentional and
   within parity scope as it does not change any schema, structural element, or
   output file format.
```

---

### IP-5: Integration Strategies Doc — Add v1.1 Deferral Note
**Risk**: None (documentation-only)
**Type**: Annotation
**Target**: `tasklist-spec-integration-strategies.md` → Strategy 3 section

Add after the existing "Concrete spec changes" block:

```markdown
### Schema expansion deferred to v1.1
The full implementation of this principle — adding `Context:`, `Verify:`, and
`Blocked-Until:` fields per task (see `taskbuilder-integration-proposals.md`
Proposal 1) — is deferred to v1.1. v1.0 adopts the generation rule and
acceptance criterion only. The v1.1 schema expansion completes the enforcement
chain with structural field-level verifiability.
```

---

## Implementation Order

| Step | Action | File | Risk | Dependency |
|------|--------|------|------|------------|
| 1 | Add §7.N Standalone Task Requirement | SKILL.md | Low | None |
| 2 | Add §8.N Task Standalone Check | SKILL.md | Low | IP-1 complete |
| 3 | Add §9 criterion 8 | command spec v1.0 | Low | IP-1, IP-2 complete |
| 4 | Modify §9 criterion 7 (parity note) | command spec v1.0 | Low | None |
| 5 | Add v1.1 deferral note | integration strategies doc | None | None |

Steps 1-2 must be sequential (§8 references §7.N). Steps 3-5 are independent of each other and can be applied in any order after steps 1-2.

---

## Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Parity dispute from strict reading of criterion 7 | Medium | Medium | IP-4 resolves by explicitly scoping parity to schema/structure |
| Generator inconsistency on "standalone" interpretation | Medium | Low | IP-1 provides 4 specific criteria; minimizes LLM interpretation variance |
| §8 check perceived as unenforceable | High | Low | Check text explicitly notes it is generation-discipline, not parse-level; sets expectation correctly |
| Scope creep into Proposal 1 fields | Medium | Medium | IP-5 documents the boundary explicitly and defers schema to v1.1 |

---

## What This Does NOT Change

- Task ID format (`T<PP>.<TT>`)
- Phase file naming convention
- `tasklist-index.md` structure
- `make lint-architecture` checks (none of these changes affect lintable structure)
- Installation behavior
- Command layer (`tasklist.md`)
- Input validation (§5.4)
- MCP server usage
- The extracted reference files (`rules/`, `templates/`)
- Any existing §8 structural checks (new check is additive only)

---

## v1.1 Roadmap Item (Out of Scope for This Patch)

The following is explicitly deferred and should be tracked as a v1.1 enhancement:

**v1.1: Add Self-Contained Task Schema Fields**
- Add `Context:` field to §6B task format (files/artifacts to read before starting)
- Add `Verify:` field to §6B task format (inline acceptance criteria)
- Add `Blocked-Until:` field to §6B task format (prerequisite task IDs with status)
- Extend §8 self-check to structurally validate `Context:` and `Verify:` field presence
- Update §9 acceptance criteria to include field presence validation
- Source: `taskbuilder-integration-proposals.md` Proposal 1

This v1.1 change completes the enforcement chain that Strategy 3 (modified) begins.
