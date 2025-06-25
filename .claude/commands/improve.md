# Code & Performance Optimization

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Improve code, perf, or quality of system specified in $ARGUMENTS.

Improvement focus w/ flags:

--quality flag:
- Improve code structure & maintainability
- w/ --solid: Apply SOLID principles systematically | w/ --refactor: Clean code refactoring
- w/ --metrics: Generate quality metrics report

--perf flag:
- Optimize system perf | Analyze bottlenecks & resource usage
- Impl caching & async ops | Improve algorithm complexity

--iterate flag:
- Iteratively improve until threshold reached | w/ --threshold: Set target % (default 85%)
- Measure progress after each iteration | Stop at diminishing returns

--watch flag:
- Continuous improvement monitoring | Auto-apply safe optimizations
- Real-time perf tracking | Automated quality maintenance

When --interactive flag is present:
- Guided improvement process
- User choice on optimization strategies
- Step-by-step quality enhancement
- Interactive threshold adjustment

## Code Quality Mode (--quality)

SOLID Principles application:
- **Single Responsibility**: One class, one purpose
- **Open/Closed**: Extensible but not modifiable
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Specific over general interfaces
- **Dependency Inversion**: Depend on abstractions

Refactoring techniques:
- Extract method/class for complex logic
- Inline unnecessary abstractions
- Rename for clarity and consistency
- Move code to appropriate modules
- Remove duplication (DRY principle)
- Simplify conditionals and loops
- Reduce coupling, increase cohesion

Quality metrics to track:
- Cyclomatic complexity (target < 5)
- Method length (target < 20 lines)
- Class cohesion and coupling
- Code duplication percentage
- Test coverage (target > 80%)
- Documentation completeness

Clean code principles:
- Meaningful, self-documenting names
- Functions do one thing well
- Consistent coding style
- Proper error handling
- No magic numbers/strings
- Comments explain why, not what

## Performance Mode (--performance)

Performance optimization areas:

**Code optimization**:
- Algorithm complexity reduction (O(n²) → O(n log n))
- Efficient data structures
- Caching frequently accessed data
- Lazy loading and pagination
- Async/parallel processing
- Memory usage optimization

**Database optimization**:
- Query optimization and indexing
- N+1 query elimination
- Connection pooling
- Batch operations
- Denormalization where appropriate
- Query result caching

**Frontend optimization**:
- Bundle size reduction
- Code splitting and lazy loading
- Image and asset optimization
- Render performance improvements
- Service worker caching
- Reducing re-renders

**System optimization**:
- Load balancing strategies
- CDN implementation
- Compression (gzip/brotli)
- HTTP/2 and caching headers
- Resource pooling
- Microservice optimization

## Iterative Mode (--iterate)

Iteration process:
1. **Baseline Measurement**
   - Current performance metrics
   - Quality scores
   - Coverage percentage
   - User satisfaction

2. **Targeted Improvements**
   - Focus on highest impact areas
   - Apply 80/20 rule
   - Make incremental changes
   - Maintain working state

3. **Progress Tracking**
   - Measure after each change
   - Document improvements
   - Calculate ROI of changes
   - Adjust strategy as needed

4. **Completion Criteria**
   - Reach target threshold
   - Diminishing returns detected
   - Time/budget constraints
   - "Good enough" achieved

Focus areas by iteration type:
- **Quality**: Complexity, duplication, coverage
- **Performance**: Response time, throughput, resources
- **User Experience**: Load time, responsiveness, errors
- **Maintainability**: Documentation, tests, structure

## Best Practices

General improvement approach:
1. Measure before changing
2. Focus on bottlenecks first
3. Make one change at a time
4. Verify improvements
5. Document changes made
6. Consider trade-offs

Avoid common pitfalls:
- Premature optimization
- Over-engineering
- Breaking changes
- Ignoring tests
- Gold-plating

Balance considerations:
- Performance vs readability
- Flexibility vs simplicity
- Speed vs correctness
- Present vs future needs

@include shared/command-templates.yml#Research_Requirements

@include shared/command-templates.yml#Report_Output

@include shared/constants.yml#Success_Messages