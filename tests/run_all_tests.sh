#!/bin/bash

# Run all SuperClaude tests
# This script runs all test suites and provides a combined report

# Get the directory of this script
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1; then
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

# Test suite tracking
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

# Overall test tracking
OVERALL_TESTS=0
OVERALL_PASSED=0
OVERALL_FAILED=0
OVERALL_SKIPPED=0

echo -e "${BLUE}SuperClaude Test Suite Runner${NC}"
echo "=============================="
echo "Running all test suites..."
echo ""

# Function to run a test suite
run_suite() {
    local suite_name="$1"
    local suite_file="$2"
    
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    
    echo -e "${BLUE}Running $suite_name...${NC}"
    
    if [[ ! -f "$suite_file" ]]; then
        echo -e "${RED}Error: Test suite not found: $suite_file${NC}"
        FAILED_SUITES=$((FAILED_SUITES + 1))
        return 1
    fi
    
    # Make sure test is executable
    chmod +x "$suite_file"
    
    # Run the test suite and capture output
    local output=$("$suite_file" 2>&1)
    local exit_code=$?
    
    # Extract test counts from output
    local tests_run=$(echo "$output" | grep -E "^Total tests:" | awk '{print $3}')
    local tests_passed=$(echo "$output" | grep -E "^Passed:" | awk '{print $2}')
    local tests_failed=$(echo "$output" | grep -E "^Failed:" | awk '{print $2}')
    local tests_skipped=$(echo "$output" | grep -E "^Skipped:" | awk '{print $2}')
    
    # Update overall counts
    OVERALL_TESTS=$((OVERALL_TESTS + ${tests_run:-0}))
    OVERALL_PASSED=$((OVERALL_PASSED + ${tests_passed:-0}))
    OVERALL_FAILED=$((OVERALL_FAILED + ${tests_failed:-0}))
    OVERALL_SKIPPED=$((OVERALL_SKIPPED + ${tests_skipped:-0}))
    
    # Show output
    echo "$output"
    
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✓ $suite_name completed successfully${NC}"
        PASSED_SUITES=$((PASSED_SUITES + 1))
    else
        echo -e "${RED}✗ $suite_name failed${NC}"
        FAILED_SUITES=$((FAILED_SUITES + 1))
    fi
    
    echo ""
    return $exit_code
}

# Run all test suites
run_suite "Installation Tests" "$TEST_DIR/test_installation.sh"
run_suite "Security Tests" "$TEST_DIR/test_security.sh"
run_suite "Compatibility Tests" "$TEST_DIR/test_compatibility.sh"

# Overall summary
echo "=============================="
echo -e "${BLUE}Overall Test Summary${NC}"
echo "=============================="
echo -e "Test Suites Run: $TOTAL_SUITES"
echo -e "Suites Passed:   ${GREEN}$PASSED_SUITES${NC}"
echo -e "Suites Failed:   ${RED}$FAILED_SUITES${NC}"
echo ""
echo -e "Total Tests:     $OVERALL_TESTS"
echo -e "Tests Passed:    ${GREEN}$OVERALL_PASSED${NC}"
echo -e "Tests Failed:    ${RED}$OVERALL_FAILED${NC}"
echo -e "Tests Skipped:   ${YELLOW}$OVERALL_SKIPPED${NC}"
echo ""

if [[ $FAILED_SUITES -eq 0 ]] && [[ $OVERALL_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi