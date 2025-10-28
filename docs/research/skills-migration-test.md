# Skills Migration Test - PM Agent

**Date**: 2025-10-21
**Goal**: Verify zero-footprint Skills migration works

## Test Setup

### Before (Current State)
```
~/.claude/superclaude/agents/pm-agent.md  # 1,927 words ≈ 2,500 tokens
~/.claude/superclaude/modules/*.md        # Always loaded

Claude Code startup: Reads all files automatically
```

### After (Skills Migration)
```
~/.claude/skills/pm/
├── SKILL.md              # ~50 tokens (description only)
├── implementation.md     # ~2,500 tokens (loaded on /sc:pm)
└── modules/*.md          # Loaded with implementation

Claude Code startup: Reads SKILL.md only (if at all)
```

## Expected Results

### Startup Tokens
- Before: ~2,500 tokens (pm-agent.md always loaded)
- After: 0 tokens (skills not loaded at startup)
- **Savings**: 100%

### When Using /sc:pm
- Load skill description: ~50 tokens
- Load implementation: ~2,500 tokens
- **Total**: ~2,550 tokens (first time)
- **Subsequent**: Cached

### Net Benefit
- Sessions WITHOUT /sc:pm: 2,500 tokens saved
- Sessions WITH /sc:pm: 50 tokens overhead (2% increase)
- **Break-even**: If >2% of sessions don't use PM, net positive

## Test Procedure

### 1. Backup Current State
```bash
cp -r ~/.claude/superclaude ~/.claude/superclaude.backup
```

### 2. Create Skills Structure
```bash
mkdir -p ~/.claude/skills/pm
# Files already created:
# - SKILL.md (50 tokens)
# - implementation.md (2,500 tokens)
# - modules/*.md
```

### 3. Update Slash Command
```bash
# plugins/superclaude/commands/pm.md
# Updated to reference skill: pm
```

### 4. Test Execution
```bash
# Test 1: Startup without /sc:pm
# - Verify no PM agent loaded
# - Check token usage in system notification

# Test 2: Execute /sc:pm
# - Verify skill loads on-demand
# - Verify full functionality works
# - Check token usage increase

# Test 3: Multiple sessions
# - Verify caching works
# - No reload on subsequent uses
```

## Validation Checklist

- [ ] SKILL.md created (~50 tokens)
- [ ] implementation.md created (full content)
- [ ] modules/ copied to skill directory
- [ ] Slash command updated (skill: pm)
- [ ] Startup test: No PM agent loaded
- [ ] Execution test: /sc:pm loads skill
- [ ] Functionality test: All features work
- [ ] Token measurement: Confirm savings
- [ ] Cache test: Subsequent uses don't reload

## Success Criteria

✅ Startup tokens: 0 (PM not loaded)
✅ /sc:pm tokens: ~2,550 (description + implementation)
✅ Functionality: 100% preserved
✅ Token savings: >90% for non-PM sessions

## Rollback Plan

If skills migration fails:
```bash
# Restore backup
rm -rf ~/.claude/skills/pm
mv ~/.claude/superclaude.backup ~/.claude/superclaude

# Revert slash command
git checkout plugins/superclaude/commands/pm.md
```

## Next Steps

If successful:
1. Migrate remaining agents (task, research, etc.)
2. Migrate modes (orchestration, brainstorming, etc.)
3. Remove ~/.claude/superclaude/ entirely
4. Document Skills-based architecture
5. Update installation system
