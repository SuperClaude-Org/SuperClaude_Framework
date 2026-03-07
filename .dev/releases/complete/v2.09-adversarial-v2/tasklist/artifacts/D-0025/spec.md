# D-0025: Blind Evaluation Specification

## Overview

`--blind` strips model-name metadata from artifacts before compare phases receive variants, ensuring unbiased evaluation (SC-003).

## Stripping Rules

- Model name patterns: opus, haiku, sonnet, claude, gpt, gemini (case-insensitive)
- File content: prose references, attribution comments, metadata headers
- File names: variant-opus-architect.md -> variant-A.md

## Integration Point

Applied during artifact routing, BEFORE passing artifacts to compare phases. Original artifacts preserved.

## SC-003 Acceptance Test

Merged output after --blind pipeline contains zero model-name references.

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Blind Evaluation subsection.

## Deliverable Status

- **Task**: T03.09
- **Roadmap Item**: R-025
- **Status**: COMPLETE
- **Tier**: STRICT
