# Research: Python Directory Naming & Automation Tools (2025)

**Research Date**: 2025-10-14
**Research Context**: PEP 8 directory naming compliance, automated linting tools, and Git case-sensitive renaming best practices

---

## Executive Summary

### Key Findings

1. **PEP 8 Standard (2024-2025)**:
   - Packages (directories): **lowercase only**, underscores discouraged but widely used in practice
   - Modules (files): **lowercase**, underscores allowed and common for readability
   - Current violations: `Developer-Guide`, `Getting-Started`, `User-Guide`, `Reference`, `Templates` (use hyphens/uppercase)

2. **Automated Linting Tool**: **Ruff** is the 2025 industry standard
   - Written in Rust, 10-100x faster than Flake8
   - 800+ built-in rules, replaces Flake8, Black, isort, pyupgrade, autoflake
   - Configured via `pyproject.toml`
   - **BUT**: No built-in rules for directory naming validation

3. **Git Case-Sensitive Rename**: **Two-step `git mv` method**
   - macOS APFS is case-insensitive by default
   - Safest approach: `git mv foo foo-tmp && git mv foo-tmp bar`
   - Alternative: `git rm --cached` + `git add .` (less reliable)

4. **Automation Strategy**: Custom pre-commit hooks + manual rename
   - Use `check-case-conflict` pre-commit hook
   - Write custom Python validator for directory naming
   - Integrate with `validate-pyproject` for configuration validation

5. **Modern Project Structure (uv/2025)**:
   - src-based layout: `src/package_name/` (recommended)
   - Configuration: `pyproject.toml` (universal standard)
   - Lockfile: `uv.lock` (cross-platform, committed to Git)

---

## Detailed Findings

### 1. PEP 8 Directory Naming Conventions

**Official Standard** (PEP 8 - https://peps.python.org/pep-0008/):
> "Python packages should also have short, all-lowercase names, although the use of underscores is discouraged."

**Practical Reality**:
- Underscores are widely used in practice (e.g., `sqlalchemy_searchable`)
- Community doesn't consider underscores poor practice
- **Hyphens are NOT allowed** in package names (Python import restrictions)
- **Camel Case / Title Case = PEP 8 violation**

**Current SuperClaude Framework Violations**:
```yaml
# ❌ PEP 8 Violations
docs/Developer-Guide/     # Contains hyphen + uppercase
docs/Getting-Started/     # Contains hyphen + uppercase
docs/User-Guide/          # Contains hyphen + uppercase
docs/User-Guide-jp/       # Contains hyphen + uppercase
docs/User-Guide-kr/       # Contains hyphen + uppercase
docs/User-Guide-zh/       # Contains hyphen + uppercase
docs/Reference/           # Contains uppercase
docs/Templates/           # Contains uppercase

# ✅ PEP 8 Compliant (Already Fixed)
docs/developer-guide/     # lowercase + hyphen (acceptable for docs)
docs/getting-started/     # lowercase + hyphen (acceptable for docs)
docs/development/         # lowercase only
```

**Documentation Directories Exception**:
- Documentation directories (`docs/`) are NOT Python packages
- Hyphens are acceptable in non-package directories
- Best practice: Use lowercase + hyphens for readability
- Example: `docs/getting-started/`, `docs/user-guide/`

---

### 2. Automated Linting Tools (2024-2025)

#### Ruff - The Modern Standard

**Overview**:
- Released: 2023, rapidly adopted as industry standard by 2024-2025
- Speed: 10-100x faster than Flake8 (written in Rust)
- Replaces: Flake8, Black, isort, pydocstyle, pyupgrade, autoflake
- Rules: 800+ built-in rules
- Configuration: `pyproject.toml` or `ruff.toml`

**Key Features**:
```yaml
Autofix:
  - Automatic import sorting
  - Unused variable removal
  - Python syntax upgrades
  - Code formatting

Per-Directory Configuration:
  - Different rules for different directories
  - Per-file-target-version settings
  - Namespace package support

Exclusions (default):
  - .git, .venv, build, dist, node_modules
  - __pycache__, .pytest_cache, .mypy_cache
  - Custom patterns via glob
```

**Configuration Example** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
target-version = "py38"

exclude = [
    ".git",
    ".venv",
    "build",
    "dist",
]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N"]  # N = naming conventions
ignore = ["E501"]  # Line too long

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports OK in __init__.py
"tests/*" = ["N802"]      # Function name conventions relaxed in tests
```

**Naming Convention Rules** (`N` prefix):
```yaml
N801: Class names should use CapWords convention
N802: Function names should be lowercase
N803: Argument names should be lowercase
N804: First argument of classmethod should be cls
N805: First argument of method should be self
N806: Variable in function should be lowercase
N807: Function name should not start/end with __

BUT: No rules for directory naming (non-Python file checks)
```

**Limitation**: Ruff validates **Python code**, not directory structure.

---

#### validate-pyproject - Configuration Validator

**Purpose**: Validates `pyproject.toml` compliance with PEP standards

**Installation**:
```bash
pip install validate-pyproject
# or with pre-commit integration
```

**Usage**:
```bash
# CLI
validate-pyproject pyproject.toml

# Python API
from validate_pyproject import validate
validate(data)
```

**Pre-commit Hook**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.16
    hooks:
      - id: validate-pyproject
```

**What It Validates**:
- PEP 517/518 build system configuration
- PEP 621 project metadata
- Tool-specific configurations ([tool.ruff], [tool.mypy])
- JSON Schema compliance

**Limitation**: Validates `pyproject.toml` syntax, not directory naming.

---

### 3. Git Case-Sensitive Rename Best Practices

**The Problem**:
- macOS APFS: case-insensitive by default
- Git: case-sensitive internally
- Result: `git mv Foo foo` doesn't work directly
- Risk: Breaking changes across systems

**Best Practice #1: Two-Step git mv (Safest)**

```bash
# Step 1: Rename to temporary name
git mv docs/User-Guide docs/user-guide-tmp

# Step 2: Rename to final name
git mv docs/user-guide-tmp docs/user-guide

# Commit
git commit -m "refactor: rename User-Guide to user-guide (PEP 8 compliance)"
```

**Why This Works**:
- First rename: Different enough for case-insensitive FS to recognize
- Second rename: Achieves desired final name
- Git tracks both renames correctly
- No data loss risk

**Best Practice #2: Cache Clearing (Alternative)**

```bash
# Remove from Git index (keeps working tree)
git rm -r --cached .

# Re-add all files (Git detects renames)
git add .

# Commit
git commit -m "refactor: fix directory naming case sensitivity"
```

**Why This Works**:
- Git re-scans working tree
- Detects same content = rename (not delete + add)
- Preserves file history

**What NOT to Do**:

```bash
# ❌ DANGEROUS: Disabling core.ignoreCase
git config core.ignoreCase false

# Risk: Unexpected behavior on case-insensitive filesystems
# Official docs warning: "modifying this value may result in unexpected behavior"
```

**Advanced Workaround (Overkill)**:
- Create case-sensitive APFS volume via Disk Utility
- Clone repository to case-sensitive volume
- Perform renames normally
- Push to remote

---

### 4. Pre-commit Hooks for Structure Validation

#### Built-in Hooks (check-case-conflict)

**Official pre-commit-hooks** (https://github.com/pre-commit/pre-commit-hooks):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-case-conflict        # Detects case sensitivity issues
      - id: check-illegal-windows-names # Windows filename validation
      - id: check-symlinks             # Symlink integrity
      - id: destroyed-symlinks         # Broken symlinks detection
      - id: check-added-large-files    # Prevent large file commits
      - id: check-yaml                 # YAML syntax validation
      - id: end-of-file-fixer          # Ensure newline at EOF
      - id: trailing-whitespace        # Remove trailing spaces
```

**check-case-conflict Details**:
- Detects files that differ only in case
- Example: `README.md` vs `readme.md`
- Prevents issues on case-insensitive filesystems
- Runs before commit, blocks if conflicts found

**Limitation**: Only detects conflicts, doesn't enforce naming conventions.

---

#### Custom Hook: Directory Naming Validator

**Purpose**: Enforce PEP 8 directory naming conventions

**Implementation** (`scripts/validate_directory_names.py`):

```python
#!/usr/bin/env python3
"""
Pre-commit hook to validate directory naming conventions.
Enforces PEP 8 compliance for Python packages.
"""
import sys
from pathlib import Path
import re

# PEP 8: Package names should be lowercase, underscores discouraged
PACKAGE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*$')

# Documentation directories: lowercase + hyphens allowed
DOC_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9\-]*$')

def validate_directory_names(root_dir='.'):
    """Validate directory naming conventions."""
    violations = []

    root = Path(root_dir)

    # Check Python package directories
    for pydir in root.rglob('__init__.py'):
        package_dir = pydir.parent
        package_name = package_dir.name

        if not PACKAGE_NAME_PATTERN.match(package_name):
            violations.append(
                f"PEP 8 violation: Package '{package_dir}' should be lowercase "
                f"(current: '{package_name}')"
            )

    # Check documentation directories
    docs_root = root / 'docs'
    if docs_root.exists():
        for doc_dir in docs_root.iterdir():
            if doc_dir.is_dir() and doc_dir.name not in ['.git', '__pycache__']:
                if not DOC_NAME_PATTERN.match(doc_dir.name):
                    violations.append(
                        f"Documentation naming violation: '{doc_dir}' should be "
                        f"lowercase with hyphens (current: '{doc_dir.name}')"
                    )

    return violations

def main():
    violations = validate_directory_names()

    if violations:
        print("❌ Directory naming convention violations found:\n")
        for violation in violations:
            print(f"  - {violation}")
        print("\n" + "="*70)
        print("Fix: Rename directories to lowercase (hyphens for docs, underscores for packages)")
        print("="*70)
        return 1

    print("✅ All directory names comply with PEP 8 conventions")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

**Pre-commit Configuration**:

```yaml
# .pre-commit-config.yaml
repos:
  # Official hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-case-conflict
      - id: trailing-whitespace
      - id: end-of-file-fixer

  # Ruff linter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Custom directory naming validator
  - repo: local
    hooks:
      - id: validate-directory-names
        name: Validate Directory Naming
        entry: python scripts/validate_directory_names.py
        language: system
        pass_filenames: false
        always_run: true
```

**Installation**:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks to .git/hooks/
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

---

### 5. Modern Python Project Structure (uv/2025)

#### Standard Layout (uv recommended)

```
project-root/
├── .git/
├── .gitignore
├── .python-version           # Python version for uv
├── pyproject.toml            # Project metadata + tool configs
├── uv.lock                   # Cross-platform lockfile (commit this)
├── README.md
├── LICENSE
├── .pre-commit-config.yaml   # Pre-commit hooks
├── src/                      # Source code (src-based layout)
│   └── package_name/
│       ├── __init__.py
│       ├── module1.py
│       └── subpackage/
│           ├── __init__.py
│           └── module2.py
├── tests/                    # Test files
│   ├── __init__.py
│   ├── test_module1.py
│   └── test_module2.py
├── docs/                     # Documentation
│   ├── getting-started/      # lowercase + hyphens OK
│   ├── user-guide/
│   └── developer-guide/
├── scripts/                  # Utility scripts
│   └── validate_directory_names.py
└── .venv/                    # Virtual environment (local to project)
```

**Key Files**:

**pyproject.toml** (modern standard):
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"  # lowercase, hyphens allowed for non-importable
version = "1.0.0"
requires-python = ">=3.8"

[tool.setuptools.packages.find]
where = ["src"]
include = ["package_name*"]  # lowercase_underscore for Python packages

[tool.ruff]
line-length = 88
target-version = "py38"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N"]
```

**uv.lock**:
- Cross-platform lockfile
- Contains exact resolved versions
- **Must be committed to version control**
- Ensures reproducible installations

**.python-version**:
```
3.12
```

**Benefits of src-based layout**:
1. **Namespace isolation**: Prevents import conflicts
2. **Testability**: Tests import from installed package, not source
3. **Modularity**: Clear separation of application logic
4. **Distribution**: Required for PyPI publishing
5. **Editor support**: .venv in project root helps IDEs find packages

---

## Recommendations for SuperClaude Framework

### Immediate Actions (Required)

#### 1. Complete Git Directory Renames

**Remaining violations** (case-sensitive renames needed):
```bash
# Still need two-step rename due to macOS case-insensitive FS
git mv docs/Reference docs/reference-tmp && git mv docs/reference-tmp docs/reference
git mv docs/Templates docs/templates-tmp && git mv docs/templates-tmp docs/templates
git mv docs/User-Guide docs/user-guide-tmp && git mv docs/user-guide-tmp docs/user-guide
git mv docs/User-Guide-jp docs/user-guide-jp-tmp && git mv docs/user-guide-jp-tmp docs/user-guide-jp
git mv docs/User-Guide-kr docs/user-guide-kr-tmp && git mv docs/user-guide-kr-tmp docs/user-guide-kr
git mv docs/User-Guide-zh docs/user-guide-zh-tmp && git mv docs/user-guide-zh-tmp docs/user-guide-zh

# Update MANIFEST.in to reflect new names
sed -i '' 's/recursive-include Docs/recursive-include docs/g' MANIFEST.in
sed -i '' 's/recursive-include Setup/recursive-include setup/g' MANIFEST.in
sed -i '' 's/recursive-include Templates/recursive-include templates/g' MANIFEST.in

# Verify no uppercase directory references remain
grep -r "Docs\|Setup\|Templates\|Reference\|User-Guide" --include="*.md" --include="*.py" --include="*.toml" --include="*.in" . | grep -v ".git"

# Commit changes
git add .
git commit -m "refactor: complete PEP 8 directory naming compliance

- Rename all remaining capitalized directories to lowercase
- Update MANIFEST.in with corrected paths
- Ensure cross-platform compatibility

Refs: PEP 8 package naming conventions"
```

---

#### 2. Install and Configure Ruff

```bash
# Install ruff
uv pip install ruff

# Add to pyproject.toml (already exists, but verify config)
```

**Verify `pyproject.toml` has**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "ruff>=0.1.0",  # Add if missing
]

[tool.ruff]
line-length = 88
target-version = ["py38", "py39", "py310", "py311", "py312"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "N",   # pep8-naming
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports OK
"tests/*" = ["N802", "N803"]  # Relaxed naming in tests
```

**Run ruff**:
```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

---

#### 3. Set Up Pre-commit Hooks

**Create `.pre-commit-config.yaml`**:
```yaml
repos:
  # Official pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-case-conflict
      - id: check-illegal-windows-names
      - id: check-yaml
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=1000']

  # Ruff linter and formatter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # pyproject.toml validation
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: v0.16
    hooks:
      - id: validate-pyproject

  # Custom directory naming validator
  - repo: local
    hooks:
      - id: validate-directory-names
        name: Validate Directory Naming
        entry: python scripts/validate_directory_names.py
        language: system
        pass_filenames: false
        always_run: true
```

**Install pre-commit**:
```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (initial check)
pre-commit run --all-files
```

---

#### 4. Create Custom Directory Validator

**Create `scripts/validate_directory_names.py`** (see full implementation above)

**Make executable**:
```bash
chmod +x scripts/validate_directory_names.py

# Test manually
python scripts/validate_directory_names.py
```

---

### Future Improvements (Optional)

#### 1. Consider Repository Rename

**Current**: `SuperClaude_Framework`
**PEP 8 Compliant**: `superclaude-framework` or `superclaude_framework`

**Rationale**:
- Package name: `superclaude` (already compliant)
- Repository name: Should match package style
- GitHub allows repository renaming with automatic redirects

**Process**:
```bash
# 1. Rename on GitHub (Settings → Repository name)
# 2. Update local remote
git remote set-url origin https://github.com/SuperClaude-Org/superclaude-framework.git

# 3. Update all documentation references
grep -rl "SuperClaude_Framework" . | xargs sed -i '' 's/SuperClaude_Framework/superclaude-framework/g'

# 4. Update pyproject.toml URLs
sed -i '' 's|SuperClaude_Framework|superclaude-framework|g' pyproject.toml
```

**GitHub Benefits**:
- Old URLs automatically redirect (no broken links)
- Clone URLs updated automatically
- Issues/PRs remain accessible

---

#### 2. Migrate to src-based Layout

**Current**:
```
SuperClaude_Framework/
├── superclaude/          # Package at root
├── setup/                # Package at root
```

**Recommended**:
```
superclaude-framework/
├── src/
│   ├── superclaude/      # Main package
│   └── setup/            # Setup package
```

**Benefits**:
- Prevents accidental imports from source
- Tests import from installed package
- Clearer separation of concerns
- Standard for modern Python projects

**Migration**:
```bash
# Create src directory
mkdir -p src

# Move packages
git mv superclaude src/superclaude
git mv setup src/setup

# Update pyproject.toml
```

```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["superclaude*", "setup*"]
```

**Note**: This is a breaking change requiring version bump and migration guide.

---

#### 3. Add GitHub Actions for CI/CD

**Create `.github/workflows/lint.yml`**:
```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv pip install -e ".[dev]"

      - name: Run pre-commit hooks
        run: |
          uv pip install pre-commit
          pre-commit run --all-files

      - name: Run ruff
        run: |
          ruff check .
          ruff format --check .

      - name: Validate directory naming
        run: python scripts/validate_directory_names.py
```

---

## Summary: Automated vs Manual

### ✅ Can Be Automated

1. **Code linting**: Ruff (autofix imports, formatting, naming)
2. **Configuration validation**: validate-pyproject (pyproject.toml syntax)
3. **Pre-commit checks**: check-case-conflict, trailing-whitespace, etc.
4. **Python naming**: Ruff N-rules (class, function, variable names)
5. **Custom validators**: Python scripts for directory naming (preventive)

### ❌ Cannot Be Fully Automated

1. **Directory renaming**: Requires manual `git mv` (macOS case-insensitive FS)
2. **Directory naming enforcement**: No standard linter rules (need custom script)
3. **Documentation updates**: Link references require manual review
4. **Repository renaming**: Manual GitHub settings change
5. **Breaking changes**: Require human judgment and migration planning

### Hybrid Approach (Best Practice)

1. **Manual**: Initial directory rename using two-step `git mv`
2. **Automated**: Pre-commit hook prevents future violations
3. **Continuous**: Ruff + pre-commit in CI/CD pipeline
4. **Preventive**: Custom validator blocks non-compliant names

---

## Confidence Assessment

| Finding | Confidence | Source Quality |
|---------|-----------|----------------|
| PEP 8 naming conventions | 95% | Official PEP documentation |
| Ruff as 2025 standard | 90% | GitHub stars, community adoption |
| Git two-step rename | 95% | Official docs, Stack Overflow consensus |
| No automated directory linter | 85% | Tool documentation review |
| Pre-commit best practices | 90% | Official pre-commit docs |
| uv project structure | 85% | Official Astral docs, Real Python |

---

## Sources

1. PEP 8 Official Documentation: https://peps.python.org/pep-0008/
2. Ruff Documentation: https://docs.astral.sh/ruff/
3. Real Python - Ruff Guide: https://realpython.com/ruff-python/
4. Git Case-Sensitive Renaming: Multiple Stack Overflow threads (2022-2024)
5. validate-pyproject: https://github.com/abravalheri/validate-pyproject
6. Pre-commit Hooks Guide (2025): https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835
7. uv Documentation: https://docs.astral.sh/uv/
8. Python Packaging User Guide: https://packaging.python.org/

---

## Conclusion

**The Reality**: There is NO fully automated one-click solution for directory renaming to PEP 8 compliance.

**Best Practice Workflow**:

1. **Manual Rename**: Use two-step `git mv` for macOS compatibility
2. **Automated Prevention**: Pre-commit hooks with custom validator
3. **Continuous Enforcement**: Ruff linter + CI/CD pipeline
4. **Documentation**: Update all references (semi-automated with sed)

**For SuperClaude Framework**:
- Complete the remaining directory renames manually (6 directories)
- Set up pre-commit hooks with custom validator
- Configure Ruff for Python code linting
- Add CI/CD workflow for continuous validation

**Total Effort Estimate**:
- Manual renaming: 15-30 minutes
- Pre-commit setup: 15-20 minutes
- Documentation updates: 10-15 minutes
- Testing and verification: 20-30 minutes
- **Total**: 60-95 minutes for complete PEP 8 compliance

**Long-term Benefit**: Prevents future violations automatically, ensuring ongoing compliance.
