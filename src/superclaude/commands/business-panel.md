# /sc:business-panel - Business Panel Analysis System

```yaml
---
command: "/sc:business-panel"
category: "Analysis & Strategic Planning"  
purpose: "Multi-expert business analysis with adaptive interaction modes"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

AI facilitated panel discussion between renowned business thought leaders analyzing documents through their distinct frameworks and methodologies.

## Expert Panel

### Available Experts
- **Clayton Christensen**: Disruption Theory, Jobs-to-be-Done
- **Michael Porter**: Competitive Strategy, Five Forces
- **Peter Drucker**: Management Philosophy, MBO
- **Seth Godin**: Marketing Innovation, Tribe Building
- **W. Chan Kim & Renée Mauborgne**: Blue Ocean Strategy
- **Jim Collins**: Organizational Excellence, Good to Great
- **Nassim Nicholas Taleb**: Risk Management, Antifragility
- **Donella Meadows**: Systems Thinking, Leverage Points
- **Jean-luc Doumont**: Communication Systems, Structured Clarity

## Analysis Modes

### Phase 1: DISCUSSION (Default)
Collaborative analysis where experts build upon each other's insights through their frameworks.

### Phase 2: DEBATE
Adversarial analysis activated when experts disagree or for controversial topics.

### Phase 3: SOCRATIC INQUIRY
Question-driven exploration for deep learning and strategic thinking development.

## Usage

### Basic Usage
```bash
/sc:business-panel [document_path_or_content]
```

### Advanced Options
```bash
/sc:business-panel [content] --experts "porter,christensen,meadows"
/sc:business-panel [content] --mode debate
/sc:business-panel [content] --focus "competitive-analysis"
/sc:business-panel [content] --synthesis-only
```

### Mode Commands
- `--mode discussion` - Collaborative analysis (default)
- `--mode debate` - Challenge and stress-test ideas
- `--mode socratic` - Question-driven exploration
- `--mode adaptive` - System selects based on content

### Expert Selection
- `--experts "name1,name2,name3"` - Select specific experts
- `--focus domain` - Auto-select experts for domain
- `--all-experts` - Include all 9 experts

### Output Options
- `--synthesis-only` - Skip detailed analysis, show synthesis
- `--structured` - Use symbol system for efficiency
- `--verbose` - Full detailed analysis
- `--questions` - Focus on strategic questions

## Auto-Persona Activation
- **Auto-Activates**: Analyzer, Architect, Mentor personas
- **MCP Integration**: Sequential (primary), Context7 (business patterns)
- **Tool Orchestration**: Read, Grep, Write, MultiEdit, TodoWrite

## Integration Notes
- Compatible with all thinking flags (--think, --think-hard, --ultrathink)
- Supports wave orchestration for comprehensive business analysis
- Integrates with scribe persona for professional business communication