# D-0035: Budget Caveats Specification

**Task**: T04.09 — Budget Caveat Language
**Status**: Complete

## Purpose

Define standard caveat language for token budget estimates, acknowledging inherent variance.

## Caveat Language

Every budget-related output must include:

```
Budget Caveat: Token estimates are approximations based on prompt and completion
token counting. Actual consumption may vary 20-50% from estimates depending on
file complexity, model behavior, and response length variability. Budget
thresholds (warn/degrade/halt) account for this variance by using conservative
activation points.
```

## Estimation Methodology Statement

```
Estimation Method: Per-batch token consumption is estimated using:
  - Input tokens: measured from prompt construction
  - Output tokens: estimated from historical averages per classification type
  - Overhead: fixed 5% buffer for system prompts and formatting
Estimates are updated after each batch with actual consumption data.
```

## Variance Range

- **Expected variance**: 20-50% from estimates.
- **Low-complexity files**: Variance toward 20% (predictable output length).
- **High-complexity files**: Variance toward 50% (variable analysis depth).

## Report Integration

- Caveat section appears in every report that includes budget data.
- Placed immediately after the budget summary section.
- Not suppressible via report depth flags (always present when budget is shown).

## Constraints

- Caveat language must not be modified by degradation levels.
- Variance range must reflect actual observed variance, updated if data warrants.
