# /git - Manage git workflows and repository operations

## Legend
| Symbol | Meaning | | Abbrev | Meaning |
|--------|---------|---|--------|---------|
| → | leads to | | cfg | configuration |
| & | and/with | | impl | implementation |
| w/ | with | | perf | performance |
| @ | at/located | | ops | operations |
| > | greater than | | val | validation |
| ∀ | for all/every | | req | requirements |
| ∃ | exists/there is | | deps | dependencies |
| ∴ | therefore | | env | environment |
| ∵ | because | | db | database |
| ≡ | equivalent | | api | interface |
| ≈ | approximately | | docs | documentation |
| 📁 | directory/path | | std | standard |
| 🔢 | number/count | | def | default |
| 📝 | text/string | | ctx | context |
| ⚙ | setting/config | | err | error |
| 🎛 | control/flags | | exec | execution |
| 🔧 | configuration | | qual | quality |
| 📋 | group/category | | rec | recovery |
| 🚨 | critical/urgent | | sev | severity |
| ⚠ | warning/caution | | resp | response |
| 🔄 | retry/recovery | | esc | escalation |
| ✅ | success/fixed | | tok | token |
| ❌ | failure/error | | opt | optimization |
| ℹ | information | | UX | user experience |
| ⚡ | fast/quick | | UI | user interface |
| 🐌 | slow/delayed | | C | critical |
| ✨ | complete/done | | H | high |
| 📖 | read operation | | M | medium |
| ✏ | edit operation | | L | low |
| 🗑 | delete operation | | |

## Purpose
Manage comprehensive git workflows for repositories specified in $ARGUMENTS with safety checks and automation.

## Syntax
`/git [flags] [operation/message]`

## Universal Flags
--plan: "Show execution plan before running"
--uc: "UltraCompressed mode (~70% token reduction)"
--ultracompressed: "Alias for --uc"
--think: "Multi-file analysis w/ context (4K tokens)"
--think-hard: "Deep architectural analysis (10K tokens)"
--ultrathink: "Critical system redesign (32K tokens)"
--c7: "Enable Context7→library documentation lookup"
--seq: "Enable Sequential→complex analysis & thinking"
--magic: "Enable Magic→UI component generation"
--pup: "Enable Puppeteer→browser automation & testing"
--all-mcp: "Enable all MCP servers"
--no-mcp: "Disable all MCP servers (native tools only)"
--no-c7: "Disable Context7 specifically"
--no-seq: "Disable Sequential thinking specifically"
--no-magic: "Disable Magic UI builder specifically"
--no-pup: "Disable Puppeteer specifically"
## Execution Control
--watch: "Continuous monitoring w/ real-time feedback"
--interactive: "Step-by-step guided process w/ user control"
--dry-run: "Preview changes without execution"
--force: "Override safety checks & confirmations"

## Command-Specific Flags

**Core Operations:**
- `--status`: Comprehensive repository status with branch and remote information
- `--commit [message]`: Create commit with automated staging and validation
- `--branch [name]`: Create, switch, or manage branches
- `--sync`: Fetch, pull, and push with conflict resolution
- `--merge [branch]`: Merge branches with conflict analysis
- `--stash [message]`: Stash management with descriptive messages

**Advanced Operations:**
- `--history`: Detailed commit history with filtering options
- `--checkpoint [message]`: Create tagged state snapshots for rollback
- `--rollback [checkpoint]`: Rollback to specific checkpoint safely
- `--rebase [branch]`: Interactive or automatic rebase operations

**Branch Management:**
- `--list`: Show all branches with descriptions and status
- `--delete [branch]`: Delete merged branches safely
- `--track [remote/branch]`: Set up branch tracking

**Safety & Validation:**
- `--verify`: Verify repository state and integrity
- `--cleanup`: Clean up stale branches and references
- `--backup`: Create backup before risky operations

## Examples
- `/git --status` → Comprehensive repository status
- `/git --commit "Add authentication feature"` → Create commit with message
- `/git --branch feature/ui-redesign` → Create and switch to branch
- `/git --sync --verify` → Sync with remote and verify state
- `/git --merge develop --think` → Merge with conflict analysis
- `/git --checkpoint "Before major refactor"` → Create safety checkpoint
- `/git --history --author "john" --since "2024-01-01"` → Filtered history

## Git Operations

**Status Operation (--status):**
- Working tree status and staged changes
- Current branch and upstream tracking
- Stashed changes with timestamps
- Recent commits (last 5) with summaries
- Unpushed commits count
- Remote repository status

**Commit Operation (--commit):**
- Automatic staging of modified files
- Generate conventional commit message if missing
- Pre-commit hooks and validation
- Test verification before commit
- Create automatic checkpoint
- GPG signing if configured

**Branch Management (--branch):**
- Create new branch from HEAD or specified base
- Switch to existing branch with safety checks
- Delete merged branches with verification
- List all branches with descriptions
- Automatic remote tracking setup
- Protection for main/master branches

**Sync Operations (--sync):**
- Fetch from all configured remotes
- Pull with rebase to maintain clean history
- Push to tracked remote branch
- Handle authentication automatically
- Resolve merge conflicts interactively
- Update submodules if present

**Merge Operations (--merge):**
- Fetch target branch before merging
- Analyze potential conflicts
- Create checkpoint before merge
- Use appropriate merge strategy
- Handle conflicts with interactive resolution
- Verify merge results

**Stash Management (--stash):**
- Save changes with descriptive message
- List stashes with timestamps and summaries
- Apply or pop specific stash entries
- Drop old or unnecessary stashes
- Handle conflicts during stash application

**History Operations (--history):**
- Formatted commit log with customizable output
- Filter by author, date, or file path
- Branch topology visualization
- Search commit messages
- File change statistics

**Checkpoint System (--checkpoint):**
- Create tagged state snapshots
- Store with descriptive messages
- Maintain checkpoint manifest
- Enable safe rollback operations
- Track checkpoint metadata

**Rollback Operations (--rollback):**
- List available checkpoints with details
- Verify rollback safety
- Create pre-rollback checkpoint
- Execute rollback with validation
- Verify final repository state

## Workflow Patterns

**Standard Development Workflow:**
1. Check status → Understand current state
2. Create checkpoint → Safety backup
3. Execute operation → Perform git action
4. Verify results → Validate changes
5. Sync with remote → Update shared repository

**Feature Development:**
1. `git --status` → Check current state
2. `git --branch feature/new-feature` → Create feature branch
3. Development work...
4. `git --commit "Implement feature"` → Commit changes
5. `git --sync` → Push to remote
6. `git --merge main` → Integrate with main

**Safe Operations:**
- Always create checkpoints before risky operations
- Verify repository state after major changes
- Use interactive mode for conflict resolution
- Maintain clean commit history with conventional messages

## Deliverables
- **Updated Repository State**: Clean, consistent git history
- **Branch Management**: Organized branch structure
- **Remote Synchronization**: Up-to-date remote repositories
- **Audit Trail**: Complete history of operations
- **Safety Checkpoints**: Rollback points for recovery

## Research Requirements
External_Library_Research:
  - Identify library/framework mentioned
  - Context7 lookup for official documentation
  - Verify API patterns and examples
  - Check version compatibility
  - Document findings in implementation
Pattern_Research:
  - Search existing codebase for similar patterns
  - Magic component search if UI-related
  - WebSearch for official documentation
  - Validate approach with Sequential thinking
  - Document pattern choice rationale
API_Integration_Research:
  - Official documentation lookup
  - Authentication requirements
  - Rate limiting and error handling
  - SDK availability and examples
  - Integration testing approach

## Lifecycle
Pre_Execution:
  Risk_Assessment: Calculate risk score 1-10 based on data loss potential, irreversibility, scope, security
  Environment_Validation: Check required tools, permissions, resources, dependencies
  State_Preparation: Create checkpoint before risky ops, cache previous results
During_Execution:
  Progress_Monitoring: Track operation progress, resource usage, error rates, token consumption
  Dynamic_Optimization: Adjust parallelism, switch strategies, cache results, fallback to native
  Error_Handling: Detect errors immediately, classify transient vs permanent, retry/fallback/halt
Post_Execution:
  Verification: Confirm expected outcomes achieved, no side effects, state consistent
  Cleanup: Remove temp files, locks, cached data; update audit logs, metrics, docs
  Reporting: Generate success/failure report, performance metrics, recommendations

## Integration Patterns

**Quality Assurance:**
- Pre-commit hooks for code quality
- Test verification before commits
- Conventional commit message enforcement
- Branch protection rules

**Team Collaboration:**
- Consistent branching strategies
- Merge request workflows
- Code review integration
- Conflict resolution procedures

## Troubleshooting
- **Merge Conflicts**: Use `--merge --interactive` for guided resolution
- **Complex History**: Apply `--history --visual` for topology understanding
- **Repository Issues**: Use `--verify --cleanup` for maintenance
- **Rollback Needs**: Apply `--rollback` with checkpoint selection

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}

