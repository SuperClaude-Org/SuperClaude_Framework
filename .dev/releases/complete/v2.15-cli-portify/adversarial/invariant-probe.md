# Invariant Probe Results

## Round 2.5 -- Fault-Finder Analysis

| ID | Category | Assumption | Status | Severity | Evidence |
|----|----------|------------|--------|----------|----------|
| INV-001 | state_variables | Subprocess receives only prompt text as input (no hidden state from environment, conversation history, or MCP servers) | ADDRESSED | LOW | Both variants confirm `stdin=subprocess.DEVNULL` at `process.py:109`; fresh subprocess means no conversation state. Build_env() behavior analyzed by both. |
| INV-002 | guard_conditions | Preamble sanitizer (S5) distinguishes frontmatter `---` from markdown horizontal rule `---` | UNADDRESSED | MEDIUM | Both variants' sanitizer implementations search for first `---` without context. A legitimate `---` horizontal rule early in non-frontmatter content could cause the sanitizer to strip valid content. |
| INV-003 | interaction_effects | Sanitizer (S5) and resilient parser (S3) applied together produce consistent results | UNADDRESSED | LOW | S5 strips preamble before first `---`; S3 scans first 20 lines for `---`. If both are active, the sanitizer runs first (pre-gate) and the parser runs second (during gate). Defense-in-depth layering means first layer handles most cases, reducing interaction risk. |
| INV-004 | count_divergence | Self-validation check count: A says 30, B says 29 | UNADDRESSED | LOW | X-001 contradiction was not resolved by either advocate. One check difference — likely counting methodology difference (per-file vs cross-file granularity). Does not affect code but affects specification accuracy. |
| INV-005 | collection_boundaries | Extract step failure generalizes to all 8 pipeline steps | ADDRESSED | N/A | Both advocates QUALIFYed A-001: infrastructure-layer root causes (RC4, RC5, RC7, RC8) generalize because they affect shared code. Prompt-layer root causes (RC1, RC2, RC3) do NOT generalize because each step has different prompts and frontmatter fields. |
| INV-006 | interaction_effects | S4 (feedback injection) and S2 (prompt reorder) in same PR: retry feedback appended after format instructions may push format instructions further from generation point | UNADDRESSED | MEDIUM | S2 moves format instructions to end of prompt. S4 appends failure feedback after the prompt. Combined effect: `preamble + embedded + format_instructions + feedback_block`. The feedback block after format instructions partially negates S2's attention-proximity benefit. |
| INV-007 | interaction_effects | S6 (subprocess cwd change) and output_file path interaction: relative vs absolute path handling | UNADDRESSED | MEDIUM | Both variants' S6 implementations add `cwd=str(self.output_file.parent)` to Popen(). Neither discusses whether `self.output_file` is absolute or relative. If relative, the subprocess may write to a different location than expected. Needs verification against `ClaudeProcess.__init__()` path handling. |

## Summary

- **Total findings**: 7
- **ADDRESSED**: 2
- **UNADDRESSED**: 5
  - HIGH: 0
  - MEDIUM: 3 (INV-002, INV-006, INV-007)
  - LOW: 2 (INV-003, INV-004)

**Invariant probe gate**: PASS -- no HIGH-severity UNADDRESSED items. Convergence not blocked.

**Warnings**: 3 MEDIUM-severity items (INV-002, INV-006, INV-007) should be acknowledged in the merged output's remediation plan as implementation considerations.
