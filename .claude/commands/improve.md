# /improve - Enhance code quality, performance and architecture

## Legend
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

## Purpose
Enhance code quality, performance, and architecture for systems specified in $ARGUMENTS using systematic improvement methodologies.

## Syntax
`/improve [flags] [target]`

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

## Command-Specific Flags

**Improvement Focus:**
- `--quality`: Code structure, maintainability, and clean code principles
- `--performance`: System performance, bottlenecks, and optimization
- `--security`: Security improvements and vulnerability fixes
- `--architecture`: System design and architectural improvements
- `--ux`: User experience and interface improvements

**Quality Enhancements:**
- `--solid`: Apply SOLID principles systematically
- `--refactor`: Clean code refactoring with modern patterns
- `--metrics`: Generate comprehensive quality metrics
- `--coverage`: Improve test coverage and quality

**Performance Optimization:**
- `--profile`: Performance profiling and bottleneck analysis
- `--cache`: Implement caching strategies
- `--async`: Optimize for asynchronous operations
- `--database`: Database query and schema optimization

**Execution Modes:**
- `--iterate`: Iterative improvement until threshold reached
- `--threshold [percent]`: Set target improvement percentage (default 85%)
- `--watch`: Continuous improvement monitoring
- `--interactive`: Guided improvement with user choices

## Examples
- `/improve --quality --solid --metrics` → Code quality with SOLID principles
- `/improve --performance --profile --cache` → Performance optimization with caching
- `/improve --iterate --threshold 90 --interactive` → Iterative improvement to 90%
- `/improve --security --architecture --seq` → Security and architecture analysis
- `/improve --ux --performance --watch` → UX and performance with monitoring

## Code Quality Mode (--quality)

**SOLID Principles Application:**
- **Single Responsibility**: One class, one clear purpose
- **Open/Closed**: Extensible without modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Specific over general interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

**Refactoring Techniques:**
- Extract methods and classes for complex logic
- Inline unnecessary abstractions
- Rename variables and functions for clarity
- Move code to appropriate modules
- Remove duplication (DRY principle)
- Simplify conditionals and loops
- Reduce coupling, increase cohesion

**Quality Metrics Tracking:**
- Cyclomatic complexity (target < 5)
- Method/function length (target < 20 lines)
- Class cohesion and coupling metrics
- Code duplication percentage
- Test coverage (target > 80%)
- Documentation completeness
- Technical debt assessment

**Clean Code Principles:**
- Meaningful, self-documenting names
- Functions that do one thing well
- Consistent coding style and formatting
- Proper error handling and logging
- Elimination of magic numbers and strings
- Comments that explain why, not what

## Performance Mode (--performance)

**Code Optimization:**
- Algorithm complexity reduction (O(n²) → O(n log n))
- Efficient data structures selection
- Caching frequently accessed data
- Lazy loading and pagination strategies
- Asynchronous and parallel processing
- Memory usage optimization

**Database Optimization:**
- Query optimization and proper indexing
- N+1 query elimination
- Connection pooling implementation
- Batch operations for bulk updates
- Strategic denormalization
- Query result caching

**Frontend Optimization:**
- Bundle size reduction and tree shaking
- Code splitting and lazy loading
- Image and asset optimization
- Render performance improvements
- Service worker caching strategies
- React/Vue re-render optimization

**System Optimization:**
- Load balancing strategies
- CDN implementation and optimization
- Compression (gzip/brotli)
- HTTP/2 and proper caching headers
- Resource pooling and connection management
- Microservice communication optimization

## Iterative Mode (--iterate)

**Improvement Process:**

**1. Baseline Measurement:**
- Current performance metrics
- Code quality scores
- Test coverage percentage
- User experience metrics
- System reliability indicators

**2. Targeted Improvements:**
- Identify highest impact areas (80/20 rule)
- Prioritize improvements by ROI
- Make incremental, measurable changes
- Maintain working state throughout

**3. Progress Tracking:**
- Measure improvement after each iteration
- Document changes and their impact
- Calculate return on investment
- Adjust strategy based on results

**4. Completion Criteria:**
- Target threshold achievement
- Diminishing returns detection
- Time or budget constraints
- "Good enough" quality level

**Focus Areas by Type:**
- **Quality**: Complexity reduction, duplication removal, coverage increase
- **Performance**: Response time, throughput, resource utilization
- **User Experience**: Load time, responsiveness, error reduction
- **Maintainability**: Documentation, test quality, code structure

## Architecture Improvements (--architecture)

**Design Patterns:**
- Apply appropriate design patterns
- Implement dependency injection
- Use domain-driven design principles
- Implement proper separation of concerns

**System Architecture:**
- Microservices decomposition
- Event-driven architecture
- CQRS implementation where appropriate
- API design and optimization

**Scalability Enhancements:**
- Horizontal scaling strategies
- Database sharding and replication
- Caching layer implementation
- Load balancing optimization

## Deliverables
- **Improvement Reports**: Detailed analysis of changes and their impact
- **Quality Metrics**: Before/after comparison of quality indicators
- **Performance Benchmarks**: Speed and efficiency improvements
- **Refactored Code**: Clean, optimized, and maintainable codebase
- **Documentation**: Updated docs reflecting improvements

## Output Locations
- **Reports**: `.claudedocs/metrics/improvement-{type}-{timestamp}.md`
- **Benchmarks**: `.claudedocs/metrics/performance-{timestamp}.json`
- **Quality Metrics**: `.claudedocs/metrics/quality-{timestamp}.md`

## Research Requirements
External_Library_Research:
  - Identify library/framework mentioned
  - Context7 lookup for official documentation
  - Verify API patterns and examples
  - Check version compatibility
  - Document findings in implementation
Pattern_Research:
  - Search existing codebase for similar patterns
  - Magic component search if UI-related
  - WebSearch for official documentation
  - Validate approach with Sequential thinking
  - Document pattern choice rationale
API_Integration_Research:
  - Official documentation lookup
  - Authentication requirements
  - Rate limiting and error handling
  - SDK availability and examples
  - Integration testing approach

## Report Notifications
📄 Analysis report saved to: {path}
📊 Metrics updated: {path}
📋 Summary saved to: {path}
💾 Checkpoint created: {path}
📚 Documentation created: {path}
📁 Created directory: {path}
✅ {operation} completed successfully
❌ {operation} failed: {reason}
⚠ {operation} completed w/ warnings

## Best Practices

**Improvement Methodology:**
1. **Measure Before Changing**: Establish baseline metrics
2. **Focus on Bottlenecks**: Address highest impact issues first
3. **Incremental Changes**: Make one improvement at a time
4. **Verify Improvements**: Validate changes with metrics
5. **Document Changes**: Record what was changed and why
6. **Consider Trade-offs**: Balance competing concerns

**Common Pitfalls to Avoid:**
- Premature optimization without profiling
- Over-engineering simple solutions
- Breaking changes without proper testing
- Ignoring existing test suite
- Gold-plating beyond requirements

**Balance Considerations:**
- Performance vs code readability
- Flexibility vs simplicity
- Speed vs correctness
- Present needs vs future scalability

## Common Improvement Scenarios

### Code Quality Issues
```bash
/improve --quality --solid --metrics --dry-run
# → Identifies SOLID principle violations
# → Suggests refactoring for better modularity
# → Measures complexity metrics before/after changes
```

### Performance Bottlenecks
```bash
/improve --performance --iterate --threshold 90%
# → Profiles CPU and memory usage patterns
# → Implements algorithmic optimizations
# → Continues until 90% performance threshold met
```

### Technical Debt Reduction
```bash
/improve --quality --iterate --technical-debt
# → Identifies code duplication and anti-patterns
# → Suggests consolidation opportunities
# → Implements incremental refactoring strategy
```

### Error Handling Enhancement
```bash
/improve --resilience --error-handling --comprehensive
# → Reviews exception handling patterns
# → Implements proper logging and monitoring
# → Adds circuit breakers and retry mechanisms
```

## Troubleshooting
- **Complex Codebases**: Use `--iterate --interactive` for guided improvements
- **Performance Issues**: Combine `--performance --profile --seq` for deep analysis
- **Quality Problems**: Apply `--quality --solid --metrics` for comprehensive fixes
- **Architecture Concerns**: Use `--architecture --think-hard` for system-wide improvements

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
