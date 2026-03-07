# D-0013: Updated Advocate Prompt Template with ACCEPT/REJECT/QUALIFY

## Overview

Updated advocate prompt template requiring ACCEPT/REJECT/QUALIFY response for each [SHARED-ASSUMPTION] point, with omission detection and flagging.

## Changes to Advocate Prompt

1. **Rule 6 added**: "For each [SHARED-ASSUMPTION] point (A-NNN), respond with ACCEPT/REJECT/QUALIFY"
2. **shared_assumption_handling section**: Mandatory response template with ACCEPT/REJECT/QUALIFY instructions
3. **omission_detection section**: Post-response scan for missing A-NNN responses with transcript flagging

## Response Options

| Response | Meaning |
|----------|---------|
| ACCEPT | Assumption is valid and should remain implicit |
| REJECT | Assumption is incorrect; counter-evidence required |
| QUALIFY | Assumption is partially valid; conditions stated |

## Omission Detection

1. Extract all A-NNN IDs from prompt
2. Scan advocate response for each A-NNN ID with ACCEPT/REJECT/QUALIFY
3. Missing responses flagged: `[OMISSION] Advocate {variant_name} did not address {A-NNN}`

## AC-AD2-4 Test

- Scenario: Advocate omits response for A-002
- Expected: `[OMISSION] Advocate Variant 1 did not address A-002` flagged in transcript

## Deliverable Status

- **Task**: T02.09 (second occurrence)
- **Roadmap Item**: R-013
- **Status**: COMPLETE
- **Tier**: STANDARD
