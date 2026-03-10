# Extraction: Personas integration with commands, skills, and agents (core)

**Source file:** `/config/workspace/SuperClaude_Framework/src/superclaude/core/PERSONAS.md`

This document extracts **all** content from the source file that describes how personas integrate with **commands**, **skills**, and **agents** inside the SuperClaude framework. Where the source does **not** mention skills/agents explicitly, that absence is recorded.

---

## 1) Integration primitives (how personas connect to the framework)

### 1.1 Persona system purpose and what it influences

Exact quotes:

> “Persona system provides specialized AI behavior patterns optimized for specific domains. Each persona has unique decision frameworks, technical preferences, and command specializations.”

### 1.2 Core features that create integration points

Exact quotes (Core Features):

> “- **Auto-Activation**: Multi-factor scoring with context awareness”
>
> “- **Decision Frameworks**: Context-sensitive with confidence scoring”
>
> “- **Cross-Persona Collaboration**: Dynamic integration and expertise sharing”
>
> “- **Manual Override**: Use `--persona-[name]` flags for explicit control”
>
> “- **Flag Integration**: Works with all thinking flags, MCP servers, and command categories”

**Integration implication (from quotes):**
- Personas integrate into the framework via **auto-activation**, **manual override flags**, and **flag integration** across command categories.

### 1.3 Persona template fields that explicitly integrate with commands

Exact quotes:

> “Each persona follows this structure. Only deltas from these defaults are specified per persona:”
>
> “- **MCP Prefs**: Primary and secondary server preferences”
>
> “- **Commands**: Optimized command set”
>
> “- **Triggers**: Keywords and context for auto-activation”

**Integration implication (from quotes):**
- Each persona declares:
  - **Commands** it is optimized for (direct coupling to command system)
  - **Triggers** for auto-selection (routing/invocation coupling)
  - **MCP preferences** (tooling/runtime coupling that affects how commands are executed)

---

## 2) Manual persona selection (CLI flags)

### 2.1 Generic manual override flag

Exact quote:

> “- **Manual Override**: Use `--persona-[name]` flags for explicit control”

### 2.2 Concrete persona flag names

The file defines the following explicit persona selectors (as headings):

```md
### `--persona-architect`
### `--persona-frontend`
### `--persona-security`
### `--persona-backend`
### `--persona-analyzer`
### `--persona-mentor`
### `--persona-refactorer`
### `--persona-performance`
### `--persona-qa`
### `--persona-devops`
### `--persona-scribe=lang`
```

---

## 3) Command integration per persona (optimized command sets)

This section extracts all “Commands” fields, since these are the direct persona→command bindings in the source.

### 3.1 Anchor personas (expanded)

#### `--persona-architect`

Exact quote:

> “**Commands**: `/analyze`, `/estimate`, `/improve --arch`, `/design`”

#### `--persona-frontend`

Exact quote:

> “**Commands**: `/build`, `/improve --perf`, `/test e2e`, `/design`”

#### `--persona-security`

Exact quote:

> “**Commands**: `/analyze --focus security`, `/improve --security`”

### 3.2 Compact personas

#### `--persona-backend`

Exact quote:

> “- **Commands**: `/build --api`, `/git`”

#### `--persona-analyzer`

Exact quote:

> “- **Commands**: `/analyze`, `/troubleshoot`, `/explain --detailed`, `/cleanup-audit`”

#### `--persona-mentor`

Exact quote:

> “- **Commands**: `/explain`, `/document`, `/index`”

#### `--persona-refactorer`

Exact quote:

> “- **Commands**: `/improve --quality`, `/cleanup`, `/analyze --quality`”

#### `--persona-performance`

Exact quote:

> “- **Commands**: `/improve --perf`, `/analyze --focus performance`, `/test --benchmark`”

#### `--persona-qa`

Exact quote:

> “- **Commands**: `/test`, `/troubleshoot`, `/analyze --focus quality`”

#### `--persona-devops`

Exact quote:

> “- **Commands**: `/git`, `/analyze --focus infrastructure`”

#### `--persona-scribe=lang`

Exact quote:

> “- **Commands**: `/document`, `/explain`, `/git`, `/build`”

---

## 4) Auto-activation integration (how personas are selected for commands)

### 4.1 Global auto-activation scoring model

Exact quote:

> “**Auto-Activation System**: Multi-factor scoring with context awareness, keyword matching (30%), context analysis (40%), user history (20%), performance metrics (10%).”

This is the only quantified mechanism in the file describing how persona selection integrates into runtime behavior.

### 4.2 Per-persona trigger phrases (routing inputs)

Per-persona “Triggers” are the explicit integration surface for automated persona selection.

#### `--persona-architect`

Exact quote:

> “**Triggers**: "architecture", "design", "scalability", complex system modifications, multi-module changes”

#### `--persona-frontend`

Exact quote:

> “**Triggers**: "component", "responsive", "accessibility", design system work, UI/UX”

#### `--persona-security`

Exact quote:

> “**Triggers**: "vulnerability", "threat", "compliance", auth/authorization work”

#### `--persona-backend`

Exact quote:

> “- **Triggers**: "API", "database", "service", "reliability"”

#### `--persona-analyzer`

Exact quote:

> “- **Triggers**: "analyze", "investigate", "root cause", debugging sessions, "audit", "dead code", "cleanup audit", "repository audit"”

#### `--persona-mentor`

Exact quote:

> “- **Triggers**: "explain", "learn", "understand", step-by-step guidance”

#### `--persona-refactorer`

Exact quote:

> “- **Triggers**: "refactor", "cleanup", "technical debt"”

#### `--persona-performance`

Exact quote:

> “- **Triggers**: "optimize", "performance", "bottleneck", speed/efficiency”

#### `--persona-qa`

Exact quote:

> “- **Triggers**: "test", "quality", "validation", edge cases”

#### `--persona-devops`

Exact quote:

> “- **Triggers**: "deploy", "infrastructure", "automation", monitoring”

#### `--persona-scribe=lang`

Exact quote:

> “- **Triggers**: "document", "write", "guide", localization work”

---

## 5) MCP integration (how personas influence runtime/tooling for commands)

The file encodes persona→MCP preference mappings, which integrate with command execution by biasing server/tool selection.

### 5.1 Anchor personas

#### `--persona-architect`

Exact quote:

> “**MCP Prefs**: Primary: Sequential | Secondary: Context7 | Avoided: Magic”

#### `--persona-frontend`

Exact quote:

> “**MCP Prefs**: Primary: Magic | Secondary: Playwright”

#### `--persona-security`

Exact quote:

> “**MCP Prefs**: Primary: Sequential | Secondary: Context7 | Avoided: Magic”

### 5.2 Compact personas

#### `--persona-backend`

Exact quote:

> “- **MCP**: Primary: Context7 | Secondary: Sequential | Avoided: Magic”

#### `--persona-analyzer`

Exact quote:

> “- **MCP**: Primary: Sequential | Secondary: Context7 | Tertiary: All servers”

#### `--persona-mentor`

Exact quote:

> “- **MCP**: Primary: Context7 | Secondary: Sequential | Avoided: Magic”

#### `--persona-refactorer`

Exact quote:

> “- **MCP**: Primary: Sequential | Secondary: Context7 | Avoided: Magic”

#### `--persona-performance`

Exact quote:

> “- **MCP**: Primary: Playwright | Secondary: Sequential | Avoided: Magic”

#### `--persona-qa`

Exact quote:

> “- **MCP**: Primary: Playwright | Secondary: Sequential | Avoided: Magic”

#### `--persona-devops`

Exact quote:

> “- **MCP**: Primary: Sequential | Secondary: Context7 | Avoided: Magic”

#### `--persona-scribe=lang`

Exact quote:

> “- **MCP**: Primary: Context7 | Secondary: Sequential | Avoided: Magic”

---

## 6) Cross-persona collaboration (multi-persona integration)

The file defines how multiple personas integrate/coordinate via an explicit collaboration framework.

### 6.1 Expertise sharing protocols

Exact quotes:

> “**Expertise Sharing Protocols**:”
>
> “- **Primary Persona**: Leads decision-making within domain expertise”
>
> “- **Consulting Personas**: Provide specialized input for cross-domain decisions”
>
> “- **Validation Personas**: Review decisions for quality, security, and performance”
>
> “- **Handoff Mechanisms**: Seamless transfer when expertise boundaries are crossed”

### 6.2 Complementary collaboration patterns

Exact quotes:

> “**Complementary Collaboration Patterns**:”
>
> “- **architect + performance**: System design with performance budgets and optimization paths”
>
> “- **security + backend**: Secure server-side development with threat modeling”
>
> “- **frontend + qa**: User-focused development with accessibility and performance testing”
>
> “- **mentor + scribe**: Educational content creation with cultural adaptation”
>
> “- **analyzer + refactorer**: Root cause analysis with systematic code improvement”
>
> “- **devops + security**: Infrastructure automation with security compliance”

### 6.3 Conflict resolution mechanisms (how coordination decisions are made)

Exact quotes:

> “**Conflict Resolution Mechanisms**:”
>
> “- **Priority Matrix**: Resolve conflicts using persona-specific priority hierarchies”
>
> “- **Context Override**: Project context can override default persona priorities”
>
> “- **User Preference**: Manual flags and user history override automatic decisions”
>
> “- **Escalation Path**: architect persona for system-wide conflicts, mentor for educational conflicts”

---

## 7) Integration with skills and agents (what PERSONAS.md does / does not specify)

### 7.1 Skills

**No explicit skills integration is defined in** `/config/workspace/SuperClaude_Framework/src/superclaude/core/PERSONAS.md`.

What the file does say that could relate indirectly:

- Persona “**Commands**” sets (command integration)
- “**Manual Override**” via `--persona-[name]` (flag integration)
- “**Cross-Persona Collaboration**” (multi-persona coordination)

Exact quote indicating scope of integration across framework features:

> “- **Flag Integration**: Works with all thinking flags, MCP servers, and command categories”

### 7.2 Agents

**No explicit agent integration is defined in** `/config/workspace/SuperClaude_Framework/src/superclaude/core/PERSONAS.md`.

The file does not mention any `@agent-*` directives, agent selection syntax, or agent names.

---

## 8) Scribe persona special parameterization (language variants)

The scribe persona is the only persona whose selector includes a parameter (`=lang`). This impacts how it integrates into commands by allowing language-specific behavior.

Exact quotes:

> “### `--persona-scribe=lang`”
>
> “- **Languages**: en (default), es, fr, de, ja, zh, pt, it, ru, ko”
>
> “- **Content Types**: Technical docs, user guides, wiki, PR content, commit messages, localization”
