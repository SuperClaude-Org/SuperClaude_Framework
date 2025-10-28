# Workflow Metrics Schema

**Purpose**: Token efficiency tracking for continuous optimization and A/B testing

**File**: `docs/memory/workflow_metrics.jsonl` (append-only log)

## Data Structure (JSONL Format)

Each line is a complete JSON object representing one workflow execution.

```jsonl
{
  "timestamp": "2025-10-17T01:54:21+09:00",
  "session_id": "abc123def456",
  "task_type": "typo_fix",
  "complexity": "light",
  "workflow_id": "progressive_v3_layer2",
  "layers_used": [0, 1, 2],
  "tokens_used": 650,
  "time_ms": 1800,
  "files_read": 1,
  "mindbase_used": false,
  "sub_agents": [],
  "success": true,
  "user_feedback": "satisfied",
  "notes": "Optional implementation notes"
}
```

## Field Definitions

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | ISO 8601 | Execution timestamp in JST | `"2025-10-17T01:54:21+09:00"` |
| `session_id` | string | Unique session identifier | `"abc123def456"` |
| `task_type` | string | Task classification | `"typo_fix"`, `"bug_fix"`, `"feature_impl"` |
| `complexity` | string | Intent classification level | `"ultra-light"`, `"light"`, `"medium"`, `"heavy"`, `"ultra-heavy"` |
| `workflow_id` | string | Workflow variant identifier | `"progressive_v3_layer2"` |
| `layers_used` | array | Progressive loading layers executed | `[0, 1, 2]` |
| `tokens_used` | integer | Total tokens consumed | `650` |
| `time_ms` | integer | Execution time in milliseconds | `1800` |
| `success` | boolean | Task completion status | `true`, `false` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `files_read` | integer | Number of files read | `1` |
| `mindbase_used` | boolean | Whether mindbase MCP was used | `false` |
| `sub_agents` | array | Delegated sub-agents | `["backend-architect", "quality-engineer"]` |
| `user_feedback` | string | Inferred user satisfaction | `"satisfied"`, `"neutral"`, `"unsatisfied"` |
| `notes` | string | Implementation notes | `"Used cached solution"` |
| `confidence_score` | float | Pre-implementation confidence | `0.85` |
| `hallucination_detected` | boolean | Self-check red flags found | `false` |
| `error_recurrence` | boolean | Same error encountered before | `false` |

## Task Type Taxonomy

### Ultra-Light Tasks
- `progress_query`: "進捗教えて"
- `status_check`: "現状確認"
- `next_action_query`: "次のタスクは？"

### Light Tasks
- `typo_fix`: README誤字修正
- `comment_addition`: コメント追加
- `variable_rename`: 変数名変更
- `documentation_update`: ドキュメント更新

### Medium Tasks
- `bug_fix`: バグ修正
- `small_feature`: 小機能追加
- `refactoring`: リファクタリング
- `test_addition`: テスト追加

### Heavy Tasks
- `feature_impl`: 新機能実装
- `architecture_change`: アーキテクチャ変更
- `security_audit`: セキュリティ監査
- `integration`: 外部システム統合

### Ultra-Heavy Tasks
- `system_redesign`: システム全面再設計
- `framework_migration`: フレームワーク移行
- `comprehensive_research`: 包括的調査

## Workflow Variant Identifiers

### Progressive Loading Variants
- `progressive_v3_layer1`: Ultra-light (memory files only)
- `progressive_v3_layer2`: Light (target file only)
- `progressive_v3_layer3`: Medium (related files 3-5)
- `progressive_v3_layer4`: Heavy (subsystem)
- `progressive_v3_layer5`: Ultra-heavy (full + external research)

### Experimental Variants (A/B Testing)
- `experimental_eager_layer3`: Always load Layer 3 for medium tasks
- `experimental_lazy_layer2`: Minimal Layer 2 loading
- `experimental_parallel_layer3`: Parallel file loading in Layer 3

## Complexity Classification Rules

```yaml
ultra_light:
  keywords: ["進捗", "状況", "進み", "where", "status", "progress"]
  token_budget: "100-500"
  layers: [0, 1]

light:
  keywords: ["誤字", "typo", "fix typo", "correct", "comment"]
  token_budget: "500-2K"
  layers: [0, 1, 2]

medium:
  keywords: ["バグ", "bug", "fix", "修正", "error", "issue"]
  token_budget: "2-5K"
  layers: [0, 1, 2, 3]

heavy:
  keywords: ["新機能", "new feature", "implement", "実装"]
  token_budget: "5-20K"
  layers: [0, 1, 2, 3, 4]

ultra_heavy:
  keywords: ["再設計", "redesign", "overhaul", "migration"]
  token_budget: "20K+"
  layers: [0, 1, 2, 3, 4, 5]
```

## Recording Points

### Session Start (Layer 0)
```python
session_id = generate_session_id()
workflow_metrics = {
    "timestamp": get_current_time(),
    "session_id": session_id,
    "workflow_id": "progressive_v3_layer0"
}
# Bootstrap: 150 tokens
```

### After Intent Classification (Layer 1)
```python
workflow_metrics.update({
    "task_type": classify_task_type(user_request),
    "complexity": classify_complexity(user_request),
    "estimated_token_budget": get_budget(complexity)
})
```

### After Progressive Loading
```python
workflow_metrics.update({
    "layers_used": [0, 1, 2],  # Actual layers executed
    "tokens_used": calculate_tokens(),
    "files_read": len(files_loaded)
})
```

### After Task Completion
```python
workflow_metrics.update({
    "success": task_completed_successfully,
    "time_ms": execution_time_ms,
    "user_feedback": infer_user_satisfaction()
})
```

### Session End
```python
# Append to workflow_metrics.jsonl
with open("docs/memory/workflow_metrics.jsonl", "a") as f:
    f.write(json.dumps(workflow_metrics) + "\n")
```

## Analysis Scripts

### Weekly Analysis
```bash
# Group by task type and calculate averages
python scripts/analyze_workflow_metrics.py --period week

# Output:
# Task Type: typo_fix
#   Count: 12
#   Avg Tokens: 680
#   Avg Time: 1,850ms
#   Success Rate: 100%
```

### A/B Testing Analysis
```bash
# Compare workflow variants
python scripts/ab_test_workflows.py \
  --variant-a progressive_v3_layer2 \
  --variant-b experimental_eager_layer3 \
  --metric tokens_used

# Output:
# Variant A (progressive_v3_layer2):
#   Avg Tokens: 1,250
#   Success Rate: 95%
#
# Variant B (experimental_eager_layer3):
#   Avg Tokens: 2,100
#   Success Rate: 98%
#
# Statistical Significance: p = 0.03 (significant)
# Recommendation: Keep Variant A (better efficiency)
```

## Usage (Continuous Optimization)

### Weekly Review Process
```yaml
every_monday_morning:
  1. Run analysis: python scripts/analyze_workflow_metrics.py --period week
  2. Identify patterns:
     - Best-performing workflows per task type
     - Inefficient patterns (high tokens, low success)
     - User satisfaction trends
  3. Update recommendations:
     - Promote efficient workflows to standard
     - Deprecate inefficient workflows
     - Design new experimental variants
```

### A/B Testing Framework
```yaml
allocation_strategy:
  current_best: 80%  # Use best-known workflow
  experimental: 20%  # Test new variant

evaluation_criteria:
  minimum_trials: 20  # Per variant
  confidence_level: 0.95  # p < 0.05
  metrics:
    - tokens_used (primary)
    - success_rate (gate: must be ≥95%)
    - user_feedback (qualitative)

promotion_rules:
  if experimental_better:
    - Statistical significance confirmed
    - Success rate ≥ current_best
    - User feedback ≥ neutral
    → Promote to standard (80% allocation)

  if experimental_worse:
    → Deprecate variant
    → Document learning in docs/patterns/
```

### Auto-Optimization Cycle
```yaml
monthly_cleanup:
  1. Identify stale workflows:
     - No usage in last 90 days
     - Success rate <80%
     - User feedback consistently negative

  2. Archive deprecated workflows:
     - Move to docs/patterns/deprecated/
     - Document why deprecated

  3. Promote new standards:
     - Experimental → Standard (if proven better)
     - Update pm.md with new best practices

  4. Generate monthly report:
     - Token efficiency trends
     - Success rate improvements
     - User satisfaction evolution
```

## Visualization

### Token Usage Over Time
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_json("docs/memory/workflow_metrics.jsonl", lines=True)
df['date'] = pd.to_datetime(df['timestamp']).dt.date

daily_avg = df.groupby('date')['tokens_used'].mean()
plt.plot(daily_avg)
plt.title("Average Token Usage Over Time")
plt.ylabel("Tokens")
plt.xlabel("Date")
plt.show()
```

### Task Type Distribution
```python
task_counts = df['task_type'].value_counts()
plt.pie(task_counts, labels=task_counts.index, autopct='%1.1f%%')
plt.title("Task Type Distribution")
plt.show()
```

### Workflow Efficiency Comparison
```python
workflow_efficiency = df.groupby('workflow_id').agg({
    'tokens_used': 'mean',
    'success': 'mean',
    'time_ms': 'mean'
})
print(workflow_efficiency.sort_values('tokens_used'))
```

## Expected Patterns

### Healthy Metrics (After 1 Month)
```yaml
token_efficiency:
  ultra_light: 750-1,050 tokens (63% reduction)
  light: 1,250 tokens (46% reduction)
  medium: 3,850 tokens (47% reduction)
  heavy: 10,350 tokens (40% reduction)

success_rates:
  all_tasks: ≥95%
  ultra_light: 100% (simple tasks)
  light: 98%
  medium: 95%
  heavy: 92%

user_satisfaction:
  satisfied: ≥70%
  neutral: ≤25%
  unsatisfied: ≤5%
```

### Red Flags (Require Investigation)
```yaml
warning_signs:
  - success_rate < 85% for any task type
  - tokens_used > estimated_budget by >30%
  - time_ms > 10 seconds for light tasks
  - user_feedback "unsatisfied" > 10%
  - error_recurrence > 15%
```

## Integration with PM Agent

### Automatic Recording
PM Agent automatically records metrics at each execution point:
- Session start (Layer 0)
- Intent classification (Layer 1)
- Progressive loading (Layers 2-5)
- Task completion
- Session end

### No Manual Intervention
- All recording is automatic
- No user action required
- Transparent operation
- Privacy-preserving (local files only)

## Privacy and Security

### Data Retention
- Local storage only (`docs/memory/`)
- No external transmission
- Git-manageable (optional)
- User controls retention period

### Sensitive Data Handling
- No code snippets logged
- No user input content
- Only metadata (tokens, timing, success)
- Task types are generic classifications

## Maintenance

### File Rotation
```bash
# Archive old metrics (monthly)
mv docs/memory/workflow_metrics.jsonl \
   docs/memory/archive/workflow_metrics_2025-10.jsonl

# Start fresh
touch docs/memory/workflow_metrics.jsonl
```

### Cleanup
```bash
# Remove metrics older than 6 months
find docs/memory/archive/ -name "workflow_metrics_*.jsonl" \
  -mtime +180 -delete
```

## References

- Specification: `plugins/superclaude/commands/pm.md` (Line 291-355)
- Research: `docs/research/llm-agent-token-efficiency-2025.md`
- Tests: `tests/pm_agent/test_token_budget.py`
