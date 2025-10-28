#!/bin/bash
# SuperClaude SessionStart initialization script
# Auto-executed when Claude Code session starts

# 1. Check git status
if git status --porcelain > /dev/null 2>&1; then
    status=$(git status --porcelain)
    if [ -z "$status" ]; then
        echo "📊 Git: clean"
    else
        count=$(echo "$status" | wc -l | tr -d ' ')
        echo "📊 Git: ${count} files"
    fi
else
    echo "📊 Git: not a repo"
fi

# 2. Remind token budget
echo "💡 Use /context to confirm token budget."

# 3. Report core services
echo ""
echo "🛠️ Core Services Available:"
echo "  ✅ Confidence Check (pre-implementation validation)"
echo "  ✅ Deep Research (web/MCP integration)"
echo "  ✅ Repository Index (token-efficient exploration)"
echo ""
echo "SC Agent ready — awaiting task assignment."

exit 0
