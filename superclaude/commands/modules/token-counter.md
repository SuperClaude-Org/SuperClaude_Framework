---
name: token-counter
description: Dynamic token usage calculation from system notifications
category: module
---

# Token Counter Module

**Purpose**: Parse and format real-time token usage from system notifications

## Input Source

System provides token notifications after each tool call:
```
<system_warning>Token usage: [used]/[total]; [remaining] remaining</system_warning>
```

**Example**:
```
Token usage: 57425/200000; 142575 remaining
```

## Calculation Logic

```yaml
Parse:
  used: Extract first number (57425)
  total: Extract second number (200000)
  remaining: Extract third number (142575)

Compute:
  percentage: (used / total) × 100
  # Example: (57425 / 200000) × 100 = 28.7125%

Format:
  percentage: Round to integer (28.7% → 28%)
  used: Round to K (57425 → 57K)
  total: Round to K (200000 → 200K)
  remaining: Round to K (142575 → 142K)

Output:
  "[%] ([used]K/[total]K) · [remaining]K avail"
  # Example: "28% (57K/200K) · 142K avail"
```

## Formatting Rules

### Number Rounding (K format)
```yaml
Rules:
  < 1,000: Show as-is (e.g., 850 → 850)
  ≥ 1,000: Divide by 1000, round to integer (e.g., 57425 → 57K)

Examples:
  500 → 500
  1500 → 1K (not 2K)
  57425 → 57K
  142575 → 142K
  200000 → 200K
```

### Percentage Rounding
```yaml
Rules:
  Always round to nearest integer
  No decimal places

Examples:
  28.1% → 28%
  28.7% → 28%
  28.9% → 29%
  30.0% → 30%
```

## Implementation Pattern

```yaml
Step 1 - Wait for System Notification:
  Execute ANY tool call (Bash, Read, etc.)
  System automatically sends token notification

Step 2 - Extract Values:
  Parse notification text using regex or string split
  Extract: used, total, remaining

Step 3 - Calculate:
  percentage = (used / total) × 100
  Round percentage to integer

Step 4 - Format:
  Convert numbers to K format
  Construct output string

Step 5 - Display:
  🧠 [percentage]% ([used]K/[total]K) · [remaining]K avail
```

## Usage in PM Command

```yaml
Session Start Protocol (Step 3):
  1. Execute git status (triggers system notification)
  2. Wait for: <system_warning>Token usage: ...</system_warning>
  3. Apply token-counter module logic
  4. Format output: 🧠 [calculated values]
  5. Display to user
```

## Anti-Patterns (FORBIDDEN)

```yaml
❌ Static Values:
   🧠 30% (60K/200K) · 140K avail  # WRONG - hardcoded

❌ Guessing:
   🧠 ~25% (estimated)  # WRONG - no evidence

❌ Placeholder:
   🧠 [calculating...]  # WRONG - incomplete

✅ Dynamic Calculation:
   🧠 28% (57K/200K) · 142K avail  # CORRECT - real data
```

## Validation

```yaml
Self-Check Questions:
  ❓ Did I parse the actual system notification?
  ❓ Are the numbers from THIS session, not a template?
  ❓ Does the math check out? (used + remaining = total)
  ❓ Are percentages rounded correctly?
  ❓ Are K values formatted correctly?

Validation Formula:
  used + remaining should equal total
  Example: 57425 + 142575 = 200000 ✅
```

## Edge Cases

```yaml
No System Notification Yet:
  Action: Execute a tool call first (e.g., git status)
  Then: Parse the notification that appears

Multiple Notifications:
  Action: Use the MOST RECENT notification
  Reason: Token usage increases over time

Parse Failure:
  Fallback: "🧠 [calculating...] (execute a tool first)"
  Then: Retry after next tool call
```

## Integration Points

**Used by**:
- `commands/pm.md` - Session start protocol
- `agents/pm-agent.md` - Status reporting
- Any command requiring token awareness

**Dependencies**:
- System-provided notifications (automatic)
- No external tools required
