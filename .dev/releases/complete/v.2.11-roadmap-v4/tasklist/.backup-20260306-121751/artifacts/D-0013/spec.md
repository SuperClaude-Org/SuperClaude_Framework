# D-0013: State Variable Detector Specification

## Module
`src/superclaude/cli/pipeline/state_detector.py`

## Detection Patterns

### 1. self._field (confidence: 0.95)
Regex: `self\.(_\w+)` — captures field name after `self.`

### 2. Explicit introductions (confidence: 0.85-0.9)
- `add [a|an] [new] counter/offset/cursor/flag [name]`
- `add X counter/offset/cursor/flag` (reverse order)
- `introduce [a|an] [new] counter/offset/cursor/flag [for ...]`
- `introduce [a|an] [new] <variable_name>` (generic)

### 3. Type replacement (confidence: 0.85)
Regex: `replace (\w+) with (\w[\w\s]*)` — checks if replacement target is state-tracking type

## Synonym Dictionary (Extensible)
`STATE_TYPE_SYNONYMS`: int, integer, offset, counter, cursor, flag, boolean, bool, enum, state, index, tracker, accumulator, pointer, sentinel, marker

## Confidence Flagging
- Detections with confidence < 0.7 are flagged for human review via `needs_review` property
- self._field: 0.95 (high)
- Explicit type keywords: 0.9 (high)
- Reverse patterns: 0.85 (medium-high)
- Generic introduce: 0.85 (medium-high)
- Replacement: 0.85 (medium-high)

## Documentation Suppression
Descriptions dominated by doc verbs (document, describe, explain, list, outline, summarize) are excluded unless they also contain strong state signals.
