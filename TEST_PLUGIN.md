# PM Agent Plugin Performance Test

## Test Commands (Run in New Session)

```bash
/plugin marketplace add superclaude-local file:///Users/kazuki/github/superclaude/.claude-plugin
/plugin install pm-agent@superclaude-local
/context
/pm
/context
```

## Expected Results

### Token Usage Before Plugin
- System prompt: ~2.5k tokens
- Memory files: ~9k tokens
- Total: ~27k tokens

### Token Usage After Plugin Install
- Plugin metadata: ~50 tokens (plugin.json only)
- Skills NOT loaded until invoked
- Expected: Minimal increase

### Token Usage After /pm Execution
- Command definition: ~324 tokens
- Skills loaded on-demand: ~1,308 tokens
- Expected total increase: ~1,632 tokens

## Comparison with Old Implementation

### Old (/sc:pm slash command)
- Always loaded: ~324 tokens (command)
- Module references (@pm/modules/*): ~1,600 tokens
- Total overhead: ~1,924 tokens (always in memory)

### New (plugin)
- Lazy loading: 0 tokens until /pm invoked
- On-demand skills: ~1,632 tokens (only when needed)
- Savings: ~292 tokens + zero-footprint when not in use

## Success Criteria

✅ Plugin installs successfully
✅ /pm command available after installation
✅ Token usage increase <2k tokens on /pm invocation
✅ Skills load on-demand (not at session start)
