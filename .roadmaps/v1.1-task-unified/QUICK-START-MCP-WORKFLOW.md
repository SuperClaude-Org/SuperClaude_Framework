# Quick Start: MCP-Optimized Workflow Execution

**For**: Claude Code users with Augment MCP  
**Purpose**: Execute complex workflows with maximum efficiency  
**Time**: 5 minutes to understand, then execute

---

## 🚀 One-Command Execution

Copy this into Claude Code:

```bash
/sc:spawn Execute docs/generated/releases/current/Infra0.2/MCP-OPTIMIZED-TEST-REMEDIATION-EXECUTOR.md
```

That's it! The workflow will:
- ✅ Use Augment MCP for semantic code understanding
- ✅ Spawn specialized sub-agents for each task
- ✅ Execute independent tasks in parallel (40-60% time savings)
- ✅ Verify each task with quality-engineer agents
- ✅ Store patterns in persistent memory
- ✅ Track progress and generate reports

---

## 📋 Pre-Flight Checklist (2 minutes)

Before running the workflow:

```bash
# 1. Activate project (ensures MCP is ready)
mcp__serena__activate_project project="."

# 2. Verify language servers are running
# Check that .serena/project.yml has both typescript and python

# 3. Ensure clean working directory
git status

# 4. Activate backend virtual environment
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

---

## 🎯 How It Works

### MCP Optimization Strategy

The workflow uses Augment MCP in 3 key ways:

#### 1. **Semantic Code Retrieval** (Before Every Edit)
```
Agent uses: codebase-retrieval
Query: "Find backend/app/core/security.py and all functions that call create_access_token"
Result: MCP loads relevant code into context
Benefit: Agent knows exactly what to change and why
```

#### 2. **Downstream Impact Analysis** (After Every Edit)
```
Agent uses: codebase-retrieval
Query: "Find all files that import create_access_token"
Result: MCP finds all affected code
Benefit: No breaking changes, all impacts addressed
```

#### 3. **Persistent Memory** (Cross-Task Learning)
```
Agent creates: .serena/memories/async-client-migration-pattern.md
Content: Documented pattern for async test migration
Benefit: Later tasks reference this pattern for consistency
```

### Sub-Agent Delegation

The workflow spawns specialized sub-agents:

| Sub-Agent | When Used | Example Task |
|-----------|-----------|--------------|
| `python-expert` | Python code fixes | Fix UUID serialization in JWT |
| `backend-architect` | Architecture decisions | Design AsyncClient pattern |
| `quality-engineer` | Verification & testing | Verify all tests pass |
| `refactoring-expert` | Code refactoring | Fix mock patterns |
| `root-cause-analyst` | Problem investigation | Analyze workflow results |

### Parallel Execution

Independent tasks run simultaneously:

```
Phase 1: Quick Wins
├─ Agent 1: Fix UUID serialization    ┐
├─ Agent 2: Fix status codes          ├─ Run in parallel (3x faster)
└─ Agent 3: Fix project model         ┘

Then verify in parallel:
├─ Verify Agent 1: Check UUID fix     ┐
├─ Verify Agent 2: Check status fix   ├─ Run in parallel
└─ Verify Agent 3: Check model fix    ┘
```

**Result**: Phase 1 completes in ~30 minutes instead of 1-2 hours

---

## 📊 What to Expect

### Phase-by-Phase Timeline

| Phase | Tasks | Strategy | Time (Optimized) | Time (Sequential) |
|-------|-------|----------|------------------|-------------------|
| Phase 0 | Setup | MCP initialization | 5 min | 5 min |
| Phase 1 | Quick Wins | 3 parallel + 3 verify | 30 min | 1-2 hours |
| Phase 2 | Test Infra | Sequential + verify | 2-3 hours | 4-6 hours |
| Phase 3 | Mock Patterns | Mixed parallel | 2 hours | 3-4 hours |
| Phase 4 | Validation | 6 parallel | 1 hour | 2-3 hours |
| Phase 5 | Re-Scan | Critical + parallel | 4-6 hours | 6-10 hours |
| **TOTAL** | **34 tasks** | **MCP-optimized** | **11-17 hours** | **19-29 hours** |

### Progress Tracking

The workflow creates memories as it progresses:

```
.serena/memories/
├── test-remediation-workflow-2026-01-23.md       # Main execution log
├── async-client-migration-pattern.md             # Reusable pattern
├── mock-patterns-best-practices.md               # Best practices
└── test-remediation-complete-analysis.md         # Final report
```

You can check progress anytime:
```bash
cat .serena/memories/test-remediation-workflow-2026-01-23.md
```

---

## 🔍 Monitoring Execution

### Watch for MCP Usage

Good signs the workflow is using MCP correctly:

```
✅ "Using codebase-retrieval to find backend/app/core/security.py"
✅ "Found 3 files that import create_access_token"
✅ "Storing pattern in .serena/memories/async-client-migration-pattern.md"
✅ "Spawning sub-agent-python-expert for Task 1.1"
✅ "Verification agent reports: PASS"
```

Bad signs (workflow not optimized):

```
❌ "Editing file without loading context"
❌ "Skipping downstream impact analysis"
❌ "Running tasks sequentially that could be parallel"
❌ "Not using codebase-retrieval before edits"
```

### Check Sub-Agent Activity

You should see multiple agents working:

```
Active Sub-Agents:
- uuid-fix-task-1-1 (python-expert) - IN PROGRESS
- status-code-fix-task-1-2 (python-expert) - IN PROGRESS  
- project-model-fix-task-1-3 (python-expert) - IN PROGRESS
```

Then verification:

```
Active Sub-Agents:
- verify-uuid-fix (quality-engineer) - IN PROGRESS
- verify-status-code-fix (quality-engineer) - IN PROGRESS
- verify-project-model-fix (quality-engineer) - IN PROGRESS
```

---

## 🎓 Learning from the Workflow

### Patterns You Can Reuse

After execution, you'll have documented patterns for:

1. **Async Test Migration**: How to convert sync tests to async
2. **Mock Patterns**: Best practices for mocking async code
3. **Downstream Impact Analysis**: How to find all affected code
4. **Parallel Execution**: Which tasks can run simultaneously
5. **Verification Strategy**: How to verify changes are correct

### Apply to Future Workflows

Use the same MCP optimization strategy for any complex task:

```bash
# Template for MCP-optimized workflow:

1. Pre-load context with codebase-retrieval
2. Identify independent tasks (can run in parallel)
3. Spawn specialized sub-agents for each task
4. Each agent uses codebase-retrieval before editing
5. Each agent finds downstream impacts after editing
6. Spawn verification agents in parallel
7. Store patterns in memories for future use
8. Generate final analysis report
```

---

## 🚨 Troubleshooting

### Workflow Doesn't Start

```bash
# Check MCP is activated
mcp__serena__activate_project project="."

# Verify .serena/project.yml exists
cat .serena/project.yml

# Check language servers are configured
# Should see: languages: [typescript, python]
```

### Sub-Agents Not Spawning

```bash
# Verify you're using Claude Code (not regular Claude)
# Sub-agents only work in Claude Code environment

# Check the spawn command syntax:
/sc:spawn Execute <path-to-workflow.md>
```

### Tests Still Failing

```bash
# The workflow includes troubleshooting steps
# Check the "🚨 Troubleshooting" section in the executor

# Spawn a root-cause-analyst to investigate:
/sc:spawn "Spawn sub-agent-root-cause-analyst to investigate why tests are still failing after workflow execution"
```

---

## ✅ Success Indicators

You'll know the workflow succeeded when:

- [ ] All 34 tasks marked complete in memory
- [ ] `pytest backend/tests/ -v` shows 0 failures
- [ ] Memories created in `.serena/memories/`
- [ ] Final analysis report generated
- [ ] Time taken: 11-17 hours (vs 19-29h sequential)

---

## 📚 Next Steps

After workflow completes:

1. **Review memories**: Learn patterns for future use
2. **Run full test suite**: Confirm everything works
3. **Commit changes**: Use semantic commit messages
4. **Update documentation**: Document any new patterns
5. **Share learnings**: Help team understand MCP optimization

---

**Pro Tip**: This MCP-optimized approach works for ANY complex workflow, not just test remediation. The key is:
- Use codebase-retrieval extensively
- Spawn specialized sub-agents
- Execute independent tasks in parallel
- Store patterns in memories
- Verify everything

**Time Investment**: 5 minutes to learn → 40-60% time savings on execution 🚀

