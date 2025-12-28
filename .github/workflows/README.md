# GitHub Actions Workflows

This directory contains CI/CD workflows for SuperClaude Framework.

## Workflows

### 1. **test.yml** - Comprehensive Test Suite
**Triggers**: Push/PR to `master` or `integration`, manual dispatch
**Jobs**:
- **test**: Run tests on Python 3.10, 3.11, 3.12
  - Install UV and dependencies
  - Run full test suite
  - Generate coverage report (Python 3.10 only)
  - Upload to Codecov
- **lint**: Run ruff linter and format checker
- **plugin-check**: Verify pytest plugin loads correctly
- **doctor-check**: Run `superclaude doctor` health check
- **test-summary**: Aggregate results from all jobs

**Status Badge**:
```markdown
[![Tests](https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml/badge.svg)](https://github.com/SuperClaude-Org/SuperClaude_Framework/actions/workflows/test.yml)
```

### 2. **quick-check.yml** - Fast PR Feedback
**Triggers**: Pull requests to `master` or `integration`
**Jobs**:
- **quick-test**: Fast check on Python 3.10 only
  - Run unit tests only (faster)
  - Run linter
  - Check formatting
  - Verify plugin loads
  - 10 minute timeout

**Purpose**: Provide rapid feedback on PRs before running full test matrix.

### 3. **publish-pypi.yml** (Existing)
**Triggers**: Manual or release tags
**Purpose**: Publish package to PyPI

### 4. **readme-quality-check.yml** (Existing)
**Triggers**: Push/PR affecting README files
**Purpose**: Validate README quality and consistency

## Local Testing

Before pushing, run these commands locally:

```bash
# Run full test suite
uv run pytest -v

# Run with coverage
uv run pytest --cov=superclaude --cov-report=term

# Run linter
uv run ruff check src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Auto-fix formatting
uv run ruff format src/ tests/

# Verify plugin loads
uv run pytest --trace-config | grep superclaude

# Run doctor check
uv run superclaude doctor --verbose
```

## CI/CD Pipeline

```
┌─────────────────────┐
│   Push/PR Created   │
└──────────┬──────────┘
           │
           ├─────────────────────────┐
           │                         │
    ┌──────▼──────┐         ┌───────▼────────┐
    │ Quick Check │         │  Full Test     │
    │  (PR only)  │         │   Matrix       │
    │             │         │                │
    │ • Unit tests│         │ • Python 3.10  │
    │ • Lint      │         │ • Python 3.11  │
    │ • Format    │         │ • Python 3.12  │
    │             │         │ • Coverage     │
    │ ~2-3 min    │         │ • Lint         │
    └─────────────┘         │ • Plugin check │
                            │ • Doctor check │
                            │                │
                            │ ~5-8 min       │
                            └────────────────┘
```

## Coverage Reporting

Coverage reports are generated for Python 3.10 and uploaded to Codecov.

To view coverage locally:
```bash
uv run pytest --cov=superclaude --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Workflow fails with "UV not found"
- UV is installed in each job via `curl -LsSf https://astral.sh/uv/install.sh | sh`
- If installation fails, check UV's status page

### Tests fail locally but pass in CI (or vice versa)
- Check Python version: `python --version`
- Reinstall dependencies: `uv pip install -e ".[dev]"`
- Clear caches: `rm -rf .pytest_cache .venv`

### Plugin not loading in CI
- Verify entry point in `pyproject.toml`: `[project.entry-points.pytest11]`
- Check plugin is installed: `uv run pytest --trace-config`

### Coverage upload fails
- This is non-blocking (fail_ci_if_error: false)
- Check Codecov token in repository secrets

## Maintenance

### Adding a New Workflow
1. Create new `.yml` file in this directory
2. Follow existing structure (checkout, setup-python, install UV)
3. Add status badge to README.md if needed
4. Document in this file

### Updating Python Versions
1. Edit `matrix.python-version` in `test.yml`
2. Update `pyproject.toml` classifiers
3. Test locally with new version first

### Modifying Test Strategy
- **quick-check.yml**: For fast PR feedback (unit tests only)
- **test.yml**: For comprehensive validation (full matrix)

## Best Practices

1. **Keep workflows fast**: Use caching, parallel jobs
2. **Fail fast**: Use `-x` flag in pytest for quick-check
3. **Clear names**: Job and step names should be descriptive
4. **Version pinning**: Pin action versions (@v4, @v5)
5. **Matrix testing**: Test on multiple Python versions
6. **Non-blocking coverage**: Don't fail on coverage upload errors
7. **Manual triggers**: Add `workflow_dispatch` for debugging

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Pytest Documentation](https://docs.pytest.org/)
- [SuperClaude Testing Guide](../../docs/developer-guide/testing-debugging.md)
