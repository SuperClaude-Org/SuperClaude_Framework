/sc:task "Comprehensive root-cause debug + fix pass for v2.05 sprint CLI"  
  --strategy enterprise --compliance strict --verify critical --delegate
  --parallel --concurrency 10 --ultrathink --seq --serena --c7 --validate    
  --focus quality --scope system                        

  Target scope:
  - /config/workspace/SuperClaude_Framework/.dev/releases/current/v2.05-sprin
  t-cli-specification
  - /config/workspace/SuperClaude_Framework/src/superclaude/cli/sprint
  - /config/workspace/SuperClaude_Framework/tests/sprint

  Mission:
  Run a full forensic debug pass with exactly 10 parallel agents, each with a
   distinct strategy, then debate findings, debate fixes, and implement only
  the highest-confidence fixes.

  Required 10-agent strategy split:
  1) subprocess lifecycle + timeout enforcement
  2) executor poll-loop + hang/stall behavior
  3) signal handling + shutdown semantics
  4) command routing (/sc:task vs /sc:task-unified) + CLI invocation
  semantics
  5) tmux path vs foreground path divergence
  6) env/runtime parity (installed binary vs source tree)
  7) monitor/TUI/thread interaction + stall detection control-plane gaps
  8) status determination logic and false PASS/false HALT classification
  9) test-suite adequacy + missing regression scenarios
  10) logs/telemetry quality for diagnosing failures (exit codes, phase
  transitions)

  Process (must follow):
  A) Root-cause discovery (parallel): each agent returns hypotheses with
  file:line evidence + confidence + falsification checks.
  B) Adversarial debate round 1: challenge each root cause; remove weak
  hypotheses.
  C) Propose fixes (multiple options per root cause): minimal, moderate,
  robust.
  D) Adversarial debate round 2: challenge each fix for correctness, risk,
  and side effects.
  E) Select final fix set by confidence/risk/impact matrix.
  F) Implement fixes in code.
  G) Add/adjust tests to lock regressions.
  H) Validate with:
     - uv run ruff check src/superclaude/cli/sprint tests/sprint
     - uv run pytest tests/sprint -v
  I) Final output:
     - ranked root causes (with evidence)
     - rejected hypotheses (and why)
     - chosen fixes (and why)
     - files changed
     - test/lint results
     - residual risks + follow-ups``` 

● I'll analyze the existing prompt and design an optimized, generic workflow. Let me first
  understand the current architecture and available tools to make informed recommendations.

● Explore(Explore available commands/skills) gpt-5.3-codex
  ⎿  Done (28 tool uses · 122.6k tokens · 1m 57s)
  (ctrl+o to expand)

● Explore(Read adversarial protocol skill) gpt-5.3-codex
  ⎿  Done (10 tool uses · 61.2k tokens · 6m 29s)
  (ctrl+o to expand)

● Explore(Read cleanup-audit and task-unified) gpt-5.3-codex
  ⎿  Done (3 tool uses · 39.9k tokens · 59s)
  (ctrl+o to expand)

● Now I have a comprehensive understanding of the existing framework. Let me analyze and
  produce the improved workflow.

● Explore(Read adversarial skill details) gpt-5.3-codex
  ⎿  Done (1 tool use · 35.5k tokens · 37s)
  (ctrl+o to expand)

● Now I have a thorough understanding of the full framework. Let me synthesize the improved
  workflow.

  ---
  Analysis of the Original Prompt

  Strengths

  - Clear 10-agent decomposition with distinct investigation domains
  - Well-defined adversarial debate rounds (A-I pipeline)
  - Evidence-based output requirements (file:line, confidence, falsification)

  Weaknesses Identified

  ┌─────┬─────────────────────────────────────────────┬─────────────────────────────────┐
  │  #  │                    Issue                    │             Impact              │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │ 1   │ Hardcoded to v2.05 sprint CLI — not         │ Zero genericity                 │
  │     │ reusable                                    │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ Orchestrator does everything — reads all 10 │ Massive token consumption (50K+ │
  │ 2   │  agent outputs, runs both debates, selects  │  on main agent)                 │
  │     │ fixes, implements, tests                    │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ No model tiering — all 10 agents presumably │ Wasted cost; Haiku can do       │
  │ 3   │  use same model                             │ surface scans, Opus should only │
  │     │                                             │  do synthesis                   │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ Debates are ad-hoc — doesn't leverage       │ Reinvents the wheel, loses      │
  │ 4   │ existing /sc:adversarial protocol with its  │ quantitative scoring            │
  │     │ 5-step scoring rubric                       │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ No MCP server delegation — --seq --serena   │                                 │
  │ 5   │ --c7 flags set but no workflow specifies    │ MCP servers underutilized       │
  │     │ WHEN each is used                           │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ No initial analysis phase — jumps straight  │ Agents may investigate          │
  │ 6   │ to 10 agents without knowing what the       │ irrelevant domains              │
  │     │ codebase contains                           │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ Sequential debate bottleneck — all 10       │                                 │
  │ 7   │ agents must complete before debate starts,  │ Could pipeline partial results  │
  │     │ then debate is serial                       │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │ 8   │ No checkpoint/resume — if session dies at   │ Risk for long-running workflows │
  │     │ step F, everything restarts                 │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │ 9   │ Fixed at 10 agents — some codebases don't   │ Wasted agent slots              │
  │     │ have tmux paths or TUI concerns             │                                 │
  ├─────┼─────────────────────────────────────────────┼─────────────────────────────────┤
  │     │ Implementation + testing not delegated —    │ Should delegate to              │
  │ 10  │ orchestrator implements fixes directly      │ python-expert or                │
  │     │                                             │ backend-architect               │
  └─────┴─────────────────────────────────────────────┴─────────────────────────────────┘

  ---
  Redesigned Workflow: /sc:forensic — Generic Forensic QA & Debug Pipeline

  Design Principles

  1. Generic-first: Works on ANY codebase/feature — investigation domains are
  auto-discovered
  2. Orchestrator is a dispatcher: Never reads source code directly; only reads agent
  summaries
  3. Model tiering: Haiku for surface scans, Sonnet for deep analysis, Opus for
  synthesis/decisions
  4. Leverage existing commands: /sc:adversarial, /sc:cleanup-audit, /sc:spawn
  5. Checkpoint-resumable: Each phase writes artifacts; any phase can restart from prior
  output
  6. MCP-aware: Serena for symbol navigation, Sequential for reasoning chains, Context7 for
  framework patterns

  Phase Architecture

  ┌─────────────────────────────────────────────────────────────────────┐
  │                    ORCHESTRATOR (Opus, ~5K tokens)                  │
  │  Reads ONLY: phase artifacts, agent summaries, decision matrices   │
  │  Writes: phase transitions, final report                           │
  └────┬──────────┬──────────┬──────────┬──────────┬──────────┬────────┘
       │          │          │          │          │          │
     Phase 0   Phase 1    Phase 2    Phase 3    Phase 4    Phase 5
     Recon     Discover   Debate     Fix-Plan   Implement  Validate

  Phase 0: Reconnaissance (Auto-Discovery)

  Model: Haiku (cheap, fast) — 3 parallel agents
  Purpose: Replace hardcoded 10-domain split with dynamic domain discovery
  MCP: Serena (get_symbols_overview), Context7 (framework detection)

  Agent 0a (Haiku): Structural inventory
    - File tree, module boundaries, entry points, test coverage map
    - Output: structural-inventory.json

  Agent 0b (Haiku): Dependency & import graph
    - Call chains, circular deps, external vs internal boundaries
    - MCP: Serena find_referencing_symbols for hot paths
    - Output: dependency-graph.json

  Agent 0c (Haiku): Risk surface scan
    - Error handling patterns, subprocess usage, signal handlers,
      env-dependent paths, untested branches
    - Output: risk-surface.json

  Orchestrator action (~500 tokens): Read 3 JSON summaries → generate
  investigation-domains.json — a dynamic list of N domains (3-10) with:
  - Domain name + description
  - Files in scope (from inventory)
  - Risk score (from surface scan)
  - Suggested specialist agent type
  - Suggested model tier (Haiku/Sonnet/Opus based on risk)

  Key innovation: The domains are discovered, not hardcoded. A CLI tool gets
  subprocess/signal/tmux domains. A web app gets route/middleware/auth domains. A library
  gets API surface/type safety/backward compat domains.

  Phase 1: Root-Cause Discovery (Parallel)

  Model: Sonnet (N agents, one per discovered domain) + Haiku (low-risk domains)
  Purpose: Each agent investigates its domain and returns structured hypotheses
  MCP: Serena (symbol lookup), Sequential (reasoning chains), Context7 (framework patterns)
  Concurrency: Up to --concurrency N (default: 10)

  Each agent receives:
  - Its domain definition from investigation-domains.json
  - The structural inventory (read-only context)
  - The dependency graph (for tracing impacts)
  - A standardized output schema:

  # Per-agent output: findings-domain-N.md
  domain: "<name>"
  files_examined: ["file:lines"]
  hypotheses:
    - id: H-N-1
      summary: "..."
      evidence: ["file:line — grep excerpt"]
      confidence: 0.0-1.0
      falsification: "How to disprove this"
      severity: critical|high|medium|low
      category: bug|design-flaw|test-gap|tech-debt|race-condition

  Orchestrator action (~1K tokens): Collect N findings files. Do NOT read them deeply. Pass
  filenames to Phase 2.

  Phase 2: Adversarial Debate (Delegated)

  Model: Opus (debate-orchestrator) + Sonnet (advocates)
  Purpose: Challenge hypotheses, remove weak ones, rank survivors
  Delegation: Invoke existing /sc:adversarial protocol (Mode A: compare findings files)

  /sc:adversarial --compare findings-domain-1.md,...,findings-domain-N.md \
    --depth deep --convergence 0.80 --focus "evidence-quality,reproducibility,severity"

  This leverages the existing 5-step adversarial protocol:
  1. Diff Analysis: Cross-domain contradiction detection, duplicate hypothesis merging
  2. Debate Round 1 (parallel): Each domain advocate defends hypotheses, steelman-critiques
  others
  3. Debate Round 2 (sequential): Rebuttals with cross-domain evidence
  4. Scoring: 25-criterion rubric applied to each hypothesis (not just each file)
  5. Selection: Ranked hypothesis list with confidence/evidence scores

  Output: adversarial/debate-transcript.md + adversarial/base-selection.md (ranked
  hypotheses)

  Orchestrator action (~500 tokens): Read base-selection.md summary scores only. Filter to
  hypotheses with confidence ≥ threshold.

  Phase 3: Fix Proposals (Parallel)

  Model: Sonnet (one agent per surviving hypothesis cluster)
  Purpose: Generate fix options with risk analysis
  MCP: Serena (impact tracing via find_referencing_symbols), Context7 (idiomatic patterns)

  Each agent receives one hypothesis cluster and produces:

  # fix-proposal-H-N.md
  hypothesis: H-N-1
  fix_options:
    - tier: minimal
      changes: [{file, line, description, diff_preview}]
      risk: "..."
      side_effects: ["..."]
      confidence: 0.0-1.0
    - tier: moderate
      # ...
    - tier: robust
      # ...
  test_requirements:
    - description: "Regression test for ..."
      type: unit|integration|e2e

  Phase 3b: Fix Debate (Delegated)

  Model: Reuse /sc:adversarial Mode A on fix proposal files
  Purpose: Challenge fixes for correctness, risk, side effects

  /sc:adversarial --compare fix-proposal-H-1.md,...,fix-proposal-H-M.md \
    --depth standard --focus "correctness,risk,side-effects"

  Output: Ranked fix set with confidence/risk/impact matrix → fix-selection.md

  Orchestrator action (~800 tokens): Read fix-selection summary. Build implementation plan.
  This is the only decision the orchestrator makes: which fixes to greenlight based on the
  matrix.

  Phase 4: Implementation (Delegated)

  Model: Sonnet (specialist agents based on domain — python-expert, backend-architect, etc.)
  Purpose: Apply selected fixes + write regression tests
  MCP: Serena (symbol-level edits via replace_symbol_body), Context7 (test patterns)

  Agent 4a (Sonnet: python-expert): Implement code fixes
    - Input: fix-selection.md (greenlit fixes only)
    - Uses: Serena replace_symbol_body for surgical edits
    - Output: list of changed files

  Agent 4b (Sonnet: quality-engineer): Write/adjust regression tests
    - Input: test_requirements from fix proposals
    - Uses: Context7 for test framework patterns
    - Output: new/modified test files

  Both agents run in worktree isolation to avoid conflicts.

  Phase 5: Validation (Delegated)

  Model: Haiku (fast lint) + Sonnet (test analysis)
  Purpose: Verify fixes don't break anything

  Agent 5a (Haiku): Lint pass
    - uv run ruff check <changed_files>
    - Output: lint-results.txt

  Agent 5b (Sonnet: quality-engineer): Test execution + analysis
    - uv run pytest <test_dirs> -v --tb=short
    - Analyze failures, correlate with fix proposals
    - Output: test-results.md with pass/fail/analysis

  Agent 5c (Sonnet: self-review): Post-implementation review
    - Read all changes, verify against original hypotheses
    - Check for introduced regressions, incomplete fixes
    - Output: self-review.md

  Phase 6: Final Report (Orchestrator)

  Model: Opus (~2K tokens)
  Purpose: Synthesize all phase artifacts into final output

  The orchestrator reads ONLY the summary artifacts (not source code):
  - investigation-domains.json (Phase 0)
  - adversarial/base-selection.md (Phase 2 — ranked hypotheses)
  - fix-selection.md (Phase 3b — chosen fixes)
  - lint-results.txt + test-results.md + self-review.md (Phase 5)

  Produces:

  # Forensic QA Report

  ## Ranked Root Causes (with evidence)
  ## Rejected Hypotheses (and why)
  ## Chosen Fixes (and why)
  ## Files Changed
  ## Test/Lint Results
  ## Residual Risks + Follow-ups
  ## Domain Coverage Map (what was/wasn't investigated)

  ---
  Token Budget Comparison

  ┌───────────────────────┬─────────────────────────┬──────────────────────────────────┐
  │       Component       │        Original         │            Redesigned            │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Orchestrator          │ ~50-80K (reads          │ ~5-8K (reads summaries only)     │
  │                       │ everything)             │                                  │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 0 (Recon)       │ N/A (hardcoded)         │ ~3K (3× Haiku)                   │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 1 (Discovery)   │ ~30K (10× agents)       │ ~20-30K (N× Sonnet, dynamic)     │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 2 (Debate 1)    │ ~15K (orchestrator does │ ~8K (delegated to adversarial    │
  │                       │  it)                    │ protocol)                        │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 3 (Fix          │ ~10K (orchestrator)     │ ~10K (parallel Sonnet agents)    │
  │ proposals)            │                         │                                  │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 3b (Debate 2)   │ ~10K (orchestrator)     │ ~5K (delegated to adversarial    │
  │                       │                         │ protocol)                        │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 4 (Implement)   │ ~8K (orchestrator)      │ ~6K (specialist agents)          │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Phase 5 (Validate)    │ ~3K                     │ ~4K (3× agents)                  │
  ├───────────────────────┼─────────────────────────┼──────────────────────────────────┤
  │ Total orchestrator    │ ~50-80K                 │ ~5-8K (90% reduction)            │
  │ tokens                │                         │                                  │
  └───────────────────────┴─────────────────────────┴──────────────────────────────────┘

  Model Tier Usage

  ┌────────┬─────────────────────────────────────────────────┬──────────────────────────┐
  │  Tier  │                    Used For                     │     Cost Efficiency      │
  ├────────┼─────────────────────────────────────────────────┼──────────────────────────┤
  │ Haiku  │ Phase 0 recon, Phase 5 lint, low-risk Phase 1   │ Cheapest, fastest scans  │
  │        │ domains                                         │                          │
  ├────────┼─────────────────────────────────────────────────┼──────────────────────────┤
  │ Sonnet │ Phase 1 investigation, Phase 3 fix proposals,   │ Balanced depth/cost      │
  │        │ Phase 4 implementation                          │                          │
  ├────────┼─────────────────────────────────────────────────┼──────────────────────────┤
  │ Opus   │ Phase 2 debate orchestration, Phase 6 final     │ Only for highest-value   │
  │        │ synthesis                                       │ decisions                │
  └────────┴─────────────────────────────────────────────────┴──────────────────────────┘

  MCP Server Utilization Map

  ┌────────────┬───────────────────────────────────────┬────────────────────────────────┐
  │   Server   │                 Phase                 │            Purpose             │
  ├────────────┼───────────────────────────────────────┼────────────────────────────────┤
  │ Serena     │ 0 (symbols overview), 1 (symbol       │ Surgical code understanding &  │
  │            │ lookup), 4 (symbol-level edits)       │ modification                   │
  ├────────────┼───────────────────────────────────────┼────────────────────────────────┤
  │ Sequential │ 1 (reasoning chains), 2 (debate       │ Complex multi-step reasoning   │
  │            │ structure), 3 (risk analysis)         │                                │
  ├────────────┼───────────────────────────────────────┼────────────────────────────────┤
  │ Context7   │ 0 (framework detection), 1 (pattern   │ Framework-idiomatic patterns   │
  │            │ matching), 4 (test patterns)          │                                │
  └────────────┴───────────────────────────────────────┴────────────────────────────────┘

  Existing Commands/Skills Leveraged

  ┌────────────────────────────────┬────────────────────────────────────────────────────┐
  │           Component            │                      How Used                      │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ /sc:adversarial +              │ Phase 2 (hypothesis debate) and Phase 3b (fix      │
  │ sc:adversarial-protocol        │ debate) — full 5-step protocol with quantitative   │
  │                                │ scoring                                            │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ /sc:spawn                      │ Phase 0 decomposition pattern (Epic → Story →      │
  │                                │ Task)                                              │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ sc:cleanup-audit-protocol      │ Phase 0 structural inventory borrows the           │
  │                                │ batch-and-checkpoint pattern                       │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: root-cause-analyst      │ Phase 1 domain agents                              │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: quality-engineer        │ Phase 5 validation                                 │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: self-review             │ Phase 5 post-implementation review                 │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: debate-orchestrator     │ Phase 2 coordination                               │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: merge-executor          │ Phase 3b fix selection merge                       │
  ├────────────────────────────────┼────────────────────────────────────────────────────┤
  │ Agent: python-expert /         │ Phase 4 implementation specialists                 │
  │ backend-architect              │                                                    │
  └────────────────────────────────┴────────────────────────────────────────────────────┘

  Checkpoint/Resume Design

  .forensic-qa/
  ├── phase-0/
  │   ├── structural-inventory.json
  │   ├── dependency-graph.json
  │   └── risk-surface.json
  ├── investigation-domains.json        ← orchestrator decision point
  ├── phase-1/
  │   ├── findings-domain-1.md
  │   └── findings-domain-N.md
  ├── phase-2/
  │   └── adversarial/                  ← standard adversarial output
  ├── phase-3/
  │   ├── fix-proposal-H-1.md
  │   └── fix-selection.md              ← orchestrator decision point
  ├── phase-4/
  │   ├── changes-manifest.json
  │   └── new-tests-manifest.json
  ├── phase-5/
  │   ├── lint-results.txt
  │   ├── test-results.md
  │   └── self-review.md
  ├── progress.json                     ← resume checkpoint
  └── final-report.md

  Any phase can resume from the last completed checkpoint. progress.json tracks:
  {
    "current_phase": 3,
    "completed_phases": [0, 1, 2],
    "investigation_domains": 7,
    "surviving_hypotheses": 12,
    "greenlit_fixes": 5,
    "started_at": "...",
    "last_checkpoint": "..."
  }

  ---
  Proposed Command & Skill (Description Only)

  Command: /sc:forensic

  Name: forensic
  Category: quality
  Complexity: advanced (wave-enabled)
  Personas: analyzer, architect, qa, security, performance (auto-selected per domain)
  MCP: Sequential (primary), Serena (secondary), Context7 (tertiary)
  Allowed tools: Read, Glob, Grep, Bash, TodoWrite, Task, Write, Skill

  Purpose: Generic forensic QA & debug pipeline for any codebase or feature release.
  Auto-discovers investigation domains, runs parallel root-cause analysis with model
  tiering, leverages existing adversarial debate protocol for hypothesis and fix validation,
   delegates implementation to specialist agents, and produces a comprehensive
  evidence-backed report.

  Usage:
  /sc:forensic [target-paths] [flags]

  # Examples:
  /sc:forensic src/auth/ tests/auth/           # Debug auth module
  /sc:forensic . --mode qa                     # Post-release QA pass
  /sc:forensic src/ --mode debug --focus "subprocess,signals"  # Guided domains
  /sc:forensic --resume .forensic-qa/          # Resume from checkpoint

  Key flags:
  - --mode debug|qa|regression — Investigation intent (default: auto-detect)
  - --depth quick|standard|deep — Maps to adversarial debate depth
  - --concurrency N — Max parallel agents (default: 10)
  - --focus "domain1,domain2" — Optional domain hints (supplements auto-discovery)
  - --confidence-threshold 0.7 — Minimum hypothesis confidence for fix proposals
  - --fix-tier minimal|moderate|robust — Default fix aggressiveness
  - --resume <path> — Resume from checkpoint directory
  - --dry-run — Run through Phase 3b (fix selection) but don't implement
  - --output <dir> — Output directory (default: .forensic-qa/)

  Skill: sc:forensic-protocol

  Purpose: Full behavioral specification for the 7-phase forensic pipeline (Phase 0-6 as
  described above). Contains:

  1. Phase specifications with input/output schemas, model tier assignments, MCP routing
  2. Domain auto-discovery algorithm — structural inventory → risk scoring → domain
  generation
  3. Agent prompt templates — standardized hypothesis/fix-proposal schemas
  4. Adversarial integration — how to invoke sc:adversarial-protocol for Phase 2 and 3b
  5. Model tier decision matrix — when to use Haiku vs Sonnet vs Opus
  6. Checkpoint/resume protocol — progress.json schema and phase restart logic
  7. Orchestrator token budget — hard cap on orchestrator context, delegation rules
  8. Output templates — final report structure, domain coverage map format

  Relationship to existing skills:
  - Depends on: sc:adversarial-protocol (Phases 2, 3b)
  - Borrows patterns from: sc:cleanup-audit-protocol (batch + checkpoint),
  sc:task-unified-protocol (compliance tiering for fix risk)
  - Delegates to agents: root-cause-analyst, quality-engineer, self-review,
  debate-orchestrator, merge-executor, python-expert/backend-architect

  ---
  This redesign achieves the stated goals:
  - 90% orchestrator token reduction through summary-only reads
  - Multi-model parallelism with cost-appropriate tiering (Haiku/Sonnet/Opus)
  - Reuses existing infrastructure (/sc:adversarial, agents, cleanup-audit patterns)
  - Fully generic — auto-discovers domains rather than hardcoding them
  - Checkpoint-resumable for long-running sessions
  - MCP-maximized — each server used at its optimal phase