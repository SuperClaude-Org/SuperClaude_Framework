**Purpose**: Database and code migration management

---

@include shared/universal-constants.yml#Universal_Legend

## Command Execution
Execute: immediate. --plan→show plan first
Legend: Generated based on symbols used in command
Purpose: "[Action][Subject] in $ARGUMENTS"

Execute database and code migrations for $ARGUMENTS.

## Purpose
Execute comprehensive database or code migrations based on specifications in $ARGUMENTS with safety checks and rollback capabilities.

## Syntax
`/migrate [flags] [migration-spec]`

@include shared/flag-inheritance.yml#Universal_Always

## Core Flags

--type flag:
- database: SQL schema migrations
- code: Codebase refactoring
- api: API version migration
- data: Data transformation
- full: Complete system migration

--direction flag:
- up: Apply migrations forward
- down: Rollback migrations
- status: Check migration state
- validate: Test without applying

--target flag:
- latest: All pending migrations
- version: Specific version
- step: Number of migrations
- timestamp: Up to date/time

## Migration Types

Database Migrations:
- Schema changes (add/drop tables)
- Column modifications
- Index optimization
- Constraint updates
- Data transformations

Code Migrations:
- API version updates
- Framework upgrades
- Dependency updates
- Structure refactoring
- Pattern modernization

Data Migrations:
- Format conversions
- Bulk transformations
- ETL operations
- Cleanup operations
- Normalization

## Safety Features

Pre-Migration:
- Backup current state
- Validate migration files
- Check dependencies
- Test in transaction
- Estimate impact

During Migration:
- Transaction wrapping
- Progress tracking
- Error handling
- Partial rollback
- Health checks

Post-Migration:
- Verify integrity
- Update documentation
- Clear caches
- Run tests
- Monitor performance

## Migration Workflow

1. Analysis Phase:
   - Scan current state
   - Identify changes needed
   - Generate migration plan
   - Estimate risks

2. Preparation Phase:
   - Create backups
   - Prepare rollback plan
   - Set up monitoring
   - Notify stakeholders

3. Execution Phase:
   - Run migrations
   - Track progress
   - Handle errors
   - Apply fixes

4. Validation Phase:
   - Verify success
   - Run test suite
   - Check performance
   - Update docs

## Best Practices

Safety:
- Always backup first
- Test in staging
- Use transactions
- Plan rollbacks
- Monitor closely

Performance:
- Batch operations
- Off-peak execution
- Index management
- Query optimization
- Resource limits

## Examples

```bash
# Database migration to latest
/migrate --type database --direction up

# Rollback last 2 migrations
/migrate --type database --direction down --step 2

# Code migration with validation
/migrate --type code --validate --think

# Full system migration plan
/migrate --type full --plan --ultrathink
```

## Deliverables

- Migration scripts
- Rollback procedures
- Execution logs
- Validation reports
- Updated documentation
- Performance metrics