# Deep Research Workflows

## Example 1: Planning-Only Strategy

### Scenario
Clear research question: "Latest TensorFlow 3.0 features"

### Execution
```bash
/sc:research "Latest TensorFlow 3.0 features" --strategy planning-only --depth standard
```

### Workflow
```yaml
1. Planning (Immediate):
   - Decompose: Official docs, changelog, tutorials
   - No user clarification needed
   
2. Execution:
   - Hop 1: Official TensorFlow documentation
   - Hop 2: Recent tutorials and examples
   - Confidence: 0.85 achieved
   
3. Synthesis:
   - Features list with examples
   - Migration guide references
   - Performance comparisons
```

## Example 2: Intent-to-Planning Strategy

### Scenario
Ambiguous request: "AI safety"

### Execution
```bash
/sc:research "AI safety" --strategy intent-planning --depth deep
```

### Workflow
```yaml
1. Intent Clarification:
   Questions:
   - "Are you interested in technical AI alignment, policy/governance, or current events?"
   - "What's your background level (researcher, developer, general interest)?"
   - "Any specific AI systems or risks of concern?"
   
2. User Response:
   - "Technical alignment for LLMs, researcher level"
   
3. Refined Planning:
   - Focus on alignment techniques
   - Academic sources priority
   - Include recent papers
   
4. Multi-Hop Execution:
   - Hop 1: Recent alignment papers
   - Hop 2: Key researchers and labs
   - Hop 3: Emerging techniques
   - Hop 4: Open problems
   
5. Self-Reflection:
   - Coverage: Complete ✓
   - Depth: Adequate ✓
   - Confidence: 0.82 ✓
```

## Example 3: Unified Intent-Planning with Replanning

### Scenario
Complex research: "Build AI startup competitive analysis"

### Execution
```bash
/sc:research "Build AI startup competitive analysis" --strategy unified --hops 5
```

### Workflow
```yaml
1. Initial Plan Presentation:
   Proposed Research Areas:
   - Current AI startup landscape
   - Funding and valuations
   - Technology differentiators
   - Market positioning
   - Growth strategies
   
   "Does this cover your needs? Any specific competitors or aspects to focus on?"
   
2. User Adjustment:
   "Focus on code generation tools, include pricing and technical capabilities"
   
3. Revised Multi-Hop Research:
   - Hop 1: List of code generation startups
   - Hop 2: Technical capabilities comparison
   - Hop 3: Pricing and business models
   - Hop 4: Customer reviews and adoption
   - Hop 5: Investment and growth metrics
   
4. Mid-Research Replanning:
   - Low confidence on technical details (0.55)
   - Switch to Playwright for interactive demos
   - Add GitHub repository analysis
   
5. Quality Gate Check:
   - Technical coverage: Improved to 0.78 ✓
   - Pricing data: Complete 0.90 ✓
   - Competitive matrix: Generated ✓
```

## Example 4: Case-Based Research with Learning

### Scenario
Similar to previous research: "Rust async runtime comparison"

### Execution
```bash
/sc:research "Rust async runtime comparison" --memory enabled
```

### Workflow
```yaml
1. Case Retrieval:
   Found Similar Case:
   - "Go concurrency patterns" research
   - Successful pattern: Technical benchmarks + code examples + community feedback
   
2. Adapted Strategy:
   - Use similar structure for Rust
   - Focus on: Tokio, async-std, smol
   - Include benchmarks and examples
   
3. Execution with Known Patterns:
   - Skip broad searches
   - Direct to technical sources
   - Use proven extraction methods
   
4. New Learning Captured:
   - Rust community prefers different metrics than Go
   - Crates.io provides useful statistics
   - Discord communities have valuable discussions
   
5. Memory Update:
   - Store successful Rust research patterns
   - Note language-specific source preferences
   - Save for future Rust queries
```

## Example 5: Self-Reflective Refinement Loop

### Scenario
Evolving research: "Quantum computing for optimization"

### Execution
```bash
/sc:research "Quantum computing for optimization" --confidence 0.8 --depth exhaustive
```

### Workflow
```yaml
1. Initial Research Phase:
   - Academic papers collected
   - Basic concepts understood
   - Confidence: 0.65 (below threshold)
   
2. Self-Reflection Analysis:
   Gaps Identified:
   - Practical implementations missing
   - No industry use cases
   - Mathematical details unclear
   
3. Replanning Decision:
   - Add industry reports
   - Include video tutorials for math
   - Search for code implementations
   
4. Enhanced Research:
   - Hop 1→2: Papers → Authors → Implementations
   - Hop 3→4: Companies → Case studies
   - Hop 5: Tutorial videos for complex math
   
5. Quality Achievement:
   - Confidence raised to 0.82 ✓
   - Comprehensive coverage achieved
   - Multiple perspectives included
```

## Example 6: Technical Documentation Research with Playwright

### Scenario
Research the latest Next.js 14 App Router features

### Execution
```bash
/sc:research "Next.js 14 App Router complete guide" --depth deep --scrape selective --screenshots
```

### Workflow
```yaml
1. Tavily Search:
   - Find official docs, tutorials, blog posts
   - Identify JavaScript-heavy documentation sites
   
2. URL Analysis:
   - Next.js docs → JavaScript rendering required
   - Blog posts → Static content, Tavily sufficient
   - Video tutorials → Need transcript extraction
   
3. Playwright Navigation:
   - Navigate to official documentation
   - Handle interactive code examples
   - Capture screenshots of UI components
   
4. Dynamic Extraction:
   - Extract code samples
   - Capture interactive demos
   - Document routing patterns
   
5. Synthesis:
   - Combine official docs with community tutorials
   - Create comprehensive guide with visuals
   - Include code examples and best practices
```

## Example 7: Competitive Intelligence with Visual Documentation

### Scenario
Analyze competitor pricing and features

### Execution
```bash
/sc:research "AI writing assistant tools pricing features 2024" --scrape all --screenshots --interactive
```

### Workflow
```yaml
1. Market Discovery:
   - Tavily finds: Jasper, Copy.ai, Writesonic, etc.
   - Identify pricing pages and feature lists
   
2. Complexity Assessment:
   - Dynamic pricing calculators detected
   - Interactive feature comparisons found
   - Login-gated content identified
   
3. Playwright Extraction:
   - Navigate to each pricing page
   - Interact with pricing sliders
   - Capture screenshots of pricing tiers
   
4. Feature Analysis:
   - Extract feature matrices
   - Compare capabilities
   - Document limitations
   
5. Report Generation:
   - Competitive positioning matrix
   - Visual pricing comparison
   - Feature gap analysis
   - Strategic recommendations
```

## Example 8: Academic Research with Authentication

### Scenario
Research latest machine learning papers

### Execution
```bash
/sc:research "transformer architecture improvements 2024" --depth exhaustive --auth --scrape auto
```

### Workflow
```yaml
1. Academic Search:
   - Tavily finds papers on arXiv, IEEE, ACM
   - Identify open vs. gated content
   
2. Access Strategy:
   - arXiv: Direct access, no auth needed
   - IEEE: Institutional access required
   - ACM: Mixed access levels
   
3. Extraction Approach:
   - Public papers: Tavily extraction
   - Gated content: Playwright with auth
   - PDFs: Download and process
   
4. Citation Network:
   - Follow reference chains
   - Identify key contributors
   - Map research lineage
   
5. Literature Synthesis:
   - Chronological development
   - Key innovations identified
   - Future directions mapped
   - Comprehensive bibliography
```

## Example 9: Real-time Market Data Research

### Scenario
Gather current cryptocurrency market analysis

### Execution
```bash
/sc:research "cryptocurrency market analysis BTC ETH 2024" --scrape all --interactive --screenshots
```

### Workflow
```yaml
1. Market Discovery:
   - Find: CoinMarketCap, CoinGecko, TradingView
   - Identify real-time data sources
   
2. Dynamic Content Handling:
   - Playwright loads live charts
   - Capture price movements
   - Extract volume data
   
3. Interactive Analysis:
   - Interact with chart timeframes
   - Toggle technical indicators
   - Capture different views
   
4. Data Synthesis:
   - Current market conditions
   - Technical analysis
   - Sentiment indicators
   - Visual documentation
   
5. Report Output:
   - Market snapshot with charts
   - Technical analysis summary
   - Trading volume trends
   - Risk assessment
```

## Example 10: Multi-Domain Research with Parallel Execution

### Scenario
Comprehensive analysis of "AI in healthcare 2024"

### Execution
```bash
/sc:research "AI in healthcare applications 2024" --depth exhaustive --hops 5 --parallel
```

### Workflow
```yaml
1. Domain Decomposition:
   Parallel Searches:
   - Medical AI applications
   - Regulatory landscape
   - Market analysis
   - Technical implementations
   - Ethical considerations
   
2. Multi-Hop Exploration:
   Each Domain:
   - Hop 1: Broad landscape
   - Hop 2: Key players
   - Hop 3: Case studies
   - Hop 4: Challenges
   - Hop 5: Future trends
   
3. Cross-Domain Synthesis:
   - Medical ↔ Technical connections
   - Regulatory ↔ Market impacts
   - Ethical ↔ Implementation constraints
   
4. Quality Assessment:
   - Coverage: All domains addressed
   - Depth: Sufficient detail per domain
   - Integration: Cross-domain insights
   - Confidence: 0.87 achieved
   
5. Comprehensive Report:
   - Executive summary
   - Domain-specific sections
   - Integrated analysis
   - Strategic recommendations
   - Visual evidence
```

## Advanced Workflow Patterns

### Pattern 1: Iterative Deepening
```yaml
Round_1:
  - Broad search for landscape
  - Identify key areas
  
Round_2:
  - Deep dive into key areas
  - Extract detailed information
  
Round_3:
  - Fill specific gaps
  - Resolve contradictions
  
Round_4:
  - Final validation
  - Quality assurance
```

### Pattern 2: Source Triangulation
```yaml
Primary_Sources:
  - Official documentation
  - Academic papers
  
Secondary_Sources:
  - Industry reports
  - Expert analysis
  
Tertiary_Sources:
  - Community discussions
  - User experiences
  
Synthesis:
  - Cross-validate findings
  - Identify consensus
  - Note disagreements
```

### Pattern 3: Temporal Analysis
```yaml
Historical_Context:
  - Past developments
  - Evolution timeline
  
Current_State:
  - Present situation
  - Recent changes
  
Future_Projections:
  - Trends analysis
  - Expert predictions
  
Synthesis:
  - Development trajectory
  - Inflection points
  - Future scenarios
```

## Performance Optimization Tips

### Query Optimization
1. Start with specific terms
2. Use domain filters early
3. Batch similar searches
4. Cache intermediate results
5. Reuse successful patterns

### Extraction Efficiency
1. Assess complexity first
2. Use appropriate tool per source
3. Parallelize when possible
4. Set reasonable timeouts
5. Handle errors gracefully

### Synthesis Strategy
1. Organize findings early
2. Identify patterns quickly
3. Resolve conflicts systematically
4. Build narrative progressively
5. Maintain evidence chains

## Quality Validation Checklist

### Planning Phase
- [ ] Clear objectives defined
- [ ] Appropriate strategy selected
- [ ] Resources estimated correctly
- [ ] Success criteria established

### Execution Phase
- [ ] All planned searches completed
- [ ] Extraction methods appropriate
- [ ] Multi-hop chains logical
- [ ] Confidence scores calculated

### Synthesis Phase
- [ ] All findings integrated
- [ ] Contradictions resolved
- [ ] Evidence chains complete
- [ ] Narrative coherent

### Delivery Phase
- [ ] Format appropriate for audience
- [ ] Citations complete and accurate
- [ ] Visual evidence included
- [ ] Confidence levels transparent