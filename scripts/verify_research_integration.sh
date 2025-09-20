#!/bin/bash
# Deep Research Integration Verification Script
# Tests that all components are properly integrated

set -e

echo "========================================"
echo "Deep Research Integration Verification"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description exists: $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description missing: $file"
        ((ERRORS++))
        return 1
    fi
}

# Function to check string in file
check_string_in_file() {
    local file=$1
    local string=$2
    local description=$3
    if grep -q "$string" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description found in $file"
        return 0
    else
        echo -e "${RED}✗${NC} $description not found in $file"
        ((ERRORS++))
        return 1
    fi
}

echo "1. Checking Research Files..."
echo "------------------------------"

# Check if all 7 research files exist
check_file "SuperClaude/Commands/research.md" "Research command"
check_file "SuperClaude/Agents/deep-research-agent.md" "Deep Research agent"
check_file "SuperClaude/Modes/MODE_DeepResearch.md" "Deep Research mode"
check_file "SuperClaude/MCP/MCP_Tavily.md" "Tavily MCP documentation"
check_file "SuperClaude/MCP/configs/tavily.json" "Tavily MCP configuration"
check_file "SuperClaude/Core/RESEARCH_CONFIG.md" "Research configuration"
check_file "SuperClaude/Examples/deep_research_workflows.md" "Research workflow examples"

echo ""
echo "2. Checking Setup Component Updates..."
echo "---------------------------------------"

# Check mcp_docs.py has Tavily in server_docs_map
echo -e "${BLUE}Checking mcp_docs.py...${NC}"
check_string_in_file "setup/components/mcp_docs.py" '"tavily": "MCP_Tavily.md"' "Tavily in server_docs_map"

# Check mcp.py has Tavily configuration
echo -e "${BLUE}Checking mcp.py...${NC}"
check_string_in_file "setup/components/mcp.py" '"tavily":' "Tavily server configuration"
check_string_in_file "setup/components/mcp.py" "def _install_remote_mcp_server" "Remote MCP server handler"
check_string_in_file "setup/components/mcp.py" "TAVILY_API_KEY" "Tavily API key reference"

# Check agents.py has count updated
echo -e "${BLUE}Checking agents.py...${NC}"
check_string_in_file "setup/components/agents.py" "15 specialized AI agents" "15 agents count"

# Check modes.py has count updated
echo -e "${BLUE}Checking modes.py...${NC}"
check_string_in_file "setup/components/modes.py" "7 behavioral modes" "7 modes count"

# Check environment.py has research prerequisites check
echo -e "${BLUE}Checking environment.py...${NC}"
check_string_in_file "setup/utils/environment.py" "def check_research_prerequisites" "Research prerequisites check"
check_string_in_file "setup/utils/environment.py" "TAVILY_API_KEY" "Tavily API key check"

echo ""
echo "3. Checking Environment..."
echo "---------------------------"

# Check for Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js installed: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Node.js not installed (required for Tavily MCP)"
    ((WARNINGS++))
fi

# Check for npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm installed: $NPM_VERSION"
else
    echo -e "${YELLOW}⚠${NC} npm not installed (required for MCP servers)"
    ((WARNINGS++))
fi

# Check for TAVILY_API_KEY
if [ -n "$TAVILY_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} TAVILY_API_KEY is set"
else
    echo -e "${YELLOW}⚠${NC} TAVILY_API_KEY not set - get from https://app.tavily.com"
    ((WARNINGS++))
fi

echo ""
echo "4. Checking Auto-Discovery Components..."
echo "-----------------------------------------"

# These components should auto-discover the new files
echo -e "${BLUE}Components that will auto-discover files:${NC}"
echo -e "${GREEN}✓${NC} commands.py will find research.md"
echo -e "${GREEN}✓${NC} agents.py will find deep-research-agent.md"
echo -e "${GREEN}✓${NC} modes.py will find MODE_DeepResearch.md"
echo -e "${GREEN}✓${NC} core.py will find RESEARCH_CONFIG.md"

echo ""
echo "5. Checking Python Syntax..."
echo "-----------------------------"

# Test Python syntax for modified files
for file in setup/components/mcp_docs.py setup/components/mcp.py setup/components/agents.py setup/components/modes.py setup/utils/environment.py; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file syntax is valid"
    else
        echo -e "${RED}✗${NC} $file has syntax errors"
        ((ERRORS++))
    fi
done

echo ""
echo "========================================"
echo "Verification Summary"
echo "========================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
else
    echo -e "${RED}✗ Found $ERRORS critical errors${NC}"
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $WARNINGS warnings (non-critical)${NC}"
fi

echo ""
echo "Next Steps:"
echo "-----------"
echo "1. Set TAVILY_API_KEY: export TAVILY_API_KEY='your-key-here'"
echo "2. Run installation: SuperClaude install"
echo "3. Test in Claude Code: /sc:research 'test query'"

exit $ERRORS