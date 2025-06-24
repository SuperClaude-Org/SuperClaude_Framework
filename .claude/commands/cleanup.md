@include shared/universal-constants.yml#Universal_Legend

## Command Execution
@include shared/command-structure.yml#Base_Execution

Cleanup project files, dependencies & artifacts in $ARGUMENTS.

@include shared/flag-inheritance.yml#Universal_Always

Clean up project artifacts, code & cfg specified in $ARGUMENTS.

--code flag:
- Remove unused imports & dead code | Clean console.log & debug code
- Remove commented blocks | Fix style inconsistencies | Remove TODO>30 days

--files flag:
- Remove build artifacts & temp files | Clean node_modules if corrupted
- Remove logs & cache dirs | Clean test outputs | Remove OS files (.DS_Store, thumbs.db)

--deps flag:
- Remove unused deps from package.json | Update vulnerable deps
- Clean duplicate deps | Optimize dep tree | Check outdated packages

--git flag:
- Remove untracked files (w/ confirmation) | Clean merged branches
- Remove large/unwanted files from history | Optimize git (.git/objects cleanup) | Clean stale refs

--cfg flag:
- Remove deprecated cfg settings | Clean unused env vars
- Update outdated cfg formats | Validate cfg consistency | Remove duplicate entries

--all flag:
- Comprehensive cleanup all areas | Generate detailed report
- Suggest maintenance schedule | Provide perf impact analysis

--dry-run flag:
- Show what would be cleaned w/o changes | Estimate space savings & perf impact | ID risks before cleanup

--watch flag:
- Monitor & auto-clean new artifacts | Continuous cleanup during dev | Prevent temp file accumulation | Real-time maintenance

## Integration & Best Practices

@include shared/research-patterns.yml#Mandatory_Research_Flows

@include shared/user-experience.yml#Standard_Notifications
- Space savings: `.claudedocs/metrics/cleanup-savings-<timestamp>.md`
- Ensure dirs: `mkdir -p .claudedocs/reports/ .claudedocs/metrics/`
- Include location: "📄 Cleanup report saved to: [path]"

Deliverables: Cleanup report w/ space saved, perf improvements, maintenance recommendations, safety analysis & cleanup strategy docs.