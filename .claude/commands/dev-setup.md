# /dev-setup - Configure development environment and CI/CD

@include shared/universal-constants.yml#Universal_Legend

## Purpose
Configure comprehensive development environments and CI/CD pipelines based on project requirements in $ARGUMENTS.

## Syntax
`/dev-setup [flags] [target]`

@include shared/flag-inheritance.yml#Universal_Always

Thinking flags (optional):
- --think→environment configuration & dependency analysis
- --think-hard→complex CI/CD pipelines & multi-stage builds
- --ultrathink→complete development ecosystem design

## Core Flags

--type flag:
- node: Node.js/TypeScript project setup
- python: Python virtual environment & tooling
- react: React + Vite/Next.js configuration
- fullstack: Complete full-stack environment
- monorepo: Multi-package monorepo setup

--ci flag:
- github: GitHub Actions workflows
- gitlab: GitLab CI/CD pipelines
- jenkins: Jenkins pipeline configuration
- circleci: CircleCI configuration
- custom: Custom CI/CD solution

--tools flag:
- Include dev tools: linters, formatters, pre-commit hooks
- Configure VS Code settings & extensions
- Setup debugging configurations
- Install recommended tooling

## Setup Components

Environment Configuration:
- Package manager setup (npm/yarn/pnpm)
- Version management (.nvmrc, .python-version)
- Environment variables & .env structure
- Docker configuration if needed

Code Quality:
- ESLint/Prettier configuration
- Pre-commit hooks (husky, lint-staged)
- Test framework setup (Jest, Pytest, etc)
- Code coverage configuration

CI/CD Pipeline:
- Build & test workflows
- Deployment configurations
- Security scanning (SAST/DAST)
- Dependency vulnerability checks
- Release automation

Development Tools:
- VS Code workspace settings
- Debug configurations
- Task runners & scripts
- Documentation generation

## Best Practices

Security:
- Never commit secrets or credentials
- Use environment variables for sensitive data
- Configure security scanning in CI
- Implement dependency vulnerability checks

Performance:
- Cache dependencies in CI
- Parallelize test execution
- Optimize build processes
- Use appropriate resource limits

Maintainability:
- Consistent tooling across team
- Clear documentation
- Automated quality checks
- Reproducible environments

## Examples

```bash
# Node.js project with GitHub Actions
/dev-setup --type node --ci github --tools

# Python project with comprehensive tooling
/dev-setup --type python --tools --think

# Full-stack monorepo with GitLab CI
/dev-setup --type monorepo --ci gitlab --think-hard

# React project with all quality tools
/dev-setup --type react --tools --ci github
```

## Deliverables

- Complete environment configuration files
- CI/CD pipeline definitions
- Development tool configurations
- Setup documentation & README updates
- Scripts for common development tasks