# /test - Create and run comprehensive tests

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
Create or run comprehensive test suites for code specified in $ARGUMENTS using modern testing frameworks and methodologies.

## Syntax
`/test [flags] [target]`

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

**Test Types:**
- `--unit`: Unit tests for individual functions and components
- `--integration`: Integration tests for APIs, services, and database interactions
- `--e2e`: End-to-end tests for complete user workflows
- `--performance`: Performance and load testing
- `--security`: Security testing and vulnerability assessment

**Test Execution:**
- `--coverage`: Generate comprehensive code coverage reports
- `--watch`: Continuous test execution on file changes
- `--interactive`: Interactive test runner with real-time feedback
- `--parallel`: Run tests in parallel for faster execution
- `--isolated`: Run tests in isolated environments

**Testing Tools:**
- `--pup`: Browser-based E2E testing with Puppeteer automation
- `--c7`: Testing framework documentation and best practices
- `--seq`: Complex test scenario planning and analysis

**Quality Control:**
- `--strict`: Strict testing mode with enhanced validation
- `--threshold [percent]`: Set minimum coverage threshold (default 80%)
- `--fail-fast`: Stop on first test failure
- `--retry [count]`: Retry failed tests specified number of times

## Examples
- `/test --unit --coverage --watch` → Unit tests with coverage and live updates
- `/test --e2e --pup --think` → E2E tests with Puppeteer and analysis
- `/test --integration --c7 --parallel` → Integration tests with docs and parallel execution
- `/test --performance --threshold 90 --seq` → Performance testing with high coverage threshold
- `/test --security --strict --interactive` → Security testing with strict validation

## Test Types and Implementation

**Unit Tests:**
- Test individual functions, methods, and components in isolation
- Mock external dependencies and services
- Focus on business logic and edge cases
- Ensure fast execution and high reliability
- Cover both happy paths and error conditions

**Integration Tests:**
- Test interactions between components and services
- Verify API contracts and data flow
- Test database operations and transactions
- Validate external service integrations
- Check error handling and recovery mechanisms

**End-to-End Tests:**
- Test complete user workflows and journeys
- Verify critical business paths through application
- Include both success and failure scenarios
- Test across different browsers and devices
- Validate user interface interactions and responses

**Performance Tests:**
- Load testing with realistic user scenarios
- Stress testing to identify breaking points
- Spike testing for traffic surge handling
- Volume testing with large datasets
- Endurance testing for long-running operations

**Security Tests:**
- Vulnerability scanning and penetration testing
- Authentication and authorization testing
- Input validation and injection attack prevention
- Data encryption and privacy protection
- Session management and access control verification

## Pre-Test Setup and Cleanup

**Environment Preparation:**
- Clean test output directories (coverage/, test-results/)
- Remove artifacts from previous test runs
- Reset test databases to clean baseline state
- Clear test cache and temporary files
- Initialize test data and fixtures

**Dependency Management:**
- Install and update testing dependencies
- Configure test environments and settings
- Set up mock services and test doubles
- Prepare test databases and seed data
- Configure network and security settings

## Coverage Analysis (--coverage)

**Coverage Metrics:**
- Line coverage: Percentage of executed code lines
- Branch coverage: Percentage of executed conditional branches
- Function coverage: Percentage of called functions
- Statement coverage: Percentage of executed statements
- Path coverage: Percentage of executed code paths

**Coverage Goals:**
- Aim for >80% overall code coverage
- Focus on critical business logic coverage
- Identify untested code paths and edge cases
- Track coverage trends and improvements
- Generate actionable coverage reports

**Coverage Reports:**
- HTML reports with detailed line-by-line analysis
- JSON reports for programmatic consumption
- XML reports for CI/CD integration
- Summary reports with key metrics
- Trend analysis and historical comparison

## Watch Mode (--watch)

**Continuous Testing:**
- Automatic test execution on file changes
- Smart test selection based on changed files
- Fast feedback loop during development
- Real-time coverage updates
- Efficient resource utilization

**Change Detection:**
- Monitor source code files for modifications
- Track test file changes and updates
- Detect configuration and dependency changes
- Handle file system events efficiently
- Provide clear change notifications

## Interactive Mode (--interactive)

**Interactive Features:**
- Test selection and filtering capabilities
- Real-time test execution and results
- Step-through debugging for failing tests
- Live code coverage visualization
- Dynamic test configuration and options

**User Experience:**
- Clear and intuitive command interface
- Rich output formatting and highlighting
- Progress indicators and status updates
- Error highlighting and debugging aids
- Keyboard shortcuts and navigation

## Testing Best Practices

**Test Structure and Organization:**
- Use descriptive test names explaining what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Group related tests in logical test suites
- Maintain consistent test file organization
- Use clear and readable test code

**Test Independence:**
- Ensure tests can run in any order
- Avoid dependencies between tests
- Clean up test state after each test
- Use fresh test data for each test
- Mock external dependencies appropriately

**Test Data Management:**
- Create reusable test fixtures and factories
- Use meaningful test data that reflects real scenarios
- Maintain test data separately from production data
- Implement data seeding and cleanup procedures
- Version control test data and schemas

**Mocking and Test Doubles:**
- Mock external services and APIs
- Use test doubles for database interactions
- Stub complex dependencies and integrations
- Verify mock interactions and expectations
- Balance mocking with integration testing

## Test Framework Integration

**Supported Frameworks:**
- **Jest**: Modern JavaScript testing framework
- **Mocha/Chai**: Flexible Node.js testing suite
- **Pytest**: Python testing framework
- **JUnit**: Java testing framework
- **RSpec**: Ruby testing framework

**CI/CD Integration:**
- Automated test execution in pipelines
- Test result reporting and notifications
- Coverage threshold enforcement
- Parallel test execution for speed
- Test artifact collection and storage

## Deliverables
- **Test Suites**: Comprehensive test coverage for all specified areas
- **Coverage Reports**: Detailed code coverage analysis and metrics
- **Test Documentation**: Test plans, strategies, and maintenance guides
- **CI/CD Integration**: Automated testing pipeline configuration
- **Performance Baselines**: Performance test results and benchmarks

## Output Locations
- **Coverage Reports**: `coverage/` directory with HTML, JSON, and XML reports
- **Test Results**: `test-results/` directory with detailed test outcomes
- **Performance Reports**: `.claudedocs/metrics/performance-test-{timestamp}.md`
- **Test Documentation**: `.claudedocs/reports/test-strategy-{timestamp}.md`

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

## Quality Assurance Standards

**Test Quality:**
- Tests should be reliable and deterministic
- Avoid flaky tests that pass/fail inconsistently
- Maintain high test code quality standards
- Regular test review and refactoring
- Continuous improvement of test effectiveness

**Coverage Standards:**
- Minimum 80% code coverage for new code
- 100% coverage for critical business logic
- Track and improve coverage over time
- Focus on meaningful coverage, not just metrics
- Regular coverage analysis and reporting

**Performance Standards:**
- Unit tests should execute in milliseconds
- Integration tests should complete within seconds
- E2E tests should finish within reasonable timeframes
- Parallel execution for improved speed
- Regular performance optimization and monitoring

## Troubleshooting
- **Slow Tests**: Use `--parallel` and optimize test performance
- **Flaky E2E Tests**: Apply `--retry` and improve test stability
- **Low Coverage**: Use `--coverage --interactive` for targeted improvement
- **Complex Scenarios**: Combine `--seq --think-hard` for comprehensive planning

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
