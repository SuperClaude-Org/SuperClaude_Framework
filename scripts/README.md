# SuperClaude PyPI Publishing Scripts

This directory contains scripts for building and publishing SuperClaude to PyPI.

## Scripts

### `publish.sh` - Main Publishing Script
Easy-to-use shell script for common publishing tasks:

```bash
# Test upload to TestPyPI
./scripts/publish.sh test

# Test installation from TestPyPI
./scripts/publish.sh test-install

# Production upload to PyPI
./scripts/publish.sh prod

# Build package only
./scripts/publish.sh build

# Clean build artifacts
./scripts/publish.sh clean

# Validate project structure
./scripts/publish.sh check
```

### `build_and_upload.py` - Advanced Build Script
Python script with detailed control over the build and upload process:

```bash
# Build and upload to TestPyPI
python scripts/build_and_upload.py --testpypi

# Test installation from TestPyPI
python scripts/build_and_upload.py --testpypi --test-install

# Production upload (with confirmation)
python scripts/build_and_upload.py

# Skip validation (for faster builds)
python scripts/build_and_upload.py --skip-validation --testpypi

# Clean only
python scripts/build_and_upload.py --clean
```

## Prerequisites

1. **PyPI Account**: Register at https://pypi.org/account/register/
2. **API Tokens**: Generate tokens at https://pypi.org/manage/account/
3. **Configuration**: Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-[your-production-token]
   
   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-[your-test-token]
   ```

## GitHub Actions

The `.github/workflows/publish-pypi.yml` workflow automates publishing:

- **Automatic**: Publishes to PyPI when a GitHub release is created
- **Manual**: Can be triggered manually for TestPyPI uploads
- **Validation**: Includes package validation and installation testing

### Required Secrets

Set these in your GitHub repository settings → Secrets and variables → Actions:

- `PYPI_API_TOKEN`: Production PyPI token
- `TEST_PYPI_API_TOKEN`: TestPyPI token

## Publishing Workflow

### 1. Development Release (TestPyPI)
```bash
# Test the build and upload process
./scripts/publish.sh test

# Verify the package installs correctly
./scripts/publish.sh test-install
```

### 2. Production Release (PyPI)

#### Option A: Manual
```bash
# Upload directly (requires confirmation)
./scripts/publish.sh prod
```

#### Option B: GitHub Release (Recommended)
1. Update version in code
2. Commit and push changes
3. Create a new release on GitHub
4. GitHub Actions will automatically build and publish

## Version Management

Before publishing, ensure version consistency across:
- `pyproject.toml`
- `superclaude/__init__.py`
- `superclaude/__main__.py`
- `setup/__init__.py`

The build script validates version consistency automatically.

## Troubleshooting

### Build Failures
- Check Python version compatibility (≥3.8)
- Ensure all required files are present
- Validate `pyproject.toml` syntax

### Upload Failures
- Verify API tokens are correct
- Check if version already exists on PyPI
- Ensure package name is available

### Import Failures
- Check package structure (`__init__.py` files)
- Verify all dependencies are listed
- Test local installation first

## Security Notes

- Never commit API tokens to version control
- Use environment variables or `.pypirc` for credentials
- Tokens should have minimal required permissions
- Consider using Trusted Publishing for GitHub Actions