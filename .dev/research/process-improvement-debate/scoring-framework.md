# Proposal Scoring Framework

## Dimensions

Each proposal is scored on 4 dimensions, each rated 1-10:

### 1. Implementation Complexity (LOWER is better → inverted for final score)
- **1-3 (Low)**: Prompt/template change only. No structural workflow changes. <1 day effort.
- **4-6 (Medium)**: New review phase or checklist. Moderate protocol restructuring. 1-3 days.
- **7-10 (High)**: New agent roles, major workflow restructuring, cross-command changes. >3 days.
- **Scoring**: Final score = 11 - raw_score (inverted so simpler = higher score)

### 2. Cost/Time Overhead per Invocation (LOWER is better → inverted)
- **1-3 (Low)**: <10% additional tokens/time per command invocation. Negligible UX impact.
- **4-6 (Medium)**: 10-30% additional overhead. Noticeable but acceptable.
- **7-10 (High)**: >30% additional overhead. Significant UX impact, may need opt-in flag.
- **Scoring**: Final score = 11 - raw_score (inverted so cheaper = higher score)

### 3. Likelihood of Impact (HIGHER is better → direct)
- **1-3 (Low)**: Would catch <20% of state-machine edge case classes. Narrow applicability.
- **4-6 (Medium)**: Would catch 20-60% of edge case classes. Moderate breadth.
- **7-10 (High)**: Would catch >60% of edge case classes. Broad applicability across domains.
- **Scoring**: Direct (higher = better)

### 4. Generalizability (HIGHER is better → direct)
- **1-3 (Low)**: Only applies to one command or one type of specification.
- **4-6 (Medium)**: Applies to 2-3 commands or moderate range of specification types.
- **7-10 (High)**: Applies across all review/debate/roadmap commands. Universal principle.
- **Scoring**: Direct (higher = better)

## Composite Score Formula

```
composite = (
    (11 - complexity) * 0.20 +    # 20% weight: prefer simpler changes
    (11 - overhead) * 0.15 +      # 15% weight: prefer cheaper runtime cost
    impact * 0.40 +                # 40% weight: primary criterion
    generalizability * 0.25        # 25% weight: cross-command value
) / 10 * 100  # normalize to 0-100
```

## Tier Classification

| Score Range | Tier | Recommendation |
|-------------|------|----------------|
| 80-100 | S-Tier | Implement immediately |
| 65-79 | A-Tier | Implement in next release cycle |
| 50-64 | B-Tier | Consider with modifications |
| 35-49 | C-Tier | Defer or redesign |
| 0-34 | D-Tier | Do not implement |

## Debate Evaluation Criteria

When debating proposals, agents should:
1. Challenge the claimed impact score with concrete counter-examples
2. Probe whether the overhead estimate accounts for worst-case scenarios
3. Test generalizability by applying the proposal to 2-3 different specification domains
4. Verify the implementation sketch is realistic and doesn't hand-wave complexity
5. Consider interaction effects between proposals from different commands
