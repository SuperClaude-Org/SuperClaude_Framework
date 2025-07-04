**Purpose**: YOLO merge - Automatic commit, PR creation, and merge without approval

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. NO --plan (bypasses safety checks)
Legend: Generated based on symbols used in command
Purpose: "[YOLO][Git] Automatic complete merge workflow in $ARGUMENTS"

⚠️ **DANGER**: This command bypasses ALL safety checks and approval processes. Use only when you understand the risks.

Automatically commits all changes, creates a pull request, and merges it immediately without review or approval.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/yolo-merge "implement user authentication"` - Complete auto-merge with message
- `/yolo-merge --branch feature/auth --target main` - Custom branch and target
- `/yolo-merge --squash --delete-branch` - Squash commits and cleanup

YOLO merge workflow:
1. **Create feature branch** - Generate unique branch name if on main/master
2. **Stage all changes** - `git add .` (includes untracked files)
3. **Auto-commit** - Generate commit message from changes
4. **Push to remote** - Create tracking branch with `-u` flag
5. **Create PR** - Auto-generate title and description
6. **Auto-merge** - Immediately merge without approval
7. **Cleanup** - Delete feature branch and return to main

**--branch:** Specify source branch (default: auto-generated from main/master)
**--target:** Target branch for merge (default: main/master)
**--message:** Custom commit message (default: auto-generated)
**--squash:** Squash commits before merge | Cleaner history
**--delete-branch:** Delete source branch after merge | Automatic cleanup (default: true)
**--force:** Force push changes | Overwrites remote conflicts

⚠️ **SAFETY BYPASS**: 
- NO pre-commit hooks validation
- NO approval requirements 
- NO conflict resolution
- NO backup creation
- NO rollback preparation

Execution pattern:
```bash
# SAFETY CHECK: Verify this is a personal repository
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)
CURRENT_USER=$(gh auth status 2>&1 | grep -o "Logged in to github.com account [^[:space:]]*" | cut -d' ' -f6 2>/dev/null)

if [ "$REPO_OWNER" != "$CURRENT_USER" ] || [ -z "$REPO_OWNER" ] || [ -z "$CURRENT_USER" ]; then
    echo "❌ ERROR: yolo-merge can only be used in your personal repositories"
    echo "Current repository owner: $REPO_OWNER"
    echo "Current authenticated user: $CURRENT_USER"
    echo "This command is restricted to personal repositories for safety"
    exit 1
fi

echo "✅ Personal repository confirmed: $REPO_OWNER"

# Determine target branch (main or master)
TARGET_BRANCH=${TARGET_BRANCH:-$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")}

# Generate unique branch name if on main/master
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    SOURCE_BRANCH=${BRANCH:-"yolo-merge-$(date +%s)"}
    echo "🌟 Creating feature branch: $SOURCE_BRANCH"
    git checkout -b "$SOURCE_BRANCH"
else
    SOURCE_BRANCH=${BRANCH:-$CURRENT_BRANCH}
    echo "🌟 Using existing branch: $SOURCE_BRANCH"
fi

# Stage everything
git add .

# Commit with auto-generated or custom message
git commit -m "${COMMIT_MESSAGE}" --no-verify

# Push to remote (create tracking branch if needed)
git push -u origin "$SOURCE_BRANCH"

# Create PR using GitHub CLI
gh pr create --title "${PR_TITLE}" --body "${PR_BODY}" --head "$SOURCE_BRANCH" --base "$TARGET_BRANCH"

# Merge the PR (with squash and branch deletion as configured)
gh pr merge --squash --delete-branch

# Return to target branch and pull updates
git checkout "$TARGET_BRANCH"
git pull origin "$TARGET_BRANCH"
```

**Auto-generated content:**
- **Commit message**: Analyze git diff for meaningful description
- **PR title**: Extract main feature/fix from changes  
- **PR description**: Include change summary and modified files list

**Risk factors addressed:**
- Merge conflicts: Aborted with error (no resolution attempt)
- Missing approvals: Bypassed completely
- Failed CI/CD: Ignored (merge proceeds)
- Protected branches: May fail (command doesn't override branch protection)

@include shared/execution-patterns.yml#Git_Integration_Patterns

@include shared/universal-constants.yml#Standard_Messages_Templates

---

**⚠️ USE WITH EXTREME CAUTION**: This command is designed for personal repositories only. It includes safety checks to prevent usage in organizational repositories.

**Safety Restrictions:**
- **Personal Repository Only**: Command verifies the repository owner matches the authenticated GitHub user
- **Organizational Protection**: Automatically fails if run in any organizational repository
- **Authentication Required**: Requires GitHub CLI authentication to verify ownership
- **No Hardcoded Users**: Uses dynamic authentication check for portability

**Error Conditions:**
- Repository owner doesn't match authenticated user
- GitHub CLI not authenticated
- Repository owner cannot be determined
- Any organizational repository (even if you have admin access)

This command is designed for personal repositories, rapid prototyping, or emergency deployments where normal approval processes are unnecessary or counterproductive. Never use on production repositories with team collaboration.