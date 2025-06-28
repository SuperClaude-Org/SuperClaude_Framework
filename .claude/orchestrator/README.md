# SuperClaude Orchestrator

## What is this? (ELI5 - Explain Like I'm 5)

Imagine you have a super smart robot helper (Claude) that can help you code, but you have to remember 19 different magic words to ask it to do different things. That's hard to remember!

This SuperClaude Orchestrator is like having a translator that lets you talk to your robot helper in normal words, and it figures out which magic words to use automatically.

**Instead of remembering:**
```
/review --files src/ --quality --evidence --persona-security --think --seq
```

**You can just say:**
```
"Check my code for security problems"
```

And it will automatically create the right magic command for you!

## What Files Do What?

This folder contains 8 special instruction files that work together:

1. **`README.md`** - This file! Explains what everything does
2. **`ORCHESTRATOR.md`** - The main translator that turns your words into commands
3. **`COMMAND_MAPPING.md`** - The dictionary that knows what each command does
4. **`FLAG_COMBINATIONS.md`** - The smart rules for making commands better
5. **`PERSONA_GUIDE.md`** - Info about 9 different expert helpers
6. **`WORKFLOW_TEMPLATES.md`** - Ready-made recipes for common tasks
7. **`INTEGRATION_GUIDE.md`** - Instructions on how to use everything
8. **`FILE_OVERVIEW.md`** - Shows how all the files work together

## How to Use This

### Step 1: Put Files in Your Project
Copy all the `.md` files into your SuperClaude project folder.

### Step 2: Tell Claude to Use the Orchestrator
In your Claude Code conversation, say:
```
Use the ORCHESTRATOR.md file to help translate my requests into SuperClaude commands.
```

### Step 3: Talk Normally
Instead of complex commands, just describe what you want:

- "Review my code for security issues" 
- "Build a React app with testing"
- "Optimize my database queries"
- "Create API documentation"

### Step 4: Get the Right Command
The orchestrator will give you the perfect SuperClaude command with all the right flags and settings.

## Quick Examples

| What You Say | What You Get |
|--------------|--------------|
| "Security review of my code" | `/review --security --evidence --persona-security --think` |
| "Build a new React feature" | `/build --react --feature --tdd --frontend` |
| "Fix performance problems" | `/improve --performance --profile --persona-performance` |
| "Deploy to production safely" | `/deploy --prod --critical --evidence --plan` |

## Why This Helps

✅ **No more memorizing** 19 commands and their flags  
✅ **Talk like a human** instead of learning robot language  
✅ **Get better results** with automatic smart flag combinations  
✅ **Save time** with pre-built workflows  
✅ **Make fewer mistakes** with built-in best practices  

## Installation

1. Fork the SuperClaude repository
2. Copy these markdown files to your project
3. Start using natural language with Claude Code
4. Let the orchestrator handle the complex commands

## Need Help?

- Read `INTEGRATION_GUIDE.md` for detailed setup instructions
- Check `WORKFLOW_TEMPLATES.md` for common development scenarios
- Look at `PERSONA_GUIDE.md` to understand the 9 expert helpers

Remember: This doesn't replace SuperClaude, it makes it easier to use!