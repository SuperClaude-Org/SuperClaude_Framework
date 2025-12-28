# Reflexion Framework Integration - PM Agent

**Date**: 2025-10-17
**Purpose**: Integrate Reflexion self-reflection mechanism into PM Agent
**Source**: Reflexion: Language Agents with Verbal Reinforcement Learning (2023, arXiv)

---

## 概要

Reflexionは、LLMエージェントが自分の行動を振り返り、エラーを検出し、次の試行で改善するフレームワーク。

### 核心メカニズム

```yaml
Traditional Agent:
  Action → Observe → Repeat
  問題: 同じ間違いを繰り返す

Reflexion Agent:
  Action → Observe → Reflect → Learn → Improved Action
  利点: 自己修正、継続的改善
```

---

## PM Agent統合アーキテクチャ

### 1. Self-Evaluation (自己評価)

**タイミング**: 実装完了後、完了報告前

```yaml
Purpose: 自分の実装を客観的に評価

Questions:
  ❓ "この実装、本当に正しい？"
  ❓ "テストは全て通ってる？"
  ❓ "思い込みで判断してない？"
  ❓ "ユーザーの要件を満たしてる？"

Process:
  1. 実装内容を振り返る
  2. テスト結果を確認
  3. 要件との照合
  4. 証拠の有無確認

Output:
  - 完了判定 (✅ / ❌)
  - 不足項目リスト
  - 次のアクション提案
```

### 2. Self-Reflection (自己反省)

**タイミング**: エラー発生時、実装失敗時

```yaml
Purpose: なぜ失敗したのかを理解する

Reflexion Example (Original Paper):
  "Reflection: I searched the wrong title for the show,
   which resulted in no results. I should have searched
   the show's main character to find the correct information."

PM Agent Application:
  "Reflection:
   ❌ What went wrong: JWT validation failed
   🔍 Root cause: Missing environment variable SUPABASE_JWT_SECRET
   💡 Why it happened: Didn't check .env.example before implementation
   ✅ Prevention: Always verify environment setup before starting
   📝 Learning: Add env validation to startup checklist"

Storage:
  → docs/memory/reflexion.jsonl (ReflexionMemory - always available)
  → docs/mistakes/[feature]-YYYY-MM-DD.md
  → mindbase (if airis-mcp-gateway installed, automatic)
```

### 3. Memory Integration (記憶統合)

**Purpose**: 過去の失敗から学習し、同じ間違いを繰り返さない

```yaml
Error Occurred:
  1. Check Past Errors (Automatic Tool Selection):
     → Search conversation history for similar errors
     → Claude selects best available tool:
       * mindbase_search (if airis-mcp-gateway installed)
         - Semantic search across all conversations
         - Cross-project pattern recognition
       * ReflexionMemory (built-in, always available)
         - Keyword search in reflexion.jsonl
         - Fast project-scoped matching

  2. IF similar error found:
     ✅ "⚠️ Same error occurred before"
     ✅ "Solution: [past_solution]"
     ✅ Apply known solution immediately
     → Skip lengthy investigation

  3. ELSE (new error):
     → Proceed with root cause investigation
     → Document solution for future reference
```

---

## 実装パターン

### Pattern 1: Pre-Implementation Reflection

```yaml
Before Starting:
  PM Agent Internal Dialogue:
    "Am I clear on what needs to be done?"
    → IF No: Ask user for clarification
    → IF Yes: Proceed

    "Do I have sufficient information?"
    → Check: Requirements, constraints, architecture
    → IF No: Research official docs, patterns
    → IF Yes: Proceed

    "What could go wrong?"
    → Identify risks
    → Plan mitigation strategies
```

### Pattern 2: Mid-Implementation Check

```yaml
During Implementation:
  Checkpoint Questions (every 30 min OR major milestone):
    ❓ "Am I still on track?"
    ❓ "Is this approach working?"
    ❓ "Any warnings or errors I'm ignoring?"

  IF deviation detected:
    → STOP
    → Reflect: "Why am I deviating?"
    → Reassess: "Should I course-correct or continue?"
    → Decide: Continue OR restart with new approach
```

### Pattern 3: Post-Implementation Reflection

```yaml
After Implementation:
  Completion Checklist:
    ✅ Tests all pass (actual results shown)
    ✅ Requirements all met (checklist verified)
    ✅ No warnings ignored (all investigated)
    ✅ Evidence documented (test outputs, code changes)

  IF checklist incomplete:
    → ❌ NOT complete
    → Report actual status honestly
    → Continue work

  IF checklist complete:
    → ✅ Feature complete
    → Document learnings
    → Update knowledge base
```

---

## Hallucination Prevention Strategies

### Strategy 1: Evidence Requirement

**Principle**: Never claim success without evidence

```yaml
Claiming "Complete":
  MUST provide:
    1. Test Results (actual output)
    2. Code Changes (file list, diff summary)
    3. Validation Status (lint, typecheck, build)

  IF evidence missing:
    → BLOCK completion claim
    → Force verification first
```

### Strategy 2: Self-Check Questions

**Principle**: Question own assumptions systematically

```yaml
Before Reporting:
  Ask Self:
    ❓ "Did I actually RUN the tests?"
    ❓ "Are the test results REAL or assumed?"
    ❓ "Am I hiding any failures?"
    ❓ "Would I trust this implementation in production?"

  IF any answer is negative:
    → STOP reporting success
    → Fix issues first
```

### Strategy 3: Confidence Thresholds

**Principle**: Admit uncertainty when confidence is low

```yaml
Confidence Assessment:
  High (90-100%):
    → Proceed confidently
    → Official docs + existing patterns support approach

  Medium (70-89%):
    → Present options
    → Explain trade-offs
    → Recommend best choice

  Low (<70%):
    → STOP
    → Ask user for guidance
    → Never pretend to know
```

---

## Token Budget Integration

**Challenge**: Reflection costs tokens

**Solution**: Budget-aware reflection based on task complexity

```yaml
Simple Task (typo fix):
  Reflection Budget: 200 tokens
  Questions: "File edited? Tests pass?"

Medium Task (bug fix):
  Reflection Budget: 1,000 tokens
  Questions: "Root cause identified? Tests added? Regression prevented?"

Complex Task (feature):
  Reflection Budget: 2,500 tokens
  Questions: "All requirements met? Tests comprehensive? Integration verified? Documentation updated?"

Anti-Pattern:
  ❌ Unlimited reflection → Token explosion
  ✅ Budgeted reflection → Controlled cost
```

---

## Success Metrics

### Quantitative

```yaml
Hallucination Detection Rate:
  Target: >90% (Reflexion paper: 94%)
  Measure: % of false claims caught by self-check

Error Recurrence Rate:
  Target: <10% (same error repeated)
  Measure: % of errors that occur twice

Confidence Accuracy:
  Target: >85% (confidence matches reality)
  Measure: High confidence → success rate
```

### Qualitative

```yaml
Culture Change:
  ✅ "わからないことをわからないと言う"
  ✅ "嘘をつかない、証拠を示す"
  ✅ "失敗を認める、次に改善する"

Behavioral Indicators:
  ✅ User questions reduce (clear communication)
  ✅ Rework reduces (first attempt accuracy increases)
  ✅ Trust increases (honest reporting)
```

---

## Implementation Checklist

- [x] Self-Check質問システム (完了前検証)
- [x] Evidence Requirement (証拠要求)
- [x] Confidence Scoring (確信度評価)
- [ ] Reflexion Pattern統合 (自己反省ループ)
- [ ] Token-Budget-Aware Reflection (予算制約型振り返り)
- [ ] 実装例とアンチパターン文書化
- [ ] workflow_metrics.jsonl統合
- [ ] テストと検証

---

## References

1. **Reflexion: Language Agents with Verbal Reinforcement Learning**
   - Authors: Noah Shinn et al.
   - Year: 2023
   - Key Insight: Self-reflection enables 94% error detection rate

2. **Self-Evaluation in AI Agents**
   - Source: Galileo AI (2024)
   - Key Insight: Confidence scoring reduces hallucinations

3. **Token-Budget-Aware LLM Reasoning**
   - Source: arXiv 2412.18547 (2024)
   - Key Insight: Budget constraints enable efficient reflection

---

**End of Report**
