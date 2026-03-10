---
title: "Auggie MCP Framework-Wide Integration"
version: "1.0.0"
status: draft
feature_id: FR-AUGGIE-MCP
parent_feature: null
spec_type: infrastructure
complexity_score: 0.88
complexity_class: high
target_release: v3.0
authors: [user, claude]
created: 2026-03-09
---

## 1. Problem Statement

SuperClaude Framework has access to Auggie MCP semantic codebase retrieval, but the framework does not currently use it correctly or consistently. Existing references are defective, most candidate commands and agents do not integrate it at all, and several high-value code-analysis surfaces still operate without any semantic code discovery layer.

This matters because the affected commands and agents are explicitly responsible for codebase understanding, architecture analysis, troubleshooting, cleanup, documentation accuracy, and implementation planning. Pattern-only discovery with `Grep`, `Glob`, and raw `Read` works, but it misses semantic matches, dynamic loading patterns, transitive relationships, and naming-variant implementations that Auggie is designed to find.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| Only 3 of ~65 components referenced Auggie, and all 3 had critical defects | `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-prd.md` | Existing usage is effectively non-functional |
| 0 of 3 existing references used the correct tool invocation with required parameters | `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-prd.md` | Current instructions cannot reliably invoke Auggie MCP |
| 0 of 30 commands listed `auggie-mcp` in frontmatter at the time of analysis | `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-prd.md` | Claude Code cannot consistently select the server |
| 4 high-value commands (`analyze`, `troubleshoot`, `document`, `design`) had zero MCP servers configured | `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-prd.md` | Largest capability gap exists where codebase understanding matters most |
| Wave 1 analysis validated 20 HIGH-benefit candidates across commands, agents, and skills | `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-wave1-consolidated.md` | Integration opportunity is framework-wide, not command-local |

### 1.2 Scope Boundary

**In scope**: correcting defective Auggie references; adding Auggie MCP to high-value commands, skills, and agents; standardizing invocation syntax, fallback behavior, circuit breaker policy, query templates, token budgets, and framework docs; defining rollout milestones and validation criteria.

**Out of scope**: changing Auggie MCP server implementation itself; modifying low/no-benefit commands and agents; requiring Auggie for baseline framework operation; unrelated refactors outside Auggie integration; implementing every medium-benefit candidate in this release unless explicitly promoted later.

## 2. Solution Overview

Adopt Auggie MCP as the framework’s primary semantic discovery layer for high-value code understanding workflows, while preserving progressive enhancement. Every integrated surface must still work without Auggie, but should work better with it.

The solution has six coordinated themes:
1. Fix the existing broken references.
2. Add Auggie to the most valuable zero-MCP commands.
3. Extend semantic discovery into code quality and cleanup workflows.
4. Extend semantic discovery into implementation and explanation workflows.
5. Integrate Auggie into high-value analysis agents.
6. Standardize cross-cutting framework conventions, documentation, and verification.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Integration model | Progressive enhancement | Mandatory Auggie everywhere | The framework must remain usable when Auggie is unavailable |
| Primary discovery pattern | Auggie for semantic discovery, Serena/Grep/Read for fallback and verification | Pattern-only search | Semantic retrieval improves precision for codebase understanding tasks |
| Existing defective surfaces | Fix `task-unified.md` and `sc-task-unified/SKILL.md`; leave deprecated `task-mcp.md` out of active rollout | Fix all 3 equally | `task-mcp.md` is deprecated and should not drive new investment |
| Rollout structure | Milestone-based phased rollout | Big-bang framework-wide edit | Phasing reduces risk and makes validation tractable |
| Fallback behavior | Standardized 4-tier fallback chain | Per-command ad hoc fallback | Consistency reduces ambiguity and maintenance burden |
| Cross-cutting governance | Standardize circuit breaker, frontmatter, token budget, and query templates in the release itself | Leave conventions implicit | The main failure mode today is inconsistent or incorrect integration |

### 2.2 Workflow / Data Flow

```text
User command / skill / agent
    |
    v
Auggie-enabled discovery step
    |
    +--> Tier 1: mcp__auggie-mcp__codebase-retrieval
    |         - semantic discovery
    |         - domain-specific information_request
    |         - absolute directory_path
    |
    +--> Tier 2 fallback: Serena symbol/ref search
    |
    +--> Tier 3 fallback: Grep + Glob
    |
    +--> Tier 4 fallback: Read + manual file inspection
    |
    v
Downstream task-specific reasoning
    - analyze / troubleshoot / design / document
    - cleanup / improve / implement / explain
    - audit / root cause / repo indexing agents
    |
    v
Validation + rollout governance
    - circuit breaker policy
    - query template standards
    - token budget controls
    - framework docs + compliance audit
```

## 3. Functional Requirements

### FR-AUGGIE-MCP.1: Correct Existing Auggie References

**Description**: The release shall fix all active defective Auggie MCP references in existing framework components that currently mention Auggie incorrectly.

**Acceptance Criteria**:
- [ ] `task-unified.md` uses `mcp__auggie-mcp__codebase-retrieval` instead of bare `codebase-retrieval`
- [ ] Every active Auggie call site documents both `information_request` and `directory_path`
- [ ] `task-unified.md` includes `auggie-mcp` in `mcp-servers` frontmatter
- [ ] Fabricated syntax such as `codebase-retrieval/view` is removed from active surfaces
- [ ] `sc-task-unified/SKILL.md` is updated to match the canonical invocation pattern
- [ ] Deprecated `task-mcp.md` is not treated as a primary rollout target

**Dependencies**: None

### FR-AUGGIE-MCP.2: Integrate Auggie into High-Value Zero-MCP Commands

**Description**: The release shall add Auggie MCP integration to the high-value commands that currently have no MCP server support: `analyze`, `troubleshoot`, `design`, and `document`.

**Acceptance Criteria**:
- [ ] Each of the 4 commands lists `auggie-mcp` in frontmatter
- [ ] Each command includes domain-specific `information_request` templates
- [ ] `analyze` includes depth-aware semantic discovery aligned to the v1.2 analyze backlog guidance
- [ ] `troubleshoot` includes semantic code-path tracing queries
- [ ] `design` includes existing-system mapping queries before design output
- [ ] `document` includes code-understanding queries before documentation generation
- [ ] All 4 commands continue to function when Auggie is unavailable

**Dependencies**: FR-AUGGIE-MCP.1

### FR-AUGGIE-MCP.3: Extend Auggie into Code Quality and Cleanup Workflows

**Description**: The release shall integrate Auggie into code quality, cleanup, and duplicate-detection workflows where semantic search materially improves results.

**Acceptance Criteria**:
- [ ] `cleanup.md` includes semantic dead-code discovery and safe-removal verification guidance
- [ ] `cleanup-audit.md` integrates Auggie into its multi-pass audit flow
- [ ] `improve.md` uses Auggie for dependency-aware improvement analysis
- [ ] `confidence-check` uses Auggie in duplicate-detection guidance for Check 1
- [ ] `sc-cleanup-audit` guidance includes Auggie for dynamic usage and semantic duplicate detection
- [ ] All affected components degrade safely without Auggie

**Dependencies**: FR-AUGGIE-MCP.1, FR-AUGGIE-MCP.2

### FR-AUGGIE-MCP.4: Extend Auggie into Implementation and Explanation Workflows

**Description**: The release shall integrate Auggie into implementation-oriented and contextual explanation workflows where semantic discovery improves planning, pattern discovery, and explanation fidelity.

**Acceptance Criteria**:
- [ ] `implement.md` includes semantic integration-point and existing-pattern discovery
- [ ] `explain.md` includes semantic related-component and behavior-context discovery
- [ ] Tier 2 candidates promoted in this release define clear optional/preferred Auggie usage
- [ ] All affected surfaces keep baseline behavior without Auggie

**Dependencies**: FR-AUGGIE-MCP.2, FR-AUGGIE-MCP.3

### FR-AUGGIE-MCP.5: Integrate Auggie into High-Value Analysis Agents

**Description**: The release shall add Auggie-first discovery guidance to the highest-value analysis agents, especially audit, root-cause, architecture, security, and repository understanding agents.

**Acceptance Criteria**:
- [ ] Audit agents define complementary, non-redundant Auggie query roles
- [ ] `root-cause-analyst` includes semantic error-path tracing guidance
- [ ] `security-engineer` includes semantic discovery for auth, validation, and secret-handling flows
- [ ] `system-architect` includes semantic dependency and boundary-mapping guidance
- [ ] `repo-index` uses Auggie as its primary discovery mechanism
- [ ] Every integrated agent includes fallback guidance when Auggie is unavailable

**Dependencies**: FR-AUGGIE-MCP.2, FR-AUGGIE-MCP.3

### FR-AUGGIE-MCP.6: Standardize Cross-Cutting Auggie Conventions

**Description**: The release shall define and enforce framework-wide standards for Auggie circuit breaking, fallback sequencing, frontmatter conventions, query templates, token budgets, and framework documentation.

**Acceptance Criteria**:
- [ ] A single circuit breaker standard is documented for Auggie integrations
- [ ] A single fallback chain is documented for all integrated surfaces
- [ ] Frontmatter conventions for `auggie-mcp` are defined and applied consistently
- [ ] A query template library spans the major command and agent domains
- [ ] Token budget guidance exists for quick, standard, and deep usage
- [ ] MCP and orchestrator documentation are updated to reflect Auggie integration
- [ ] A compliance audit verifies M1-M5 outputs against the standard

**Dependencies**: FR-AUGGIE-MCP.1, FR-AUGGIE-MCP.2, FR-AUGGIE-MCP.3, FR-AUGGIE-MCP.4, FR-AUGGIE-MCP.5

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `docs/generated/auggie-mcp-framework-wide-integration-release-spec.md` | Canonical release-spec-formatted version of the Auggie integration plan | Source PRD and release-spec template |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/commands/task-unified.md` | Fix Auggie tool naming, parameters, frontmatter, and fallback guidance | Existing active integration is defective |
| `src/superclaude/skills/sc-task-unified/SKILL.md` | Fix Auggie invocation guidance and fallback behavior | Existing active skill guidance is defective |
| `src/superclaude/commands/analyze.md` | Add Auggie semantic discovery workflow and frontmatter | Highest-value zero-MCP command |
| `src/superclaude/commands/troubleshoot.md` | Add Auggie code-path tracing workflow and frontmatter | High-value troubleshooting gap |
| `src/superclaude/commands/design.md` | Add Auggie system-mapping workflow and frontmatter | Design needs semantic understanding of current state |
| `src/superclaude/commands/document.md` | Add Auggie code-understanding workflow and frontmatter | Documentation accuracy depends on code understanding |
| `src/superclaude/commands/cleanup.md` | Add semantic dead-code and safe-removal guidance | Cleanup benefits strongly from semantic search |
| `src/superclaude/commands/cleanup-audit.md` | Integrate Auggie into audit passes | Audit flow needs semantic duplicate and dynamic usage checks |
| `src/superclaude/commands/improve.md` | Add dependency-aware semantic improvement guidance | Improvement planning benefits from transitive dependency awareness |
| `src/superclaude/commands/implement.md` | Add integration-point and pattern discovery guidance | Implementation planning benefits from semantic context |
| `src/superclaude/commands/explain.md` | Add contextual semantic explanation support | Explanations improve with codebase-wide context |
| `src/superclaude/skills/confidence-check/SKILL.md` | Add semantic duplicate-detection guidance | Grep-only duplicate detection misses functional equivalents |
| `src/superclaude/skills/sc-cleanup-audit/**` | Add Auggie-aware audit guidance where applicable | Audit output quality improves with semantic discovery |
| `src/superclaude/agents/audit-analyzer.md` | Add Auggie-first discovery instructions | Deep structural audit is a semantic problem |
| `src/superclaude/agents/audit-comparator.md` | Add semantic overlap discovery instructions | Functional duplication is semantic |
| `src/superclaude/agents/audit-scanner.md` | Add dynamic-loading and usage-discovery instructions | Static grep misses runtime loading patterns |
| `src/superclaude/agents/audit-validator.md` | Add independent semantic verification instructions | Validation benefits from a different search modality |
| `src/superclaude/agents/root-cause-analyst.md` | Add semantic error-path tracing guidance | Root cause analysis needs cross-module tracing |
| `src/superclaude/agents/refactoring-expert.md` | Add semantic duplication/coupling guidance | Refactoring candidates are often naming-variant |
| `src/superclaude/agents/security-engineer.md` | Add auth/data-path semantic discovery guidance | Security reviews require end-to-end flow visibility |
| `src/superclaude/agents/system-architect.md` | Add dependency and boundary mapping guidance | Architecture analysis requires semantic graph discovery |
| `src/superclaude/agents/repo-index.md` | Add primary semantic repository overview workflow | Repo indexing is fundamentally a semantic discovery task |
| `/config/.claude/MCP.md` | Document Auggie MCP server usage and fallback standards | Framework docs must match release behavior |
| `/config/.claude/ORCHESTRATOR.md` | Update routing guidance to recognize Auggie | Tool-selection logic must reflect new server role |

### 4.3 Removed Files

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| Active reliance on `src/superclaude/commands/task-mcp.md` for Auggie rollout | Deprecated command surface | Route active rollout and future maintenance to `task-unified.md` |

### 4.4 Module Dependency Graph

```text
Wave 1 analysis
    -> PRD / release spec
        -> M1 fix existing integrations
        -> M2 zero-MCP commands
        -> M3 quality / cleanup surfaces
        -> M4 implementation / explanation surfaces
        -> M5 agents
        -> M6 standards / docs / compliance

Cross-cutting standards from M6
    -> command guidance
    -> skill guidance
    -> agent guidance
    -> MCP.md
    -> ORCHESTRATOR.md
```

### 4.5 Implementation Order

```text
1. Fix active defective Auggie references (M1) — removes known bad instructions first
2. Add Auggie to zero-MCP high-value commands (M2) — highest impact gap closure
   Extend quality / cleanup surfaces (M3) — [parallel with step 2 after M1]
3. Extend implementation / explanation surfaces (M4) — depends on patterns from 2
4. Integrate high-value agents (M5) — depends on established command/skill conventions
5. Standardize docs, query libraries, budgets, and compliance audit (M6) — depends on 1-4
```

## 5. Interface Contracts

### 5.1 CLI Surface

```text
No end-user CLI syntax change is required.
This release changes command, skill, and agent specifications so they invoke or prefer:
- mcp__auggie-mcp__codebase-retrieval
with required parameters:
- information_request
- directory_path
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `information_request` | string | none | Natural-language semantic retrieval query tailored to the command/agent domain |
| `directory_path` | absolute path string | none | Required absolute project root for Auggie retrieval |
| `auggie-mcp` frontmatter entry | list item | omitted today | Declares Auggie as an available MCP server for the command |

### 5.2 Gate Criteria

| Step | Gate Tier | Frontmatter | Min Lines | Semantic Checks |
|------|-----------|-------------|-----------|-----------------|
| Existing integration fix | critical | `auggie-mcp` present where workflow uses Auggie | N/A | Correct tool name, required params, no fabricated syntax |
| New command integration | high | `mcp-servers` updated | N/A | Domain-specific queries, fallback defined, progressive enhancement retained |
| Agent integration | high | N/A for frontmatter; workflow instructions updated | N/A | Auggie-first discovery role, fallback guidance, non-redundant query scope |
| Standards completion | high | Framework docs updated where applicable | N/A | Circuit breaker, fallback chain, token budget, template library, compliance audit |

### 5.3 Phase Contracts

```yaml
phase_contracts:
  M1:
    produces:
      - canonical_augie_invocation_pattern
      - corrected_existing_surfaces
    required_for:
      - M2
      - M3
      - M4
      - M5
  M2:
    produces:
      - zero_mcp_command_pattern
      - analyze_specific_depth_guidance
    required_for:
      - M4
      - M5
  M3:
    produces:
      - cleanup_quality_semantic_patterns
    required_for:
      - M4
      - M5
  M4:
    produces:
      - implementation_explanation_patterns
    required_for:
      - M6
  M5:
    produces:
      - agent_integration_patterns
    required_for:
      - M6
  M6:
    produces:
      - framework_standardization
      - compliance_verification
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-AUGGIE-MCP.1 | Existing active Auggie defects are eliminated | 0 remaining bare active `codebase-retrieval` references in rollout targets | grep / review audit |
| NFR-AUGGIE-MCP.2 | Zero-MCP high-value commands are eliminated | 0 remaining high-value zero-MCP commands in rollout scope | frontmatter audit |
| NFR-AUGGIE-MCP.3 | Integration consistency is maintained | 100% of integrated surfaces define fallback behavior | compliance audit |
| NFR-AUGGIE-MCP.4 | Circuit breaker policy is consistent | 100% of integrated surfaces align to the standard Auggie breaker policy | compliance audit |
| NFR-AUGGIE-MCP.5 | Query coverage is sufficient | 30+ domain-specific query templates across command/agent domains | template inventory |
| NFR-AUGGIE-MCP.6 | Analyze quality materially improves | precision >= 85%, recall >= 90%, false positive rate < 10% for analyze-specific validation targets | human review and benchmark comparison |
| NFR-AUGGIE-MCP.7 | Analyze latency remains bounded | p95 < 30s quick, p95 < 90s deep | timed validation runs |
| NFR-AUGGIE-MCP.8 | Progressive enhancement is preserved | All integrated surfaces remain usable without Auggie | fallback-path validation |
| NFR-AUGGIE-MCP.9 | MCP overhead stays bounded | < 15% overhead relative to expected workflow budget | protocol profiling |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Auggie server is unavailable during rollout or usage | MED | HIGH | Standardize fallback chain and circuit breaker behavior |
| Incorrect tool name or missing parameters propagate into additional files | MED | HIGH | Fix active surfaces first and audit all new integrations |
| Query templates are too generic to be useful | MED | MED | Require domain-specific templates and validate during compliance review |
| Token usage grows too much for deep workflows | LOW | MED | Publish token budget guidance by operation depth |
| Audit agents become redundant or overlapping | MED | MED | Define distinct query responsibilities per audit agent |
| Documentation and orchestrator guidance drift from actual rollout | MED | MED | Include explicit documentation updates and final compliance audit |
| Deprecated `task-mcp.md` causes confusion | LOW | LOW | Exclude it from primary rollout and point active logic to `task-unified.md` |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| Invocation syntax audit | command/skill markdown audit | Correct Auggie tool name and required parameter presence |
| Frontmatter audit | command markdown audit | `auggie-mcp` appears where workflows require it |
| Query template audit | command/agent/skill markdown audit | Domain-specific `information_request` templates exist |
| Fallback audit | command/agent/skill markdown audit | Standard fallback chain is documented |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| Existing-use fix validation | `task-unified.md` and `sc-task-unified` no longer contain defective Auggie guidance |
| Zero-MCP command validation | `analyze`, `troubleshoot`, `design`, and `document` all expose valid Auggie workflows |
| Quality/cleanup validation | `cleanup`, `cleanup-audit`, `improve`, and confidence/audit skills integrate semantic discovery correctly |
| Agent rollout validation | High-value agents define Auggie-first discovery plus fallback guidance |
| Documentation consistency validation | MCP and orchestrator docs reflect actual framework behavior |
| Sync verification | `make sync-dev` and `make verify-sync` pass once source and `.claude/` copies align |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Auggie available path | Run representative command workflows with Auggie available | Semantic discovery guidance is present and actionable |
| Auggie unavailable path | Simulate unavailable Auggie and follow fallback instructions | Workflow remains usable and explicitly degrades |
| Analyze deep workflow | Review `analyze` spec after integration | Depth-aware guidance, query templates, and metrics are all represented |
| Audit agent handoff | Review audit agent docs together | Query scopes are complementary rather than duplicative |

## 9. Migration & Rollout

- **Breaking changes**: No user-facing CLI breaking change is intended; this is a framework-behavior and specification rollout.
- **Backwards compatibility**: Preserve baseline workflows through progressive enhancement and explicit fallbacks.
- **Rollback plan**: Remove or revert Auggie-specific guidance in descending order of rollout phase; fallback-only behavior remains valid, so rollback is primarily documentation/spec reversion rather than runtime migration.

## 10. Downstream Inputs

### For sc:roadmap
Use the six requirement themes as roadmap milestones:
- M1 fix broken existing Auggie references
- M2 integrate zero-MCP high-value commands
- M3 integrate quality and cleanup surfaces
- M4 integrate implementation and explanation surfaces
- M5 integrate high-value agents
- M6 standardize docs, contracts, budgets, and compliance

Roadmap prioritization should weight M1 and M2 highest because they resolve active defects and the largest capability gaps.

### For sc:tasklist
Break work into batches by milestone and file cluster:
- Batch 1: existing fixes (`task-unified`, `sc-task-unified`)
- Batch 2: zero-MCP commands (`analyze`, `troubleshoot`, `design`, `document`)
- Batch 3: quality/cleanup commands and skills
- Batch 4: implementation/explanation commands and selected medium candidates
- Batch 5: agent integrations
- Batch 6: framework docs, template library, compliance audit, sync verification

Each batch should include explicit verification tasks for frontmatter, invocation syntax, fallback behavior, and template coverage.

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| O1 | Should any medium-benefit candidates be promoted into the mandatory v3.0 scope beyond those already named in M4? | Scope and effort | Before roadmap finalization |
| O2 | Should `task-mcp.md` receive only a deprecation note or be removed in a later cleanup release? | Documentation clarity | Before implementation starts |
| O3 | What exact compliance script or audit command will be the canonical post-rollout verifier? | Validation consistency | Before M6 completion |
| O4 | Which deferred v1.2 analyze enhancements should remain in v3.0 versus move to a later release? | Release scope control | Before roadmap approval |

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Auggie MCP | The `mcp__auggie-mcp__codebase-retrieval` semantic codebase retrieval tool |
| Progressive enhancement | Design rule that workflows remain usable without Auggie but improve when it is available |
| Fallback chain | Ordered degradation from Auggie to Serena to Grep/Glob to Read/manual inspection |
| Zero-MCP command | A command whose frontmatter currently declares no MCP servers |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-prd.md` | Primary source content for this release spec |
| `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-wave1-consolidated.md` | Evidence base and candidate ranking summary |
| `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-phase3-implementation-spec.md` | Detailed implementation guidance and query template patterns |
| `.dev/releases/backlog/v3.0-analyze-auggie/auggie-mcp-analysis-prompt.md` | Upstream orchestration prompt showing how source analysis was generated |
| `src/superclaude/examples/release-spec-template.md` | Template used to normalize this release specification |
| `.dev/releases/backlog/v1.2-analyze-auggie/sc-analyze-auggie-feature-spec.md` | Detailed analyze-specific predecessor referenced by M2 in the source PRD |
