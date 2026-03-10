# Phase 3 -- Roadmap File Passing

This phase replaces the unreliable roadmap `--file` passing path with inline content embedding guarded by size-based fallback. The work stays narrowly focused on the roadmap executor behavior and the integration checks named in the roadmap.

### T03.01 -- Add inline input embedding and 100KB guard to roadmap step execution

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | The roadmap requires roadmap step execution to embed input file contents inline instead of relying on `--file`, while preserving a fallback when embedded content grows too large. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/evidence.md`

**Deliverables:**
- Inline embedding design record for roadmap executor inputs
- Evidence note for the 100KB fallback guard and empty-input no-op behavior
- Validation evidence placeholder for embedded prompt behavior

**Steps:**
1. **[PLANNING]** Load roadmap context for inline embedding and size-guard behavior.
2. **[PLANNING]** Check dependencies and confirm roadmap executor dead-code cleanup is complete.
3. **[EXECUTION]** Add the `_embed_inputs()` behavior described by the roadmap for fenced inline input embedding with path headers.
4. **[EXECUTION]** Record the 100KB total-content guard, the empty-input no-op case, and the fallback to `--file` with warning logging.
5. **[VERIFICATION]** Run the roadmap step validation path covering inline embedding and fallback behavior.
6. **[COMPLETION]** Document the embedding behavior and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/spec.md` records `_embed_inputs()` behavior, inline fenced blocks, and the 100KB guard.
- The task preserves the roadmap requirement that `extra_args=[]` is used unless the size guard triggers fallback behavior.
- Re-running the same design review uses the same inline embedding, empty-input, and fallback expectations.
- Traceability from `R-014` to `D-0009` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/notes.md`.

**Validation:**
- Manual check: validation scope includes inline embedding, empty-input no-op handling, and size-guard fallback behavior.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/evidence.md`

**Dependencies:** T02.04
**Rollback:** TBD (if not specified in roadmap)

### T03.02 -- Add integration tests for embedded roadmap input content and fallback handling

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | The roadmap requires integration coverage for embedded prompt content, paths with spaces, and 100KB fallback handling. These tests validate the changed roadmap executor behavior before final acceptance begins. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Required: None \| Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/spec.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/notes.md`
- `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/evidence.md`

**Deliverables:**
- Integration test plan for embedded input content and fallback conditions
- Evidence note for spaced-path handling and prompt-content verification
- Validation evidence placeholder for the file-passing integration suite

**Steps:**
1. **[PLANNING]** Load roadmap context for file-passing integration coverage.
2. **[PLANNING]** Check dependencies and confirm inline embedding behavior is defined before testing it.
3. **[EXECUTION]** Add integration coverage for embedded prompt content from roadmap inputs.
4. **[EXECUTION]** Add integration coverage for paths with spaces and for the 100KB fallback trigger.
5. **[VERIFICATION]** Run the integration validation path for roadmap file-passing behavior.
6. **[COMPLETION]** Document the integration scope and evidence placeholders in the intended artifact files.

**Acceptance Criteria:**
- Manual check: `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/spec.md` records embedded prompt content, spaced-path handling, and 100KB fallback coverage.
- The task preserves the roadmap requirement that the integration tests validate all three named file-passing scenarios.
- Re-running the same integration review uses the same three observable scenarios without added scope.
- Traceability from `R-015` to `D-0010` is documented in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/notes.md`.

**Validation:**
- Manual check: integration coverage includes embedded prompt content, paths with spaces, and fallback triggering.
- Evidence: linkable artifact produced in `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/evidence.md`

**Dependencies:** T03.01
**Rollback:** TBD (if not specified in roadmap)

### Checkpoint: End of Phase 3
**Purpose:** Confirm roadmap file-passing behavior and its integration coverage are ready for final acceptance validation.
**Checkpoint Report Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/CP-P03-END.md`
**Verification:**
- Confirm Phase 3 tasks cover inline embedding design and the three named integration scenarios.
- Confirm D-0009 and D-0010 have intended artifact paths and evidence placeholders under the tasklist root.
- Confirm Phase 4 acceptance tasks can rely on the file-passing behavior defined in this phase.
**Exit Criteria:**
- T03.01 and T03.02 are complete or explicitly recorded as blocked.
- D-0009 and D-0010 are registered in the index and linked from this phase file.
- Phase 4 can start without unresolved roadmap file-passing scope gaps.
