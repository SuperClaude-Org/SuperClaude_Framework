**Purpose**: Project cleanup and maintenance

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Cleanup project files, dependencies & artifacts in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Examples:
- `/cleanup --code --dry-run` - Preview code cleanup changes
- `/cleanup --deps --all` - Remove unused dependencies
- `/cleanup --files --watch` - Continuous file cleanup

Cleanup modes:

**--code:** Remove unused imports & dead code | Clean console.log & debug code | Remove commented blocks | Fix style inconsistencies | Remove TODO>30 days

**--files:** Remove build artifacts & temp files | Clean node_modules if corrupted | Remove logs & cache dirs | Clean test outputs | Remove OS files (.DS_Store, thumbs.db)

**--deps:** Remove unused deps from package.json | Update vulnerable deps | Clean duplicate deps | Optimize dep tree | Check outdated packages

**--git:** Remove untracked files (w/ confirmation) | Clean merged branches | Remove large/unwanted files from history | Optimize git (.git/objects cleanup) | Clean stale refs

**--cfg:** Remove deprecated cfg settings | Clean unused env vars | Update outdated cfg formats | Validate cfg consistency | Remove duplicate entries

**--all:** Comprehensive cleanup all areas | Generate detailed report | Suggest maintenance schedule | Provide perf impact analysis

**--dry-run:** Show what would be cleaned w/o changes | Estimate space savings & perf impact | ID risks before cleanup

**--watch:** Monitor & auto-clean new artifacts | Continuous cleanup during dev | Prevent temp file accumulation | Real-time maintenance

## Integration & Best Practices

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/docs-patterns.yml#Standard_Notifications

@include shared/universal-constants.yml#Standard_Messages_Templates