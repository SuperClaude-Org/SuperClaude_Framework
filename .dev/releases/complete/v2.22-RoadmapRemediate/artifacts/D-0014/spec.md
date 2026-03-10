# D-0014: Remediation Prompt Builder

## Module
`src/superclaude/cli/roadmap/remediate_prompts.py`

## Function
`build_remediation_prompt(target_file: str, findings: list[Finding]) -> str`

## Template Structure (spec section 2.3.4)
1. **Header**: "You are a remediation specialist..."
2. **Target File**: Single file path in backticks
3. **Findings to Fix**: Per-finding blocks with 6 detail fields:
   - ID, Severity, Description, Location, Evidence, Fix Guidance
4. **Constraints**: Edit-only-target-file, apply-only-listed-fixes, preserve YAML/headings

## NFR Compliance
- NFR-004: Pure function (no I/O, no subprocess, no side effects)
- All inputs are string/list parameters, output is a string
