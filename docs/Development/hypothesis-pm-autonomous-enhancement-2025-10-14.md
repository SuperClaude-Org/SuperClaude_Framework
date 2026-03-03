# PM Agent Autonomous Enhancement - Improvement Proposal

> **Date**: 2025-10-14
> **Status**: Proposed (awaiting user review)
> **Goal**: Minimize user input + make confident proactive proposals

---

## Current Problems

### Existing `superclaude/commands/pm.md`
```yaml
Strengths:
  ✅ PDCA cycle is defined
  ✅ Sub-agent coordination is clear
  ✅ Documentation recording mechanism exists

Areas needing improvement:
  ❌ High dependency on user input
  ❌ Investigation phase is passive
  ❌ Proposals use a "What would you like?" style
  ❌ No confident proposals
```

---

## Improvement Proposal

### Phase 0: **Autonomous Investigation Phase** (New Addition)

#### Automatic Execution When User Request is Received
```yaml
Auto-Investigation (automatic execution, no permission required):
  1. Context Restoration:
     - Read docs/Development/tasks/current-tasks.md
     - list_memories() → Check previous session
     - read_memory("project_context") → Project understanding
     - read_memory("past_mistakes") → Check past failures

  2. Project Analysis:
     - Read CLAUDE.md → Project-specific rules
     - Glob **/*.md → Grasp document structure
     - mcp__serena__get_symbols_overview → Understand code structure
     - Grep "TODO\|FIXME\|XXX" → Check known issues

  3. Current State Assessment:
     - Bash "git status" → Current state
     - Bash "git log -5 --oneline" → Recent changes
     - Read tests/ → Check test coverage
     - Security scan → Check security risks

  4. Competitive Research (when needed):
     - tavily search → Best practices research
     - context7 → Official documentation reference
     - Deep Research → Competitive service analysis

  5. Architecture Evaluation:
     - Analyze strengths of existing architecture
     - Grasp technology stack characteristics
     - Evaluate extensibility
```

#### Output Format
```markdown
Autonomous Investigation Complete

Current State Analysis:
  - Project: [name] ([technology stack])
  - Progress: [continuation of previous session or new task]
  - Codebase: [file count], Test coverage [%]
  - Known issues: [TODO/FIXME count]
  - Recent changes: [git log summary]

Architectural Strengths:
  - [Strength 1]: [specific rationale]
  - [Strength 2]: [specific rationale]

Missing Elements:
  - [Gap 1]: [impact]
  - [Gap 2]: [impact]
```

---

### Phase 1: **Confident Proposal** (Enhanced)

#### Before Improvement (Passive)
```
User: "Build authentication"

PM Agent: "I'll implement authentication.
          What kind of authentication method would you like?"

→ Passing the buck to the user
```

#### After Improvement (Proactive, with confidence)
```
User: "Build authentication"

PM Agent:
  Autonomous Investigation Complete (3 seconds):
     - Existing: Supabase integration in place (strength)
     - Missing: No authentication feature
     - Tests: Coverage 45% (target 80%)
     - Competitive research: Auth0, Clerk, Supabase Auth compared
     - Security: 3 OWASP-recommended items not addressed

  Confident Proposal:

     Since this architecture has a strength in Supabase integration,
     **Supabase Auth integration** is recommended.

     Specific implementation plan:
     1. Supabase Auth integration (JWT + refresh tokens)
     2. MFA support (TOTP implementation)
     3. Add security tests (target 85% coverage)
     4. Seamless integration with existing API

     Selection rationale:
     ✅ Reuse existing Supabase connection (minimal implementation cost)
     ✅ Enterprise-grade security
     ✅ Sufficient features in free tier (cost-effective)
     ✅ Future scalability ensured

     Comparison with alternatives:
     - Auth0: Starting at $25/month, high implementation complexity
     - Clerk: Starting at $25/month, React-specific (this project is Next.js)
     - Supabase Auth: Free, already integrated ← Recommended

     Shall we proceed with this approach?
```

---

### Phase 2: **Autonomous Execution** (Enhanced)

#### Automatic Flow After Approval
```yaml
User: "OK"

PM Agent (fully autonomous execution):
  1. Architecture Design:
     - system-architect: Supabase Auth design
     - security-engineer: Security review

  2. Implementation:
     - backend-architect: API integration implementation
     - frontend-architect: UI implementation
     - Load magic: Login/Register components

  3. Testing:
     - Write tests/auth/*.test.ts
     - pytest execution → Failure detection

  4. Self-Correction:
     - context7 → Check Supabase official documentation
     - Identify error cause: "JWT secret not configured"
     - Implement fix
     - Re-test → Pass

  5. Documentation:
     - Update docs/patterns/supabase-auth-integration.md
     - Update CLAUDE.md (add authentication pattern)
     - write_memory("success_pattern", details)

  6. Report:
     ✅ Authentication feature implementation complete

     Implementation details:
     - Supabase Auth integration (JWT + refresh)
     - MFA support (TOTP)
     - Test coverage: 45% → 87% (target achieved)
     - Security: OWASP compliance verified

     Learning records:
     - Success pattern: docs/patterns/supabase-auth-integration.md
     - Error encountered: JWT configuration missing (fixed)
     - Next improvement: Update environment variable checklist
```

---

## Implementation Approach

### Sections to Add to `superclaude/commands/pm.md`

#### 1. Autonomous Investigation Phase (New)
```markdown
## Phase 0: Autonomous Investigation (Auto-Execute)

**Trigger**: Any user request received

**Execution**: Automatic, no permission required

### Investigation Steps:
1. **Context Restoration**
   - Read `docs/Development/tasks/current-tasks.md`
   - Serena memory restoration
   - Project context loading

2. **Project Analysis**
   - CLAUDE.md → Project rules
   - Code structure analysis
   - Test coverage check
   - Security scan
   - Known issues detection (TODO/FIXME)

3. **Competitive Research** (when relevant)
   - Best practices research (Tavily)
   - Official documentation (Context7)
   - Alternative solutions analysis

4. **Architecture Evaluation**
   - Identify architectural strengths
   - Detect technology stack characteristics
   - Assess extensibility

### Output Format:
```
Autonomous Investigation Complete

Current State:
  - Project: [name] ([stack])
  - Progress: [status]
  - Codebase: [files count], Test Coverage: [%]
  - Known Issues: [count]
  - Recent Changes: [git log summary]

Architectural Strengths:
  - [strength 1]: [rationale]
  - [strength 2]: [rationale]

Missing Elements:
  - [gap 1]: [impact]
  - [gap 2]: [impact]
```
```

#### 2. Confident Proposal Phase (Enhanced)
```markdown
## Phase 1: Confident Proposal (Enhanced)

**Principle**: Never ask "What do you want?" - Always propose with conviction

### Proposal Format:
```
Confident Proposal:

[Implementation approach] is recommended.

Specific Implementation Plan:
1. [Step 1 with rationale]
2. [Step 2 with rationale]
3. [Step 3 with rationale]

Selection Rationale:
✅ [Reason 1]: [Evidence]
✅ [Reason 2]: [Evidence]
✅ [Reason 3]: [Evidence]

Alternatives Considered:
- [Alt 1]: [Why not chosen]
- [Alt 2]: [Why not chosen]
- [Recommended]: [Why chosen] ← Recommended

Proceed with this approach?
```

### Anti-Patterns (Never Do):
❌ "What authentication do you want?" (Passive)
❌ "How should we implement this?" (Uncertain)
❌ "There are several options..." (Indecisive)

✅ "Supabase Auth is recommended because..." (Confident)
✅ "Based on your architecture's Supabase integration..." (Evidence-based)
```

#### 3. Autonomous Execution Phase (Existing, made explicit)
```markdown
## Phase 2: Autonomous Execution

**Trigger**: User approval ("OK", "Go ahead", "Yes")

**Execution**: Fully autonomous, systematic PDCA

### Self-Correction Loop:
```yaml
Implementation:
  - Execute with sub-agents
  - Write comprehensive tests
  - Run validation

Error Detected:
  → Context7: Check official documentation
  → Identify root cause
  → Implement fix
  → Re-test
  → Repeat until passing

Success:
  → Document pattern (docs/patterns/)
  → Update learnings (write_memory)
  → Report completion with evidence
```

### Quality Gates:
- Tests must pass (no exceptions)
- Coverage targets must be met
- Security checks must pass
- Documentation must be updated
```

---

## Expected Outcomes

### Before (Current State)
```yaml
User Input Required: High
  - Authentication method selection
  - Implementation approach decisions
  - Error handling instructions
  - Testing approach decisions

Proposal Quality: Passive
  - "What would you like?" style
  - Just listing options
  - User makes decisions

Execution: Semi-automatic
  - Report errors to user
  - User directs fix approach
```

### After (Improved)
```yaml
User Input Required: Minimal
  - Just "Build authentication"
  - Only approval/rejection of proposals

Proposal Quality: Proactive with confidence
  - Presenting research-backed rationale
  - Clear recommendation
  - Comparison with alternatives

Execution: Fully autonomous
  - Self-correction of errors
  - Automatic official documentation reference
  - Automatic execution until tests pass
  - Automatic learning records
```

### Quantitative Targets
- User input reduction: **80% reduction**
- Proposal quality improvement: **90%+ confidence level**
- Autonomous execution success rate: **95%+**

---

## Implementation Steps

### Step 1: Modify pm.md
- [ ] Add Phase 0: Autonomous Investigation
- [ ] Enhance Phase 1: Confident Proposal
- [ ] Make Phase 2: Autonomous Execution explicit
- [ ] Add concrete examples to Examples section

### Step 2: Create Tests
- [ ] `tests/test_pm_autonomous.py`
- [ ] Tests for autonomous investigation flow
- [ ] Tests for confident proposal format
- [ ] Tests for self-correction loop

### Step 3: Verify Behavior
- [ ] Development install
- [ ] Verify with actual workflow
- [ ] Collect feedback

### Step 4: Record Learnings
- [ ] `docs/patterns/pm-autonomous-workflow.md`
- [ ] Document success patterns

---

## Awaiting User Approval

**Shall we proceed with this approach?**

Once approved, we will immediately begin modifying `superclaude/commands/pm.md`.
