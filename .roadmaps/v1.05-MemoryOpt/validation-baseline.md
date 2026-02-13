# A/B Validation Baseline: v1.05-MemoryOpt

**Captured**: 2026-02-13
**State**: Unmodified ~/.claude/ files (checkpoint-pre-phase-1)

## Test Task Definitions & Baseline Behaviors

### T-001: Persona Activation + MCP Routing + Flag Processing

**Command**: `/sc:analyze @src/main.py --think --persona-security`

**Expected Baseline Behavior**:
- Security persona activates (via `--persona-security` explicit flag)
- Sequential MCP activates (via `--think` flag → `--seq` auto-activation)
- Analysis depth matches `--think` flag (~4K token analysis)
- Security-focused analysis output with threat modeling vocabulary
- ORCHESTRATOR.md routing: "analyze" → complex domain → security persona
- PERSONAS.md provides: security identity, priority hierarchy, core principles, MCP prefs

**Key Verification Points**:
1. Persona identity: "Threat modeler, compliance expert, vulnerability specialist"
2. Priority hierarchy: "Security > compliance > reliability > performance > convenience"
3. MCP primary: Sequential (for threat modeling)
4. MCP secondary: Context7 (for security patterns)
5. Analysis includes: threat assessment, vulnerability identification

**Files Involved**: PERSONAS.md (persona definition), ORCHESTRATOR.md (routing), FLAGS.md (--think), MCP.md (Sequential config)

---

### T-002: Business Panel On-Demand Loading

**Command**: `/sc:business-panel @strategy.md --mode debate`

**Expected Baseline Behavior**:
- Business panel mode activates (MODE_Business_Panel.md loaded)
- Debate mode triggers adversarial analysis
- Expert selection: auto-select 3-5 from 9 experts
- Business symbols available (BUSINESS_SYMBOLS.md loaded)
- Examples available (BUSINESS_PANEL_EXAMPLES.md loaded)
- Three-phase methodology: Discussion → Debate → Synthesis

**Key Verification Points**:
1. Expert personas available: Christensen, Porter, Drucker, Godin, Kim/Mauborgne, Collins, Taleb, Meadows, Doumont
2. Debate mode triggers: structured disagreement, evidence marshaling
3. Business symbols: strategic (🎯📈💰), framework (🔨⚔️🌊), process (🔍💡🤝)
4. Synthesis framework: convergent insights, productive tensions, system patterns
5. MCP: Sequential primary for multi-expert coordination

**Files Involved**: MODE_Business_Panel.md, BUSINESS_SYMBOLS.md, BUSINESS_PANEL_EXAMPLES.md, ORCHESTRATOR.md

---

### T-003: Research Configuration On-Demand Loading

**Command**: `/sc:research "token optimization" --depth deep`

**Expected Baseline Behavior**:
- Deep research mode activates (MODE_DeepResearch.md)
- RESEARCH_CONFIG.md provides depth profiles
- Deep profile: max_sources=40, max_hops=4, iterations=3, time_limit=8min, confidence=0.8
- Source credibility tiers: T1 (0.9-1.0), T2 (0.7-0.9), T3 (0.5-0.7), T4 (0.3-0.5)
- Extraction routing: tavily (static), playwright (JS), context7 (tech docs), native (local)

**Key Verification Points**:
1. Depth profile "deep": max_sources=40, max_hops=4, confidence_target=0.8
2. Source credibility T1: academic journals, government pubs, official docs, peer-reviewed
3. Parallel execution rules: DEFAULT_MODE=PARALLEL
4. Hop patterns: entity_expansion, concept_deepening, temporal_progression, causal_chain
5. Quality gates: planning_gate, execution_gate (min 0.6), synthesis_gate

**Files Involved**: RESEARCH_CONFIG.md, MODE_DeepResearch.md, MCP.md (tavily/sequential config)

---

### T-004: Tier Classification + Wave Routing

**Command**: `/sc:implement "add auth middleware" --compliance strict`

**Expected Baseline Behavior**:
- STRICT tier classification (explicit --compliance strict)
- Security persona auto-activates (auth keyword → security domain)
- Backend persona co-activates (middleware → server-side)
- Wave eligibility assessed (complexity scoring)
- Sequential MCP enabled for STRICT tier
- Validation gates enforced

**Key Verification Points**:
1. Tier: STRICT (explicit override, 100% confidence)
2. Compound phrase: "add authentication" → STRICT override
3. Context booster: security path detected → +0.4 STRICT
4. Auto-personas: security (auth keyword), backend (middleware keyword)
5. Verification: sub-agent (quality-engineer) per tier mapping
6. Wave assessment: complexity scoring against threshold

**Files Involved**: ORCHESTRATOR.md (tier classification, wave scoring), PERSONAS.md (security + backend), COMMANDS.md (/implement definition), MCP.md (Sequential for STRICT)

---

### T-005: MCP Selection + Command Routing + Wave System

**Command**: `/sc:build --feature --magic --react`

**Expected Baseline Behavior**:
- Frontend persona auto-activates (react keyword → frontend domain)
- Magic MCP activated (explicit --magic flag)
- Context7 MCP auto-activated (React framework → documentation needs)
- Wave eligibility assessed for /build command (wave-enabled Tier 1)
- Build command routes through development category
- Framework detection: React

**Key Verification Points**:
1. Persona: frontend (react/component keywords)
2. MCP activated: Magic (explicit --magic), Context7 (React framework auto-detect)
3. Command category: Development & Deployment
4. Wave-enabled: Yes (Tier 1 command)
5. Tool orchestration: Read, Grep, Glob, Bash, TodoWrite, Edit, MultiEdit
6. Performance profile: optimization

**Files Involved**: COMMANDS.md (/build definition, wave system), ORCHESTRATOR.md (routing, wave assessment), PERSONAS.md (frontend persona), FLAGS.md (--magic flag), MCP.md (Magic + Context7 config)

---

## Validation Protocol

### A/B Comparison Method
1. **Baseline** (this document): Expected behaviors captured from unmodified files
2. **Post-change**: Run same command/scenario on compressed files
3. **Comparison**: Score each verification point as PASS / DEGRADED / FAIL
4. **Threshold**: 0 FAIL allowed, ≤1 DEGRADED per milestone

### Scoring Rubric
- **PASS**: Behavior identical to baseline (persona, MCP, routing, output quality all match)
- **DEGRADED**: Minor difference that doesn't affect functionality (e.g., slightly different wording but same persona activates)
- **FAIL**: Broken functionality (wrong persona, missing MCP, incorrect routing, lost information)

### Cross-Reference Validation
After each milestone, additionally verify:
- All "See X.md §Y" references resolve to valid sections
- No orphaned references to removed content
- Canonical sources contain complete definitions
