---
name: pm-formatter
description: PM Agent status output formatting with actionable structure
category: module
---

# PM Formatter Module

**Purpose**: Format PM Agent status output with maximum clarity and actionability

## Output Structure

```yaml
Line 1: Branch indicator
  Format: 📍 [branch-name]
  Source: git-status module

Line 2: Workspace status
  Format: [symbol] [description]
  Source: git-status module

Line 3: Token usage
  Format: 🧠 [%] ([used]K/[total]K) · [remaining]K avail
  Source: token-counter module

Line 4: Ready actions
  Format: 🎯 Ready: [comma-separated-actions]
  Source: Static list based on context
```

## Complete Output Template

```
📍 [branch-name]
[status-symbol] [status-description]
🧠 [%] ([used]K/[total]K) · [remaining]K avail
🎯 Ready: [comma-separated-actions]
```

## Symbol System

```yaml
Branch:
  📍 - Current branch indicator

Status:
  ✅ - Clean workspace (green light)
  ⚠️ - Uncommitted changes (caution)
  🔴 - Conflicts detected (critical)

Resources:
  🧠 - Token usage/cognitive load

Actions:
  🎯 - Ready actions/next steps
```

## Ready Actions Selection

```yaml
Always Available:
  - Implementation
  - Research
  - Analysis
  - Planning
  - Testing

Conditional:
  Documentation:
    Condition: Documentation files present

  Debugging:
    Condition: Errors or failures detected

  Refactoring:
    Condition: Code quality improvements needed

  Review:
    Condition: Changes ready for review
```

## Formatting Rules

```yaml
Conciseness:
  - One line per component
  - No explanations
  - No prose
  - Symbol-first communication

Actionability:
  - Always end with Ready actions
  - User knows what they can request
  - No "How can I help?" questions

Clarity:
  - Symbols convey meaning instantly
  - Numbers are formatted consistently
  - Status is unambiguous
```

## Examples

### Example 1: Clean Workspace
```
📍 main
✅ Clean workspace
🧠 28% (57K/200K) · 142K avail
🎯 Ready: Implementation, Research, Analysis, Planning, Testing
```

### Example 2: Uncommitted Changes
```
📍 refactor/docs-core-split
⚠️ Uncommitted changes (2M, 3 untracked)
🧠 30% (60K/200K) · 140K avail
🎯 Ready: Implementation, Research, Analysis
```

### Example 3: Conflicts
```
📍 feature/new-auth
🔴 Conflicts detected (1 file)
🧠 15% (30K/200K) · 170K avail
🎯 Ready: Debugging, Analysis
```

### Example 4: High Token Usage
```
📍 develop
✅ Clean workspace
🧠 87% (174K/200K) · 26K avail
🎯 Ready: Testing, Documentation
```

## Integration Logic

```yaml
Step 1 - Gather Components:
  branch = git-status module → branch name
  status = git-status module → symbol + description
  tokens = token-counter module → formatted string
  actions = ready-actions logic → comma-separated list

Step 2 - Assemble Output:
  line1 = "📍 " + branch
  line2 = status
  line3 = "🧠 " + tokens
  line4 = "🎯 Ready: " + actions

Step 3 - Display:
  Print all 4 lines
  No additional commentary
  No "How can I help?"
```

## Context-Aware Action Selection

```yaml
Token Budget Awareness:
  IF tokens < 25%:
    → All actions available
  IF tokens 25-75%:
    → Standard actions (Implementation, Research, Analysis)
  IF tokens > 75%:
    → Lightweight actions only (Testing, Documentation)

Workspace State Awareness:
  IF conflicts detected:
    → Debugging, Analysis only
  IF uncommitted changes:
    → Reduce action list (exclude Planning)
  IF clean workspace:
    → All actions available
```

## Anti-Patterns (FORBIDDEN)

```yaml
❌ Verbose Explanations:
   "You are on the refactor/docs-core-split branch which has..."
   # WRONG - too much prose

❌ Asking Questions:
   "What would you like to work on?"
   # WRONG - user knows from Ready list

❌ Status Elaboration:
   "⚠️ You have uncommitted changes which means you should..."
   # WRONG - symbols are self-explanatory

❌ Token Warnings:
   "🧠 87% - Be careful, you're running low on tokens!"
   # WRONG - user can see the percentage

✅ Clean Format:
   📍 branch
   ✅ status
   🧠 tokens
   🎯 Ready: actions
   # CORRECT - concise, actionable
```

## Validation

```yaml
Self-Check Questions:
  ❓ Is the output exactly 4 lines?
  ❓ Are all symbols present and correct?
  ❓ Are numbers formatted consistently (K format)?
  ❓ Is the Ready list appropriate for context?
  ❓ Did I avoid explanations and questions?

Format Test:
  Count lines: Should be exactly 4
  Check symbols: 📍, [status], 🧠, 🎯
  Verify: No extra text beyond the template
```

## Adaptive Formatting

```yaml
Minimal Mode (when token budget is tight):
  📍 [branch] | [status] | 🧠 [%] | 🎯 [actions]
  # Single-line format, same information

Standard Mode (normal operation):
  📍 [branch]
  [status-symbol] [status-description]
  🧠 [%] ([used]K/[total]K) · [remaining]K avail
  🎯 Ready: [comma-separated-actions]
  # Four-line format, maximum clarity

Trigger for Minimal Mode:
  IF tokens > 85%:
    → Use single-line format
  ELSE:
    → Use standard four-line format
```

## Integration Points

**Used by**:
- `commands/pm.md` - Session start output
- `agents/pm-agent.md` - Status reporting
- Any command requiring PM status display

**Dependencies**:
- `modules/token-counter.md` - Token calculation
- `modules/git-status.md` - Git state detection
- System context - Token notifications, git repository
