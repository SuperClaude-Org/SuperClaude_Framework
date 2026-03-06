# Phase 2 -- Duplication Elimination

This phase removes the duplicated process behavior and dead roadmap executor code identified in the roadmap. The sequence follows the roadmap's split refactor plan so each sub-step can be validated with limited blast radius.

### T02.01 -- Remove the duplicated wait() override from sprint process handling

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-010 |
| Why | The roadmap identifies the sprint `wait()` override as pure no-op duplication. Removing this isolated override is the first low-risk step in the duplication-elimination sequence. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/evidence.md`

**Deliverables:**
- Removal plan for the duplicated `wait()` override
- Evidence note tying the removal to the roadmap's no-op duplication claim
- Validation evidence placeholder for unchanged test behavior

**Steps:**
1. **[PLANNING]** Load roadmap context for the wait-override deletion step.
2. **[PLANNING]** Check dependencies and confirm Phase 1 characterization tasks are available as the safety gate.
3. **[EXECUTION]** Remove the duplicated `wait()` override from the sprint process implementation scope described by the roadmap.
4. **[EXECUTION]** Record that this step is the isolated M2a refactor action with unchanged behavior intent.
5. **[VERIFICATION]** Run the existing tests that validate sprint process behavior after the override removal.
6. **[COMPLETION]** Document the removal evidence and traceability in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/spec.md` records removal of the duplicated `wait()` override step.
- The task preserves the roadmap requirement that existing tests pass unchanged after the no-op deletion.
- Repeating the same removal validation uses the same characterization gate and unchanged behavior expectation.
- Traceability from `R-009` and `R-010` to `D-0005` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/notes.md`.

**Validation:**
- Manual check: the wait-override deletion remains isolated from later hook-migration changes.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/evidence.md`

**Dependencies:** T01.04
**Rollback:** TBD (if not specified in roadmap)

### T02.02 -- Add lifecycle hook parameters to pipeline ClaudeProcess and record on_exit behavior

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-011 |
| Why | The roadmap's M2b-base work adds `on_spawn`, `on_signal`, and `on_exit` hooks to the pipeline base class and requires `on_exit` to run on the wait success path. This is the foundation for the later sprint hook migration. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena \| Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/evidence.md`

**Deliverables:**
- Lifecycle hook parameter design record for `on_spawn`, `on_signal`, and `on_exit`
- Evidence note for `wait()` success-path `on_exit` behavior
- Verification evidence placeholder for hook call-site coverage

**Steps:**
1. **[PLANNING]** Load roadmap context for the pipeline `ClaudeProcess` lifecycle hook addition.
2. **[PLANNING]** Check dependencies and confirm the wait-override deletion step is complete.
3. **[EXECUTION]** Add the `on_spawn`, `on_signal`, and `on_exit` hook parameters with `None` defaults to the pipeline `ClaudeProcess` initialization scope.
4. **[EXECUTION]** Record the required hook call sites in `start()`, `terminate()`, and `wait()`, including the normal-exit `on_exit` call before handle cleanup.
5. **[VERIFICATION]** Run the hook-focused validation path aligned to STRICT verification routing.
6. **[COMPLETION]** Document lifecycle-hook coverage and evidence in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/spec.md` records `on_spawn`, `on_signal`, and `on_exit` parameters plus the `wait()` success-path `on_exit` behavior.
- The task preserves the roadmap requirement that the new hook parameters default to `None` and cover the named lifecycle methods.
- The same hook design can be reviewed repeatedly without changing the named call-site expectations.
- Traceability from `R-009` and `R-011` to `D-0006` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/notes.md`.

**Validation:**
- Manual check: hook design coverage includes initialization parameters and `wait()` normal-exit `on_exit` behavior.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/evidence.md`

**Dependencies:** T02.01
**Rollback:** TBD (if not specified in roadmap)

### T02.03 -- Migrate sprint process logging to lifecycle hook factories and verify NFR-007

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-012 |
| Why | The roadmap's M2b-migrate step replaces sprint overrides with hook factories and requires explicit NFR-007 verification. This is the highest-sensitivity refactor because it changes how sprint process logging is attached to the base lifecycle. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena \| Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/evidence.md`

**Deliverables:**
- Hook-factory migration record for sprint process logging
- NFR-007 verification note for pipeline import boundaries
- Evidence placeholder for pre/post characterization validation

**Steps:**
1. **[PLANNING]** Load roadmap context for the sprint hook-factory migration and NFR-007 requirement.
2. **[PLANNING]** Check dependencies and confirm the pipeline lifecycle hooks are defined before migration.
3. **[EXECUTION]** Add the `_make_spawn_hook`, `_make_signal_hook`, and `_make_exit_hook` factory behavior described by the roadmap.
4. **[EXECUTION]** Record the wiring of these hooks in sprint `ClaudeProcess.__init__`, along with deletion of the old `start()` and `terminate()` override behavior.
5. **[VERIFICATION]** Run the STRICT verification path for characterization pass-before-and-after validation and NFR-007 import checks.
6. **[COMPLETION]** Document migration outcomes and NFR-007 evidence in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/spec.md` records the three lifecycle hook factories and the sprint `ClaudeProcess.__init__` migration scope.
- The task preserves the roadmap requirement that characterization coverage passes before and after the hook migration and that NFR-007 remains satisfied.
- The same migration review can be repeated using the same hook-factory and NFR-007 checkpoints.
- Traceability from `R-009` and `R-012` to `D-0007` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/notes.md`.

**Validation:**
- Manual check: migration scope includes factory creation, sprint hook wiring, override deletion, and NFR-007 verification.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/evidence.md`

**Dependencies:** T02.02
**Rollback:** TBD (if not specified in roadmap)

**Notes:** Tier conflict: [STRICT refactor vs STANDARD add] -> resolved to STRICT by priority rule.

### T02.04 -- Remove roadmap executor dead code for forbidden flags and subprocess argv helpers

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009, R-013 |
| Why | The roadmap explicitly identifies `_FORBIDDEN_FLAGS` and `_build_subprocess_argv` as confirmed dead code. Removing them completes the final M2 cleanup step before file-passing changes begin. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███████---] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/evidence.md`

**Deliverables:**
- Dead-code removal record for forbidden flags and subprocess argv helpers
- Evidence note for zero remaining grep matches
- Validation evidence placeholder for post-removal test coverage

**Steps:**
1. **[PLANNING]** Load roadmap context for removing `_FORBIDDEN_FLAGS` and `_build_subprocess_argv`.
2. **[PLANNING]** Check dependencies and confirm the hook migration step is complete before roadmap executor cleanup.
3. **[EXECUTION]** Remove the dead `_FORBIDDEN_FLAGS` and `_build_subprocess_argv` behaviors from the roadmap executor scope described by the roadmap.
4. **[EXECUTION]** Record the required zero-match grep checks and unchanged test expectations in the task artifacts.
5. **[VERIFICATION]** Run the dead-code removal validation path that checks for zero remaining references and passing tests.
6. **[COMPLETION]** Document the dead-code removal evidence in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/spec.md` records removal of `_FORBIDDEN_FLAGS` and `_build_subprocess_argv`.
- The task preserves the roadmap requirement that both dead-code identifiers return zero grep matches after removal.
- Re-running the same dead-code validation uses the same zero-match and passing-test expectations.
- Traceability from `R-009` and `R-013` to `D-0008` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/notes.md`.

**Validation:**
- Manual check: validation scope includes both zero-match grep checks and test-pass confirmation.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/evidence.md`

**Dependencies:** T02.03
**Rollback:** TBD (if not specified in roadmap)

### Checkpoint: End of Phase 2
**Purpose:** Confirm duplication elimination and dead-code removal are complete before roadmap file-passing changes begin.
**Checkpoint Report Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/CP-P02-END.md`
**Verification:**
- Confirm Phase 2 tasks preserve the roadmap sequence of wait deletion, hook base work, hook migration, and dead-code removal.
- Confirm STRICT tasks have hook-migration evidence placeholders and STANDARD tasks have direct-validation placeholders.
- Confirm D-0005 through D-0008 remain traceable to the duplication-elimination roadmap items.
**Exit Criteria:**
- T02.01 through T02.04 are complete or explicitly recorded as blocked.
- D-0005 through D-0008 are registered in the index and linked from this phase file.
- Phase 3 can start without unresolved Phase 2 dependency gaps.
