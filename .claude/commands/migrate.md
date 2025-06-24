# /migrate - Execute database and code migrations

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
Execute comprehensive database or code migrations based on specifications in $ARGUMENTS with safety checks and rollback capabilities.

## Syntax
`/migrate [flags] [migration-spec]`

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

**Migration Types:**
- `--schema`: Database schema migrations (tables, indexes, constraints)
- `--data`: Data transformation and migration operations
- `--code`: Code refactoring and modernization migrations
- `--framework`: Framework or library version migrations
- `--config`: Configuration and environment migrations

**Execution Control:**
- `--dry-run`: Preview changes without execution
- `--rollback`: Revert to pre-migration state
- `--checkpoint`: Create checkpoint before migration
- `--force`: Override safety checks (use with caution)

**Safety & Validation:**
- `--backup`: Create full backup before migration
- `--validate`: Validate migration integrity and consistency
- `--test-mode`: Run in isolated test environment
- `--zero-downtime`: Implement zero-downtime migration strategy

**Monitoring:**
- `--progress`: Show detailed progress during migration
- `--log-level [level]`: Set logging verbosity (info|debug|trace)
- `--timeout [seconds]`: Set maximum migration duration

## Examples
- `/migrate --schema --dry-run --think` → Schema migration preview with analysis
- `/migrate --data --backup --validate --think-hard` → Data migration with safety checks
- `/migrate --framework --zero-downtime --ultrathink` → Framework upgrade with zero downtime
- `/migrate --rollback --checkpoint restore-20240115` → Rollback to specific checkpoint
- `/migrate --code --test-mode --progress` → Code migration in test environment

## Migration Types

**Schema Migrations:**
- Create, alter, or drop database tables
- Add or modify indexes for performance
- Update constraints and relationships
- Manage database versioning and compatibility
- Handle foreign key dependencies

**Data Migrations:**
- Transform existing data to new formats
- Backfill missing or derived data fields
- Clean up obsolete or orphaned records
- Ensure referential integrity throughout process
- Handle large dataset migrations efficiently

**Code Migrations:**
- Refactor to new architectural patterns
- Update to new framework versions
- Migrate between different technologies
- Modernize legacy code and patterns
- Update API contracts and interfaces

**Framework Migrations:**
- Upgrade major framework versions
- Migrate between competing frameworks
- Update dependency chains
- Handle breaking changes systematically
- Maintain backward compatibility where possible

## Safe Migration Workflow

**1. Planning Phase:**
- Analyze migration requirements and scope
- Design migration strategy and approach
- Create comprehensive rollback plan
- Identify dependencies and prerequisites
- Estimate duration and resource requirements

**2. Preparation Phase:**
- Create full backup of affected systems
- Set up isolated test environment
- Prepare migration scripts and procedures
- Validate rollback procedures
- Notify stakeholders and schedule downtime

**3. Testing Phase:**
- Run migration in test environment
- Validate data integrity and functionality
- Test rollback procedures
- Performance test with realistic data
- Document any issues and resolutions

**4. Execution Phase:**
- Apply migration with transaction support
- Monitor system performance and health
- Track progress and log all operations
- Handle errors gracefully with fallbacks
- Maintain communication with stakeholders

**5. Verification Phase:**
- Validate migration success and completeness
- Verify data integrity with checksums
- Run comprehensive test suite
- Monitor system stability post-migration
- Document lessons learned and improvements

## Dry Run Operations (--dry-run)

**Preview Capabilities:**
- Show all changes without executing them
- Display affected records and files count
- Estimate migration duration and resource usage
- Identify potential issues and conflicts
- Generate detailed execution plan

**Risk Assessment:**
- Analyze impact on system performance
- Identify data integrity risks
- Assess rollback complexity
- Evaluate downtime requirements
- Calculate resource utilization

## Rollback Operations (--rollback)

**Rollback Strategies:**
- Transaction-based rollback for database changes
- Backup restoration for complex changes
- Code version control reversion
- Configuration rollback procedures
- Progressive rollback for staged migrations

**Rollback Verification:**
- Verify system returns to pre-migration state
- Validate data integrity after rollback
- Test system functionality completely
- Monitor performance and stability
- Document rollback effectiveness

## Zero-Downtime Migrations (--zero-downtime)

**Strategies:**
- Blue-green deployment patterns
- Rolling updates with health checks
- Shadow migration and cutover
- Feature flags for gradual rollout
- Database read replica promotion

**Implementation:**
- Maintain dual-write compatibility
- Implement backward-compatible schemas
- Use load balancers for traffic switching
- Monitor key metrics during transition
- Prepare instant rollback mechanisms

## Safety Measures

**Data Protection:**
- Automatic backup creation before migration
- Transaction atomicity for database operations
- Checksum validation for data integrity
- Idempotent migration scripts
- Recovery point objectives (RPO) compliance

**System Protection:**
- Resource usage monitoring and limits
- Timeout protection for long operations
- Health checks and circuit breakers
- Progressive execution with validation
- Automated rollback triggers

## Deliverables
- **Migration Scripts**: Complete, tested migration procedures
- **Execution Report**: Detailed migration statistics and outcomes
- **Backup Confirmation**: Verified backup creation and integrity
- **Data Integrity Report**: Validation of data consistency post-migration
- **Rollback Procedures**: Documented and tested rollback plans
- **Performance Metrics**: Before/after performance comparisons

## Output Locations
- **Migration Logs**: `.claudedocs/reports/migration-{timestamp}.md`
- **Data Validation**: `.claudedocs/metrics/data-validation-{timestamp}.md`
- **Rollback Plans**: `.claudedocs/summaries/rollback-plan-{timestamp}.md`
- **Performance Reports**: `.claudedocs/metrics/migration-performance-{timestamp}.md`

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

**Planning:**
- Always test migrations in staging environment
- Create detailed rollback plans before execution
- Communicate with stakeholders about timing
- Plan for peak and off-peak execution windows
- Document all migration decisions and rationale

**Execution:**
- Use transactions for atomicity where possible
- Monitor system health throughout migration
- Keep detailed logs of all operations
- Have rollback procedures ready and tested
- Validate data integrity at each step

**Post-Migration:**
- Verify system functionality completely
- Monitor performance for regression
- Clean up temporary migration artifacts
- Update documentation and procedures
- Conduct post-mortem for improvement

## Troubleshooting
- **Large Datasets**: Use `--progress --timeout` for monitoring
- **Complex Dependencies**: Apply `--think-hard` for comprehensive planning
- **Production Systems**: Combine `--zero-downtime --backup --validate`
- **Failed Migrations**: Use `--rollback` with specific checkpoint

## Success Messages
✅ {operation} completed successfully
📝 Created: {file_path}
✏ Updated: {file_path}
✨ Task completed: {task_title}
