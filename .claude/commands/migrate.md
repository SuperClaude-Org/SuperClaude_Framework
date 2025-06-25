# Database & Code Migration

@include shared/constants.yml#Process_Symbols

@include shared/command-templates.yml#Universal_Flags

Execute comprehensive DB or code migration based on specs in $ARGUMENTS.

Thinking flags (optional):
- --think→multi-system migration coordination
- --think-hard→complex data transformation & rollback planning
- --ultrathink→enterprise-scale migration w/ zero-downtime requirements

Examples:
- `/user:migrate --dry-run --think` - Migration preview w/ impact analysis
- `/user:migrate --think-hard` - Complex migration w/ comprehensive safety planning
- `/user:migrate --rollback --ultrathink` - Critical rollback w/ full system analysis

Migration types:

Schema migrations:
- Create, alter, or drop tables | Add or modify indexes→perf
- Update constraints & relationships | Manage DB versioning

Data migrations:
- Transform existing data→new format | Backfill missing or derived data
- Clean up obsolete or orphaned records | Ensure data integrity throughout

Code migrations:
- Refactor→new patterns or arch
- Update to new framework versions
- Migrate between different technologies
- Modernize legacy code

Follow the safe migration workflow:
1. Plan - Design migration strategy and rollback plan
2. Backup - Create full backup of affected data/code
3. Test - Run migration in test environment first
4. Execute - Apply migration with transaction support
5. Verify - Validate migration success and data integrity

When --dry-run flag is present:
- Preview all changes without executing
- Show affected records/files count
- Estimate migration duration
- Identify potential issues

When --rollback flag is present:
- Revert to pre-migration state
- Use transaction rollback when possible
- Restore from backup if needed
- Verify system stability

## Safety Measures & Best Practices

Safety measures:
- Use database transactions for atomicity
- Calculate checksums for data validation
- Implement idempotent migrations
- Test rollback procedure before execution
- Monitor system during migration

Research requirements for migration:
- Database patterns → C7 documentation for database-specific migration patterns
- Framework migrations → Must verify with official migration guides and best practices
- Data transformation → Research ETL patterns and data integrity verification methods
- Zero-downtime patterns → WebSearch for platform-specific blue-green migration strategies
- Never migrate without tested rollback - always verify migration patterns
- All migration scripts must cite sources: // Source: [migration guide reference]

Report Output:
- Migration logs: `.claudedocs/reports/migration-<timestamp>.md`
- Data integrity reports: `.claudedocs/metrics/data-validation-<timestamp>.md`
- Rollback procedures: `.claudedocs/summaries/rollback-plan-<timestamp>.md`
- Ensure directory exists: `mkdir -p .claudedocs/reports/ .claudedocs/metrics/ .claudedocs/summaries/`
- Include report location in output: "📄 Migration report saved to: [path]"

Deliverables: Migration script with rollback capability, execution report with statistics, backup confirmation, data integrity verification, and rollback procedure documentation.