# Specification Generator Framework Research

> **Status**: Ready for Execution
> **Purpose**: Build knowledge base to inform the Ultimate Spec Generator Framework

---

## What This Research Will Produce

A comprehensive wiki covering best practices for software specification generation, optimized for AI/LLM consumption:

```
spec-generator-framework/
├── README.md                    ← You are here
├── RESEARCH_PROMPT.md           ← Detailed research methodology
├── EXECUTE.md                   ← Step-by-step execution guide
│
├── best-practices/              ← Distilled wisdom (Phase 2-3)
│   ├── structure.md
│   ├── content.md
│   ├── quality.md
│   ├── process.md
│   └── ai-optimization.md
│
├── sources/                     ← Deep dives (Phase 1)
│   ├── bmad-method/
│   ├── spec-kitchen/
│   ├── kiro/
│   ├── standards/
│   ├── industry/
│   └── ai-native/
│
├── synthesis/                   ← Cross-source analysis (Phase 2)
│   ├── overlapping-themes.md
│   ├── unique-contributions.md
│   └── unified-best-practices.md
│
└── appendices/                  ← Reference materials (Phase 3)
    ├── glossary.md
    └── source-urls.md
```

---

## Why This Research Matters

The goal is to create a **Spec Generator Framework** that:

1. **Transforms vague ideas** → Detailed, structured specifications
2. **Through collaborative dialogue** → AI-human iterative refinement
3. **Produces AI-optimized output** → Specs that LLMs can reliably consume
4. **Maximizes downstream quality** → Better roadmaps, task lists, execution

This research ensures we build on proven best practices rather than reinventing the wheel.

---

## Sources Being Analyzed

### Mandatory (Deep Dive)
| Source | What We'll Extract |
|--------|-------------------|
| **BMAD-METHOD** | Complete methodology for AI-driven development |
| **GitHub Spec Kitchen** | GitHub's internal specification patterns |
| **Kiro Documentation** | Modern spec concepts, correctness, best practices |

### Standards
| Source | What We'll Extract |
|--------|-------------------|
| **IEEE 830 / ISO 29148** | Formal SRS structure and requirements |
| **RFC 2119** | MUST/SHOULD/MAY keyword conventions |

### Industry Practices
| Source | What We'll Extract |
|--------|-------------------|
| **Shape Up** | Pitches, appetites, appetite-based scoping |
| **Amazon Working Backwards** | PR-FAQ specification method |
| **Google Design Docs** | Tech company spec templates |

### AI-Native Patterns
| Source | What We'll Extract |
|--------|-------------------|
| **Prompt Engineering Guides** | How to structure specs for AI |
| **Cursor Rules / CLAUDE.md** | AI coding assistant spec formats |
| **Structured Output Schemas** | Machine-readable spec patterns |

---

## How to Execute

See **[EXECUTE.md](./EXECUTE.md)** for step-by-step instructions.

**Quick version**:

```bash
# Phase 0: Discover additional sources
/sc:research "specification best practices software AI LLM 2024 2025"

# Phase 1: Spawn 6 parallel agents for source analysis
/sc:spawn --parallel @RESEARCH_PROMPT.md#phase-1-agents

# Phase 2: Synthesize findings
/sc:spawn synthesizer --wait-for phase-1

# Phase 3: Assemble wiki
/sc:spawn wiki-assembler --wait-for synthesizer
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Sources fully analyzed | 10+ |
| BMAD-METHOD file coverage | 100% |
| Best practices extracted | 50+ |
| Templates documented | 10+ |
| Anti-patterns identified | 20+ |
| AI-optimization patterns | 15+ |

---

## Next Steps After Research

Once this wiki is complete, it will inform:

1. **Spec Generator Command Design** (`/rf:spec-gen` or similar)
2. **Spec Templates** for different project types
3. **Quality Rubrics** for spec validation
4. **AI-Optimization Guidelines** for maximum LLM comprehension

---

*Research framework created for InfraDocs/IBOpenCode integration*
