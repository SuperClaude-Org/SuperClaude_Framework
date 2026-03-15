---
comparison_pair: 1
ic_component: Roadmap Pipeline
lw_component: Pipeline Orchestration (Rigorflow)
ic_source: src/superclaude/cli/roadmap/executor.py, src/superclaude/skills/sc-roadmap-protocol/SKILL.md
lw_source: .claude/commands/rf/pipeline.md
mapping_type: functional_analog
verdict_class: split by context
confidence: 0.82
patterns_not_mass_verified: true
generated: 2026-03-15
---

# Adversarial Comparison: Roadmap Pipeline (IC) vs Pipeline Orchestration (LW)

## 1. Debating Positions

### IC Advocate Position
The IronClaude roadmap pipeline employs a **deterministic, file-on-disk 9-step sequential pipeline** with explicit gate validation at every step. Each artifact is independently reviewable and the pipeline is resumable via `.roadmap-state.json` with stale-spec hash detection. The dual-agent generate strategy (parallel `generate-a` + `generate-b`) is a direct quality mechanism: by forcing two independent LLM variants and running adversarial debate (step 4), IC surfaces assumptions that a single-model generation suppresses. Critically, **the pipeline is implemented in Python — not bash, not experimental infrastructure**. It runs on any standard Python environment with no special flags.

**Key strengths** (`src/superclaude/cli/roadmap/executor.py:302`, `src/superclaude/cli/pipeline/executor.py:46`):
- Resume from any step via `_apply_resume()` with stale-spec sha256 detection
- Pure-Python gate validation: `gate_passed()` is deterministic and testable
- 9 discrete steps each producing a named, reviewable artifact
- Spec-fidelity step (step 8) explicitly cannot be skipped by `--no-validate`

### LW Advocate Position
The llm-workflows Rigorflow pipeline implements **event-driven multi-track parallelism with full track isolation**. Where IC's pipeline processes one roadmap sequentially, LW supports N independent work streams running concurrently, with fast tracks not blocked by slow ones. The explicit per-track state machine (`research=[pending|done|skipped]`, `build=[pending|in_progress|done]`, `execute=[pending|done|failed]`) at `pipeline.md:464-470` is more rigorous than IC's simple step pass/fail. The formal documented fallback (event-driven → phased-parallel) acknowledges experimental instability and provides a deterministic degradation path.

**Key strengths** (`pipeline.md:55-67`, `pipeline.md:458-462`):
- Event-driven per-track progression: fast tracks complete without waiting for slow tracks
- Explicit fallback path with documented trigger conditions
- Per-track state map maintained by orchestrator (tracked, not inferred)
- Hard cap at 5 tracks / 15 agents prevents runaway resource usage

## 2. Evidence from Both Repositories

### IC Evidence
| File | Line | Claim |
|---|---|---|
| `src/superclaude/cli/roadmap/executor.py` | 302 | `_build_steps()` builds declarative 9-step list |
| `src/superclaude/cli/pipeline/executor.py` | 46 | `execute_pipeline()` shared between sprint and roadmap |
| `src/superclaude/cli/roadmap/executor.py` | 1273 | `_apply_resume()` re-enters at first uncompleted step |
| `src/superclaude/cli/roadmap/executor.py` | 1287 | Stale spec detection via sha256 comparison |
| `src/superclaude/cli/pipeline/gates.py` | 20 | `gate_passed()` pure Python, no subprocess |
| `src/superclaude/cli/roadmap/executor.py` | 827 | Spec-fidelity step not skippable by `--no-validate` |
| `src/superclaude/cli/roadmap/executor.py` | 883 | Spec-fidelity auto-resume for late-stage failure |

### LW Evidence
| File | Line | Claim |
|---|---|---|
| `.claude/commands/rf/pipeline.md` | 55-67 | Multi-track architecture with track isolation |
| `.claude/commands/rf/pipeline.md` | 464-470 | Per-track state map with explicit states |
| `.claude/commands/rf/pipeline.md` | 458-462 | Fallback: event-driven → phased-parallel with trigger conditions |
| `.claude/commands/rf/pipeline.md` | 769 | Fallback mode specification |
| `.claude/commands/rf/pipeline.md` | 7-13 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` required |
| `.claude/commands/rf/pipeline.md` | 83 | Hard cap: 5 tracks / 15 agents |
| `.claude/agents/rf-team-lead.md` | 1-30 | All agents use `model: opus` |

## 3. Adversarial Debate

**IC attacks LW**: LW's pipeline depends on `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` — an explicitly experimental API that the document itself acknowledges "may not work reliably." The fallback exists precisely because the primary mode is unstable. IC's pipeline runs on standard Python infrastructure with no experimental dependencies. Furthermore, LW uses all-opus agents for all roles (including codebase research), creating prohibitive cost for routine roadmap generation.

**LW attacks IC**: IC's 9-step pipeline is strictly sequential — each step blocks the next. For multi-track execution (e.g., generating roadmaps for multiple feature areas simultaneously), IC provides no parallelism at the track level. The per-step gate is pure Python (shallow structural checks), while LW's per-track state machine provides richer orchestration visibility. IC's stale-spec detection is clever but scoped only to spec changes — it does not detect stale intermediate artifacts.

**IC counter**: LW's event-driven model introduces coordination complexity that directly increases failure surface. The team lead must handle interleaved messages from multiple researchers — a bug surface IC avoids entirely by sequential processing. For roadmap generation (a document-generating task with strong sequential dependencies between steps), parallelism at the track level adds complexity without a corresponding quality benefit.

**LW counter**: IC's dual-variant generation (steps 2a + 2b) is parallel — IC already exploits parallelism where it matters. But the output validation is file-structure-based, not state-machine-based. LW's state map provides richer failure attribution.

**Convergence**: Both frameworks agree that artifact-producing pipelines with explicit state management are superior to single-shot generation. They diverge on: (a) parallelism model (LW: multi-track concurrent; IC: single-track with internal parallel generate), (b) infrastructure requirements (LW: experimental agent teams; IC: standard Python), and (c) quality mechanism (LW: state machine + QA agents; IC: gate tiers + spec-fidelity step).

## 4. Verdict

**Verdict class: SPLIT BY CONTEXT**

**Conditions where IC is stronger:**
- Single-roadmap generation tasks where sequential step dependencies are natural
- Environments where stability and standard infrastructure are required
- When spec-fidelity verification (coverage of all spec requirements) is a hard requirement
- When the 9-step pipeline's structured artifact trail is needed for audit

**Conditions where LW is stronger:**
- Multi-track parallel roadmap generation (e.g., multiple features in a sprint simultaneously)
- Environments with CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS support and opus budget
- When per-track isolation and independent failure/success per stream is required

**Confidence: 0.82**

**Adopt patterns, not mass**: From IC: the stale-spec hash detection pattern (resume triggers re-run if input changed), the spec-fidelity step design (non-bypassable final coverage check), and the `_apply_resume()` step-level re-entry model. From LW: the per-track state machine pattern (explicit states, not inferred), the documented fallback degradation path (primary fails → known secondary path with documented trigger), and the track isolation rule (no cross-track agent communication).

**Do NOT adopt**: IC's specific 9-step sequence wholesale; LW's experimental agent team infrastructure or all-opus model selection.
