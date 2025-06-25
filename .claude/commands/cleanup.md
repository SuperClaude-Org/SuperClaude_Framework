# Project Maintenance & Organization

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

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

@include shared/command-templates.yml#Research_Requirements

@include shared/command-templates.yml#Report_Output
- Space savings: `.claudedocs/metrics/cleanup-savings-<timestamp>.md`
- Ensure dirs: `mkdir -p .claudedocs/reports/ .claudedocs/metrics/`
- Include location: "📄 Cleanup report saved to: [path]"

Deliverables: Cleanup report w/ space saved, perf improvements, maintenance recommendations, safety analysis & cleanup strategy docs.