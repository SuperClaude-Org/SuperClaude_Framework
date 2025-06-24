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

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Cleanup project files, dependencies & artifacts in $ARGUMENTS.

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


```yaml
Mandatory_Research_Flows:
  External_Library_Research:
    Step_1: "Identify library/framework mentioned"
    Step_2: "Context7 lookup for official documentation"
    Step_3: "Verify API patterns and examples"
    Step_4: "Check version compatibility"
    Step_5: "Document findings in implementation"
    
  Pattern_Research:
    Step_1: "Search existing codebase for similar patterns"
    Step_2: "Magic component search if UI-related"
    Step_3: "WebSearch for official documentation"
    Step_4: "Validate approach with Sequential thinking"
    Step_5: "Document pattern choice rationale"
    
  API_Integration_Research:
    Step_1: "Official documentation lookup"
    Step_2: "Authentication requirements"
    Step_3: "Rate limiting and error handling"
    Step_4: "SDK availability and examples"
    Step_5: "Integration testing approach"
```


```yaml
Standard_Notifications:
  Operation_Start: "▶ Starting {operation}"
  Operation_Complete: "✅ {operation} completed successfully"
  File_Created: "📝 Created: {file_path}"
  File_Updated: "✏ Updated: {file_path}"
  Report_Generated: "📄 Report saved to: {path}"
  Error_Occurred: "❌ {operation} failed: {reason}"
  Warning_Issued: "⚠ {warning_message}"
  Info_Message: "ℹ {information}"

Output_Notifications:
  Success_Format: "✅ {operation} completed in {duration}"
  Error_Format: "❌ {operation} failed: {error_details}"
  Warning_Format: "⚠ {warning}: {details}"
  Info_Format: "ℹ {message}"
  Progress_Format: "🔄 {operation}: {current}/{total} ({percentage}%)"
```
- Space savings: `.claudedocs/metrics/cleanup-savings-<timestamp>.md`
- Ensure dirs: `mkdir -p .claudedocs/reports/ .claudedocs/metrics/`
- Include location: "📄 Cleanup report saved to: [path]"

Deliverables: Cleanup report w/ space saved, perf improvements, maintenance recommendations, safety analysis & cleanup strategy docs.
