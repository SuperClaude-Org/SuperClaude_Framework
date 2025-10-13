# BUSINESS_PANEL_EXAMPLES.md - Usage Examples and Integration Patterns

## Basic Usage Examples

### Example 1: Strategic Plan Analysis
```bash
/sc:business-panel @strategy_doc.pdf

# Output: Discussion mode with Porter, Collins, Meadows, Doumont
# Analysis focuses on competitive positioning, organizational capability, 
# system dynamics, and communication clarity
```

### Example 2: Innovation Assessment  
```bash
/sc:business-panel "We're developing AI-powered customer service" --experts "christensen,drucker,godin"

# Output: Discussion mode focusing on jobs-to-be-done, customer value, 
# and remarkability/tribe building
```

### Example 3: Risk Analysis with Debate
```bash
/sc:business-panel @risk_assessment.md --mode debate

# Output: Debate mode with Taleb challenging conventional risk assessments,
# other experts defending their frameworks, systems perspective on conflicts
```

### Example 4: Strategic Learning Session
```bash
/sc:business-panel "Help me understand competitive strategy" --mode socratic

# Output: Socratic mode with strategic questions from multiple frameworks,
# progressive questioning based on user responses
```

## Advanced Usage Patterns

### Multi-Document Analysis
```bash
/sc:business-panel @market_research.pdf @competitor_analysis.xlsx @financial_projections.csv --synthesis-only

# Comprehensive analysis across multiple documents with focus on synthesis
```

### Domain-Specific Analysis
```bash
/sc:business-panel @product_strategy.md --focus "innovation" --experts "christensen,drucker,meadows"

# Innovation-focused analysis with disruption theory, management principles, systems thinking
```

### Structured Communication Focus
```bash
/sc:business-panel @exec_presentation.pptx --focus "communication" --structured

# Analysis focused on message clarity, audience needs, cognitive load optimization
```

## Integration with SuperClaude Commands

### Combined with /analyze
```bash
/analyze @business_model.md --business-panel

# Technical analysis followed by business expert panel review
```

### Combined with /improve  
```bash
/improve @strategy_doc.md --business-panel --iterative

# Iterative improvement with business expert validation
```

### Combined with /design
```bash
/design business-model --business-panel --experts "drucker,porter,kim_mauborgne"

# Business model design with expert guidance
```

## Expert Selection Strategies

### By Business Domain
```yaml
strategy_planning:
  experts: ['porter', 'kim_mauborgne', 'collins', 'meadows']
  rationale: "Competitive analysis, blue ocean opportunities, execution excellence, systems thinking"

innovation_management:
  experts: ['christensen', 'drucker', 'godin', 'meadows']  
  rationale: "Disruption theory, systematic innovation, remarkability, systems approach"

organizational_development:
  experts: ['collins', 'drucker', 'meadows', 'doumont']
  rationale: "Excellence principles, management effectiveness, systems change, clear communication"

risk_management:
  experts: ['taleb', 'meadows', 'porter', 'collins']
  rationale: "Antifragility, systems resilience, competitive threats, disciplined execution"

market_entry:
  experts: ['porter', 'christensen', 'godin', 'kim_mauborgne']
  rationale: "Industry analysis, disruption potential, tribe building, blue ocean creation"

business_model_design:
  experts: ['christensen', 'drucker', 'kim_mauborgne', 'meadows']
  rationale: "Value creation, customer focus, value innovation, system dynamics"
```

### By Analysis Type
```yaml
comprehensive_audit:
  experts: "all"
  mode: "discussion → debate → synthesis"
  
strategic_validation:
  experts: ['porter', 'collins', 'taleb']
  mode: "debate"
  
learning_facilitation:
  experts: ['drucker', 'meadows', 'doumont']
  mode: "socratic"

quick_assessment:
  experts: "auto-select-3"
  mode: "discussion"
  flags: "--synthesis-only"
```

## Output Format Variations

### Executive Summary Format
```bash
/sc:business-panel @doc.pdf --structured --synthesis-only

# Output:
## 🎯 Strategic Assessment
**💰 Financial Impact**: [Key economic drivers]
**🏆 Competitive Position**: [Advantage analysis]  
**📈 Growth Opportunities**: [Expansion potential]
**⚠️ Risk Factors**: [Critical threats]
**🧩 Synthesis**: [Integrated recommendation]
```

### Framework-by-Framework Format  
```bash
/sc:business-panel @doc.pdf --verbose

# Output:
## 📚 CHRISTENSEN - Disruption Analysis
[Detailed jobs-to-be-done and disruption assessment]

## 📊 PORTER - Competitive Strategy  
[Five forces and value chain analysis]

## 🧩 Cross-Framework Synthesis
[Integration and strategic implications]
```

### Question-Driven Format
```bash
/sc:business-panel @doc.pdf --questions

# Output:
## 🤔 Strategic Questions for Consideration
**🔨 Innovation Questions** (Christensen):
- What job is this being hired to do?

**⚔️ Competitive Questions** (Porter):  
- What are the sustainable advantages?

**🧭 Management Questions** (Drucker):
- What should our business be?
```

## Integration Workflows

### Business Strategy Development
```yaml
workflow_stages:
  stage_1: "/sc:business-panel @market_research.pdf --mode discussion"
  stage_2: "/sc:business-panel @competitive_analysis.md --mode debate"  
  stage_3: "/sc:business-panel 'synthesize findings' --mode socratic"
  stage_4: "/design strategy --business-panel --experts 'porter,kim_mauborgne'"
```

### Innovation Pipeline Assessment
```yaml
workflow_stages:
  stage_1: "/sc:business-panel @innovation_portfolio.xlsx --focus innovation"
  stage_2: "/improve @product_roadmap.md --business-panel"
  stage_3: "/analyze @market_opportunities.pdf --business-panel --think"
```

### Risk Management Review
```yaml  
workflow_stages:
  stage_1: "/sc:business-panel @risk_register.pdf --experts 'taleb,meadows,porter'"
  stage_2: "/sc:business-panel 'challenge risk assumptions' --mode debate"
  stage_3: "/implement risk_mitigation --business-panel --validate"
```

## Customization Options

### Expert Behavior Modification
```bash
# Focus specific expert on particular aspect
/sc:business-panel @doc.pdf --christensen-focus "disruption-potential"
/sc:business-panel @doc.pdf --porter-focus "competitive-moats"

# Adjust expert interaction style  
/sc:business-panel @doc.pdf --interaction "collaborative" # softer debate mode
/sc:business-panel @doc.pdf --interaction "challenging" # stronger debate mode
```

### Output Customization
```bash
# Symbol density control
/sc:business-panel @doc.pdf --symbols minimal  # reduce symbol usage
/sc:business-panel @doc.pdf --symbols rich     # full symbol system

# Analysis depth control
/sc:business-panel @doc.pdf --depth surface    # high-level overview
/sc:business-panel @doc.pdf --depth detailed   # comprehensive analysis
```

### Time and Resource Management
```bash
# Quick analysis for time constraints
/sc:business-panel @doc.pdf --quick --experts-max 3

# Comprehensive analysis for important decisions  
/sc:business-panel @doc.pdf --comprehensive --all-experts

# Resource-aware analysis
/sc:business-panel @doc.pdf --budget 10000  # token limit
```

## Quality Validation

### Analysis Quality Checks
```yaml
authenticity_validation:
  voice_consistency: "Each expert maintains characteristic style"
  framework_fidelity: "Analysis follows authentic methodology"
  interaction_realism: "Expert dynamics reflect professional patterns"

business_relevance:
  strategic_focus: "Analysis addresses real strategic concerns"  
  actionable_insights: "Recommendations are implementable"
  evidence_based: "Conclusions supported by framework logic"

integration_quality:
  synthesis_value: "Combined insights exceed individual analysis"
  framework_preservation: "Integration maintains framework distinctiveness"
  practical_utility: "Results support strategic decision-making"
```

### Performance Standards
```yaml
response_time:
  simple_analysis: "< 30 seconds"
  comprehensive_analysis: "< 2 minutes"
  multi_document: "< 5 minutes"

token_efficiency:
  discussion_mode: "8-15K tokens"
  debate_mode: "10-20K tokens"  
  socratic_mode: "12-25K tokens"
  synthesis_only: "3-8K tokens"

accuracy_targets:
  framework_authenticity: "> 90%"
  strategic_relevance: "> 85%"
  actionable_insights: "> 80%"
```