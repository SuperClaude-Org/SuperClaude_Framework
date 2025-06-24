# /git - Manage git workflows and repository operations

## Legend
@include shared/universal-constants.yml#Universal_Legend

## Purpose
Manage comprehensive git workflows for repositories specified in $ARGUMENTS with safety checks and automation.

## Syntax
`/git [flags] [operation/message]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Operations

--commit flag:
- Stage appropriate files
- Generate meaningful commit message
- Include co-author attribution
- Follow conventional commits

--pr flag:
- Create pull request
- Generate PR description
- Set reviewers & labels
- Link related issues

--flow flag:
- feature: Feature branch workflow
- hotfix: Emergency fix workflow
- release: Release branch workflow
- gitflow: Full GitFlow model

## Git Workflows

Feature Development:
```bash
# Start new feature
/git --flow feature "user-authentication"

# Commit progress
/git --commit "Add login form validation"

# Create PR when ready
/git --pr --reviewers @team
```

Hotfix Process:
```bash
# Emergency fix
/git --flow hotfix "security-patch"

# Quick commit & PR
/git --commit --pr "Fix SQL injection vulnerability"
```

Release Management:
```bash
# Start release
/git --flow release "v2.0.0"

# Tag & merge
/git --tag --merge "Release version 2.0.0"
```

## Safety Features

Pre-commit Checks:
- Verify branch is up to date
- Run linters & formatters
- Execute test suite
- Check for secrets
- Validate commit message

Merge Protection:
- Require PR reviews
- Ensure CI passes
- Check branch policies
- Prevent force pushes
- Backup before risky ops

## Advanced Features

--interactive flag:
- Interactive staging (git add -p)
- Commit message editor
- Conflict resolution helper
- Cherry-pick assistance

--history flag:
- Clean up commit history
- Interactive rebase
- Squash related commits
- Reorder for clarity

--stats flag:
- Contribution analytics
- Code churn metrics
- Review turnaround time
- Branch lifetime stats

## Best Practices

Commits:
- Atomic, focused changes
- Present tense messages
- Reference issue numbers
- Co-author attribution
- Sign commits when required

Branches:
- Descriptive names
- Regular rebasing
- Clean before merging
- Delete after merge
- Protect main branches

## Examples

```bash
# Standard commit with message
/git --commit "Add user profile API endpoint"

# Create PR with reviewers
/git --pr --reviewers alice,bob --labels api,feature

# Interactive cleanup before PR
/git --history --interactive

# Full feature workflow
/git --flow feature "payment-integration" --think
```

## Deliverables

- Clean git history
- Meaningful commit messages
- Automated PR creation
- Branch management
- Workflow documentation