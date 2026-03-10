#!/usr/bin/env bash
# ============================================================================
# research-memory-optimization.sh
# Launches 3 parallel Claude agents to research memory file compression
# techniques from GitHub, articles, and community discussions.
#
# Each agent gets the /sc:research methodology injected via
# --append-system-prompt (since slash commands don't work in -p mode).
#
# Usage: ./scripts/research-memory-optimization.sh [output_dir]
# Default output: ./research-results/
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR="${1:-./research-results}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="${OUTPUT_DIR}/${TIMESTAMP}"

# Models - change these to control cost/quality tradeoff
MODEL_GITHUB="sonnet"
MODEL_ARTICLES="sonnet"
MODEL_COMMUNITY="haiku"

# MCP config - Tavily for web search capability
MCP_CONFIG="/config/.claude/mcp.json"

# /sc:research skill file - injected as system prompt for research methodology
RESEARCH_SKILL="/config/.claude/commands/sc/research.md"

# Timeout per agent (seconds)
AGENT_TIMEOUT=300

# Common flags for all agents
COMMON_FLAGS=(
    --print
    --dangerously-skip-permissions
    --no-session-persistence
    --mcp-config "$MCP_CONFIG"
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "Memory File Optimization Research"
echo "============================================"
echo "Output directory: $RESULTS_DIR"
echo "Models: GitHub=$MODEL_GITHUB | Articles=$MODEL_ARTICLES | Community=$MODEL_COMMUNITY"
echo "MCP config: $MCP_CONFIG"
echo "Research skill: $RESEARCH_SKILL"
echo "Timeout: ${AGENT_TIMEOUT}s per agent"
echo ""

# Verify dependencies
if [[ ! -f "$MCP_CONFIG" ]]; then
    echo "ERROR: MCP config not found at $MCP_CONFIG"
    exit 1
fi

if [[ ! -f "$RESEARCH_SKILL" ]]; then
    echo "WARNING: Research skill not found at $RESEARCH_SKILL"
    echo "Agents will run without /sc:research methodology injection."
    RESEARCH_SYSTEM_PROMPT=""
else
    RESEARCH_SYSTEM_PROMPT=$(cat "$RESEARCH_SKILL")
    echo "Research skill loaded ($(wc -c < "$RESEARCH_SKILL") bytes)"
fi

if ! command -v claude &>/dev/null; then
    echo "ERROR: 'claude' CLI not found in PATH"
    exit 1
fi

echo ""

# ---------------------------------------------------------------------------
# Build system prompt and write to temp file (primary method)
# ---------------------------------------------------------------------------
# This gives each agent the /sc:research behavioral framework:
# - Parallel-first searches
# - Evidence management with citations
# - Confidence scoring
# - Adaptive depth
# - Source credibility tracking

SYSTEM_PROMPT_FILE=$(mktemp "${TMPDIR:-/tmp}/research-system-prompt.XXXXXX")
trap 'rm -f "$SYSTEM_PROMPT_FILE"' EXIT

cat > "$SYSTEM_PROMPT_FILE" <<SYSPROMPT_EOF
You are a deep research agent. Follow this research methodology:

${RESEARCH_SYSTEM_PROMPT}

CRITICAL RULES:
- Use Tavily web search tools (tavily-search, tavily-extract) for all searches.
- Run multiple searches in parallel when possible.
- Track source credibility: Tier 1 (official docs, academic) > Tier 2 (established blogs) > Tier 3 (forums) > Tier 4 (comments).
- Provide confidence levels for each finding (high/medium/low).
- Include URLs for every finding.
- If results are sparse, say so honestly - do NOT fabricate or pad results.
- End with a clear synthesis section.
SYSPROMPT_EOF

echo "System prompt written to temp file: $SYSTEM_PROMPT_FILE ($(wc -c < "$SYSTEM_PROMPT_FILE") bytes)"

# ---------------------------------------------------------------------------
# Agent Prompts
# ---------------------------------------------------------------------------

read -r -d '' PROMPT_GITHUB << 'GITHUB_EOF' || true
RESEARCH DOMAIN: GitHub Repositories

TASK: Search GitHub for repositories related to optimizing Claude Code memory files (.claude/ directory, CLAUDE.md, system prompt configuration files).

SEARCH FOR:
1. Repos that compress, optimize, or manage Claude Code CLAUDE.md or ~/.claude/ configuration files
2. System prompt compression tools or token optimization utilities for any LLM
3. Instruction file distillation or minification frameworks
4. Any "awesome-claude-code" or curated lists mentioning prompt compression
5. Tools that measure token counts and suggest compression strategies

SEARCH TERMS (run these in parallel batches):
Batch 1:
- "claude code CLAUDE.md optimization github"
- "system prompt compression tool github"
- "CLAUDE.md token optimization"

Batch 2:
- "LLM instruction token reduction github"
- "claude code memory files optimization"
- "prompt minification tool github"

Batch 3:
- "awesome claude code system prompt"
- "claude code context window optimization tool"

FOR EACH FINDING, PROVIDE:
- Repository URL
- Star count (if visible)
- What it does (1-2 sentences)
- Key compression technique used
- Relevance to optimizing ~/.claude/ markdown files (high/medium/low)
- Confidence level (high/medium/low)

If fewer than 3 relevant results exist, say so honestly. Do not pad results.

OUTPUT FORMAT:
## Findings
[numbered list of repos]

## KEY TECHNIQUES SUMMARY
[unique compression approaches discovered, ranked by potential token savings]
GITHUB_EOF

read -r -d '' PROMPT_ARTICLES << 'ARTICLES_EOF' || true
RESEARCH DOMAIN: Technical Articles & Best Practices

TASK: Search for blog posts, articles, and technical documentation about compressing and optimizing AI system prompts / instruction files to reduce token consumption while maintaining effectiveness.

SEARCH FOR:
1. Best practices for writing token-efficient system prompts and LLM instructions
2. Techniques for compressing AI agent configuration files without losing effectiveness
3. Markdown/YAML compression strategies for LLM context windows
4. Research or benchmarks on verbose vs compressed instruction formats
5. Specific measured compression ratios or token savings from prompt optimization

SEARCH TERMS (run these in parallel batches):
Batch 1:
- "optimize system prompt token usage best practices 2025 2026"
- "compress LLM system instructions techniques"
- "AI agent instruction compression guide"

Batch 2:
- "claude code system prompt optimization"
- "token efficient prompt engineering markdown"
- "system prompt minification without quality loss"

Batch 3:
- "LLM context window optimization techniques"
- "reducing system prompt size AI assistant"

FOR EACH FINDING, PROVIDE:
- Article URL
- Author/publication
- Key technique or insight (2-3 sentences)
- Any measured compression ratios or token savings reported
- Applicability to markdown instruction files (high/medium/low)
- Source credibility tier (1-4)

OUTPUT FORMAT:
## Findings
[numbered list of articles]

## ACTIONABLE TECHNIQUES
[ranked list of specific compression techniques ordered by expected token savings, with implementation notes]
ARTICLES_EOF

read -r -d '' PROMPT_COMMUNITY << 'COMMUNITY_EOF' || true
RESEARCH DOMAIN: Community Discussions & Sentiment

TASK: Search Reddit and developer forums for discussions about optimizing Claude Code memory files, system prompt size management, or LLM instruction compression.

SEARCH TERMS (run these in parallel batches):
Batch 1:
- "CLAUDE.md too large tokens site:reddit.com"
- "claude code system prompt optimization reddit"
- "claude code context window memory files reddit"

Batch 2:
- "system prompt compression reddit LLM"
- "claude code .claude directory optimization"
- "reduce claude code token usage system prompt"

Batch 3:
- "claude code memory files too many tokens"
- "LLM system prompt best size reddit"

LOOK FOR:
1. r/ClaudeAI posts about CLAUDE.md or .claude/ file optimization
2. r/ChatGPTPro or r/LocalLLaMA discussions on system prompt compression
3. Community sentiment: do compressed prompts work as well as verbose ones?
4. Real user experiences with before/after token counts
5. Any shared templates, compressed instruction frameworks, or tools
6. Common pitfalls or things that DON'T work

FOR EACH FINDING, PROVIDE:
- URL
- Subreddit or forum
- Summary of discussion (2-3 sentences)
- Community consensus or key takeaway
- Upvote/engagement level if visible

OUTPUT FORMAT:
## Findings
[numbered list of discussions]

## COMMUNITY CONSENSUS
- What techniques users report actually working
- What techniques users report NOT working
- Overall sentiment on compressed vs verbose instructions
COMMUNITY_EOF

# ---------------------------------------------------------------------------
# Launch Agents in Parallel
# ---------------------------------------------------------------------------
echo "Launching 3 parallel research agents..."
echo ""

# Agent 1: GitHub repos (sonnet)
echo "[Agent 1] GitHub Research (model: $MODEL_GITHUB) → ${RESULTS_DIR}/github.md"
(
    CLAUDECODE= timeout "$AGENT_TIMEOUT" claude \
        "${COMMON_FLAGS[@]}" \
        --model "$MODEL_GITHUB" \
        --append-system-prompt "$(cat "$SYSTEM_PROMPT_FILE")" \
        -p "$PROMPT_GITHUB" \
        > "${RESULTS_DIR}/github.md" 2>"${RESULTS_DIR}/github.err"
    echo "[Agent 1] DONE (exit: $?)"
) &
PID_GITHUB=$!

# Agent 2: Articles & blog posts (sonnet)
echo "[Agent 2] Articles Research (model: $MODEL_ARTICLES) → ${RESULTS_DIR}/articles.md"
(
    CLAUDECODE= timeout "$AGENT_TIMEOUT" claude \
        "${COMMON_FLAGS[@]}" \
        --model "$MODEL_ARTICLES" \
        --append-system-prompt "$(cat "$SYSTEM_PROMPT_FILE")" \
        -p "$PROMPT_ARTICLES" \
        > "${RESULTS_DIR}/articles.md" 2>"${RESULTS_DIR}/articles.err"
    echo "[Agent 2] DONE (exit: $?)"
) &
PID_ARTICLES=$!

# Agent 3: Community discussions (haiku)
echo "[Agent 3] Community Research (model: $MODEL_COMMUNITY) → ${RESULTS_DIR}/community.md"
(
    CLAUDECODE= timeout "$AGENT_TIMEOUT" claude \
        "${COMMON_FLAGS[@]}" \
        --model "$MODEL_COMMUNITY" \
        --append-system-prompt "$(cat "$SYSTEM_PROMPT_FILE")" \
        -p "$PROMPT_COMMUNITY" \
        > "${RESULTS_DIR}/community.md" 2>"${RESULTS_DIR}/community.err"
    echo "[Agent 3] DONE (exit: $?)"
) &
PID_COMMUNITY=$!

echo ""
echo "PIDs: GitHub=$PID_GITHUB | Articles=$PID_ARTICLES | Community=$PID_COMMUNITY"
echo "Waiting for all agents to complete..."
echo ""

# ---------------------------------------------------------------------------
# Wait & Collect Results
# ---------------------------------------------------------------------------
FAILED=0

wait $PID_GITHUB || { echo "WARNING: Agent 1 (GitHub) failed or timed out"; FAILED=$((FAILED+1)); }
wait $PID_ARTICLES || { echo "WARNING: Agent 2 (Articles) failed or timed out"; FAILED=$((FAILED+1)); }
wait $PID_COMMUNITY || { echo "WARNING: Agent 3 (Community) failed or timed out"; FAILED=$((FAILED+1)); }

echo ""
echo "============================================"
echo "All agents finished. Failures: $FAILED/3"
echo "============================================"
echo ""

# ---------------------------------------------------------------------------
# Show Results Summary
# ---------------------------------------------------------------------------
for file in github.md articles.md community.md; do
    filepath="${RESULTS_DIR}/${file}"
    if [[ -f "$filepath" ]] && [[ -s "$filepath" ]]; then
        bytes=$(wc -c < "$filepath")
        lines=$(wc -l < "$filepath")
        echo "✅ ${file}: ${lines} lines, ${bytes} bytes"
    else
        echo "❌ ${file}: EMPTY or missing"
        errfile="${RESULTS_DIR}/${file%.md}.err"
        if [[ -f "$errfile" ]] && [[ -s "$errfile" ]]; then
            echo "   Error log (first 10 lines):"
            head -10 "$errfile" | sed 's/^/   /'
        fi
    fi
done

# Show any non-empty error logs even for successful agents
echo ""
echo "--- Error/Warning Logs ---"
for errfile in "${RESULTS_DIR}"/*.err; do
    if [[ -f "$errfile" ]] && [[ -s "$errfile" ]]; then
        echo "$(basename "$errfile"):"
        head -5 "$errfile" | sed 's/^/  /'
        echo ""
    fi
done

echo ""
echo "Results saved to: $RESULTS_DIR/"
echo ""
echo "============================================"
echo "NEXT STEP: Synthesize results"
echo "============================================"
echo ""
echo "Run this to combine all findings into an actionable plan:"
echo ""
echo "  cat ${RESULTS_DIR}/github.md ${RESULTS_DIR}/articles.md ${RESULTS_DIR}/community.md | \\"
echo "  CLAUDECODE= claude -p \\"
echo "    'Synthesize these 3 research reports into a single actionable compression plan for ~/.claude/ memory files (currently 54K tokens across 23 files). Produce:"
echo "    1. Ranked techniques by expected token savings"
echo "    2. Specific implementation steps for each technique"
echo "    3. Risk assessment (what might break)"
echo "    4. Recommended compression order (which files to tackle first)"
echo "    5. Expected total savings estimate' \\"
echo "    --model sonnet --dangerously-skip-permissions --no-session-persistence"
