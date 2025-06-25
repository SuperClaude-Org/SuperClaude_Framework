# SuperClaude Test Suite

This directory contains the test suite for the SuperClaude installer.

## Test Structure

```
tests/
├── test_framework.sh      # Core test framework and utilities
├── test_installation.sh   # Installation functionality tests
├── test_security.sh       # Security and validation tests
├── test_compatibility.sh  # Bash 3.2 and cross-platform tests
├── run_all_tests.sh      # Run all test suites
└── README.md             # This file
```

## Running Tests

### Run All Tests
```bash
cd tests
./run_all_tests.sh
```

### Run Individual Test Suites
```bash
# Installation tests
./test_installation.sh

# Security tests
./test_security.sh

# Compatibility tests
./test_compatibility.sh
```

## Test Categories

### Installation Tests
- Basic installation
- Dry run mode
- Update mode
- Uninstall functionality
- Backup creation
- Checksum generation
- Custom directory installation
- Verification mode

### Security Tests
- Path traversal protection
- System directory protection
- Input validation
- Command injection prevention
- Symlink attack protection
- File permission handling
- Dangerous character filtering
- Configuration file validation

### Compatibility Tests
- Bash version checking
- Bash 3.2 specific compatibility
- POSIX feature support
- Platform detection
- Cross-platform command compatibility
- Special character handling

## Writing New Tests

1. Source the test framework:
   ```bash
   source "$TEST_DIR/test_framework.sh"
   ```

2. Use assertion functions:
   - `assert_equals expected actual [message]`
   - `assert_true condition [message]`
   - `assert_false condition [message]`
   - `assert_file_exists file [message]`
   - `assert_contains string substring [message]`
   - `assert_exit_code expected actual [message]`

3. Create test functions prefixed with `test_`:
   ```bash
   test_my_feature() {
       # Test implementation
   }
   ```

4. Run tests with `run_test_suite`:
   ```bash
   run_test_suite "My Tests" test_my_feature test_another_feature
   ```

## Known Issues

Some tests may fail in certain environments:
- Dry run test: The installer may create the base directory structure
- Platform detection: Requires sourcing the installer script
- File permissions: May vary based on umask settings

## Requirements

- Bash 3.2 or higher
- Standard Unix utilities (find, grep, awk, sed, etc.)
- Write permissions in temp directory