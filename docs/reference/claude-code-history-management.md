# Claude Code Conversation History Management Research

**Research Date**: 2025-10-09
**Purpose**: Understand .jsonl file structure, performance impact, and establish rotation policy

---

## 1. Official Documentation & Purpose

### .jsonl File Structure
**Location**: `~/.claude/projects/{project-directory}/`

**Data Structure** (from analysis of actual files):
```json
{
  "type": "summary|file-history-snapshot|user|assistant|system|tool_use|tool_result|message",
  "timestamp": "ISO-8601 timestamp",
  "cwd": "/absolute/path/to/working/directory",
  "sessionId": "uuid",
  "gitBranch": "branch-name",
  "content": "message content or command",
  "messageId": "uuid for message tracking"
}
```

**Key Message Types** (from 2.6MB conversation analysis):
- `message` (228): Container for conversation messages
- `assistant` (228): Claude's responses
- `user` (182): User inputs
- `tool_use` (137): Tool invocations
- `tool_result` (137): Tool execution results
- `text` (74): Text content blocks
- `file-history-snapshot` (39): File state tracking
- `thinking` (31): Claude's reasoning process
- `system` (12): System-level messages

### File History Snapshot Purpose
```json
{
  "type": "file-history-snapshot",
  "messageId": "uuid",
  "snapshot": {
    "messageId": "uuid",
    "trackedFileBackups": {},
    "timestamp": "ISO-8601"
  },
  "isSnapshotUpdate": false
}
```

**Purpose** (inferred from structure):
- Tracks file states at specific conversation points
- Enables undo/redo functionality for file changes
- Provides rollback capability for edits
- **Note**: No official documentation found on this feature

### Conversation Loading Behavior
**Official Best Practices** ([source](https://www.anthropic.com/engineering/claude-code-best-practices)):
- "All conversations are automatically saved locally with their full message history"
- "When resuming, the entire message history is restored to maintain context"
- "Tool usage and results from previous conversations preserved"

**Resume Commands**:
- `--continue`: Automatically continue most recent conversation
- `/resume`: Show list of recent sessions and choose one
- Session ID specification: Resume specific conversation

---

## 2. Performance Impact

### Known Issues from GitHub

#### Issue #5024: History Accumulation Causing Performance Issues
**Status**: Open (Major Issue)
**URL**: https://github.com/anthropics/claude-code/issues/5024

**Reported Problems**:
- File sizes growing to "hundreds of MB or more"
- Slower application startup times
- System performance degradation
- No automatic cleanup mechanism
- One user reported file size of 968KB+ continuously growing

**Current Workaround**:
- Manual editing of `.claude.json` (risky - can break configurations)
- `claude history clear` (removes ALL history across ALL projects)

#### Issue #7985: Severe Memory Leak
**Status**: Critical
**URL**: https://github.com/anthropics/claude-code/issues/7985

**Reported Problems**:
- Context accumulation causing massive memory usage
- Memory leaks with objects not garbage collected
- One user reported ~570GB of virtual memory usage
- Long-running sessions become unusable

#### Issue #8839: Conversation Compaction Failure
**Status**: Regression (after undo/redo feature)
**URL**: https://github.com/anthropics/claude-code/issues/8839

**Impact**:
- Claude Code can no longer automatically compact long conversations
- "Too long" errors after conversation history navigation feature added
- Conversations become unmanageable without manual intervention

#### Issue #8755: /clear Command Not Working
**Status**: Bug
**URL**: https://github.com/anthropics/claude-code/issues/8755

**Impact**:
- `/clear` command stopped functioning for some users
- "Clear Conversations" menu option non-functional
- Users cannot reset context window as recommended

### Actual Performance Data (Your Environment)

**Current State** (as of 2025-10-09):
- **Total agiletec project**: 33MB (57 conversation files)
- **Largest file**: 2.6MB (462 lines)
- **Average file**: ~580KB
- **Files >1MB**: 3 files
- **Total across all projects**: ~62MB

**Age Distribution**:
- Files older than 30 days: 0
- Files older than 7 days: 4
- Most files: <7 days old

**Comparison to Other Projects**:
```
33M   agiletec (57 files) - Most active
14M   SSD-2TB project
6.3M  tokium
2.6M  bunseki
```

---

## 3. Official Retention Policies

### Standard Retention (Consumer)
**Source**: [Anthropic Privacy Center](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data)

- **Prompts/Responses**: Up to 30 days in back-end logs
- **Deleted chats**: Immediately removed from UI, purged within 30 days
- **API logs**: Reducing to 7 days starting September 15, 2025 (from 30 days)

### Enterprise Controls
**Source**: [Custom Data Retention Controls](https://privacy.anthropic.com/en/articles/10440198-custom-data-retention-controls-for-claude-enterprise)

- **Minimum retention**: 30 days
- **Retention start**: Last observed activity (last message or project update)
- **Custom periods**: Available for organizations

### Local Storage (No Official Policy)
**Finding**: No official documentation found regarding:
- Recommended local .jsonl file retention periods
- Automatic cleanup of old conversations
- Performance thresholds for file sizes
- Safe deletion procedures

**Current Tools**:
- `claude history clear`: Removes ALL history (all projects, destructive)
- No selective cleanup tools available
- No archive functionality

---

## 4. Best Practices (Official & Community)

### Official Recommendations

#### Context Management
**Source**: [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

**Key Guidelines**:
1. **Use `/clear` frequently**: "Reset context window between tasks"
2. **Scope conversations**: "One project or feature per conversation"
3. **Clear before switching**: "/clear before fixing bugs to prevent context pollution"
4. **Don't rely on long context**: "Claude's context window can fill with irrelevant conversation"

**Quote**: "During long sessions, Claude's context window can fill with irrelevant conversation, file contents, and commands which can reduce performance, so use the /clear command frequently between tasks to reset the context window."

#### CLAUDE.md Strategy
- **Persistent context**: Use CLAUDE.md files for stable instructions
- **Auto-loaded**: "Claude automatically pulls into context when starting"
- **Hierarchy**: Global (`~/.claude/CLAUDE.md`) → Workspace → Project
- **Refinement**: "Take time to experiment and determine what produces best results"

#### When to Restart vs /clear
**Source**: [Community Best Practices](https://claudelog.com/faqs/does-claude-code-store-my-data/)

**Use `/clear` when**:
- Starting new task/feature
- Switching between features
- Context becomes polluted
- Before bug fixing

**Restart session when**:
- Switching projects
- Updating CLAUDE.md files
- Experiencing session issues
- Memory usage high

### Community Strategies

#### Conversation Organization
**Pattern**: "Scope a chat to one project or feature"
- Start conversation for specific goal
- Use `/clear` when goal complete
- Don't mix unrelated tasks in same conversation

#### Context Optimization
**Pattern**: "Avoid extensive, unrefined context"
- Iterate on CLAUDE.md effectiveness
- Remove ineffective instructions
- Test and refine periodically

#### Incognito Mode for Sensitive Work
**Pattern**: "Ghost icon for temporary conversations"
- Not saved to chat history
- No contribution to context memory
- Useful for experimental or sensitive work

---

## 5. Recommended Rotation Policy

### Immediate Actions (No Risk)

#### 1. Delete Very Old Conversations (>30 days)
```bash
# Backup first
mkdir -p ~/.claude/projects-archive/$(date +%Y-%m)

# Find and archive
find ~/.claude/projects/ -name "*.jsonl" -mtime +30 -type f \
  -exec mv {} ~/.claude/projects-archive/$(date +%Y-%m)/ \;
```

**Rationale**:
- Aligns with Anthropic's 30-day back-end retention
- Minimal functionality loss (context rarely useful after 30 days)
- Significant space savings

#### 2. Archive Project-Specific Old Conversations (>14 days)
```bash
# Per-project archive
mkdir -p ~/.claude/projects-archive/agiletec/$(date +%Y-%m)

find ~/.claude/projects/-Users-kazuki-github-agiletec -name "*.jsonl" -mtime +14 -type f \
  -exec mv {} ~/.claude/projects-archive/agiletec/$(date +%Y-%m)/ \;
```

**Rationale**:
- 14 days provides buffer for resumed work
- Most development tasks complete within 2 weeks
- Easy to restore if needed

### Periodic Maintenance (Weekly)

#### 3. Identify Large Files for Manual Review
```bash
# Find files >1MB
find ~/.claude/projects/ -name "*.jsonl" -type f -size +1M -exec ls -lh {} \;

# Review and archive if not actively used
```

**Criteria for Archival**:
- File >1MB and not modified in 7 days
- Completed feature/project conversations
- Debugging sessions that are resolved

### Aggressive Cleanup (Monthly)

#### 4. Archive All Inactive Conversations (>7 days)
```bash
# Monthly archive
mkdir -p ~/.claude/projects-archive/$(date +%Y-%m)

find ~/.claude/projects/ -name "*.jsonl" -mtime +7 -type f \
  -exec mv {} ~/.claude/projects-archive/$(date +%Y-%m)/ \;
```

**When to Use**:
- Project directory >50MB
- Startup performance degraded
- Running low on disk space

### Emergency Cleanup (Performance Issues)

#### 5. Nuclear Option - Keep Only Recent Week
```bash
# BACKUP EVERYTHING FIRST
tar -czf ~/claude-history-backup-$(date +%Y%m%d).tar.gz ~/.claude/projects/

# Keep only last 7 days
find ~/.claude/projects/ -name "*.jsonl" -mtime +7 -type f -delete
```

**When to Use**:
- Claude Code startup >10 seconds
- Memory usage abnormally high
- Experiencing Issue #7985 symptoms

---

## 6. Proposed Automated Solution

### Shell Script: `claude-history-rotate.sh`
```bash
#!/usr/bin/env bash
# Claude Code Conversation History Rotation
# Usage: ./claude-history-rotate.sh [--dry-run] [--days N]

set -euo pipefail

DAYS=${DAYS:-30}
DRY_RUN=false
ARCHIVE_BASE=~/.claude/projects-archive

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --days) DAYS="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Create archive directory
ARCHIVE_DIR="$ARCHIVE_BASE/$(date +%Y-%m)"
mkdir -p "$ARCHIVE_DIR"

# Find old conversations
OLD_FILES=$(find ~/.claude/projects/ -name "*.jsonl" -mtime "+$DAYS" -type f)

if [[ -z "$OLD_FILES" ]]; then
  echo "No files older than $DAYS days found."
  exit 0
fi

# Count and size
FILE_COUNT=$(echo "$OLD_FILES" | wc -l | tr -d ' ')
TOTAL_SIZE=$(echo "$OLD_FILES" | xargs du -ch | tail -1 | awk '{print $1}')

echo "Found $FILE_COUNT files older than $DAYS days ($TOTAL_SIZE total)"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "DRY RUN - Would archive:"
  echo "$OLD_FILES"
  exit 0
fi

# Archive files
echo "$OLD_FILES" | while read -r file; do
  mv "$file" "$ARCHIVE_DIR/"
  echo "Archived: $(basename "$file")"
done

echo "✓ Archived $FILE_COUNT files to $ARCHIVE_DIR"
```

### Cron Job Setup (Optional)
```bash
# Add to crontab (monthly cleanup)
# 0 3 1 * * /Users/kazuki/.local/bin/claude-history-rotate.sh --days 30

# Or use launchd on macOS
cat > ~/Library/LaunchAgents/com.user.claude-history-rotate.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.claude-history-rotate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/kazuki/.local/bin/claude-history-rotate.sh</string>
        <string>--days</string>
        <string>30</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>3</integer>
    </dict>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.user.claude-history-rotate.plist
```

---

## 7. Monitoring & Alerts

### Disk Usage Check Script
```bash
#!/usr/bin/env bash
# claude-history-check.sh

THRESHOLD_MB=100
PROJECTS_DIR=~/.claude/projects

TOTAL_SIZE_MB=$(du -sm "$PROJECTS_DIR" | awk '{print $1}')

echo "Claude Code conversation history: ${TOTAL_SIZE_MB}MB"

if [[ $TOTAL_SIZE_MB -gt $THRESHOLD_MB ]]; then
  echo "⚠️  WARNING: History size exceeds ${THRESHOLD_MB}MB threshold"
  echo "Consider running: claude-history-rotate.sh --days 30"

  # Find largest projects
  echo ""
  echo "Largest projects:"
  du -sm "$PROJECTS_DIR"/*/ | sort -rn | head -5
fi
```

### Performance Indicators to Watch
1. **Startup time**: >5 seconds = investigate
2. **File sizes**: >2MB per conversation = review
3. **Total size**: >100MB across all projects = cleanup
4. **Memory usage**: >2GB during session = Issue #7985
5. **Conversation length**: >500 message pairs = use `/clear`

---

## 8. Key Takeaways & Recommendations

### Critical Findings

✅ **Safe to Delete**:
- Conversations >30 days old (aligns with Anthropic retention)
- Completed feature/project conversations
- Large files (>1MB) not accessed in 14+ days

⚠️ **Caution Required**:
- Active project conversations (<7 days)
- Files referenced in recent work
- Conversations with unfinished tasks

❌ **Known Issues**:
- No official cleanup tools (Issue #5024)
- Memory leaks in long sessions (Issue #7985)
- `/clear` command bugs (Issue #8755)
- Conversation compaction broken (Issue #8839)

### Recommended Policy for Your Environment

**Daily Practice**:
- Use `/clear` between major tasks
- Scope conversations to single features
- Restart session if >2 hours continuous work

**Weekly Review** (Sunday):
```bash
# Check current state
du -sh ~/.claude/projects/*/

# Archive old conversations (>14 days)
claude-history-rotate.sh --days 14 --dry-run  # Preview
claude-history-rotate.sh --days 14            # Execute
```

**Monthly Cleanup** (1st of month):
```bash
# Aggressive cleanup (>30 days)
claude-history-rotate.sh --days 30

# Review large files
find ~/.claude/projects/ -name "*.jsonl" -size +1M -mtime +7
```

**Performance Threshold Actions**:
- Total size >50MB: Archive 30-day-old conversations
- Total size >100MB: Archive 14-day-old conversations
- Total size >200MB: Emergency cleanup (7-day retention)
- Startup >10s: Investigate memory leaks, consider Issue #7985

### Future-Proofing

**Watch for Official Solutions**:
- `claude history prune` command (requested in #5024)
- Automatic history rotation feature
- Configurable retention settings
- Separate configuration from history storage

**Community Tools**:
- [cclogviewer](https://github.com/hesreallyhim/awesome-claude-code): View .jsonl files
- Consider contributing to #5024 discussion
- Monitor anthropics/claude-code releases

---

## 9. References

### Official Documentation
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [How Long Do You Store My Data?](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data)
- [Custom Data Retention Controls](https://privacy.anthropic.com/en/articles/10440198-custom-data-retention-controls-for-claude-enterprise)

### GitHub Issues
- [#5024: History accumulation causes performance issues](https://github.com/anthropics/claude-code/issues/5024)
- [#7985: Severe memory leak](https://github.com/anthropics/claude-code/issues/7985)
- [#8839: Conversation compaction failure](https://github.com/anthropics/claude-code/issues/8839)
- [#8755: /clear command not working](https://github.com/anthropics/claude-code/issues/8755)

### Community Resources
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)
- [Claude Code Context Guide](https://www.arsturn.com/blog/beyond-prompting-a-guide-to-managing-context-in-claude-code)
- [ClaudeLog Documentation](https://claudelog.com/)

---

## Appendix: Current Environment Statistics

**Generated**: 2025-10-09 04:24 JST

### Project Size Breakdown
```
33M   -Users-kazuki-github-agiletec (57 files)
14M   -Volumes-SSD-2TB (project count: N/A)
6.3M  -Users-kazuki-github-tokium
2.6M  -Users-kazuki-github-bunseki
1.9M  -Users-kazuki
1.9M  -Users-kazuki-github-superclaude
---
Total: ~62MB across all projects
```

### agiletec Project Details
- **Total conversations**: 57
- **Largest file**: 2.6MB (d4852655-b760-4311-8f67-26f593f2403f.jsonl)
- **Files >1MB**: 3 files
- **Avg file size**: ~580KB
- **Files >7 days**: 4 files
- **Files >30 days**: 0 files

### Immediate Recommendation
**Status**: ✅ Healthy (no immediate action required)

**Reasoning**:
- Total size (33MB) well below concern threshold (100MB)
- No files >30 days old
- Only 4 files >7 days old
- Largest file (2.6MB) within acceptable range

**Next Review**: 2025-10-16 (weekly check)
