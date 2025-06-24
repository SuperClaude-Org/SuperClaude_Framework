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

Multi-dimensional analysis on code, arch, or problem in $ARGUMENTS.

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

Examples:
- `/analyze --code --think` - Code review w/ context
- `/analyze --arch --think-hard` - Deep arch analysis  
- `/analyze --security --ultrathink` - Comprehensive security audit

Analysis modes:

**--code:** Quality review→naming, structure, DRY, complexity | Bugs→null checks, boundaries, types | Security→injection, auth, validation | Perf→O(n²), N+1, memory

**--arch:** System design & patterns | Layer coupling | Scalability bottlenecks | Maintainability assessment | Improvement suggestions

**--profile:** CPU, memory, execution time | Network latency, DB queries | Frontend metrics | Bottleneck identification | Optimization recommendations  

**--security:** OWASP top 10 | Auth & authorization | Data handling & encryption | Attack vector identification

**--perf:** Bottleneck analysis | Algorithm complexity | DB queries & indexes | Caching strategies | Resource utilization

**--watch:** Continuous file monitoring | Real-time quality tracking | Auto re-analysis | Live metrics

**--interactive:** Guided exploration | Step-by-step fixes | Live improvement


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

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
