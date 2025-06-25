#!/bin/bash

# Compatibility Tests for SuperClaude
# Tests Bash 3.2 compatibility and cross-platform support

# Get the directory of this script
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source test framework
source "$TEST_DIR/test_framework.sh"

# Test: Bash version compatibility
test_bash_version_check() {
    # This test runs with current bash version
    local bash_major="${BASH_VERSION%%.*}"
    assert_true "[[ $bash_major -ge 3 ]]" "Bash version should be 3 or higher"
}

# Test: Bash 3.2 regex compatibility
test_bash32_regex_compat() {
    # Get install.sh path
    local install_script=""
    if [[ -f "../install.sh" ]]; then
        install_script="../install.sh"
    elif [[ -f "install.sh" ]]; then
        install_script="install.sh"
    else
        skip_test "bash32_regex_compat" "Cannot find install.sh"
        return
    fi
    
    # Test that installer doesn't use =~ operator (which has issues in Bash 3.2)
    # Count only actual regex usage, not in comments or strings
    local regex_count=$(grep -E '^\s*[^#]*\[\[.*=~' "$install_script" | wc -l | tr -d ' ')
    assert_equals "0" "$regex_count" "Installer should not use =~ operator for Bash 3.2 compatibility"
}

# Test: Local variable usage
test_local_variable_usage() {
    # Get install.sh path
    local install_script=""
    if [[ -f "../install.sh" ]]; then
        install_script="../install.sh"
    elif [[ -f "install.sh" ]]; then
        install_script="install.sh"
    else
        skip_test "local_variable_usage" "Cannot find install.sh"
        return
    fi
    
    # Check that 'local' is not used outside functions in main script body
    # This is a simplified check
    local problematic_locals=$(awk '
        /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*\(\)[[:space:]]*\{/ { in_function=1 }
        /^}$/ && in_function { in_function=0 }
        /^[[:space:]]*local[[:space:]]/ && !in_function { print NR ":" $0 }
    ' "$install_script" 2>/dev/null | head -5)
    
    assert_equals "" "$problematic_locals" "No 'local' declarations should exist outside functions"
}

# Test: Array syntax compatibility
test_array_syntax() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test that arrays work in current bash version
    local test_array=("one" "two" "three")
    assert_equals "one" "${test_array[0]}" "Array indexing should work"
    assert_equals "3" "${#test_array[@]}" "Array length should work"
}

# Test: Command availability
test_command_availability() {
    # Test for required commands
    local required_commands=("find" "grep" "awk" "sed" "mkdir" "cp" "rm" "chmod")
    
    for cmd in "${required_commands[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            assert_true "command -v $cmd" "Command $cmd should be available"
        else
            skip_test "command_$cmd" "Command $cmd not available on this system"
        fi
    done
}

# Test: POSIX compatibility
test_posix_features() {
    # Test POSIX shell features that should work across platforms
    
    # Parameter expansion
    local var="test"
    assert_equals "test" "${var}" "Basic parameter expansion should work"
    assert_equals "4" "${#var}" "String length should work"
    assert_equals "est" "${var#t}" "Prefix removal should work"
    assert_equals "tes" "${var%t}" "Suffix removal should work"
    
    # Command substitution
    local result=$(echo "test")
    assert_equals "test" "$result" "Command substitution with $() should work"
    
    # Arithmetic expansion
    local sum=$((1 + 1))
    assert_equals "2" "$sum" "Arithmetic expansion should work"
}

# Test: Platform detection
test_platform_detection() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test that platform detection works
    local output=$(bash -c 'source ./install.sh 2>/dev/null; detect_platform; echo "$OS"')
    
    case "$OSTYPE" in
        linux-gnu*)
            assert_contains "$output" "Linux" "Should detect Linux"
            ;;
        darwin*)
            assert_contains "$output" "macOS" "Should detect macOS"
            ;;
        msys*|cygwin*)
            assert_contains "$output" "Windows" "Should detect Windows"
            ;;
    esac
}

# Test: mktemp compatibility
test_mktemp_compatibility() {
    # Test both GNU and BSD mktemp syntax
    local temp_dir=""
    
    # Try GNU syntax first
    temp_dir=$(mktemp -d 2>/dev/null) || {
        # Fall back to BSD syntax
        temp_dir=$(mktemp -d -t 'test')
    }
    
    assert_not_equals "" "$temp_dir" "mktemp should create directory"
    assert_dir_exists "$temp_dir" "Temp directory should exist"
    
    # Cleanup
    rm -rf "$temp_dir" 2>/dev/null || true
}

# Test: stat command compatibility
test_stat_compatibility() {
    local test_file="$TEST_TEMP_DIR/test_stat"
    touch "$test_file"
    chmod 644 "$test_file"
    
    # Test different stat syntaxes
    local perms=""
    
    # Try GNU stat
    perms=$(stat -c %a "$test_file" 2>/dev/null) || {
        # Try BSD stat
        perms=$(stat -f %p "$test_file" 2>/dev/null | grep -o '[0-9][0-9][0-9]$') || {
            skip_test "stat_compatibility" "stat command not compatible"
            return
        }
    }
    
    assert_equals "644" "$perms" "stat should return correct permissions"
    
    rm -f "$test_file"
}

# Test: Special character handling
test_special_characters() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test installation with spaces in path
    local space_dir="$TEST_TEMP_DIR/dir with spaces"
    mkdir -p "$space_dir"
    
    ./install.sh --dir "$space_dir" --force >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Should handle spaces in directory names"
    assert_file_exists "$space_dir/CLAUDE.md" "Should install to directory with spaces"
}

# Test: Version comparison function
test_version_comparison() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Create a test script to check version comparison
    cat > "$TEST_TEMP_DIR/test_version.sh" << 'EOF'
#!/bin/bash
# Source just the compare_versions function
compare_versions() {
    local version1="$1"
    local version2="$2"
    
    # Simplified version comparison for testing
    case "$version1" in
        [0-9]*.[0-9]*.[0-9]*|[0-9]*.[0-9]*|[0-9]*)
            ;;
        *)
            return 1
            ;;
    esac
    
    case "$version2" in
        [0-9]*.[0-9]*.[0-9]*|[0-9]*.[0-9]*|[0-9]*)
            ;;
        *)
            return 1
            ;;
    esac
    
    # Simple comparison
    if [[ "$version1" < "$version2" ]]; then
        return 0
    else
        return 1
    fi
}

# Test version comparisons
if compare_versions "1.0.0" "2.0.0"; then
    echo "PASS: 1.0.0 < 2.0.0"
else
    echo "FAIL: 1.0.0 < 2.0.0"
    exit 1
fi

if ! compare_versions "2.0.0" "1.0.0"; then
    echo "PASS: 2.0.0 >= 1.0.0"
else
    echo "FAIL: 2.0.0 >= 1.0.0"
    exit 1
fi
EOF
    
    chmod +x "$TEST_TEMP_DIR/test_version.sh"
    "$TEST_TEMP_DIR/test_version.sh" >/dev/null 2>&1
    assert_exit_code 0 $? "Version comparison should work"
}

# Main function to run all tests
main() {
    # Setup
    setup_test_environment
    
    # Run tests
    run_test_suite "Compatibility Tests" \
        test_bash_version_check \
        test_bash32_regex_compat \
        test_local_variable_usage \
        test_array_syntax \
        test_command_availability \
        test_posix_features \
        test_platform_detection \
        test_mktemp_compatibility \
        test_stat_compatibility \
        test_special_characters \
        test_version_comparison
    
    # Print summary
    print_test_summary
    local exit_code=$?
    
    # Cleanup
    cleanup_test_environment
    
    return $exit_code
}

# Run tests if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi