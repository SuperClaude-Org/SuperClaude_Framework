# CLAUDE.md - SuperClaude Cfg

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | docs | documentation |
| > | greater than | | ops | operations |

@RULES.md
@MCP.md
@PERSONAS.md

## Core Cfg

```yaml
Philosophy: Code>docs | Simple→complex | Security first
Communication: Concise format | Symbols: →|&:» | Bullets>prose
Workflow: TodoRead()→TodoWrite(3+)→Execute | Update immediate
Stack: React|TS|Vite + Node|Express|PostgreSQL + Git|ESLint|Jest
Commands: /<command> [flags] | /task:<action> | Ex: /build --init
```

## Thinking Modes

```yaml
Activation: Natural language OR command flags
Flags: --think | --think-hard | --ultrathink
none: Single file|Basic | think: Multi-file|Standard
think hard: Architecture|Complex | ultrathink: Redesign|Critical
Examples: /analyze --code --think | /design --api --ultrathink
```

## Token Economy

```yaml
Targets: Minimal commands | Concise responses | Concise docs
Symbols: →(leads to) |(separator) &(combine) :(define) »(sequence)
Remove: the|a|very|really|that|which | "in order to"→to | and→&
```

## UltraCompressed Mode

```yaml
Purpose: Substantial token reduction | Telegram-style docs | Symbols & abbrevs
Activation: --uc flag | Natural language | Auto when context usage high
Rules: shared/ultracompressed.yml | Remove filler | Use symbols
Output: Direct info only | No intros/outros | Lists>prose
Legend: Auto-generate | Used symbols/abbrevs only | Start of docs
```

## Code Economy

```yaml
Generation: No comments | Short names | No boilerplate
Documentation: Only on request | Bullets>prose | Essential facts only
Patterns: Destructure | Chain | Ternary | Arrow functions
Output: Code only | No explanation unless asked
```

## Cost Optimization

```yaml
Models: Simple→sonnet | Complex→sonnet-4 | Critical→opus-4
MCP: C7 progressive loading | Seq adaptive thinking | Batch similar
Efficiency: Min tokens | Cache results | Batch ops
```

## Auto-Activation

```yaml
Files: *.tsx→frontend | *.sql→data | Docker→devops | *.test→qa
Keywords: bug|error→debugger | optimize→performance | secure→security
Context: TypeError→trace | Module error→deps | Permission→security
Tasks: Auto-detect complexity→seamless task creation | ./claudedocs/tasks/in-progress→auto-resume
```

## Task Management

```yaml
Mode: Automatic | No user prompts | Seamless activation
Detection: High complexity→auto-create | Medium complexity→brief notify | Low complexity→normal
Triggers: "build|create|implement" + "system|feature" + complexity flags
Flow: requirement→analyze→create→breakdown→implement | Background operation
Recovery: Auto-resume active tasks | Context preservation | Git integration
```

## Performance

```yaml
Ops: Parallel>sequential | Batch similar | One in-progress
```

---
*SuperClaude v4.0.0 | Critical load order | Internal Claude cfg*