# D-0047 Spec: Non-Determinism Sources and Known Limitations

## Task Reference
- Task: T05.08
- Roadmap Item: R-047
- AC: AC6 (quality extension)

## Limitations Section Format

The limitations section is placed in the final report between validation results and appendix.

## Identified Non-Determinism Sources

### 1. LLM Classification Variance

**Source**: When the audit delegates classification decisions to an LLM (e.g., for ambiguous INVESTIGATE candidates), the output can vary between runs even with identical input.

**Impact**: Classification of borderline files may differ between runs by 1-2 action categories. This primarily affects Tier-2 and Tier-3 files where confidence is lower.

**Mitigation**:
- Evidence-gated decisions: DELETE requires grep evidence with 0 references
- Confidence thresholds: findings below threshold are flagged as INVESTIGATE rather than acted upon
- Anti-lazy guard: detects suspiciously uniform batches (>90% same classification) that may indicate lazy LLM responses
- Spot-check validation: 10% stratified sample re-classification measures self-consistency

### 2. Git History Dependency

**Source**: Staleness checks, file age computation, and churn metrics depend on git history depth. Shallow clones or repos with squashed history may produce different profiling results.

**Impact**: Files may be incorrectly assessed as "old" or "low churn" if git history is truncated. This affects profiling accuracy for risk tier assignment.

**Mitigation**:
- Staleness checks use `git log --follow` where available
- Missing git dates are treated as "unknown" rather than defaulting
- Profile generator documents when git data is unavailable
- Budget caveat notes explicitly state that results depend on available git history

### 3. Dynamic Import Detection Limits

**Source**: Static analysis cannot resolve dynamic imports (`importlib.import_module`, `__import__`, `getattr` on modules). Files that are only imported dynamically may be falsely classified as dead code.

**Impact**: False positive DELETE recommendations for files consumed exclusively through dynamic import patterns. This is a fundamental limitation of static analysis.

**Mitigation**:
- Dynamic import pattern scanner detects `importlib`, `__import__`, and `getattr` patterns
- Files with detected dynamic import consumption receive KEEP:monitor classification (never DELETE)
- Exclusion list for known framework hooks (pytest fixtures, Django migrations, etc.)
- Documentation warns that dynamic import consumers should be verified manually

### 4. Tier-C Inference Confidence

**Source**: Tier-C dependency edges (co-occurrence inference) are heuristic — they detect files that frequently appear together in git commits but may not have actual import relationships.

**Impact**: Low-confidence dependency edges may create false relationships, causing some dead code to be missed (false negatives) or non-dead code to appear referenced (reducing detection rate).

**Mitigation**:
- Tier-C edges are weighted at 40% vs Tier-A's 100%
- Dead code detection primarily relies on Tier-A (static imports) and Tier-B (grep references)
- Tier-C evidence is labeled in reports to distinguish from stronger evidence types
