# Testing & Quality Assurance

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Create or run comprehensive tests for code in $ARGUMENTS.

Thinking flags (optional):
- --think→multi-component test planning
- --think-hard→complex test arch & strategy
- --ultrathink→comprehensive test system design

MCP flags (optional):
- --pup→browser-based E2E testing w/ Puppeteer | --c7→testing framework docs
- --seq→complex test scenario planning | --no-mcp→native test runners only

Examples:
- `/user:test --e2e --pup --think` - E2E tests w/ Puppeteer & context analysis
- `/user:test --coverage --c7` - Test w/ framework docs support
- `/user:test --integration --seq --think-hard` - Complex test scenarios w/ deep planning

Pre-test cleanup:
- Clean test output dirs (coverage/, test-results/) | Remove test artifacts from previous runs
- Reset test DB/state→clean baseline | Clear test cache & temp files

When --coverage flag is present:
- Generate comprehensive coverage reports
- Identify untested code paths
- Aim for >80% code coverage
- Focus on critical business logic

When --watch flag is present:
- Set up automatic test execution on file changes
- Provide fast feedback during development
- Only run affected tests for efficiency
- Continuous integration during development

When --interactive flag is present:
- Interactive test runner with real-time feedback
- Allow test selection and filtering
- Step-through debugging for failing tests
- Live code coverage visualization

When --e2e flag is present:
- Create end-to-end tests for user flows
- Test critical paths through the application
- Include both happy paths and error scenarios
- Use appropriate E2E testing frameworks

Test types to implement:
- Unit tests: Test individual functions, logic, and utilities in isolation
- Integration tests: Test APIs, services, and database interactions
- E2E tests: Test complete user workflows and critical paths

## Testing Best Practices

Follow testing standards:
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Use appropriate mocking for external dependencies
- Create fixtures for consistent test data
- Ensure tests are independent and can run in any order

@include shared/command-templates.yml#Research_Requirements

@include shared/command-templates.yml#Report_Output

@include shared/constants.yml#Success_Messages