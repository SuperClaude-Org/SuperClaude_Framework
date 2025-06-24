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

Build project/feature based on req in $ARGUMENTS.

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
- `/user:build --react --magic` - React app w/ UI gen
- `/user:build --api --c7` - API w/ docs
- `/user:build --react --magic --pup` - Build & test UI

Pre-build: Remove artifacts (dist/, build/, .next/) | Clean temp files & cache | Validate deps | Remove debug

Build modes:
**--init:** New project w/ stack (React|API|Fullstack|Mobile|CLI) | TS default | Testing setup | Git workflow
**--feature:** Impl feature→existing patterns | Maintain consistency | Include tests  
**--tdd:** Write failing tests→minimal code→pass tests→refactor

Templates:
- **React:** Vite|TS|Router|state mgmt|testing
- **API:** Express|TS|auth|validation|OpenAPI  
- **Fullstack:** React+Node.js+Docker
- **Mobile:** React Native+Expo
- **CLI:** Commander.js+cfg+testing

**--watch:** Continuous build | Real-time feedback | Incremental | Live reload
**--interactive:** Step-by-step cfg | Interactive deps | Build customization


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
Git_Workflows:
  Auto_Safety_Checks:
    Before_Commit:
      - "git status → Verify intended files"
      - "git diff --staged → Review changes"
      - "Run tests if available"
      - "Check for secrets/credentials"
    Before_Push:
      - "Verify target branch & remote"
      - "Check for force push implications"
      - "Ensure CI/CD readiness"
    Before_Merge:
      - "Test for conflicts"
      - "Verify branch policies"
      - "Check approval requirements"
      
  Commit_Standards:
    Format: "{type}: {description}\n\n{body}\n\n🤖 Generated with [Claude Code]\n\nCo-Authored-By: Claude"
    Types: ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
    Validation:
      - "Type matches change nature"
      - "Description < 50 chars"
      - "Body explains why, not what"
      
  Branch_Management:
    Strategy:
      Feature: "feature/{description}"
      Bugfix: "bugfix/{description}"
      Release: "release/{version}"
      Hotfix: "hotfix/{description}"
    Protection:
      Main: "No direct push, PR required"
      Release: "Admin approval required"
      Feature: "Auto-delete after merge"
      
  Conflict_Resolution:
    Detection: "Auto-detect during pull/merge"
    Strategies:
      Simple: "Auto-resolve if non-overlapping"
      Complex: "Interactive 3-way merge"
      Binary: "Choose version explicitly"
    Recovery:
      Abort: "git merge --abort → restore state"
      Stash: "git stash → try different approach"
      Branch: "Create conflict-resolution branch"
```

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
