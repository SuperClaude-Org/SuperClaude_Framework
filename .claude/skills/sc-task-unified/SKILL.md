---
name: sc-task-unified
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

> **⚠️ MANDATORY FIRST OUTPUT**: You MUST output the classification header block below as your VERY FIRST output, before ANY text, questions, or analysis. This is NON-NEGOTIABLE for telemetry.

```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [comma-separated keywords or "none"]
OVERRIDE: [true|false]
RATIONALE: [one-line reason]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

# /sc:task-unified - Unified Task Execution with Compliance

## Purpose

Unified command that merges orchestration capabilities with MCP compliance enforcement. Automatically classifies tasks into compliance tiers and enforces appropriate verification.

**Key Benefits**:
- Single command replaces confusion between `sc:task` and `sc:task-mcp`
- Automatic tier classification with confidence scoring
- Appropriate verification for each task type
- Prevents over-engineering for trivial changes
- Ensures safety for critical changes

## Triggers

Use `/sc:task` when:
- Task involves code modifications with downstream impacts
- Complexity score >0.6 with code modifications
- Multi-file scope (>2 estimated affected files)
- Security domain paths detected (auth/, security/, crypto/)
- Refactoring or system-wide changes requested

**Auto-Suggest Keywords**:
- High confidence: "implement feature", "refactor system", "fix security", "add authentication", "update database schema"
- Moderate confidence: "add new", "create component", "update service", "modify API"

## Usage

```bash
/sc:task [description]                           # Auto-detect all dimensions
/sc:task [description] --compliance strict       # Force STRICT tier
/sc:task [description] --compliance light        # Force LIGHT tier
/sc:task [description] --skip-compliance         # Bypass compliance (escape hatch)
/sc:task [description] --verify auto             # Auto-select verification
```

## Behavioral Flow

### 0. MANDATORY Classification Header (ALWAYS FIRST)

**CRITICAL**: Before ANY other output (including questions, clarifications, or responses), you MUST output the machine-readable classification header in this EXACT format:

```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [comma-separated list or "none"]
OVERRIDE: [true|false]
RATIONALE: [brief one-line explanation]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

**Example outputs**:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: STRICT
CONFIDENCE: 0.92
KEYWORDS: authentication, security, password
OVERRIDE: false
RATIONALE: Security-critical change involving password handling
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: LIGHT
CONFIDENCE: 0.88
KEYWORDS: typo, fix, documentation
OVERRIDE: false
RATIONALE: Trivial documentation change
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

**Rules**:
1. Output this header IMMEDIATELY as your first action
2. Output it BEFORE asking clarifying questions
3. Output it BEFORE any explanations or analysis
4. Output it even if you will ask questions afterward
5. Use the HTML comment wrapper for machine parsing
6. Never skip this header - it enables A/B testing and telemetry

### 1. Classification Phase

Classify task into compliance tier using priority order: STRICT > EXEMPT > LIGHT > STANDARD

**STRICT** (Priority 1): Security, data integrity, system-wide changes
- Keywords: authentication, database, migration, refactor, breaking change, security, encrypt, token, session, oauth
- Context: >2 files, security paths, API contracts
- Compound phrases: "fix security", "add authentication", "update database", "change api"

**EXEMPT** (Priority 2): Read-only, documentation, git operations
- Keywords: explain, search, commit, push, plan, discuss, brainstorm, what, how, why
- Context: is_read_only, is_documentation_only, is_git_operation
- Patterns: "^what (is|are|does)", "^how (do|does|can|should)", "^explain"

**LIGHT** (Priority 3): Trivial changes, formatting
- Keywords: typo, comment, whitespace, lint, docstring, formatting, spacing, minor
- Context: <=2 files, <=50 lines
- Compound phrases: "quick fix", "minor change", "fix typo", "refactor comment"

**STANDARD** (Priority 4): Default for typical development
- Keywords: implement, add, create, update, fix, build, modify, change
- Default tier when no other triggers match

### 2. Confidence Display (Human-Readable)

After the mandatory classification header, show a human-readable summary:

```
**Tier: STANDARD** [████████░░] 80%

Classified as STANDARD:
- Keywords matched: add, implement
- Confidence score: 0.78
- Considered alternatives: STRICT (0.35)
```

If confidence <70%, add prompt: "⚠️ Low confidence. Override with: `--compliance [strict|standard|light|exempt]`"

**Note**: The machine-readable header (Section 0) is for telemetry/A/B testing. This human-readable display is for user understanding.

### 3. Execution Phase

Execute task according to tier requirements:

**STRICT Execution**:
1. Activate project (mcp__serena__activate_project)
2. Verify git working directory clean (git status)
3. Load codebase context (codebase-retrieval)
4. Check relevant memories (list_memories -> read_memory)
5. Identify all affected files and test files
6. Make changes with full checklist
7. Identify all files that import changed code
8. Update all affected files
9. Spawn verification agent (quality-engineer)
10. Run comprehensive tests: `pytest [path] -v`
11. Answer adversarial questions

**STANDARD Execution**:
1. Load context via codebase-retrieval
2. Search downstream impacts (find_referencing_symbols OR grep)
3. Make changes
4. Run affected tests OR document manual verification
5. Verify basic functionality

**LIGHT Execution**:
1. Quick scope check (files/lines within bounds)
2. Make changes
3. Quick sanity check (syntax valid, no obvious errors)
4. Proceed with judgment

**EXEMPT Execution**:
1. Execute immediately
2. No verification overhead

### 4. Verification Phase

Route to appropriate verification based on tier and paths:

| Compliance Tier | Verification Method | Token Cost | Timeout |
|-----------------|---------------------|------------|---------|
| STRICT | Sub-agent (quality-engineer) | 3-5K | 60s |
| STANDARD | Direct test execution | 300-500 | 30s |
| LIGHT | Skip verification | 0 | 0s |
| EXEMPT | Skip verification | 0 | 0s |

**Critical Path Override**: Paths matching `auth/`, `security/`, `crypto/`, `models/`, `migrations/` always trigger CRITICAL verification regardless of compliance tier.

**Trivial Path Override**: Paths matching `*.md`, `docs/`, `*test*.py` may skip verification.

### 5. Feedback Collection

After completion, collect implicit feedback:
- Track if user overrode tier (implicit classification feedback)
- Note smooth completion vs errors (quality signal)
- Store for calibration learning

## MCP Integration

**Required Servers by Tier**:
- STRICT: Sequential, Serena (fallback not allowed)
- STANDARD: Sequential, Context7 (fallback allowed)
- LIGHT: None required (fallback allowed)
- EXEMPT: None required

**Circuit Breaker Behavior**:
- If required servers unavailable for STRICT tier, block task execution
- For other tiers, use fallbacks with noted limitations

## Tool Coordination

**Planning Phase**:
1. TodoWrite: Create task breakdown
2. codebase-retrieval: Load context
3. list_memories / read_memory: Check project state

**Execution Phase**:
1. Edit/MultiEdit/Write: Make changes
2. Grep/Glob: Find references
3. find_referencing_symbols: Trace dependencies

**Verification Phase**:
1. Task (quality-engineer): Spawn verification agent (STRICT only)
2. Bash: Run tests directly (STANDARD)
3. think_about_task_adherence: Reflect on completeness

**Completion Phase**:
1. write_memory: Save session state
2. think_about_whether_you_are_done: Final check

## Examples

### STRICT Task
```
/sc:task "implement user authentication with JWT"

-> Classified as STRICT (security domain, authentication keyword)
-> Full 6-category checklist enforced
-> Verification agent spawned
-> Adversarial questions answered
```

### STANDARD Task
```
/sc:task "add pagination to user list"

-> Classified as STANDARD (add keyword, typical feature)
-> Context loaded before editing
-> Downstream impacts checked
-> Direct test execution
```

### LIGHT Task
```
/sc:task "fix typo in README"

-> Classified as LIGHT (trivial keyword, documentation path)
-> Quick sanity check only
-> No verification delay
```

### EXEMPT Task
```
/sc:task "explain how the auth flow works"

-> Classified as EXEMPT (explain pattern detected)
-> Immediate execution
-> No compliance overhead
```

### Override Example
```
/sc:task "update config file" --compliance strict

-> User override to STRICT regardless of classification
-> Full verification enforced
```

## Boundaries

**Will:**
- Classify tasks into appropriate compliance tiers
- Enforce tier-appropriate verification requirements
- Provide confidence scoring with rationale
- Track feedback for continuous calibration
- Support user overrides with justification

**Will Not:**
- Skip safety-critical verification for STRICT tasks
- Apply STRICT overhead to genuinely trivial changes
- Override user's explicit compliance choice
- Proceed with <70% confidence without user confirmation

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tier classification accuracy | >=80% | User feedback on appropriateness |
| User confusion rate | <10% | "Which command?" questions eliminated |
| Skip rate (--skip-compliance) | <12% | Override tracking |
| Regression prevention | >=85% | Post-verification bug detection |
| STRICT tier overhead | <25% | Execution telemetry |

## Configuration References

- Keywords: `config/tier-keywords.yaml`
- Verification routing: `config/verification-routing.yaml`
- Acceptance criteria: `config/tier-acceptance-criteria.yaml`
- Circuit breakers: See MCP.md
- Routing logic: See ORCHESTRATOR.md
