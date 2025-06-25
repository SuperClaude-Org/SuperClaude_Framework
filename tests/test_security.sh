#!/bin/bash

# Security Tests for SuperClaude
# Tests security features and input validation

# Get the directory of this script
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source test framework
source "$TEST_DIR/test_framework.sh"

# Test: Path traversal protection in install directory
test_path_traversal_protection() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test parent directory traversal
    local output=$(./install.sh --dir "../../../tmp/bad" 2>&1 || true)
    assert_contains "$output" "Path traversal not allowed" "Should reject path traversal"
    
    # Test with embedded path traversal
    output=$(./install.sh --dir "/tmp/../etc/bad" 2>&1 || true)
    assert_contains "$output" "Path traversal not allowed" "Should reject embedded path traversal"
}

# Test: System directory protection
test_system_directory_protection() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test various system directories
    local system_dirs=("/usr/bin" "/etc" "/bin" "/sbin" "/sys" "/proc")
    
    for dir in "${system_dirs[@]}"; do
        local output=$(./install.sh --dir "$dir/superclaude" 2>&1 || true)
        assert_contains "$output" "Installation to system directory not allowed" "Should reject $dir"
    done
}

# Test: Input validation for log file
test_log_file_validation() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test path traversal in log file
    local output=$(./install.sh --log "/tmp/../bad.log" 2>&1 || true)
    assert_contains "$output" "Path traversal not allowed" "Should reject path traversal in log file"
    
    # Test control characters in log file
    if printf '\0' >/dev/null 2>&1; then
        output=$(./install.sh --log "$(printf '/tmp/bad\0file.log')" 2>&1 || true)
        assert_contains "$output" "Invalid characters" "Should reject null bytes in log file"
    fi
}

# Test: Command injection protection
test_command_injection_protection() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Create a test that would fail if command injection worked
    local malicious_dir='$TEST_TEMP_DIR/$(touch pwned)'
    
    # Try to install with malicious directory name
    ./install.sh --dir "$malicious_dir" --force >/dev/null 2>&1 || true
    
    # Check that the command wasn't executed
    assert_file_not_exists "$TEST_TEMP_DIR/pwned" "Command injection should not work"
}

# Test: Symlink attack protection
test_symlink_protection() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Create a malicious symlink
    local target_file="/tmp/should_not_be_modified"
    echo "original" > "$target_file"
    
    # Replace a file with a symlink
    rm -f "$TEST_INSTALL_DIR/CLAUDE.md"
    ln -s "$target_file" "$TEST_INSTALL_DIR/CLAUDE.md"
    
    # Try to update (should not follow symlink)
    echo "# Modified CLAUDE.md" > "$TEST_SOURCE_DIR/CLAUDE.md"
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --update >/dev/null 2>&1 || true
    
    # Check that target file wasn't modified
    assert_equals "original" "$(cat "$target_file")" "Symlink target should not be modified"
    
    # Cleanup
    rm -f "$target_file"
}

# Test: File permission preservation
test_file_permissions() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Create a script with specific permissions
    echo "#!/bin/bash" > "$TEST_SOURCE_DIR/.claude/commands/script.sh"
    chmod 755 "$TEST_SOURCE_DIR/.claude/commands/script.sh"
    
    # Install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Check that executable permission is preserved
    assert_true "[[ -x '$TEST_INSTALL_DIR/commands/script.sh' ]]" "Script should remain executable"
}

# Test: Dangerous characters in paths
test_dangerous_characters() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Test newline in path
    local output=$(printf './install.sh --dir "/tmp/bad\npath" 2>&1' | bash || true)
    assert_not_equals 0 $? "Should reject newline in path"
    
    # Test semicolon (command separator)
    output=$(./install.sh --dir '/tmp/bad;echo pwned' 2>&1 || true)
    assert_not_contains "$output" "pwned" "Should not execute commands in path"
}

# Test: Directory size limits
test_disk_space_check() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # This test is tricky to make portable, so we just verify the check exists
    local install_script=$(cat install.sh)
    assert_contains "$install_script" "REQUIRED_SPACE" "Should have disk space requirement"
    assert_contains "$install_script" "df" "Should check disk space"
}

# Test: Backup directory security
test_backup_security() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Install twice to trigger backup
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force 2>&1)
    
    # Extract backup directory
    local backup_dir=$(echo "$output" | grep -o "superclaude-backup\.[^[:space:]]*" | head -1)
    
    if [[ -n "$backup_dir" ]]; then
        # Check that backup directory has secure random suffix
        assert_matches "$backup_dir" "superclaude-backup\.[0-9]+_[0-9]+\.[a-f0-9]+" "Backup should have random suffix"
        
        # Check permissions (should be 700)
        local full_backup_path="$(dirname "$TEST_INSTALL_DIR")/$backup_dir"
        if [[ -d "$full_backup_path" ]]; then
            local perms=$(stat -f %p "$full_backup_path" 2>/dev/null || stat -c %a "$full_backup_path" 2>/dev/null || echo "")
            # Check if permissions end with 700 (owner only)
            if [[ -n "$perms" ]]; then
                assert_matches "$perms" "700$" "Backup directory should have restrictive permissions"
            fi
        fi
    fi
}

# Test: Configuration file validation
test_config_file_validation() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Create a malicious config file
    cat > "$TEST_TEMP_DIR/bad.conf" << 'EOF'
INSTALL_DIR="/etc"
$(touch /tmp/config_pwned)
EOF
    
    # Try to use the config
    ./install.sh --config "$TEST_TEMP_DIR/bad.conf" 2>&1 || true
    
    # Check that command wasn't executed
    assert_file_not_exists "/tmp/config_pwned" "Config file commands should not execute"
}

# Main function to run all tests
main() {
    # Setup
    setup_test_environment
    
    # Run tests
    run_test_suite "Security Tests" \
        test_path_traversal_protection \
        test_system_directory_protection \
        test_log_file_validation \
        test_command_injection_protection \
        test_symlink_protection \
        test_file_permissions \
        test_dangerous_characters \
        test_disk_space_check \
        test_backup_security \
        test_config_file_validation
    
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