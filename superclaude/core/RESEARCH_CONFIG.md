# Deep Research Configuration

## Default Settings

```yaml
research_defaults:
  planning_strategy: unified
  max_hops: 5
  confidence_threshold: 0.7
  memory_enabled: true
  parallelization: true
  parallel_first: true  # MANDATORY DEFAULT
  sequential_override_requires_justification: true  # NEW
  
parallel_execution_rules:
  DEFAULT_MODE: PARALLEL  # EMPHASIZED
  
  mandatory_parallel:
    - "Multiple search queries"
    - "Batch URL extractions"
    - "Independent analyses"
    - "Non-dependent hops"
    - "Result processing"
    - "Information extraction"
    
  sequential_only_with_justification:
    - reason: "Explicit dependency"
      example: "Hop N requires Hop N-1 results"
    - reason: "Resource constraint"
      example: "API rate limit reached"
    - reason: "User requirement"
      example: "User requests sequential for debugging"
    
  parallel_optimization:
    batch_sizes:
      searches: 5
      extractions: 3
      analyses: 2
    intelligent_grouping:
      by_domain: true
      by_complexity: true
      by_resource: true
  
planning_strategies:
  planning_only:
    clarification: false
    user_confirmation: false
    execution: immediate
    
  intent_planning:
    clarification: true
    max_questions: 3
    execution: after_clarification
    
  unified:
    clarification: optional
    plan_presentation: true
    user_feedback: true
    execution: after_confirmation

hop_configuration:
  max_depth: 5
  timeout_per_hop: 60s
  parallel_hops: true
  loop_detection: true
  genealogy_tracking: true

confidence_scoring:
  relevance_weight: 0.5
  completeness_weight: 0.5
  minimum_threshold: 0.6
  target_threshold: 0.8

self_reflection:
  frequency: after_each_hop
  triggers:
    - confidence_below_threshold
    - contradictions_detected
    - time_elapsed_percentage: 80
    - user_intervention
  actions:
    - assess_quality
    - identify_gaps
    - consider_replanning
    - adjust_strategy

memory_management:
  case_based_reasoning: true
  pattern_learning: true
  session_persistence: true
  cross_session_learning: true
  retention_days: 30

tool_coordination:
  discovery_primary: tavily
  extraction_smart_routing: true
  reasoning_engine: sequential
  memory_backend: serena
  parallel_tool_calls: true

quality_gates:
  planning_gate:
    required_elements: [objectives, strategy, success_criteria]
  execution_gate:
    min_confidence: 0.6
  synthesis_gate:
    coherence_required: true
    clarity_required: true

extraction_settings:
  scraping_strategy: selective
  screenshot_capture: contextual
  authentication_handling: ethical
  javascript_rendering: auto_detect
  timeout_per_page: 15s
```

## Performance Optimizations

```yaml
optimization_strategies:
  caching:
    - Cache Tavily search results: 1 hour
    - Cache Playwright extractions: 24 hours
    - Cache Sequential analysis: 1 hour
    - Reuse case patterns: always

  parallelization:
    - Parallel searches: max 5
    - Parallel extractions: max 3
    - Parallel analysis: max 2
    - Tool call batching: true

  resource_limits:
    - Max time per research: 10 minutes
    - Max search iterations: 10
    - Max hops: 5
    - Max memory per session: 100MB
```

## Strategy Selection Rules

```yaml
strategy_selection:
  planning_only:
    indicators:
      - Clear, specific query
      - Technical documentation request
      - Well-defined scope
      - No ambiguity detected
    
  intent_planning:
    indicators:
      - Ambiguous terms present
      - Broad topic area
      - Multiple possible interpretations
      - User expertise unknown
    
  unified:
    indicators:
      - Complex multi-faceted query
      - User collaboration beneficial
      - Iterative refinement expected
      - High-stakes research
```

## Source Credibility Matrix

```yaml
source_credibility:
  tier_1_sources:
    score: 0.9-1.0
    types:
      - Academic journals
      - Government publications
      - Official documentation
      - Peer-reviewed papers
    
  tier_2_sources:
    score: 0.7-0.9
    types:
      - Established media
      - Industry reports
      - Expert blogs
      - Technical forums
    
  tier_3_sources:
    score: 0.5-0.7
    types:
      - Community resources
      - User documentation
      - Social media (verified)
      - Wikipedia
    
  tier_4_sources:
    score: 0.3-0.5
    types:
      - User forums
      - Social media (unverified)
      - Personal blogs
      - Comments sections
```

## Depth Configurations

```yaml
research_depth_profiles:
  quick:
    max_sources: 10
    max_hops: 1
    iterations: 1
    time_limit: 2 minutes
    confidence_target: 0.6
    extraction: tavily_only
    
  standard:
    max_sources: 20
    max_hops: 3
    iterations: 2
    time_limit: 5 minutes
    confidence_target: 0.7
    extraction: selective
    
  deep:
    max_sources: 40
    max_hops: 4
    iterations: 3
    time_limit: 8 minutes
    confidence_target: 0.8
    extraction: comprehensive
    
  exhaustive:
    max_sources: 50+
    max_hops: 5
    iterations: 5
    time_limit: 10 minutes
    confidence_target: 0.9
    extraction: all_sources
```

## Multi-Hop Patterns

```yaml
hop_patterns:
  entity_expansion:
    description: "Explore entities found in previous hop"
    example: "Paper → Authors → Other works → Collaborators"
    max_branches: 3
    
  concept_deepening:
    description: "Drill down into concepts"
    example: "Topic → Subtopics → Details → Examples"
    max_depth: 4
    
  temporal_progression:
    description: "Follow chronological development"
    example: "Current → Recent → Historical → Origins"
    direction: backward
    
  causal_chain:
    description: "Trace cause and effect"
    example: "Effect → Immediate cause → Root cause → Prevention"
    validation: required
```

## Extraction Routing Rules

```yaml
extraction_routing:
  use_tavily:
    conditions:
      - Static HTML content
      - Simple article structure
      - No JavaScript requirement
      - Public access
    
  use_playwright:
    conditions:
      - JavaScript rendering required
      - Dynamic content present
      - Authentication needed
      - Interactive elements
      - Screenshots required
    
  use_context7:
    conditions:
      - Technical documentation
      - API references
      - Framework guides
      - Library documentation
    
  use_native:
    conditions:
      - Local file access
      - Simple explanations
      - Code generation
      - General knowledge
```

## Case-Based Learning Schema

```yaml
case_schema:
  case_id:
    format: "research_[timestamp]_[topic_hash]"
    
  case_content:
    query: "original research question"
    strategy_used: "planning approach"
    successful_patterns:
      - query_formulations: []
      - extraction_methods: []
      - synthesis_approaches: []
    findings:
      key_discoveries: []
      source_credibility_scores: {}
      confidence_levels: {}
    lessons_learned:
      what_worked: []
      what_failed: []
      optimizations: []
    metrics:
      time_taken: seconds
      sources_processed: count
      hops_executed: count
      confidence_achieved: float
```

## Replanning Thresholds

```yaml
replanning_triggers:
  confidence_based:
    critical: < 0.4
    low: < 0.6
    acceptable: 0.6-0.7
    good: > 0.7
    
  time_based:
    warning: 70% of limit
    critical: 90% of limit
    
  quality_based:
    insufficient_sources: < 3
    contradictions: > 30%
    gaps_identified: > 50%
    
  user_based:
    explicit_request: immediate
    implicit_dissatisfaction: assess
```

## Output Format Templates

```yaml
output_formats:
  summary:
    max_length: 500 words
    sections: [key_finding, evidence, sources]
    confidence_display: simple
    
  report:
    sections: [executive_summary, methodology, findings, synthesis, conclusions]
    citations: inline
    confidence_display: detailed
    visuals: included
    
  academic:
    sections: [abstract, introduction, methodology, literature_review, findings, discussion, conclusions]
    citations: academic_format
    confidence_display: statistical
    appendices: true
```

## Error Handling

```yaml
error_handling:
  tavily_errors:
    api_key_missing: "Check TAVILY_API_KEY environment variable"
    rate_limit: "Wait and retry with exponential backoff"
    no_results: "Expand search terms or try alternatives"
    
  playwright_errors:
    timeout: "Skip source or increase timeout"
    navigation_failed: "Mark as inaccessible, continue"
    screenshot_failed: "Continue without visual"
    
  quality_errors:
    low_confidence: "Trigger replanning"
    contradictions: "Seek additional sources"
    insufficient_data: "Expand search scope"
```

## Integration Points

```yaml
mcp_integration:
  tavily:
    role: primary_search
    fallback: native_websearch
    
  playwright:
    role: complex_extraction
    fallback: tavily_extraction
    
  sequential:
    role: reasoning_engine
    fallback: native_reasoning
    
  context7:
    role: technical_docs
    fallback: tavily_search
    
  serena:
    role: memory_management
    fallback: session_only
```

## Monitoring Metrics

```yaml
metrics_tracking:
  performance:
    - search_latency
    - extraction_time
    - synthesis_duration
    - total_research_time
    
  quality:
    - confidence_scores
    - source_diversity
    - coverage_completeness
    - contradiction_rate
    
  efficiency:
    - cache_hit_rate
    - parallel_execution_rate
    - memory_usage
    - api_cost
    
  learning:
    - pattern_reuse_rate
    - strategy_success_rate
    - improvement_trajectory
```