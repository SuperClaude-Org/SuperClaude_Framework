**Purpose**: Git workflow with checkpoint management

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Manage comprehensive git workflows for repositories specified in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/git --commit "Add user profile API endpoint"` - Standard commit w/ message
- `/git --pr --reviewers alice,bob --labels api,feature` - Create PR w/ reviewers
- `/git --flow feature "payment-integration" --think` - Full feature workflow

Git operations:

**--commit:** Stage appropriate files | Generate meaningful commit message | Include co-author attribution | Follow conventional commits

**--pr:** Create pull request | Generate PR description | Set reviewers & labels | Link related issues

**--flow:** Git workflow patterns
- feature: Feature branch workflow | hotfix: Emergency fix workflow
- release: Release branch workflow | gitflow: Full GitFlow model

@include shared/execution-patterns.yml#Git_Integration_Patterns

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates