# D-0007: Smoke Test Evidence — Prompt/Gate Field-Name Alignment

## Test Inputs

- `build_reflect_prompt('output/roadmap.md', 'output/test-strategy.md', 'output/extraction.md')`
- `build_merge_prompt(['output/validate/reflect-opus-architect.md', 'output/validate/reflect-haiku-architect.md'])`

## REFLECT_GATE Alignment

| Gate Field | Present in `build_reflect_prompt` output | Status |
|---|---|---|
| `blocking_issues_count` | Yes | PASS |
| `warnings_count` | Yes | PASS |
| `tasklist_ready` | Yes | PASS |

## ADVERSARIAL_MERGE_GATE Alignment

| Gate Field | Present in `build_merge_prompt` output | Status |
|---|---|---|
| `blocking_issues_count` | Yes | PASS |
| `warnings_count` | Yes | PASS |
| `tasklist_ready` | Yes | PASS |
| `validation_mode` | Yes | PASS |
| `validation_agents` | Yes | PASS |

## Semantic Check Alignment

| Check | Gate | Prompt Instructs It | Status |
|---|---|---|---|
| `frontmatter_values_non_empty` | Both gates | Prompt specifies exact field names with type annotations (integer, boolean, string) | PASS |
| `agreement_table_present` | ADVERSARIAL_MERGE_GATE | Merge prompt explicitly instructs markdown agreement table with `\|` columns | PASS |

## Additional Checks

| Check | Result |
|---|---|
| `blocking_issues_count == 0` condition for `tasklist_ready` | Referenced in reflect prompt |
| REFLECT_GATE `min_lines=20` feasibility | Prompt structure (Findings + Summary + Interleave Ratio sections) will produce >20 lines |
| ADVERSARIAL_MERGE_GATE `min_lines=30` feasibility | Prompt structure (Agreement Table + Consolidated Findings + Summary) will produce >30 lines |
| Interleave ratio formula verbatim | Present in reflect prompt |
| False-positive constraint | Present in reflect prompt |

## Result

**PASS** — Zero field-name mismatches between Phase 1 gate definitions and Phase 2 prompt templates.

## Verification Command

```bash
uv run python -c "
from superclaude.cli.roadmap.validate_prompts import build_reflect_prompt, build_merge_prompt
from superclaude.cli.roadmap.validate_gates import REFLECT_GATE, ADVERSARIAL_MERGE_GATE
p = build_reflect_prompt('r','t','e')
m = build_merge_prompt(['a','b'])
for f in REFLECT_GATE.required_frontmatter_fields: assert f in p, f
for f in ADVERSARIAL_MERGE_GATE.required_frontmatter_fields: assert f in m, f
print('ALL PASS')
"
```

Exit code: 0
