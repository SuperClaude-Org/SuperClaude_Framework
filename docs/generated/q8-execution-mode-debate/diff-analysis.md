# Diff Analysis: Automatic vs Manual vs Hybrid Execution Mode Annotation

## Variants Under Comparison

| ID | Variant | Core Mechanism |
|----|---------|---------------|
| A | **Auto** | Generator heuristics detect and annotate `execution_mode: python` |
| B | **Manual** | Roadmap/spec author explicitly declares execution mode |
| C | **Hybrid** | Generator auto-detects, marks provisional, user confirms |

---

## Structural Differences

### 1. Where the Decision Lives

| Aspect | Auto (A) | Manual (B) | Hybrid (C) |
|--------|----------|------------|------------|
| Decision point | Tasklist generator runtime | Roadmap authoring time | Both: generator proposes, user ratifies |
| Decision owner | Algorithm | Human | Shared (algorithm + human) |
| Persistence | Generated tasklist only | Source roadmap + generated tasklist | Generated tasklist with provenance marker |
| Reversibility | Re-run generator | Edit roadmap | Re-run with `--dry-run`, toggle annotations |

### 2. Heuristic Complexity

| Aspect | Auto (A) | Manual (B) | Hybrid (C) |
|--------|----------|------------|------------|
| Heuristic code required | Full detection engine | None (passthrough only) | Same as Auto + UI/dry-run presentation |
| Maintenance burden | High (heuristics evolve) | Zero (no logic) | High (same heuristics + confirmation UI) |
| False positive handling | Silent misclassification | N/A | Explicit review catches errors |
| False negative handling | Missed annotation | Human remembers or forgets | Same as Auto (detection misses are invisible) |

### 3. Workflow Integration

| Aspect | Auto (A) | Manual (B) | Hybrid (C) |
|--------|----------|------------|------------|
| Roadmap format changes | None | New metadata field required | None (annotation is output-side) |
| `--dry-run` behavior | Shows auto-detected modes | Shows declared modes | Shows provisional annotations for review |
| Sprint executor impact | Reads `execution_mode` from tasklist | Same | Same, but may see `(auto-detected)` marker |
| Pipeline steps affected | Tasklist generator only | Roadmap authoring + generator | Tasklist generator + dry-run review step |

---

## Content Differences

### Accuracy Model

- **Auto**: Relies on heuristic signals (tier=EXEMPT, backtick commands, keywords). Accuracy bounded by heuristic coverage. Novel phase patterns may evade detection.
- **Manual**: 100% accuracy when author is diligent; 0% when author forgets. Binary failure mode.
- **Hybrid**: Same detection accuracy as Auto, but false positives are caught at review. False negatives remain invisible unless reviewer proactively adds annotations.

### Safety Model

- **Auto**: Risk of annotating a phase as `python` when it requires Claude judgment (e.g., an EXEMPT phase that says "review output and decide next steps"). No human checkpoint before execution.
- **Manual**: No automated risk -- human explicitly opts in. Risk is only in human error (declaring python for a judgment-requiring phase).
- **Hybrid**: Auto-detection risk is mitigated by review checkpoint. But reviewer fatigue could rubber-stamp incorrect annotations.

### User Control Model

- **Auto**: User has no pre-execution visibility unless they inspect generated tasklist. Override requires post-generation editing.
- **Manual**: Full control. User declares intent at authoring time.
- **Hybrid**: User reviews proposals during `--dry-run`. Can accept, reject, or add annotations. Best of both worlds if the review step is actually used.

---

## Contradictions Between Variants

1. **Auto vs Manual on "who knows best"**: Auto assumes the generator can reliably infer execution mode from content. Manual assumes only the human author understands the intent behind a phase. These are fundamentally different epistemic claims.

2. **Hybrid's false negative blind spot**: Hybrid claims to catch Auto's errors through review, but only catches false positives (phases incorrectly marked `python`). False negatives (phases that should be `python` but are not flagged) pass through silently -- same as Auto.

3. **Manual's friction claim**: Manual proponents argue the annotation is trivial. But the existing roadmap format has no `execution_mode` field -- adding one changes the roadmap schema, which affects all existing roadmaps and the roadmap generator pipeline.

---

## Unique Contributions

| Variant | Unique Value |
|---------|-------------|
| Auto | Zero-friction pipeline; works with existing roadmaps without schema changes |
| Manual | Explicit intent documentation; roadmap is self-describing |
| Hybrid | Error-catching review loop; provisional annotation pattern reusable for other auto-detected metadata |

---

## Quantitative Assessment: Heuristic Accuracy (Estimated)

Based on the v2.24.5 Phase 0 as exemplar:

| Heuristic Signal | Phase 0 Match | Confidence |
|-----------------|---------------|------------|
| All tasks EXEMPT tier | Yes (validation/verification tasks) | High |
| Steps contain backtick shell commands | Yes (`claude --print`, `echo >`) | High |
| No file modification steps | Yes (only artifact writing) | Medium |
| Keywords: "validation", "empirical", "gate" | Yes (3/4 match) | High |
| **Combined heuristic confidence** | **Strong match** | **~90%** |

But this is one exemplar. The question is how many non-obvious cases exist where heuristics would fail.
