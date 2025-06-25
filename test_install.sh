#!/bin/bash

# SuperClaude Installer Test Suite
# Tests installer functionality, security, and Bash 3.2 compatibility
# Version: 1.0.0

set -e
set -o pipefail

# Test framework setup
readonly TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'superclaude-test')
readonly TEST_INSTALL_DIR="$TEMP_DIR/test-install"
readonly TEST_SOURCE_DIR="$TEMP_DIR/test-source"

# Colors for output
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
    readonly GREEN='\033[0;32m'
    readonly RED='\033[0;31m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly NC='\033[0m'
else
    readonly GREEN=''
    readonly RED=''
    readonly YELLOW=''
    readonly BLUE=''
    readonly NC=''
fi

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Cleanup on exit
cleanup() {
    if [[ "${CLEANUP_DONE:-false}" != "true" ]]; then
        CLEANUP_DONE=true
        echo -e "\n${BLUE}Cleaning up test environment...${NC}"
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Test framework functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Values should be equal}"
    
    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Expected: '$expected'"
        echo "  Actual:   '$actual'"
        return 1
    fi
}

assert_not_equals() {
    local unexpected="$1"
    local actual="$2"
    local message="${3:-Values should not be equal}"
    
    if [[ "$unexpected" != "$actual" ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Value: '$actual'"
        return 1
    fi
}

assert_true() {
    local condition="$1"
    local message="${2:-Condition should be true}"
    
    if eval "$condition"; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Condition: $condition"
        return 1
    fi
}

assert_false() {
    local condition="$1"
    local message="${2:-Condition should be false}"
    
    if ! eval "$condition"; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Condition: $condition"
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local message="${2:-File should exist}"
    
    if [[ -f "$file" ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  File: $file"
        return 1
    fi
}

assert_dir_exists() {
    local dir="$1"
    local message="${2:-Directory should exist}"
    
    if [[ -d "$dir" ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Directory: $dir"
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-String should contain substring}"
    
    if [[ "$haystack" == *"$needle"* ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  String: '$haystack'"
        echo "  Should contain: '$needle'"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Exit code should match}"
    
    if [[ "$expected" -eq "$actual" ]]; then
        return 0
    else
        echo -e "${RED}✗ Assertion failed: $message${NC}"
        echo "  Expected exit code: $expected"
        echo "  Actual exit code: $actual"
        return 1
    fi
}

# Run a test
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    echo -ne "${BLUE}Running: ${NC}$test_name... "
    
    # Create clean test environment for each test
    rm -rf "$TEST_INSTALL_DIR" "$TEST_SOURCE_DIR" 2>/dev/null || true
    mkdir -p "$TEST_INSTALL_DIR" "$TEST_SOURCE_DIR"
    
    # Run test in subshell to isolate failures
    if (
        cd "$TEST_SOURCE_DIR"
        $test_function
    ); then
        echo -e "${GREEN}✓ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Skip a test
skip_test() {
    local test_name="$1"
    local reason="${2:-No reason given}"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    
    echo -e "${BLUE}Skipping: ${NC}$test_name... ${YELLOW}⚠ SKIPPED${NC} ($reason)"
}

# Setup test source directory
setup_test_source() {
    # Create minimal SuperClaude structure
    mkdir -p "$TEST_SOURCE_DIR/.claude/commands/shared"
    mkdir -p "$TEST_SOURCE_DIR/.claude/shared"
    
    # Create test files
    echo "# Test CLAUDE.md" > "$TEST_SOURCE_DIR/CLAUDE.md"
    echo "1.0.0" > "$TEST_SOURCE_DIR/VERSION"
    echo "# Test command" > "$TEST_SOURCE_DIR/.claude/commands/test.md"
    echo "key: value" > "$TEST_SOURCE_DIR/.claude/shared/test.yml"
    
    # Copy the installer
    cp "$TEST_DIR/install.sh" "$TEST_SOURCE_DIR/"
    chmod +x "$TEST_SOURCE_DIR/install.sh"
}

# Test: Bash version compatibility
test_bash_version_check() {
    setup_test_source
    
    # This test runs with current bash version
    local bash_major="${BASH_VERSION%%.*}"
    assert_true "[[ $bash_major -ge 3 ]]" "Bash version should be 3 or higher"
}

# Test: Basic installation
test_basic_install() {
    setup_test_source
    
    # Run installer
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Installation should succeed"
    assert_dir_exists "$TEST_INSTALL_DIR" "Install directory should exist"
    assert_file_exists "$TEST_INSTALL_DIR/CLAUDE.md" "CLAUDE.md should be installed"
    assert_file_exists "$TEST_INSTALL_DIR/commands/test.md" "Command file should be installed"
    assert_file_exists "$TEST_INSTALL_DIR/shared/test.yml" "Shared file should be installed"
}

# Test: Dry run mode
test_dry_run() {
    setup_test_source
    
    # Run installer in dry-run mode
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force --dry-run 2>&1)
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Dry run should succeed"
    assert_false "[[ -f '$TEST_INSTALL_DIR/CLAUDE.md' ]]" "No files should be created in dry run"
}

# Test: Update mode
test_update_mode() {
    setup_test_source
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Modify a file to simulate customization
    echo "# Customized" >> "$TEST_INSTALL_DIR/CLAUDE.md"
    
    # Update
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --update >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Update should succeed"
    assert_file_exists "$TEST_INSTALL_DIR/CLAUDE.md.new" "New version should be created for customized file"
}

# Test: Uninstall mode
test_uninstall() {
    setup_test_source
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Create a user data file
    echo "user data" > "$TEST_INSTALL_DIR/.credentials.json"
    
    # Uninstall
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --uninstall >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Uninstall should succeed"
    assert_file_exists "$TEST_INSTALL_DIR/.credentials.json" "User data should be preserved"
    assert_false "[[ -f '$TEST_INSTALL_DIR/CLAUDE.md' ]]" "SuperClaude files should be removed"
}

# Test: Path traversal protection
test_path_traversal_protection() {
    setup_test_source
    
    # Test dangerous paths
    local output
    
    # Test parent directory traversal
    output=$(./install.sh --dir "../../../tmp/bad" 2>&1 || true)
    assert_contains "$output" "Path traversal not allowed" "Should reject path traversal"
    
    # Test system directory
    output=$(./install.sh --dir "/usr/bin/bad" 2>&1 || true)
    assert_contains "$output" "Installation to system directory not allowed" "Should reject system directories"
}

# Test: Input validation
test_input_validation() {
    setup_test_source
    
    # Test invalid log file path
    local output
    output=$(./install.sh --log "/tmp/../bad.log" 2>&1 || true)
    assert_contains "$output" "Path traversal not allowed" "Should reject path traversal in log file"
}

# Test: Backup functionality
test_backup() {
    setup_test_source
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Add custom file
    echo "custom" > "$TEST_INSTALL_DIR/custom.file"
    
    # Install again (should trigger backup)
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force 2>&1)
    local backup_dir=$(echo "$output" | grep -o "superclaude-backup\.[^[:space:]]*" | head -1)
    
    assert_not_equals "" "$backup_dir" "Backup directory should be created"
    assert_dir_exists "$(dirname "$TEST_INSTALL_DIR")/$backup_dir" "Backup directory should exist"
}

# Test: Checksum generation
test_checksum_generation() {
    setup_test_source
    
    # Check if sha256sum is available
    if ! command -v sha256sum >/dev/null 2>&1; then
        skip_test "test_checksum_generation" "sha256sum not available"
        return
    fi
    
    # Install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    assert_file_exists "$TEST_INSTALL_DIR/.checksums" "Checksums file should be created"
    
    # Verify checksum format
    local checksum_line=$(head -1 "$TEST_INSTALL_DIR/.checksums" 2>/dev/null || echo "")
    assert_true "[[ '$checksum_line' =~ ^[a-f0-9]{64}[[:space:]] ]]" "Checksum should be valid SHA256 format"
}

# Test: Version comparison
test_version_comparison() {
    setup_test_source
    
    # Create a test script to check version comparison
    cat > "$TEST_SOURCE_DIR/test_version.sh" << 'EOF'
#!/bin/bash
source ./install.sh

# Test version comparisons
if compare_versions "1.0.0" "2.0.0"; then
    echo "1.0.0 < 2.0.0: PASS"
else
    echo "1.0.0 < 2.0.0: FAIL"
    exit 1
fi

if ! compare_versions "2.0.0" "1.0.0"; then
    echo "2.0.0 >= 1.0.0: PASS"
else
    echo "2.0.0 >= 1.0.0: FAIL"
    exit 1
fi

if ! compare_versions "1.0.0" "1.0.0"; then
    echo "1.0.0 == 1.0.0: PASS"
else
    echo "1.0.0 == 1.0.0: FAIL"
    exit 1
fi
EOF
    
    chmod +x "$TEST_SOURCE_DIR/test_version.sh"
    ./test_version.sh >/dev/null 2>&1
    assert_exit_code 0 $? "Version comparison should work correctly"
}

# Test: Bash 3.2 regex compatibility
test_bash32_regex_compat() {
    setup_test_source
    
    # Test that installer doesn't use =~ operator
    local regex_count=$(grep -c "=~" "$TEST_SOURCE_DIR/install.sh" || echo "0")
    assert_equals "0" "$regex_count" "Installer should not use =~ operator for Bash 3.2 compatibility"
}

# Test: Local variable usage
test_local_variable_usage() {
    setup_test_source
    
    # Check that 'local' is not used outside functions in main script body
    # This is a simplified check - in practice would need more sophisticated parsing
    local problematic_locals=$(awk '
        /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*\(\)[[:space:]]*{/ { in_function=1 }
        /^}$/ && in_function { in_function=0 }
        /^[[:space:]]*local[[:space:]]/ && !in_function { print NR ":" $0 }
    ' "$TEST_SOURCE_DIR/install.sh" | head -5)
    
    assert_equals "" "$problematic_locals" "No 'local' declarations should exist outside functions"
}

# Test: Error handling
test_error_handling() {
    setup_test_source
    
    # Remove required file to trigger error
    rm -f "$TEST_SOURCE_DIR/CLAUDE.md"
    
    # Run installer (should fail gracefully)
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force 2>&1 || true)
    assert_contains "$output" "Error:" "Should show error message"
    assert_contains "$output" "CLAUDE.md" "Should indicate missing file"
}

# Test: Rollback functionality
test_rollback() {
    setup_test_source
    
    # Create a script that will fail during installation
    cat > "$TEST_SOURCE_DIR/.claude/commands/bad.sh" << 'EOF'
#!/bin/bash
exit 1
EOF
    chmod +x "$TEST_SOURCE_DIR/.claude/commands/bad.sh"
    
    # Modify installer to fail after creating some files
    # This is a controlled test - in real scenarios, failures could happen at any point
    
    # For now, we'll test that rollback configuration works
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force --no-rollback 2>&1 || true)
    assert_contains "$output" "rollback" "Should acknowledge rollback is disabled"
}

# Main test runner
main() {
    echo -e "${BLUE}SuperClaude Installer Test Suite${NC}"
    echo "=================================="
    echo "Test directory: $TEST_DIR"
    echo "Temp directory: $TEMP_DIR"
    echo "Bash version: ${BASH_VERSION}"
    echo ""
    
    # Run all tests
    run_test "Bash version compatibility" test_bash_version_check
    run_test "Basic installation" test_basic_install
    run_test "Dry run mode" test_dry_run
    run_test "Update mode" test_update_mode
    run_test "Uninstall mode" test_uninstall
    run_test "Path traversal protection" test_path_traversal_protection
    run_test "Input validation" test_input_validation
    run_test "Backup functionality" test_backup
    run_test "Checksum generation" test_checksum_generation
    run_test "Version comparison" test_version_comparison
    run_test "Bash 3.2 regex compatibility" test_bash32_regex_compat
    run_test "Local variable usage" test_local_variable_usage
    run_test "Error handling" test_error_handling
    run_test "Rollback functionality" test_rollback
    
    # Summary
    echo ""
    echo "=================================="
    echo -e "${BLUE}Test Summary${NC}"
    echo "=================================="
    echo -e "Total tests:    $TESTS_RUN"
    echo -e "Passed:         ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:         ${RED}$TESTS_FAILED${NC}"
    echo -e "Skipped:        ${YELLOW}$TESTS_SKIPPED${NC}"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        exit 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi