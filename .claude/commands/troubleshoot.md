**Purpose**: Professional debugging and issue resolution

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Systematically debug and resolve issues in $ARGUMENTS using root cause analysis and evidence-based solutions.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/troubleshoot "app crashes on startup"` - Debug crash
- `/troubleshoot --performance "slow API"` - Performance issues
- `/troubleshoot --interactive "login fails"` - Guided debugging

## Command-Specific Flags
--performance: "Focus on performance bottlenecks"
--memory: "Memory leak detection and analysis"
--network: "Network-related debugging"
--interactive: "Step-by-step guided troubleshooting"
--trace: "Enable detailed execution tracing"
--bisect: "Git bisect to find breaking commit"

## Troubleshooting Approach

**1. Reproduce:** Isolate minimal reproduction | Document steps | Verify consistency | Capture full context

**2. Gather Evidence:** Error messages & stack traces | Logs & metrics | System state | Recent changes | Environment differences

**3. Form Hypotheses:** Most likely causes | Alternative explanations | Test predictions | Rule out possibilities

**4. Test & Verify:** Targeted experiments | Change one variable | Document results | Confirm root cause

**5. Fix & Prevent:** Implement solution | Add tests | Document fix | Prevent recurrence

## Common Issue Categories

**Performance:** Slow queries | Memory leaks | CPU bottlenecks | Network latency | Inefficient algorithms

**Crashes/Errors:** Null references | Type mismatches | Race conditions | Memory corruption | Stack overflow

**Integration:** API failures | Authentication issues | Version conflicts | Configuration problems | Network timeouts

**Data Issues:** Corruption | Inconsistency | Migration failures | Encoding problems | Concurrency conflicts

@include shared/quality-patterns.yml#Root_Cause_Analysis

## Deliverables

**Root Cause Report:** Issue description | Evidence collected | Analysis process | Root cause identified | Fix implemented

**Fix Documentation:** What was broken | Why it broke | How it was fixed | Prevention measures | Test cases added

**Knowledge Base:** Problem→Solution mapping | Troubleshooting guides | Common patterns | Prevention checklist

@include shared/universal-constants.yml#Standard_Messages_Templates