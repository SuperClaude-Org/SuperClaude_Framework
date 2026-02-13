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

## Expert Selection

### By Domain
| Domain | Experts | Focus |
|--------|---------|-------|
| Strategy | porter, kim_mauborgne, collins, meadows | Competitive, blue ocean, execution, systems |
| Innovation | christensen, drucker, godin, meadows | Disruption, systematic innovation, remarkability |
| Organization | collins, drucker, meadows, doumont | Excellence, management, systems change, communication |
| Risk | taleb, meadows, porter, collins | Antifragility, resilience, threats, discipline |
| Market Entry | porter, christensen, godin, kim_mauborgne | Industry, disruption, tribes, blue ocean |
| Business Model | christensen, drucker, kim_mauborgne, meadows | Value creation, customer focus, innovation |

### By Analysis Type
| Type | Experts | Mode |
|------|---------|------|
| Comprehensive audit | all | discussion → debate → synthesis |
| Strategic validation | porter, collins, taleb | debate |
| Learning facilitation | drucker, meadows, doumont | socratic |
| Quick assessment | auto-select-3 | discussion --synthesis-only |

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

**Strategy Development**: discussion @market_research → debate @competitive → socratic synthesis → /design strategy
**Innovation Pipeline**: /sc:business-panel --focus innovation → /improve roadmap → /analyze opportunities --think
**Risk Review**: /sc:business-panel --experts taleb,meadows,porter → debate assumptions → /implement mitigation --validate

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

## Quality Standards
- **Authenticity**: Expert voice consistency, framework fidelity, realistic interactions
- **Relevance**: Strategic focus, actionable insights, evidence-based conclusions
- **Integration**: Synthesis > individual analysis, framework distinctiveness preserved

**Performance**: Simple <30s, comprehensive <2min, multi-doc <5min
**Token budgets**: Discussion 8-15K, debate 10-20K, socratic 12-25K, synthesis 3-8K
**Accuracy**: Framework authenticity >90%, relevance >85%, actionable >80%