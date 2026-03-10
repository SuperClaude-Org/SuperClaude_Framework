# D-0005 Spec: 10% Stratified Consistency Validation

## Module
`src/superclaude/cli/audit/validation.py`

## Sampling Methodology
- Sample fraction: 10% of total classified files (minimum 1)
- Stratification: proportional allocation per tier, minimum 1 per populated tier
- Seed-based reproducibility via random.Random(seed)

## Consistency Formula
`consistency_rate = consistent_count / sample_size`
