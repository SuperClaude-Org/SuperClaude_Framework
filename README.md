# Meet SuperClaude – The Missing Power-Up for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/NomenAK/SuperClaude)
[![GitHub issues](https://img.shields.io/github/issues/NomenAK/SuperClaude)](https://github.com/NomenAK/SuperClaude/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/NomenAK/SuperClaude/blob/master/CONTRIBUTING.md)

**A lightweight framework that transforms generic Claude Code into your specialized development partner – no external tools, no complex setup, just pure configuration magic.**

> **New in v4.0.0**: Template reference system achieves 65% efficiency gains with @pattern includes and validation system

## 🎯 The Problem

Claude Code is powerful, but let's be honest – it's generic. You find yourself:
- Losing context mid-debugging session
- Repeating the same instructions every project
- Wishing it understood YOUR coding style
- Watching tokens vanish on verbose responses

## ✨ Enter SuperClaude

Think of it as a brain upgrade for Claude Code. Drop it in once, and suddenly Claude:
- **Remembers everything** with Git-based checkpoints
- **Thinks like you want** with 9 specialized personas
- **Works 65% more efficiently** with @pattern template system (v4.0.0)
- **Never guesses** – always finds the official docs first

## 🚀 Zero-Friction Install

```bash
git clone https://github.com/NomenAK/SuperClaude.git
cd SuperClaude
./install.sh                           # Default: ~/.claude/
# OR
./install.sh --dir /opt/claude          # Custom location
./install.sh --dir ./project-claude    # Project-specific
```

That's it. No databases, no services, no dependencies. Installs to `~/.claude/` by default or any directory you choose. The installer even backs up your existing config automatically!

## 💡 Why You'll Love It

### 🔄 **Never Lose Context Again**
Git-integrated checkpoint system lets you jump back to any point in your conversation. Debugging a nasty bug at 3am? Create a checkpoint. Need to try a different approach? Roll back and branch off.

### 📚 **Smart Documentation That Evolves**
Your docs write themselves using our token-optimized templates. Project docs go in `/docs`, while Claude's working notes live in `/.claudedocs`. Everything stays organized, nothing gets lost.

### 🎭 **9 Instant Personas**
Switch Claude's entire mindset with one command:

```bash
/persona:architect    # Big-picture system design mode
/persona:frontend     # Pixel-perfect UI obsession mode
/persona:security     # Paranoid threat-modeling mode
/persona:analyzer     # Sherlock Holmes debugging mode
```

Each persona thinks differently, asks different questions, and solves problems their own way.

### ⚡ **18 Power Commands**
Real shortcuts for real work:

```bash
/build --react --magic   # Spin up a React app with AI-generated components
/troubleshoot --prod     # Production fire? This knows what to do
/analyze --security      # Full security audit in seconds
/git --checkpoint        # Save your progress before that risky refactor
/spawn --task "debug"    # Launch specialized debugging agent
```

### 🧠 **Actually Intelligent Integration**
- **Context7** finds library docs instantly (no more "I think this is how it works")
- **Sequential** thinking for complex problems (watch it reason step-by-step)
- **Magic** generates UI components that actually match your style
- **Puppeteer** tests everything in a real browser

### 🚄 **70% More Efficient**
Our UltraCompressed mode strips unnecessary tokens without losing clarity. Plus, the new @pattern template system eliminates command duplication. More context, longer conversations, bigger projects – same token budget.

## 🎮 Quick Start Examples

### The "New Project" Flow
```bash
/persona:architect
/design --api --ddd     # Domain-driven design from the start
/estimate --detailed    # Know what you're getting into
/persona:backend
/build --api --tdd      # Build it right the first time
```

### The "Something's Broken" Flow
```bash
/persona:analyzer
/troubleshoot --investigate --prod
/analyze --profile      # Find the real bottleneck
/persona:performance
/improve --performance --threshold 90%
```

### The "Make It Pretty" Flow
```bash
/persona:frontend
/build --react --magic  # AI-generated components
/test --e2e --pup       # See it work in a real browser
/improve --quality      # Polish until it shines
```

## 🔧 How It Actually Works

SuperClaude is pure configuration – no code, no external dependencies. It works by:

1. **Loading specialized instructions** when Claude Code starts
2. **Activating different rulesets** based on your commands
3. **Switching cognitive modes** through personas
4. **Optimizing token usage** with @pattern templates & UltraCompressed mode

The framework includes:
- **CLAUDE.md** – Core configuration and behaviors
- **RULES.md** – Engineering standards and practices
- **PERSONAS.md** – 9 specialized thinking modes
- **MCP.md** – Smart tool orchestration
- **18 Commands** – Ready-made workflows
- **25 Shared Resources** – Battle-tested patterns

## 🎨 Pick Your Fighter (Persona)

| Persona | Superpower | Activate When You Need... |
|---------|------------|---------------------------|
| **architect** | Sees the big picture | System design that scales |
| **frontend** | UX perfectionist | Interfaces users love |
| **backend** | Performance obsessed | APIs that never fail |
| **security** | Professional paranoid | Code that's bulletproof |
| **analyzer** | Root cause detective | To solve the unsolvable |
| **qa** | Bug hunter supreme | Testing that catches everything |
| **performance** | Speed demon | Every millisecond to count |
| **refactorer** | Code beautifier | To simplify the complex |
| **mentor** | Patient teacher | To understand, not just copy |

## 🛠️ Advanced Features

### Thinking Modes
Control how deep Claude analyzes:
```bash
"think about X"              # Standard analysis
"think hard about Y"         # Architecture-level depth
"ultrathink Z"               # When you need EVERYTHING considered
```

### Smart Tool Control
```bash
--c7           # Force documentation lookup
--seq          # Force step-by-step reasoning
--magic        # Force UI component generation
--no-mcp       # Use only native tools
--all-mcp      # Kitchen sink mode
```

### Evidence-Based Everything
No more "this is better" without proof. SuperClaude enforces:
- Metrics for performance claims
- Documentation for library usage (Context7 integration)
- Test results for quality assertions
- Security scans for safety claims
- Research-first methodology for external libraries
- Template reference validation system ensures integrity

## 🤝 Community-Driven Development

SuperClaude is MIT-licensed and built by developers, for developers. We welcome:
- New personas for specialized workflows
- Commands that solve your daily pain points
- Patterns that make Claude Code smarter
- Ideas that push the boundaries

Check out our [Contributing Guide](CONTRIBUTING.md) and join the conversation!

## 📊 What Makes It Different?

| Feature | Without SuperClaude | With SuperClaude |
|---------|-------------------|------------------|
| **Context** | Lost after errors | Git checkpoints preserve everything |
| **Personas** | Generic responses | Specialized thinking modes |
| **Tokens** | Verbose outputs | 65-70% reduction, same information |
| **Docs** | "I think this works" | Always finds official sources |
| **Workflows** | Repeat instructions | One command, complete flow |
| **Quality** | Hope for the best | Evidence-based standards |
| **Templates** | Copy-paste commands | @pattern system eliminates duplication |

## 🔮 Coming Soon

- VS Code extension for deeper integration
- Persona marketplace for community contributions
- Team sync for shared configurations
- Analytics dashboard (privacy-first)

## 💬 Real Developer Stories

> "I was debugging a production issue at 2am. Created a checkpoint, tried three different approaches, rolled back to the one that worked. Saved my sanity." – *Backend Dev*

> "The frontend persona just *gets* UX. It asks questions I didn't even think of." – *Full-Stack Dev*

> "65-70% token reduction means I can keep entire codebases in context. The @pattern system is brilliant." – *Tech Lead*

## 🎯 Is SuperClaude For You?

Perfect if you:
- ✅ Want consistent AI assistance across projects
- ✅ Value evidence over opinions
- ✅ Need specialized thinking modes
- ✅ Care about token efficiency
- ✅ Like tools that just work

Skip if you:
- ❌ Prefer completely manual control
- ❌ Don't use Claude Code regularly
- ❌ Happy with generic AI responses

## 🚦 Get Started in 2 Minutes

1. **Install**
   ```bash
   git clone https://github.com/NomenAK/SuperClaude.git && cd SuperClaude && ./install.sh
   # Or custom location: ./install.sh --dir /your/path
   ```

2. **Test Drive**
   ```bash
   /analyze --code        # See what it finds
   /persona:architect          # Try a new mindset
   ```

3. **Go Deeper**
   - Explore commands: `/load`
   - Read the guides: `~/.claude/commands/`
   - Join the community: [Discussions](https://github.com/NomenAK/SuperClaude/discussions)

## 🛟 Need Help?

- **Installation issues?** Run `./install.sh` again – it's idempotent. Use `./install.sh --help` for options
- **Commands not working?** Check `ls ~/.claude/commands/`
- **Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Found a bug?** [Open an issue](https://github.com/NomenAK/SuperClaude/issues)

## 🎉 Join the Revolution

SuperClaude isn't just a tool – it's a movement to make AI assistance actually useful for real developers. Every persona added, every command refined, every pattern shared makes Claude Code better for everyone.

**What would make YOUR workflow better? Let's build it together.**

---

*SuperClaude v4.0.0 – Because generic AI assistance isn't good enough anymore.*

[⭐ Star us on GitHub](https://github.com/NomenAK/SuperClaude) | [💬 Join the Discussion](https://github.com/NomenAK/SuperClaude/discussions) | [🐛 Report an Issue](https://github.com/NomenAK/SuperClaude/issues)