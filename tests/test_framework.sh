#!/bin/bash

# Test Framework for SuperClaude
# Provides assertion functions and test utilities

# Colors for output
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
    readonly TEST_GREEN='\033[0;32m'
    readonly TEST_RED='\033[0;31m'
    readonly TEST_YELLOW='\033[1;33m'
    readonly TEST_BLUE='\033[0;34m'
    readonly TEST_NC='\033[0m'
else
    readonly TEST_GREEN=''
    readonly TEST_RED=''
    readonly TEST_YELLOW=''
    readonly TEST_BLUE=''
    readonly TEST_NC=''
fi

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Assertion functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Values should be equal}"
    
    if [[ "$expected" == "$actual" ]]; then
        return 0
    else
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  File: $file"
        return 1
    fi
}

assert_file_not_exists() {
    local file="$1"
    local message="${2:-File should not exist}"
    
    if [[ ! -f "$file" ]]; then
        return 0
    else
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  Directory: $dir"
        return 1
    fi
}

assert_dir_not_exists() {
    local dir="$1"
    local message="${2:-Directory should not exist}"
    
    if [[ ! -d "$dir" ]]; then
        return 0
    else
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  String: '${haystack:0:100}...'"
        echo "  Should contain: '$needle'"
        return 1
    fi
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-String should not contain substring}"
    
    if [[ "$haystack" != *"$needle"* ]]; then
        return 0
    else
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  String: '${haystack:0:100}...'"
        echo "  Should not contain: '$needle'"
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
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  Expected exit code: $expected"
        echo "  Actual exit code: $actual"
        return 1
    fi
}

assert_matches() {
    local string="$1"
    local pattern="$2"
    local message="${3:-String should match pattern}"
    
    if echo "$string" | grep -qE "$pattern"; then
        return 0
    else
        echo -e "${TEST_RED}✗ Assertion failed: $message${TEST_NC}"
        echo "  String: '$string'"
        echo "  Pattern: '$pattern'"
        return 1
    fi
}

# Test runner functions
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    echo -ne "${TEST_BLUE}Running: ${TEST_NC}$test_name... "
    
    # Run test in subshell to isolate failures
    if (
        set +e  # Allow test failures
        $test_function
    ); then
        echo -e "${TEST_GREEN}✓ PASSED${TEST_NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${TEST_RED}✗ FAILED${TEST_NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

skip_test() {
    local test_name="$1"
    local reason="${2:-No reason given}"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    
    echo -e "${TEST_BLUE}Skipping: ${TEST_NC}$test_name... ${TEST_YELLOW}⚠ SKIPPED${TEST_NC} ($reason)"
}

# Test suite functions
run_test_suite() {
    local suite_name="$1"
    shift
    local tests=("$@")
    
    echo -e "\n${TEST_BLUE}=== $suite_name ===${TEST_NC}"
    
    for test in "${tests[@]}"; do
        if declare -f "$test" >/dev/null; then
            run_test "${test#test_}" "$test"
        else
            echo -e "${TEST_RED}Warning: Test function '$test' not found${TEST_NC}"
        fi
    done
}

print_test_summary() {
    echo ""
    echo "=================================="
    echo -e "${TEST_BLUE}Test Summary${TEST_NC}"
    echo "=================================="
    echo -e "Total tests:    $TESTS_RUN"
    echo -e "Passed:         ${TEST_GREEN}$TESTS_PASSED${TEST_NC}"
    echo -e "Failed:         ${TEST_RED}$TESTS_FAILED${TEST_NC}"
    echo -e "Skipped:        ${TEST_YELLOW}$TESTS_SKIPPED${TEST_NC}"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${TEST_GREEN}✓ All tests passed!${TEST_NC}"
        return 0
    else
        echo -e "${TEST_RED}✗ Some tests failed${TEST_NC}"
        return 1
    fi
}

# Setup functions
setup_test_environment() {
    # Create temporary test directory
    export TEST_TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'superclaude-test')
    export TEST_INSTALL_DIR="$TEST_TEMP_DIR/test-install"
    export TEST_SOURCE_DIR="$TEST_TEMP_DIR/test-source"
    
    # Create directories
    mkdir -p "$TEST_INSTALL_DIR" "$TEST_SOURCE_DIR"
}

cleanup_test_environment() {
    if [[ -n "$TEST_TEMP_DIR" ]] && [[ -d "$TEST_TEMP_DIR" ]]; then
        rm -rf "$TEST_TEMP_DIR" 2>/dev/null || true
    fi
}

# Setup minimal SuperClaude source for testing
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
    if [[ -f "install.sh" ]]; then
        cp "install.sh" "$TEST_SOURCE_DIR/"
    elif [[ -f "../install.sh" ]]; then
        cp "../install.sh" "$TEST_SOURCE_DIR/"
    else
        echo "Error: Cannot find install.sh"
        return 1
    fi
    
    chmod +x "$TEST_SOURCE_DIR/install.sh"
}

# Export all functions for use in test files
export -f assert_equals assert_not_equals assert_true assert_false
export -f assert_file_exists assert_file_not_exists assert_dir_exists assert_dir_not_exists
export -f assert_contains assert_not_contains assert_exit_code assert_matches
export -f run_test skip_test run_test_suite print_test_summary
export -f setup_test_environment cleanup_test_environment setup_test_source