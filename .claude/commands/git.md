# Version Control Workflow Management

@include shared/command-templates.yml#Command_Header

Manage git workflows for repo in $ARGUMENTS.

@see shared/thinking-modes.yml ∀ thinking flags

Examples:
- `/user:git --status` - Comprehensive repo status
- `/user:git --commit "Add feature"` - Create commit
- `/user:git --branch feature/ui` - Create & switch→branch
- `/user:git --sync` - Fetch, pull & push
- `/user:git --merge develop --think` - Merge w/ conflict analysis

Git operations:

**--status:** Working tree status | Current branch & upstream | Stashed changes | Recent commits (5) | Unpushed commits | Remote status

**--commit:** Stage files (-a→all) | Generate message if missing | Follow conventions | Verify tests pass | Create chkpt | GPG sign if configured

**--branch:** Create from HEAD/base | Switch to existing | --delete→remove merged | --list→show all w/ descriptions | Auto-track remote | Protect current/main

**--sync:** Fetch all remotes | Pull w/ rebase | Push to tracked remote | Handle auth | Resolve conflicts | Update submodules

**--merge:** Fetch target branch | Check conflicts | Create chkpt | Use merge strategy | Handle conflicts interactively | Verify results

**--stash:** Save w/ message | List w/ timestamps | Apply/pop specific | Drop old/unnecessary | Handle conflicts

**--history:** Commit log w/ formats | Filter by author/date/path | Branch topology | Search messages | File change stats

**--checkpoint:** Tagged state snapshot | Descriptive message | Store in manifest | Enable rollback

**--rollback:** List available chkpts | Verify safety | Pre-rollback chkpt | Execute rollback | Verify state

@see shared/git-workflow.yml ∀ best practices
@see shared/checkpoint.yml ∀ checkpoint system
@see shared/error-handling.yml ∀ safety checks

Workflow: Check status→Create chkpt→Execute→Verify→Sync

Deliverables: Updated repo state, commit history, branch mgmt, remote sync.