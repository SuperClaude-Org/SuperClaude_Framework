---
name: Spec Panel
description: Multi-expert specification review panel. Use when reviewing or improving specifications, requirements documents, API contracts, design docs, or user stories. Applies named expert lenses (Wiegers, Adzic, Fowler, Nygard, et al.) in discussion, critique, or socratic mode to produce expert-attributed findings with severity ratings and concrete rewrite suggestions.
---

# Spec Panel Skill

Review a specification through a panel of named experts, each applying their
distinct methodology. Every finding must be attributed to an expert, rated by
severity, and paired with a concrete rewrite — never a vague "improve clarity".

## Expert Lenses

Each expert reviews ONLY through their methodology. Do not blend voices.

| Expert | Lens | Methodology | Characteristic question |
|---|---|---|---|
| **Karl Wiegers** | Requirements quality | SMART criteria, testability, measurable acceptance criteria | "How would you validate compliance with this in production?" |
| **Gojko Adzic** | Specification by example | Given/When/Then scenarios, executable examples | "Show me a concrete example demonstrating this requirement." |
| **Alistair Cockburn** | Use cases | Primary actors, goal-oriented scenarios | "Who is the stakeholder, and what goal are they pursuing?" |
| **Martin Fowler** | Architecture & API design | Interface segregation, bounded contexts, evolutionary design | "What happens to consumers when this interface changes?" |
| **Michael Nygard** | Production reliability | Failure mode analysis, stability patterns, operability | "What happens when this component fails? Where is recovery defined?" |
| **Sam Newman** | Distributed systems | Service boundaries, API versioning, backward compatibility | "How does this spec handle service evolution?" |
| **Gregor Hohpe** | Integration | Messaging patterns, ordering and delivery guarantees | "What is the message exchange pattern? Who guarantees delivery?" |
| **Lisa Crispin** | Testing strategy | Risk-based testing, edge cases, acceptance criteria | "How would a tester validate this? What are the failure scenarios?" |
| **Janet Gregory** | Collaborative quality | Specification workshops, shared quality expectations | "Are quality expectations explicit enough for the whole team?" |
| **Kelsey Hightower** | Cloud-native operations | Deployment, observability, infrastructure as code | "What monitoring does this spec require to operate?" |

## Panel Selection

Pick 3-5 experts matching the document type, or honor an explicit user request.

- **Requirements / user stories**: Wiegers (lead), Adzic, Cockburn
- **Architecture / API contracts**: Fowler (lead), Newman, Hohpe, Nygard
- **Testing / acceptance criteria**: Crispin (lead), Gregory, Adzic
- **Compliance / security / operations**: Wiegers (lead), Nygard, Hightower

## Modes

Default to **critique** unless the user asks otherwise.

### Critique mode

Systematic review. Each expert lists findings in this exact structure:

```
=== <FOCUS AREA> ===

KARL WIEGERS — Requirements Quality:
[CRITICAL] R-001 lacks measurable acceptance criteria.
  Rewrite: Replace "handle failures gracefully" with "open circuit
  breaker after 5 consecutive failures within 30 seconds".

GOJKO ADZIC — Specification Testability:
[MAJOR] No executable examples for the retry behavior.
  Rewrite: Add scenario —
    Given: service timeout after 30 seconds
    When: circuit breaker activates
    Then: return cached response within 100ms
```

Severity scale:
- **CRITICAL** — spec cannot be implemented or validated as written
- **MAJOR** — ambiguity or gap likely to cause divergent implementations
- **MINOR** — quality improvement; not a functional defect

### Discussion mode

Experts build on each other's points in dialogue, converging on a shared
recommendation. Each turn must add new substance (a sharper question, a
concrete example, an interface implication) — not restate the previous point.

```
KARL WIEGERS: "'SHALL handle failures gracefully' — what constitutes
graceful? Which failure types?"

MICHAEL NYGARD: "Building on that: name the modes — network timeout,
service unavailable, rate limiting. Each needs a distinct strategy."

GOJKO ADZIC: "Make it executable: Given a 30s timeout, When the breaker
opens, Then return the cached response within 100ms."
```

End discussion mode with a short **Consensus** block: the 2-4 changes all
experts agree on.

### Socratic mode

No findings or rewrites — only questions, to deepen the author's own
analysis. Each expert asks 1-2 questions from their lens, ordered from
foundational to specific:

```
ALISTAIR COCKBURN: "What problem is this specification solving, and for whom?"
KARL WIEGERS: "Which of these requirements could two engineers implement
differently while both claiming compliance?"
MARTIN FOWLER: "What breaks if this requirement is removed entirely?"
LISA CRISPIN: "How would you detect in production that this is violated?"
```

## Review Process

1. **Read the spec** and identify its type (requirements, API contract,
   architecture doc, test plan) to select the panel.
2. **Per-expert pass**: each expert reviews the full document through their
   lens only. An expert with nothing substantive to say says nothing —
   no filler findings.
3. **Synthesize**: deduplicate overlapping findings (attribute to the
   expert whose lens is most specific), then rank by severity.
4. **Summarize**: close with a prioritized list —
   - **Fix now**: all CRITICAL findings
   - **Fix before implementation**: MAJOR findings
   - **Consider**: MINOR findings
5. If the user asks for an improved spec, apply the CRITICAL and MAJOR
   rewrites and present the revised document. Never modify the user's file
   without explicit request.

## Rules

- Every finding names its expert and quotes or references the exact spec
  text it concerns.
- Every CRITICAL or MAJOR finding includes a concrete rewrite, not advice.
- Experts disagree when their methodologies genuinely conflict (e.g.
  Fowler's interface flexibility vs. Newman's versioning discipline);
  surface the trade-off instead of forcing consensus.
- Do not invent requirements the author never implied; socratic questions
  are the vehicle for exploring scope gaps.
- Do not provide legal or regulatory compliance guarantees — compliance
  findings are analysis, not certification.
