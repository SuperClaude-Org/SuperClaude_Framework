# Refactoring Plan

## Overview
- **Base**: Variant B (Final Root Cause Analysis Report)
- **Incorporated from**: Variant A (Context Document)
- **Changes planned**: 4
- **Changes rejected**: 1
- **Overall risk**: Low

## Planned Changes

### Change #1: Add Protocol Mismatch Section
- **Source**: Variant A, "Important Mismatch Discovered" section (lines 98-120)
- **Target**: After "Impact Analysis" in base, as new H2 "Protocol Drift: Separate Issue"
- **Rationale**: Debate point C-003 — A wins at 95% confidence. This is a real second bug that B completely ignores. The CLI extract prompt requests 3 fields; the source protocol expects 13+. Omitting this from the final report means the team fixes the gate but ships structurally incomplete artifacts.
- **Integration approach**: Insert new section with A's finding, framed as a tracked follow-up separate from the immediate fix
- **Risk**: Low (additive — does not modify existing content)

### Change #2: Add --verbose Investigation Note
- **Source**: Variant A, "Command Invocation Details" (lines 122-132) and "Likely Root-Cause Families" item 3 (lines 144-145)
- **Target**: Append to "Priority 3: Prompt Hardening" section as a caveat
- **Rationale**: Debate point X-002 — B won the debate (70%), but the rebuttal acknowledged this is worth investigating. Adding as a follow-up note is prudent without blocking the fix.
- **Integration approach**: Add "Investigation Note" paragraph after prompt hardening code
- **Risk**: Low (additive caveat)

### Change #3: Add Key Files Reference
- **Source**: Variant A, "Key Files" section (lines 22-44)
- **Target**: After "Root Cause Chain" in base, as new H3 "Key Files"
- **Rationale**: Unique contribution U-001 (Medium value). Developers implementing the fixes need to know which files to modify. B references files inline but lacks a consolidated inventory.
- **Integration approach**: Insert condensed file listing
- **Risk**: Low (additive)

### Change #4: Add Fix Evaluation Constraints
- **Source**: Variant A, "Constraints for Follow-up Investigation" (lines 147-153)
- **Target**: Before "Decision for Human Review" in base
- **Rationale**: Unique contribution U-004 (Medium value). Evaluation criteria (protocol parity, resumability, gate strictness) strengthen the fix validation.
- **Integration approach**: Insert as bullet list under "Evaluation Criteria for Fixes"
- **Risk**: Low (additive)

## Changes NOT Being Made

### Rejected: Replace root cause framing with A's "root cause families"
- **Diff point**: X-001
- **Non-base approach**: A frames 3 coordinate hypotheses as "Likely Root-Cause Families"
- **Rationale**: B's causal chain (Contributing Factor → Enabler → Direct Cause) won the debate at 65% confidence. It is structurally clearer and more actionable. A's coordinate hypotheses lack causal ordering.

## Risk Summary
| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Protocol mismatch | Low | Adds awareness of second bug | Remove section |
| #2 --verbose note | Low | Adds investigation caveat | Remove paragraph |
| #3 Key files | Low | Developer reference | Remove section |
| #4 Evaluation constraints | Low | Strengthens validation | Remove bullets |

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-07
