# SuperClaude Diagnostic Reference Guide

## Overview

This guide provides procedures for diagnosing issues with SuperClaude context files and configurations. Since SuperClaude is a collection of text files (not running software), diagnostics focus on file verification and configuration checking.

**Important**: There are no processes to monitor, no performance metrics to measure, and no system resources to analyze. SuperClaude is purely configuration files that Claude Code reads.

## Quick Diagnostics

### One-Line Health Check

```bash
# Quick status check
ls ~/.claude/CLAUDE.md && echo "✅ SuperClaude installed" || echo "❌ Not installed"
```

### Basic Diagnostic Commands

```bash
# Check if SuperClaude is installed
python3 -m SuperClaude --version

# Count context files
find ~/.claude -name "*.md" -type f | wc -l
# Expected: 40+ files

# Check file sizes (context files should have content)
find ~/.claude -name "*.md" -type f -size 0
# Expected: No output (no empty files)

# Verify directory structure
tree -L 2 ~/.claude/
# Or without tree command:
ls -la ~/.claude/
```

## File System Diagnostics

### Context File Verification

```bash
#!/bin/bash
# Comprehensive context file check

echo "=== SuperClaude Context File Diagnostic ==="

# Define expected counts
EXPECTED_AGENTS=14
EXPECTED_COMMANDS=21
EXPECTED_MODES=6

# Count actual files
ACTUAL_AGENTS=$(ls ~/.claude/agents/*.md 2>/dev/null | wc -l)
ACTUAL_COMMANDS=$(ls ~/.claude/commands/*.md 2>/dev/null | wc -l)
ACTUAL_MODES=$(ls ~/.claude/modes/*.md 2>/dev/null | wc -l)

# Report findings
echo "Agents: $ACTUAL_AGENTS/$EXPECTED_AGENTS $([ $ACTUAL_AGENTS -ge $EXPECTED_AGENTS ] && echo ✅ || echo ⚠️)"
echo "Commands: $ACTUAL_COMMANDS/$EXPECTED_COMMANDS $([ $ACTUAL_COMMANDS -ge $EXPECTED_COMMANDS ] && echo ✅ || echo ⚠️)"
echo "Modes: $ACTUAL_MODES/$EXPECTED_MODES $([ $ACTUAL_MODES -ge $EXPECTED_MODES ] && echo ✅ || echo ⚠️)"

# Check core files
for file in CLAUDE.md FLAGS.md RULES.md PRINCIPLES.md; do
    if [ -f ~/.claude/$file ]; then
        SIZE=$(wc -c < ~/.claude/$file)
        echo "$file: $SIZE bytes ✅"
    else
        echo "$file: MISSING ❌"
    fi
done
```

### Import System Check

```bash
# Verify import statements in CLAUDE.md
echo "=== Import System Check ==="
if [ -f ~/.claude/CLAUDE.md ]; then
    echo "Imports found in CLAUDE.md:"
    grep "^@import" ~/.claude/CLAUDE.md
    
    # Count import statements
    IMPORT_COUNT=$(grep -c "^@import" ~/.claude/CLAUDE.md)
    echo "Total imports: $IMPORT_COUNT"
    
    if [ $IMPORT_COUNT -ge 5 ]; then
        echo "✅ Import system configured correctly"
    else
        echo "⚠️ Some imports may be missing"
    fi
else
    echo "❌ CLAUDE.md not found"
fi
```

## Configuration Diagnostics

### MCP Server Configuration Check

```bash
# Check MCP configuration
echo "=== MCP Configuration Diagnostic ==="

CONFIG_FILE=~/.claude.json

if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Configuration file exists"
    
    # Validate JSON syntax
    if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        echo "✅ Valid JSON syntax"
        
        # List configured servers
        echo "Configured MCP servers:"
        python3 -c "
import json
with open('$HOME/.claude.json') as f:
    config = json.load(f)
    if 'mcpServers' in config:
        for server in config['mcpServers']:
            print(f'  - {server}')
    else:
        print('  No servers configured')
        "
    else
        echo "❌ Invalid JSON syntax in $CONFIG_FILE"
    fi
else
    echo "⚠️ No MCP configuration file found"
    echo "  This is OK if you don't use MCP servers"
fi
```

### Permission Diagnostics

```bash
# Check file permissions
echo "=== File Permission Check ==="

# Check if files are readable
UNREADABLE_COUNT=0
for file in ~/.claude/**/*.md; do
    if [ ! -r "$file" ]; then
        echo "❌ Cannot read: $file"
        ((UNREADABLE_COUNT++))
    fi
done

if [ $UNREADABLE_COUNT -eq 0 ]; then
    echo "✅ All context files are readable"
else
    echo "⚠️ Found $UNREADABLE_COUNT unreadable files"
    echo "Fix with: chmod 644 ~/.claude/**/*.md"
fi

# Check directory permissions
for dir in ~/.claude ~/.claude/agents ~/.claude/commands ~/.claude/modes; do
    if [ -d "$dir" ]; then
        if [ -x "$dir" ]; then
            echo "✅ $dir is accessible"
        else
            echo "❌ $dir is not accessible"
        fi
    else
        echo "❌ $dir does not exist"
    fi
done
```

## Common Issue Diagnostics

### Issue: Commands Not Recognized

```bash
# Diagnose command issues
COMMAND="implement"  # Change to test different commands

echo "=== Diagnosing command: $COMMAND ==="

FILE=~/.claude/commands/$COMMAND.md

if [ -f "$FILE" ]; then
    echo "✅ Command file exists"
    
    # Check file size
    SIZE=$(wc -c < "$FILE")
    if [ $SIZE -gt 100 ]; then
        echo "✅ File has content ($SIZE bytes)"
    else
        echo "⚠️ File seems too small ($SIZE bytes)"
    fi
    
    # Check for metadata
    if head -10 "$FILE" | grep -q "^---"; then
        echo "✅ Has metadata header"
    else
        echo "⚠️ Missing metadata header"
    fi
    
    # Check for command pattern
    if grep -q "/sc:$COMMAND" "$FILE"; then
        echo "✅ Contains command pattern"
    else
        echo "⚠️ Missing command pattern"
    fi
else
    echo "❌ Command file not found: $FILE"
    echo "Available commands:"
    ls ~/.claude/commands/ | sed 's/.md$//'
fi
```

### Issue: Agent Not Activating

```bash
# Diagnose agent issues
AGENT="python-expert"  # Change to test different agents

echo "=== Diagnosing agent: $AGENT ==="

FILE=~/.claude/agents/$AGENT.md

if [ -f "$FILE" ]; then
    echo "✅ Agent file exists"
    
    # Check for trigger keywords
    echo "Trigger keywords found:"
    grep -A 5 "## Triggers" "$FILE" | tail -n +2
    
    # Check for metadata
    if head -10 "$FILE" | grep -q "^name:"; then
        echo "✅ Has metadata"
    else
        echo "⚠️ Missing metadata"
    fi
else
    echo "❌ Agent file not found: $FILE"
    echo "Available agents:"
    ls ~/.claude/agents/ | sed 's/.md$//'
fi
```

## Installation Repair

### Quick Fix Script

```bash
#!/bin/bash
# SuperClaude Quick Fix Script

echo "=== SuperClaude Quick Fix ==="

# Check for common issues and fix them
ISSUES_FOUND=0

# Fix permissions
echo "Fixing file permissions..."
chmod 644 ~/.claude/*.md 2>/dev/null
chmod 644 ~/.claude/**/*.md 2>/dev/null
chmod 755 ~/.claude ~/.claude/agents ~/.claude/commands ~/.claude/modes 2>/dev/null

# Check for missing directories
for dir in agents commands modes; do
    if [ ! -d ~/.claude/$dir ]; then
        echo "⚠️ Missing directory: $dir"
        echo "  Run: SuperClaude install --components $dir"
        ((ISSUES_FOUND++))
    fi
done

# Check for empty files
EMPTY_FILES=$(find ~/.claude -name "*.md" -type f -size 0 2>/dev/null)
if [ -n "$EMPTY_FILES" ]; then
    echo "⚠️ Found empty files:"
    echo "$EMPTY_FILES"
    echo "  Run: SuperClaude install --force"
    ((ISSUES_FOUND++))
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No issues found"
else
    echo "Found $ISSUES_FOUND issues - see recommendations above"
fi
```

### Complete Reinstallation

```bash
# Complete clean reinstall
echo "=== Clean Reinstall ==="

# Backup current installation
BACKUP_DIR=~/.claude.backup.$(date +%Y%m%d_%H%M%S)
if [ -d ~/.claude ]; then
    cp -r ~/.claude "$BACKUP_DIR"
    echo "✅ Backed up to $BACKUP_DIR"
fi

# Remove current installation
rm -rf ~/.claude

# Reinstall
SuperClaude install

# Verify installation
if [ -f ~/.claude/CLAUDE.md ]; then
    echo "✅ Reinstallation successful"
else
    echo "❌ Reinstallation failed"
    echo "Restoring backup..."
    cp -r "$BACKUP_DIR" ~/.claude
fi
```

## What These Diagnostics DON'T Do

### Not Applicable Concepts

- **CPU/Memory Monitoring**: No processes to monitor
- **Performance Metrics**: No code execution to measure
- **Network Analysis**: No network operations (except MCP)
- **Process Management**: No running processes
- **Resource Optimization**: No resources consumed
- **Execution Timing**: No code executes

### Focus on What Matters

- **File Presence**: Are context files installed?
- **File Integrity**: Are files readable and complete?
- **Configuration Validity**: Is JSON syntax correct?
- **Directory Structure**: Is organization correct?
- **Permissions**: Can Claude Code read the files?

## Summary

SuperClaude diagnostics are simple: verify files exist, check they're readable, and ensure configurations are valid. Since it's just text files that Claude Code reads, there's no complex system monitoring or performance analysis needed. If files are present and readable, SuperClaude is working.