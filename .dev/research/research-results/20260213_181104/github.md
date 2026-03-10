## Findings

Based on extensive GitHub searches, here are repositories specifically related to optimizing Claude Code memory files:

### **HIGH RELEVANCE: Claude Code Memory/CLAUDE.md Optimization**

1. **daymade/claude-code-skills** ⭐ (exact match)
   - https://github.com/daymade/claude-code-skills
   - Stars: Not visible
   - **What it does**: Provides `claude-md-progressive-disclosurer` skill that optimizes CLAUDE.md files by reducing bloat through progressive disclosure
   - **Key technique**: Section classification (keep/move/extract/remove), reference file creation, before/after line-count reporting
   - **Relevance**: **HIGH** - Directly targets CLAUDE.md optimization
   - **Confidence**: High

2. **ruvnet/claude-flow** (Issue #585) ⭐⭐
   - https://github.com/ruvnet/claude-flow/issues/585
   - Stars: 14k (main repo)
   - **What it does**: Project specifically documented the need to reduce CLAUDE.md from 45,948 → <40,000 characters
   - **Key technique**: Consolidate redundant sections, merge duplicate agent listings, replace verbose examples with concise versions, convert explanations to bullet points
   - **Relevance**: **HIGH** - Specific Claude Code CLAUDE.md optimization issue
   - **Confidence**: High

3. **ooples/token-optimizer-mcp** ⭐⭐⭐
   - https://github.com/ooples/token-optimizer-mcp
   - Stars: 17
   - **What it does**: MCP server achieving 95%+ token reduction through caching, compression, and smart tool intelligence for Claude Code
   - **Key technique**: Intelligent caching, compression, smart tool intelligence
   - **Relevance**: **HIGH** - MCP-based token optimization for Claude Code
   - **Confidence**: High

4. **SuperClaude-Org/SuperClaude_Framework** (Issue #286) ⭐⭐
   - https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/286
   - Stars: Not visible
   - **What it does**: Successfully achieved 33% reduction in memory file tokens (7.9k tokens saved) while preserving 100% functionality
   - **Key technique**: PERSONAS.md template compression, FLAGS.md consolidation, COMMANDS.md YAML simplification, symbol system implementation
   - **Relevance**: **HIGH** - Real-world optimization of SuperClaude framework memory files
   - **Confidence**: High

5. **oxygen-fragment/claude-modular** ⭐⭐⭐
   - https://github.com/oxygen-fragment/claude-modular
   - Stars: Not visible
   - **What it does**: Production-ready modular framework achieving 50-80% token savings through progressive disclosure and modular instructions
   - **Key technique**: Progressive disclosure, modular instructions, context compression, smart boundaries
   - **Relevance**: **HIGH** - Direct CLAUDE.md optimization framework
   - **Confidence**: High

6. **johnlindquist/claude-code-context-optimization** (Gist) ⭐⭐⭐
   - https://gist.github.com/johnlindquist/849b813e76039a908d962b2f0923dc9a
   - **What it does**: Achieved 54% reduction in initial context (7,584 → 3,434 tokens)
   - **Key technique**: Lazy loading, trigger-based skill injection, compressed skill stubs, hook optimization
   - **Relevance**: **HIGH** - Documented real-world optimization with metrics
   - **Confidence**: High

7. **anthropics/claude-code** (Feature Request #23727) ⭐
   - https://github.com/anthropics/claude-code/issues/23727
   - Stars: 65.1k (main repo)
   - **What it does**: Feature request for built-in memory file optimization suggestions (e.g., `/optimize-memory` command)
   - **Key technique**: Proposes automated detection of verbose explanations, redundant rules, obsolete entries
   - **Relevance**: **MEDIUM** - Feature request, not implemented tool
   - **Confidence**: Medium

### **MEDIUM RELEVANCE: General LLM Prompt/Context Compression**

8. **3DAgentWorld/Toolkit-for-Prompt-Compression** ⭐⭐
   - https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression
   - Stars: Not visible
   - **What it does**: Unified plug-and-play toolkit for compressing prompts in LLMs with multiple compression methods
   - **Key technique**: Multiple prompt compression algorithms (SCRL, SCCompressor)
   - **Relevance**: **MEDIUM** - General prompt compression, not Claude Code specific
   - **Confidence**: Medium

9. **microsoft/LLMLingua** ⭐⭐⭐
   - https://github.com/microsoft/LLMLingua
   - Stars: Not visible (high profile)
   - **What it does**: Compresses prompts by up to 20x with minimal overhead, maintains context
   - **Key technique**: LLMLingua, LongLLMLingua, LLMLingua-2 algorithms for prompt compression
   - **Relevance**: **MEDIUM** - General LLM prompt compression, adaptable to Claude Code
   - **Confidence**: High

10. **wilpel/caveman-compression** ⭐⭐
    - https://github.com/wilpel/caveman-compression
    - Stars: Not visible
    - **What it does**: Semantic compression achieving 40% average token reduction (171 → 72 tokens for system prompts)
    - **Key technique**: Remove predictable grammar, keep unpredictable facts
    - **Relevance**: **MEDIUM** - General semantic compression applicable to CLAUDE.md
    - **Confidence**: Medium

11. **rtk-ai/rtk** (Rust Token Killer) ⭐⭐
    - https://github.com/rtk-ai/rtk
    - Stars: Not visible
    - **What it does**: CLI proxy reducing LLM token consumption by 60-90% on common operations
    - **Key technique**: Smart filtering, grouping, truncation, deduplication
    - **Relevance**: **MEDIUM** - General token optimization for LLM workflows
    - **Confidence**: Medium

### **LOW RELEVANCE: General Code/Web Minification (Not Prompt-Specific)**

12. **tdewolff/minify** - HTML/CSS/JS minifier (web content, not prompts)
13. **terser/html-minifier-terser** - HTML minifier (web content)
14. **matthiasmullie/minify** - PHP-based minifier (web content)

## KEY TECHNIQUES SUMMARY

Ranked by potential token savings for `~/.claude/` markdown files:

### **1. Progressive Disclosure & Lazy Loading** (50-80% savings)
- **Technique**: Load detailed content only when needed via references
- **Tools**: claude-modular, johnlindquist's optimization, claude-code-skills
- **Example**: Replace inline verbose sections with `@references/detail.md` pointers

### **2. Symbol System Implementation** (30-50% savings)
- **Technique**: Replace verbose language with symbols (→, ✅, ⚡) and abbreviations
- **Tools**: SuperClaude Framework optimization
- **Example**: `auth.js:45 → 🛡️ security risk` vs "The authentication file has a security vulnerability"

### **3. Template/Pattern Consolidation** (33-64% savings)
- **Technique**: Compress repetitive persona/command structures into templates
- **Tools**: SuperClaude Framework, ruvnet/claude-flow
- **Example**: 11 verbose persona definitions → single template format

### **4. Semantic Compression (Caveman Method)** (22-58% savings)
- **Technique**: Remove grammar, keep facts
- **Tools**: caveman-compression
- **Example**: "In order to optimize..." → "Optimize X. Add index."

### **5. Context Caching & Compression** (85-95% latency reduction)
- **Technique**: Cache static content, only process dynamic changes
- **Tools**: token-optimizer-mcp, claude-deep-research-skill
- **Example**: 18K tokens → 2K cached + 4K dynamic = 6K total

### **6. Reference Externalization** (60-75% savings)
- **Technique**: Move code samples and detailed procedures to external files
- **Tools**: claude-code-skills, Plan Optimizer Skill
- **Example**: Replace inline code examples with `See examples/auth.md`

### **7. Section Classification & Pruning** (40-60% savings)
- **Technique**: Identify and remove redundant, obsolete, or verbose content
- **Tools**: claude-md-progressive-disclosurer, Issue #23727 proposal
- **Example**: Detect overlapping rules, consolidate or remove

**Sources:**
- [claude-code-skills (daymade)](https://github.com/daymade/claude-code-skills)
- [claude-flow Issue #585](https://github.com/ruvnet/claude-flow/issues/585)
- [token-optimizer-mcp](https://github.com/ooples/token-optimizer-mcp)
- [SuperClaude Framework Issue #286](https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/286)
- [claude-modular](https://github.com/oxygen-fragment/claude-modular)
- [Claude Code Context Optimization Gist](https://gist.github.com/johnlindquist/849b813e76039a908d962b2f0923dc9a)
- [Claude Code Feature Request #23727](https://github.com/anthropics/claude-code/issues/23727)
- [Toolkit-for-Prompt-Compression](https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression)
- [LLMLingua](https://github.com/microsoft/LLMLingua)
- [caveman-compression](https://github.com/wilpel/caveman-compression)
- [rtk (Rust Token Killer)](https://github.com/rtk-ai/rtk)
