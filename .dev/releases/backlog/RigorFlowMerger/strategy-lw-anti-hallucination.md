# Strategy: LW Component — Anti-Hallucination Rules

**Component**: Anti-Hallucination Rules
**Source**: `.gfdoc/rules/core/anti_hallucination_task_completion_rules.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

This document defines a zero-tolerance protocol for preventing LLM fabrication. Its central innovation is inverting the default epistemic stance: claims are "Incorrect" by default, not "Correct pending refutation."

**Core rigor mechanisms:**

- **Presumption of Falsehood**: Every claim starts with status "Incorrect." The burden of proof lies entirely with the agent to verify every claim. Nothing is assumed true. `anti_hallucination_task_completion_rules.md:59-66`
- **Non-negotiable evidence format**: A claim cannot be "Verified" without a valid, accessible, relevant authoritative source. Format is explicit: `[Source: {authoritative_url}#{specific_section}]`. `anti_hallucination_task_completion_rules.md:67-74`
- **Zero-tolerance forgery penalty**: Fabricated URLs, dead links, or sources that fail to support the claim result in an immediate final FAS score of -100. Task fails with no exceptions. `anti_hallucination_task_completion_rules.md:76-82`
- **Mandatory negative evidence**: Failed verification attempts must be documented. "Not found" is a valid and required evidence entry. This prevents silence-as-success. `anti_hallucination_task_completion_rules.md:83-89`
- **Strict COMPLETE definition**: "COMPLETE" requires: all requirements satisfied, code integrated and functional, all warnings resolved (not suppressed), functionality tested, no dead code, all claims verified. `anti_hallucination_task_completion_rules.md:128-137`
- **Evidence table format**: Mandatory structured table with Claim, Status, Evidence/Justification, Source columns for all technical claims. `anti_hallucination_task_completion_rules.md:148-155`

**Rigor verdict**: The Presumption of Falsehood + FAS -100 penalty for forgery creates genuine deterrence against confabulation. The mandatory documentation of negative evidence is particularly well-designed — it prevents agents from claiming "I couldn't find anything" without recording what was searched.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The evidence table requirement applies to "all tasks involving technical claims" — which is nearly every task. Maintaining a formal evidence table per-claim is high overhead.
- The "Explore Multiple Options" requirement (identify at least two, preferably three approaches for non-trivial tasks) adds deliberation overhead even when the correct approach is known. `anti_hallucination_task_completion_rules.md:105-108`
- The "Propose Research" step (step 6) and the sequentialthinking/decisionframework tool requirements add prescribed process even to well-understood tasks. `anti_hallucination_task_completion_rules.md:124-126, 156-165`

**Operational drag:**
- The verification workflow (make claim → search sources → validate → update status) requires a tool call per claim. For tasks with many claims, this multiplies the tool call count significantly.
- The "source code verification" requirement for all technical claims means no claim about code can be made without a fresh file read, even when the agent has just read that file.

**Token/runtime expense:**
- The evidence table format requires writing a structured markdown table for every technical claim. For analysis-heavy tasks, the overhead of maintaining this table competes with the actual analysis content for context space.
- The FAS -100 penalty has the side effect of making agents extremely verbose in their verification documentation, increasing response length.

**Maintenance burden:**
- The `anti_sycophancy.md` file is a duplicate of this document (confirmed by D-0009). This indicates maintenance drift — two files with the same content but different purposes in the conceptual model. Managing this distinction requires ongoing vigilance.

---

## 3. Execution Model

The anti-hallucination protocol operates as a **per-claim verification workflow** embedded in every task execution:

1. Agent makes a claim → status: "Incorrect"
2. Agent searches authoritative sources (project knowledge first, external second)
3. If found: validates source supports claim exactly → status: "Verified"
4. If not found: documents negative evidence → status: "Incorrect" with note
5. Any forgery: immediate task failure (-100 FAS)
6. Evidence table updated with each claim's status

**Quality enforcement**: The FAS score creates agent-level behavioral incentives. The evidence table creates auditable proof of verification. The sequential verification workflow creates a process trail.

**Extension points**:
- Tool selection is prescribed (`sequentialthinking`, `project_knowledge_search`, `web_search`, `repl`) — these can be swapped for project-appropriate tools.
- FAS threshold can conceptually be adjusted per context.

---

## 4. Pattern Categorization

**Directly Adoptable:**
- Presumption of Falsehood as the default epistemic stance for all claims is directly adoptable. This maps to SuperClaude's "Evidence > assumptions" principle but makes it more explicit.
- Mandatory negative evidence documentation ("Not found" is a required entry) is directly adoptable — it prevents silent omission.
- The strict COMPLETE definition (all requirements + no suppressed warnings + tested + all claims verified) is directly adoptable as SuperClaude's task completion standard.

**Conditionally Adoptable:**
- The evidence table format is conditionally adoptable at STRICT tier. At STANDARD tier, inline citations suffice. At LIGHT/EXEMPT, skip.
- The FAS -100 forgery penalty is conditionally adoptable as a behavioral directive (agents should treat fabrication as a fatal error), but the scoring mechanism itself is internal to llm-workflows.

**Reject:**
- The mandatory "explore multiple options" requirement for non-trivial tasks. SuperClaude's confidence-check approach (assess confidence before implementation) is more efficient.
- The prescribed tool list (`sequentialthinking`, `decisionframework`, `debuggingapproach`) — these are llm-workflows-specific MCP tools, not portable.
