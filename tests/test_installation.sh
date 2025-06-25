#!/bin/bash

# Installation Tests for SuperClaude
# Tests basic installation functionality

# Get the directory of this script
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source test framework
source "$TEST_DIR/test_framework.sh"

# Test: Basic installation
test_basic_install() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
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
    cd "$TEST_SOURCE_DIR"
    
    # Run installer in dry-run mode
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --dry-run >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Dry run should succeed"
    assert_file_not_exists "$TEST_INSTALL_DIR/CLAUDE.md" "No files should be created in dry run"
}

# Test: Update mode
test_update_mode() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Modify a file to simulate customization
    echo "# Customized" >> "$TEST_INSTALL_DIR/CLAUDE.md"
    
    # Update
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --update >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Update should succeed"
    assert_file_exists "$TEST_INSTALL_DIR/CLAUDE.md.new" "New version should be created for customized file"
    
    # Verify original was preserved
    assert_contains "$(cat "$TEST_INSTALL_DIR/CLAUDE.md")" "Customized" "Original customization should be preserved"
}

# Test: Uninstall mode
test_uninstall() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Create a user data file
    echo "user data" > "$TEST_INSTALL_DIR/.credentials.json"
    
    # Uninstall
    ./install.sh --dir "$TEST_INSTALL_DIR" --force --uninstall >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Uninstall should succeed"
    assert_file_exists "$TEST_INSTALL_DIR/.credentials.json" "User data should be preserved"
    assert_file_not_exists "$TEST_INSTALL_DIR/CLAUDE.md" "SuperClaude files should be removed"
}

# Test: Backup functionality
test_backup() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Add custom file
    echo "custom" > "$TEST_INSTALL_DIR/custom.file"
    
    # Install again (should trigger backup)
    local output=$(./install.sh --dir "$TEST_INSTALL_DIR" --force 2>&1)
    local backup_dir=$(echo "$output" | grep -o "superclaude-backup\.[^[:space:]]*" | head -1)
    
    assert_not_equals "" "$backup_dir" "Backup directory should be created"
    
    local full_backup_path="$(dirname "$TEST_INSTALL_DIR")/$backup_dir"
    assert_dir_exists "$full_backup_path" "Backup directory should exist"
    assert_file_exists "$full_backup_path/custom.file" "Custom file should be in backup"
}

# Test: Checksum generation
test_checksum_generation() {
    # Check if sha256sum is available
    if ! command -v sha256sum >/dev/null 2>&1; then
        skip_test "checksum_generation" "sha256sum not available"
        return
    fi
    
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # Install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    assert_file_exists "$TEST_INSTALL_DIR/.checksums" "Checksums file should be created"
    
    # Verify checksum format
    local checksum_line=$(head -1 "$TEST_INSTALL_DIR/.checksums" 2>/dev/null || echo "")
    assert_matches "$checksum_line" "^[a-f0-9]{64}[[:space:]]" "Checksum should be valid SHA256 format"
}

# Test: Installation to custom directory
test_custom_directory() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    local custom_dir="$TEST_TEMP_DIR/my-custom-claude"
    
    # Install to custom directory
    ./install.sh --dir "$custom_dir" --force >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Installation to custom directory should succeed"
    assert_dir_exists "$custom_dir" "Custom directory should exist"
    assert_file_exists "$custom_dir/CLAUDE.md" "Files should be installed to custom directory"
}

# Test: Verify mode
test_verify_mode() {
    setup_test_source
    cd "$TEST_SOURCE_DIR"
    
    # First install
    ./install.sh --dir "$TEST_INSTALL_DIR" --force >/dev/null 2>&1
    
    # Verify installation
    ./install.sh --dir "$TEST_INSTALL_DIR" --verify-checksums >/dev/null 2>&1
    local exit_code=$?
    
    assert_exit_code 0 "$exit_code" "Verification should succeed for clean installation"
    
    # Modify a file
    echo "modified" >> "$TEST_INSTALL_DIR/CLAUDE.md"
    
    # Verify again (should fail if checksums are working)
    if command -v sha256sum >/dev/null 2>&1; then
        ./install.sh --dir "$TEST_INSTALL_DIR" --verify-checksums >/dev/null 2>&1
        local modified_exit_code=$?
        assert_not_equals 0 "$modified_exit_code" "Verification should fail for modified installation"
    fi
}

# Main function to run all tests
main() {
    # Setup
    setup_test_environment
    
    # Run tests
    run_test_suite "Installation Tests" \
        test_basic_install \
        test_dry_run \
        test_update_mode \
        test_uninstall \
        test_backup \
        test_checksum_generation \
        test_custom_directory \
        test_verify_mode
    
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