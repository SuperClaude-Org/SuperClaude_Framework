# D-0047: User Review Gate

## Deliverable

User review gate integrated into `design_pipeline` step.

## Implementation

When `config.skip_review` is False:
1. Prompts on stderr: `[REVIEW GATE] Pipeline design produced: <path>`
2. Reads `y`/`n` response via `input()`
3. On `y`/`yes`: continues to SC-004 gate
4. On `n`/any other/EOF: returns FAIL with `USER_REJECTED` classification
5. Sets `review_required=True` and `review_accepted` in step result

## Verification

- `TestDesignPipelineReviewGate::test_review_accept` - verifies y path
- `TestDesignPipelineReviewGate::test_review_reject` - verifies n path with USER_REJECTED
