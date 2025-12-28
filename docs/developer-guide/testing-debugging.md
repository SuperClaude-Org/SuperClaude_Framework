# SuperClaude Verification and Troubleshooting Guide

## Overview

This guide covers how to verify your SuperClaude installation and troubleshoot common issues with context files and configurations.

**Important**: SuperClaude is a collection of context files, not executable software. This guide focuses on verifying context files are properly installed and accessible to Claude Code.

## Table of Contents

1. [Installation Verification](#installation-verification)
2. [Context File Verification](#context-file-verification)
3. [MCP Server Verification](#mcp-server-verification)
4. [Common Issues](#common-issues)
5. [Troubleshooting Commands](#troubleshooting-commands)

## Installation Verification

### Check Installation Status

```bash
# Verify SuperClaude installation system is available
python3 -m SuperClaude --version
# Expected: SuperClaude Framework installation help

# Verify Claude Code CLI integration
claude --version
# Expected: Claude Code version info

# Check if context files were installed
ls ~/.claude/
# Expected: CLAUDE.md, FLAGS.md, RULES.md, agents/, commands/, modes/

# Verify main context file
head ~/.claude/CLAUDE.md
# Expected: Should show import statements
```

### Verify Directory Structure

```bash
# Check all directories exist
for dir in agents commands modes; do
    if [ -d ~/.claude/$dir ]; then
        echo "✅ $dir directory exists"
        ls ~/.claude/$dir | wc -l
    else
        echo "❌ $dir directory missing"
    fi
done
```

### Count Installed Components

```bash
# Should have 14 agents
ls ~/.claude/agents/*.md | wc -l

# Should have 21 commands  
ls ~/.claude/commands/*.md | wc -l

# Should have 5 modes
ls ~/.claude/modes/*.md | wc -l
```

## Context File Verification

### Verify Core Files

```bash
# Check core context files exist
for file in CLAUDE.md FLAGS.md RULES.md PRINCIPLES.md; do
    if [ -f ~/.claude/$file ]; then
        echo "✅ $file exists ($(wc -l < ~/.claude/$file) lines)"
    else
        echo "❌ $file missing"
    fi
done
```

### Verify Import System

```bash
# Check CLAUDE.md has correct imports
grep "@import" ~/.claude/CLAUDE.md
# Expected output:
# @import commands/*.md
# @import agents/*.md
# @import modes/*.md
# @import FLAGS.md
# @import RULES.md
# @import PRINCIPLES.md
```

### Check File Integrity

```bash
# Verify files are readable text files
file ~/.claude/CLAUDE.md
# Expected: ASCII text or UTF-8 text

# Check for corruption
for file in ~/.claude/**/*.md; do
    if file "$file" | grep -q "text"; then
        echo "✅ $file is valid text"
    else
        echo "❌ $file may be corrupted"
    fi
done
```

## MCP Server Verification

### Check MCP Configuration

```bash
# Verify .claude.json exists
if [ -f ~/.claude.json ]; then
    echo "✅ MCP configuration file exists"
    # Check which servers are configured
    grep -o '"[^"]*":' ~/.claude.json | grep -v mcpServers
else
    echo "❌ No MCP configuration found"
fi
```

### Test MCP Server Availability

```bash
# Check if Node.js is available (required for MCP)
node --version
# Expected: v16.0.0 or higher

# Check if npx is available
npx --version
# Expected: Version number

# Test Context7 MCP (if configured)
npx -y @upstash/context7-mcp@latest --help 2>/dev/null && echo "✅ Context7 available" || echo "❌ Context7 not available"
```

## Common Issues

### Issue: Commands Not Working

**Symptom**: `/sc:` context triggers don't produce expected Claude Code behavior

**Verification**:
```bash
# Check if command file exists
ls ~/.claude/commands/implement.md
# If missing, reinstall SuperClaude

# Verify file content
head -20 ~/.claude/commands/implement.md
# Should show command metadata and instructions
```

**Solution**:
```bash
# Reinstall commands component
PYTHONPATH=/path/to/SuperClaude_Framework python3 -m setup install --components commands --force
```

### Issue: Agents Not Activating

**Symptom**: `@agent-` invocations don't work in Claude Code

**Verification**:
```bash
# List all agents
ls ~/.claude/agents/

# Check specific agent
cat ~/.claude/agents/python-expert.md | head -20
```

**Solution**:
```bash
# Reinstall agents
PYTHONPATH=/path/to/SuperClaude_Framework python3 -m setup install --components agents --force
```

### Issue: Context Not Loading

**Symptom**: Claude Code doesn't seem to read SuperClaude context

**Verification**:
```bash
# Check CLAUDE.md is in correct location
ls -la ~/.claude/CLAUDE.md

# Verify Claude Code can access the directory
# In Claude Code, check if context is loading properly
```

**Solution**:
1. Restart Claude Code
2. Ensure you're in a project directory
3. Check file permissions: `chmod 644 ~/.claude/*.md`

### Issue: MCP Servers Not Working

**Symptom**: MCP features unavailable

**Verification**:
```bash
# Check Node.js installation
which node

# Verify .claude.json syntax
python3 -c "import json; json.load(open('$HOME/.claude.json'))" && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
```

**Solution**:
```bash
# Install Node.js if missing
# Ubuntu: sudo apt install nodejs npm
# macOS: brew install node
# Windows: Download from nodejs.org

# Fix JSON syntax if invalid
PYTHONPATH=/path/to/SuperClaude_Framework python3 -m setup install --components mcp --force
```

## Troubleshooting Commands

### Quick Diagnostic

```bash
#!/bin/bash
# SuperClaude Quick Diagnostic Script

echo "=== SuperClaude Diagnostic ==="
echo ""

# Check installation system
echo "1. Installation System:"
if command -v SuperClaude &> /dev/null; then
    echo "   ✅ SuperClaude installation available"
    python3 -m SuperClaude --version
else
    echo "   ❌ SuperClaude not found - install with: pipx install SuperClaude (or pip install SuperClaude)"
fi

# Check context files
echo ""
echo "2. Context Files:"
if [ -d ~/.claude ]; then
    echo "   ✅ ~/.claude directory exists"
    echo "   - Agents: $(ls ~/.claude/agents/*.md 2>/dev/null | wc -l)"
    echo "   - Commands: $(ls ~/.claude/commands/*.md 2>/dev/null | wc -l)"
    echo "   - Modes: $(ls ~/.claude/modes/*.md 2>/dev/null | wc -l)"
else
    echo "   ❌ ~/.claude directory not found"
fi

# Check MCP
echo ""
echo "3. MCP Configuration:"
if [ -f ~/.claude.json ]; then
    echo "   ✅ MCP configuration exists"
else
    echo "   ❌ No MCP configuration"
fi

# Check Node.js
echo ""
echo "4. Node.js (for MCP):"
if command -v node &> /dev/null; then
    echo "   ✅ Node.js installed: $(node --version)"
else
    echo "   ⚠️  Node.js not installed (optional, needed for MCP)"
fi

echo ""
echo "=== Diagnostic Complete ==="
```

### File Permission Fix

```bash
# Fix permissions on all context files
chmod 644 ~/.claude/*.md
chmod 644 ~/.claude/**/*.md
chmod 755 ~/.claude ~/.claude/agents ~/.claude/commands ~/.claude/modes
```

### Complete Reinstall

```bash
# Backup existing configuration
cp -r ~/.claude ~/.claude.backup.$(date +%Y%m%d)

# Remove existing installation
rm -rf ~/.claude

# Reinstall everything
PYTHONPATH=/path/to/SuperClaude_Framework python3 -m setup install

# Restore any customizations from backup if needed
```

## Important Notes

### What We're NOT Verifying

- **No Code Execution**: Context files don't execute, so no runtime verification needed
- **No Performance Metrics**: No code runs, so no performance to measure
- **No Unit Tests**: Context files are instructions, not functions
- **No Integration Tests**: Claude Code reads files; verification is behavioral

### What We ARE Verifying

- **File Presence**: Context files exist in correct locations
- **File Integrity**: Files are valid text and readable
- **Directory Structure**: Proper organization maintained
- **Configuration Validity**: JSON files are syntactically correct
- **Dependencies Available**: Node.js for MCP servers (optional)
- **Behavioral Testing**: Context files produce expected Claude Code behavior

## Summary

Verification for SuperClaude focuses on ensuring context files are properly installed and accessible to Claude Code. Since SuperClaude is not software but a configuration framework, verification centers on file presence, integrity, and behavioral testing in Claude Code conversations.