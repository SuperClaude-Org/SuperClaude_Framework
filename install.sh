#!/bin/bash

# SuperClaude Installer Script
# Installs SuperClaude configuration framework to enhance Claude Code
# Version: 2.0.0
# License: MIT
# Repository: https://github.com/nshkrdotcom/SuperClaude

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Script version
readonly SCRIPT_VERSION="2.0.0"

# Constants
readonly REQUIRED_SPACE_KB=51200  # 50MB in KB
readonly MIN_BASH_VERSION=4
readonly CHECKSUM_FILE=".checksums"
readonly CONFIG_FILE=".superclaude.conf"

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration patterns
readonly -a CUSTOMIZABLE_CONFIGS=("CLAUDE.md" "RULES.md" "PERSONAS.md" "MCP.md")

# Default settings
INSTALL_DIR="$HOME/.claude"
FORCE_INSTALL=false
UPDATE_MODE=false
UNINSTALL_MODE=false
VERIFY_MODE=false
VERBOSE=false
DRY_RUN=false
LOG_FILE=""
VERIFICATION_FAILURES=0
ROLLBACK_ON_FAILURE=true
BACKUP_DIR=""

# Command availability cache
declare -A COMMAND_CACHE

# Original working directory
ORIGINAL_DIR=$(pwd)

# Cleanup on exit
cleanup() {
    local exit_code=$?
    
    # Return to original directory
    cd "$ORIGINAL_DIR" 2>/dev/null || true
    
    # Clean up temp directory
    if [[ $exit_code -ne 0 ]] && [[ -n "$TEMP_DIR" ]] && [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi
    
    # Rollback on failure if enabled
    if [[ $exit_code -ne 0 ]] && [[ "$ROLLBACK_ON_FAILURE" = true ]] && [[ -n "$BACKUP_DIR" ]]; then
        rollback_installation
    fi
    
    exit $exit_code
}
trap cleanup EXIT INT TERM

# Exception patterns - files/patterns to never delete during cleanup
EXCEPTION_PATTERNS=(
    "*.custom"
    "*.local"
    "*.new"
    "backup.*"
    ".git*"
    "CLAUDE.md"  # User might customize main config
    "RULES.md"   # User might customize rules
    "PERSONAS.md" # User might customize personas
    "MCP.md"     # User might customize MCP config
)

# User data files that should NEVER be deleted or overwritten
PRESERVE_FILES=(
    ".credentials.json"
    "settings.json"
    "settings.local.json"
    ".claude/todos"
    ".claude/statsig"
    ".claude/projects"
)

# Function: check_command
# Description: Check if a command exists (with caching)
# Parameters: $1 - command name
# Returns: 0 if command exists, 1 otherwise
check_command() {
    local cmd=$1
    if [[ -z "${COMMAND_CACHE[$cmd]:-}" ]]; then
        if command -v "$cmd" &> /dev/null; then
            COMMAND_CACHE[$cmd]="yes"
        else
            COMMAND_CACHE[$cmd]="no"
        fi
    fi
    [[ "${COMMAND_CACHE[$cmd]}" == "yes" ]]
}

# Function: rollback_installation
# Description: Rollback a failed installation using backup
# Parameters: None (uses global BACKUP_DIR)
# Returns: 0 on success, 1 on failure
rollback_installation() {
    if [[ -z "$BACKUP_DIR" ]] || [[ ! -d "$BACKUP_DIR" ]]; then
        log_error "No backup available for rollback"
        return 1
    fi
    
    echo -e "${YELLOW}Rolling back installation...${NC}" >&2
    
    # Remove failed installation
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR" 2>/dev/null || {
            log_error "Failed to remove failed installation"
            return 1
        }
    fi
    
    # Restore backup
    mv "$BACKUP_DIR" "$INSTALL_DIR" 2>/dev/null || {
        log_error "Failed to restore backup"
        return 1
    }
    
    echo -e "${GREEN}Installation rolled back successfully${NC}" >&2
    return 0
}

# Function: load_config
# Description: Load configuration from file if exists
# Parameters: $1 - config file path
# Returns: 0 on success
load_config() {
    local config_file="$1"
    if [[ -f "$config_file" ]] && [[ -r "$config_file" ]]; then
        # Source config file in a subshell to validate
        if (source "$config_file" 2>/dev/null); then
            source "$config_file"
            log_verbose "Loaded configuration from $config_file"
        else
            log_error "Invalid configuration file: $config_file"
            return 1
        fi
    fi
    return 0
}

# Function: show_usage
# Description: Display usage information
# Parameters: None
# Returns: None
show_usage() {
    echo "SuperClaude Installer v$SCRIPT_VERSION"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dir <directory>    Install to custom directory (default: $HOME/.claude)"
    echo "  --force              Skip confirmation prompts (for automation)"
    echo "  --update             Update existing installation (preserves customizations)"
    echo "  --uninstall          Remove SuperClaude from specified directory"
    echo "  --verify-checksums   Verify integrity of an existing installation"
    echo "  --verbose            Show detailed output during installation"
    echo "  --dry-run            Preview changes without making them"
    echo "  --log <file>         Save installation log to file"
    echo "  --config <file>      Load configuration from file"
    echo "  --no-rollback        Disable automatic rollback on failure"
    echo "  --check-update       Check for SuperClaude updates"
    echo "  --version            Show installer version"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Install to default location"
    echo "  $0 --dir /opt/claude        # Install to /opt/claude"
    echo "  $0 --dir ./local-claude     # Install to ./local-claude"
    echo "  $0 --force                  # Install without prompts"
    echo "  $0 --update                 # Update existing installation"
    echo "  $0 --uninstall              # Remove SuperClaude"
    echo "  $0 --verify-checksums       # Verify existing installation"
    echo "  $0 --dry-run --verbose      # Preview with detailed output"
}

# Function: log
# Description: Log a message to stdout and optionally to file
# Parameters: $1 - message
# Returns: None
log() {
    local message="$1"
    if [[ -n "$LOG_FILE" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
    fi
    echo "$message"
}

# Function: log_verbose
# Description: Log a verbose message (only shown with --verbose)
# Parameters: $1 - message
# Returns: None
log_verbose() {
    local message="$1"
    if [[ -n "$LOG_FILE" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [VERBOSE] $message" >> "$LOG_FILE"
    fi
    if [[ "$VERBOSE" = true ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $message" >&2
    fi
}

# Function: log_error
# Description: Log an error message to stderr
# Parameters: $1 - message
# Returns: None
log_error() {
    local message="$1"
    if [[ -n "$LOG_FILE" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $message" >> "$LOG_FILE"
    fi
    echo -e "${RED}[ERROR]${NC} $message" >&2
}

# Function: log_warning
# Description: Log a warning message to stderr
# Parameters: $1 - message
# Returns: None
log_warning() {
    local message="$1"
    if [[ -n "$LOG_FILE" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $message" >> "$LOG_FILE"
    fi
    echo -e "${YELLOW}[WARNING]${NC} $message" >&2
}

# Function: is_exception
# Description: Check if a file matches any exception pattern
# Parameters: $1 - file path
# Returns: 0 if matches exception pattern, 1 otherwise
is_exception() {
    local file="$1"
    local basename_file=$(basename "$file")
    
    for pattern in "${EXCEPTION_PATTERNS[@]}"; do
        if [[ "$basename_file" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Function: is_preserve_file
# Description: Check if a file should be preserved (user data)
# Parameters: $1 - file path
# Returns: 0 if file should be preserved, 1 otherwise
is_preserve_file() {
    local file="$1"
    
    for preserve in "${PRESERVE_FILES[@]}"; do
        # Check if the file path ends with the preserve pattern
        if [[ "$file" == *"$preserve" ]]; then
            return 0
        fi
    done
    return 1
}

# Function: verify_file_integrity
# Description: Verify file integrity using SHA256 checksums
# Parameters: $1 - source file, $2 - destination file
# Returns: 0 if checksums match, 1 otherwise
verify_file_integrity() {
    local src_file="$1"
    local dest_file="$2"
    
    # If sha256sum is not available, skip verification
    if ! check_command sha256sum; then
        log_verbose "sha256sum not available, skipping integrity check"
        return 0
    fi
    
    # Calculate checksums
    local src_checksum=$(sha256sum "$src_file" 2>/dev/null | awk '{print $1}')
    local dest_checksum=$(sha256sum "$dest_file" 2>/dev/null | awk '{print $1}')
    
    # Verify checksums match
    if [[ -z "$src_checksum" ]] || [[ -z "$dest_checksum" ]]; then
        log_verbose "Could not calculate checksums for $src_file"
        return 1
    fi
    
    if [[ "$src_checksum" != "$dest_checksum" ]]; then
        log_verbose "Checksum mismatch: $src_file ($src_checksum) != $dest_file ($dest_checksum)"
        return 1
    fi
    
    return 0
}

# Function: get_source_files
# Description: Get all source files relative to source root
# Parameters: $1 - source root directory
# Returns: List of files (one per line)
get_source_files() {
    local source_root="$1"
    local current_dir=$(pwd)
    cd "$source_root" || return 1
    
    # Find all files, excluding .git and backup directories
    find . -type f \
        -not -path "./.git*" \
        -not -path "./backup.*" \
        -not -name "install.sh" \
        -not -name "README.md" \
        -not -name "LICENSE" \
        -not -name "*.log" \
        -not -name "settings.local.json" \
        | sed 's|^\./||' | sort
    
    cd "$current_dir" || return 1
}

# Function: get_installed_files
# Description: Get all installed files relative to install directory
# Parameters: $1 - install directory
# Returns: List of files (one per line)
get_installed_files() {
    local install_dir="$1"
    local current_dir=$(pwd)
    cd "$install_dir" || return 1
    
    # Find all files, excluding backups
    find . -type f \
        -not -path "./backup.*" \
        | sed 's|^\./||' | sort
    
    cd "$current_dir" || return 1
}

# Function: check_for_updates
# Description: Check for SuperClaude updates from GitHub
# Parameters: None
# Returns: 0 if update available, 1 if up to date, 2 on error
check_for_updates() {
    local repo_url="https://api.github.com/repos/nshkrdotcom/SuperClaude/releases/latest"
    
    if ! check_command curl; then
        log_error "curl is required for update checking"
        return 2
    fi
    
    log "Checking for SuperClaude updates..."
    
    # Get latest release info
    local release_info=$(curl -s "$repo_url" 2>/dev/null)
    if [[ -z "$release_info" ]] || [[ "$release_info" == *"Not Found"* ]]; then
        log_error "Failed to check for updates"
        return 2
    fi
    
    # Extract version from release
    local latest_version=$(echo "$release_info" | grep -o '"tag_name":\s*"v\?[^"]*"' | sed 's/.*"v\?\([^"]*\)".*/\1/')
    if [[ -z "$latest_version" ]]; then
        log_error "Could not determine latest version"
        return 2
    fi
    
    log "Current version: $SCRIPT_VERSION"
    log "Latest version: $latest_version"
    
    # Compare versions (simple string comparison)
    if [[ "$SCRIPT_VERSION" < "$latest_version" ]]; then
        echo -e "${YELLOW}Update available!${NC}"
        echo "Download: https://github.com/nshkrdotcom/SuperClaude/releases/latest"
        return 0
    else
        echo -e "${GREEN}You have the latest version${NC}"
        return 1
    fi
}

# Function: find_obsolete_files
# Description: Find files in destination but not in source
# Parameters: $1 - source root, $2 - install directory
# Returns: List of obsolete files
find_obsolete_files() {
    local source_root="$1"
    local install_dir="$2"
    
    # Get file lists
    local source_files=$(get_source_files "$source_root" | sort | uniq)
    local installed_files=$(get_installed_files "$install_dir" | sort | uniq)
    
    # Find files that exist in installed but not in source
    comm -13 <(echo "$source_files") <(echo "$installed_files")
}

# Function: cleanup_obsolete_files
# Description: Remove obsolete files from installation
# Parameters: $1 - install directory, $2 - list of obsolete files
# Returns: 0 on success
cleanup_obsolete_files() {
    local install_dir="$1"
    local obsolete_files="$2"
    local cleaned_count=0
    
    if [[ -z "$obsolete_files" ]]; then
        echo "No obsolete files to clean up."
        return 0
    fi
    
    echo -e "${YELLOW}Found obsolete files to clean up:${NC}"
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            local full_path="$install_dir/$file"
            
            # Check if file should be preserved
            if is_exception "$file" || is_preserve_file "$file"; then
                echo "  Preserving: $file (protected file)"
            else
                if [[ "$DRY_RUN" = true ]]; then
                    echo "  Would remove: $file"
                else
                    echo "  Removing: $file"
                    rm -f "$full_path"
                fi
                ((cleaned_count++))
                
                # Remove empty parent directories
                if [[ "$DRY_RUN" != true ]]; then
                    local parent_dir=$(dirname "$full_path")
                    while [[ "$parent_dir" != "$install_dir" ]] && [[ -d "$parent_dir" ]] && [[ -z "$(ls -A "$parent_dir" 2>/dev/null)" ]]; do
                        rmdir "$parent_dir" 2>/dev/null
                        parent_dir=$(dirname "$parent_dir")
                    done
                fi
            fi
        fi
    done <<< "$obsolete_files"
    
    if [[ $cleaned_count -gt 0 ]]; then
        echo -e "${GREEN}Cleaned up $cleaned_count obsolete file(s)${NC}"
    fi
}

# Function: detect_platform
# Description: Detect the operating system platform
# Parameters: None
# Returns: Sets global OS variable
detect_platform() {
    OS="Unknown"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
        if grep -q Microsoft /proc/version 2>/dev/null; then
            OS="WSL"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="Windows"
    fi
    log_verbose "Detected platform: $OS"
}

# Function: run_preflight_checks
# Description: Run pre-installation validation checks
# Parameters: None
# Returns: 0 on success, exits on failure
run_preflight_checks() {
    log_verbose "Running pre-flight checks..."
    
    # Detect platform
    detect_platform
    
    # Check required commands
    local required_commands=("find" "comm" "cmp" "sort" "uniq" "basename" "dirname")
    local missing_commands=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        echo "Please install the missing commands and try again."
        exit 1
    fi
    
    # Check bash version (need at least 4.0 for associative arrays)
    local bash_major_version="${BASH_VERSION%%.*}"
    if [[ -z "$bash_major_version" ]] || [[ "$bash_major_version" -lt "$MIN_BASH_VERSION" ]]; then
        log_error "Bash version $MIN_BASH_VERSION.0 or higher required (current: ${BASH_VERSION:-unknown})"
        exit 1
    fi
    
    # Check disk space
    if [[ ! "$DRY_RUN" = true ]]; then
        local install_parent=$(dirname "$INSTALL_DIR")
        if [[ -d "$install_parent" ]]; then
            local available_space=$(df -k "$install_parent" 2>/dev/null | awk 'NR==2 {print $4}')
            if [[ -n "$available_space" ]] && [[ "$available_space" -lt "$REQUIRED_SPACE_KB" ]]; then
                log_error "Insufficient disk space. Need at least $((REQUIRED_SPACE_KB / 1024))MB free."
                exit 1
            fi
        fi
    fi
    
    # Platform-specific checks
    if [[ "$OS" == "macOS" ]]; then
        # macOS specific checks
        if ! command -v sw_vers &> /dev/null; then
            log_verbose "Running on macOS but sw_vers not found"
        else
            log_verbose "macOS version: $(sw_vers -productVersion)"
        fi
    fi
    
    log_verbose "Pre-flight checks passed"
}

# Load configuration from default locations
load_default_config() {
    # System-wide config
    if [[ -f "/etc/superclaude.conf" ]]; then
        load_config "/etc/superclaude.conf"
    fi
    
    # User config
    if [[ -f "$HOME/.superclaude.conf" ]]; then
        load_config "$HOME/.superclaude.conf"
    fi
    
    # Local config
    if [[ -f ".superclaude.conf" ]]; then
        load_config ".superclaude.conf"
    fi
}

# Load default configuration
load_default_config

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --force)
            FORCE_INSTALL=true
            shift
            ;;
        --update)
            UPDATE_MODE=true
            shift
            ;;
        --uninstall)
            UNINSTALL_MODE=true
            shift
            ;;
        --verify-checksums)
            VERIFY_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --config)
            if [[ -f "$2" ]]; then
                load_config "$2"
            else
                log_error "Configuration file not found: $2"
                exit 1
            fi
            shift 2
            ;;
        --no-rollback)
            ROLLBACK_ON_FAILURE=false
            shift
            ;;
        --check-update)
            check_for_updates
            exit $?
            ;;
        --log)
            LOG_FILE="$2"
            # Create log directory if needed
            log_dir=$(dirname "$LOG_FILE")
            if [[ ! -d "$log_dir" ]]; then
                mkdir -p "$log_dir" || {
                    echo -e "${RED}Error: Cannot create log directory $log_dir${NC}"
                    exit 1
                }
            fi
            shift 2
            ;;
        --version)
            echo "SuperClaude Installer v$SCRIPT_VERSION"
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Convert to absolute path if relative
if [[ ! "$INSTALL_DIR" = /* ]]; then
    # Check if parent directory exists
    parent_dir=$(dirname "$INSTALL_DIR")
    if [[ ! -d "$parent_dir" ]]; then
        echo -e "${RED}Error: Parent directory '$parent_dir' does not exist${NC}"
        exit 1
    fi
    INSTALL_DIR="$(cd "$parent_dir" && pwd)/$(basename "$INSTALL_DIR")" || {
        echo -e "${RED}Error: Failed to resolve installation directory${NC}"
        exit 1
    }
fi

# Handle uninstall mode
if [[ "$UNINSTALL_MODE" = true ]]; then
    echo -e "${GREEN}SuperClaude Uninstaller${NC}"
    echo "========================"
    echo -e "Target directory: ${YELLOW}$INSTALL_DIR${NC}"
    echo ""
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        echo -e "${RED}Error: SuperClaude not found at $INSTALL_DIR${NC}"
        exit 1
    fi
    
    if [[ "$FORCE_INSTALL" != true ]]; then
        echo -e "${YELLOW}This will remove SuperClaude from $INSTALL_DIR${NC}"
        echo -n "Are you sure you want to continue? (y/n): "
        read -r confirm_uninstall
        if [ "$confirm_uninstall" != "y" ]; then
            echo "Uninstall cancelled."
            exit 0
        fi
    fi
    
    echo "Removing SuperClaude files while preserving user data..."
    
    # Remove SuperClaude files but preserve user data
    removed_count=0
    preserved_count=0
    
    # First, remove all SuperClaude files (those that would be installed)
    if [[ -d "$INSTALL_DIR" ]]; then
        # Get list of files that would be installed from source
        current_dir=$(pwd)
        cd "$INSTALL_DIR" || exit 1
        
        # Process files and count them properly (avoid subshell issue)
        while IFS= read -r installed_file; do
            installed_file="${installed_file#./}"  # Remove leading ./
            
            if is_preserve_file "$installed_file"; then
                echo "  Preserving: $installed_file"
                ((preserved_count++))
            else
                # Check if this file exists in source (is a SuperClaude file)
                if [[ -f "$current_dir/$installed_file" ]] || [[ "$installed_file" =~ \.expanded$ ]]; then
                    if [[ "$DRY_RUN" = true ]]; then
                        echo "  Would remove: $installed_file"
                    else
                        echo "  Removing: $installed_file"
                        rm -f "$installed_file"
                    fi
                    ((removed_count++))
                fi
            fi
        done < <(find . -type f)
        
        # Remove empty directories, but not the main directory if it contains preserved files
        if [[ "$DRY_RUN" != true ]]; then
            find . -type d -empty -delete 2>/dev/null || true
        fi
        
        cd "$current_dir" || exit 1
        
        # Check if main directory is empty (no preserved files)
        if [[ -z "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]]; then
            if [[ "$DRY_RUN" != true ]]; then
                rmdir "$INSTALL_DIR" 2>/dev/null || true
            fi
            echo -e "${GREEN}✓ SuperClaude uninstalled completely!${NC}"
        else
            echo ""
            echo -e "${GREEN}✓ SuperClaude uninstalled successfully!${NC}"
            echo -e "${YELLOW}Note: User data files preserved in $INSTALL_DIR${NC}"
        fi
        
        # Show summary
        echo ""
        echo "Summary:"
        echo "  Files removed: $removed_count"
        echo "  Files preserved: $preserved_count"
    fi
    exit 0
fi

# Handle verify mode
if [[ "$VERIFY_MODE" = true ]]; then
    echo -e "${GREEN}SuperClaude Verification${NC}"
    echo "========================="
    echo -e "Target directory: ${YELLOW}$INSTALL_DIR${NC}"
    echo ""
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        echo -e "${RED}Error: SuperClaude not found at $INSTALL_DIR${NC}"
        exit 1
    fi
    
    # Check if we're in SuperClaude directory
    if [ ! -f "CLAUDE.md" ] || [ ! -d ".claude/commands" ]; then
        echo -e "${RED}Error: This script must be run from the SuperClaude directory${NC}"
        echo ""
        echo "Expected files not found. Please ensure you are in the root SuperClaude directory."
        echo "Missing: $([ ! -f "CLAUDE.md" ] && echo "CLAUDE.md ")$([ ! -d ".claude/commands" ] && echo ".claude/commands/")"
        echo ""
        echo "Solution: cd to the SuperClaude directory and run: ./install.sh --verify-checksums"
        exit 1
    fi
    
    # Check if checksums file exists
    checksums_file="$INSTALL_DIR/.checksums"
    if [[ ! -f "$checksums_file" ]]; then
        echo -e "${YELLOW}Warning: No checksums file found at $checksums_file${NC}"
        echo "The installation may have been done with an older version of the installer."
        echo ""
    fi
    
    # Verify installation against source
    echo "Verifying installation integrity..."
    
    if ! command -v sha256sum &> /dev/null; then
        echo -e "${YELLOW}Warning: sha256sum not available, cannot verify checksums${NC}"
        echo "Performing basic file comparison instead..."
        
        # Basic file existence check
        missing_files=0
        total_checked=0
        
        while IFS= read -r file; do
            ((total_checked++))
            if [[ ! -f "$INSTALL_DIR/$file" ]]; then
                echo -e "  Missing: $file"
                ((missing_files++))
            fi
        done < <(get_source_files ".")
        
        echo ""
        echo "Files checked: $total_checked"
        echo "Missing files: $missing_files"
        
        if [[ $missing_files -eq 0 ]]; then
            echo -e "${GREEN}✓ All files present${NC}"
        else
            echo -e "${RED}✗ Some files are missing${NC}"
            exit 1
        fi
    else
        # Full checksum verification
        verification_failures=0
        files_checked=0
        files_missing=0
        
        while IFS= read -r file; do
            ((files_checked++))
            src_file="./$file"
            dest_file="$INSTALL_DIR/$file"
            
            if [[ ! -f "$dest_file" ]]; then
                echo -e "  Missing: $file"
                ((files_missing++))
            elif ! verify_file_integrity "$src_file" "$dest_file"; then
                echo -e "  Mismatch: $file"
                ((verification_failures++))
            else
                log_verbose "  Verified: $file"
            fi
        done < <(get_source_files ".")
        
        echo ""
        echo "Summary:"
        echo "  Files checked: $files_checked"
        echo "  Files missing: $files_missing"
        echo "  Checksum mismatches: $verification_failures"
        echo ""
        
        if [[ $files_missing -eq 0 ]] && [[ $verification_failures -eq 0 ]]; then
            echo -e "${GREEN}✓ Installation verified successfully!${NC}"
            echo "All files match the source."
        else
            echo -e "${RED}✗ Verification failed${NC}"
            if [[ $files_missing -gt 0 ]]; then
                echo "Some files are missing from the installation."
            fi
            if [[ $verification_failures -gt 0 ]]; then
                echo "Some files differ from the source (may have been customized)."
            fi
            exit 1
        fi
    fi
    
    exit 0
fi

echo -e "${GREEN}SuperClaude Installer${NC}"
echo "======================"
echo -e "Installation directory: ${YELLOW}$INSTALL_DIR${NC}"
if [[ "$DRY_RUN" = true ]]; then
    echo -e "${BLUE}Mode: DRY RUN (no changes will be made)${NC}"
fi
if [[ "$VERBOSE" = true ]]; then
    echo -e "${BLUE}Mode: VERBOSE${NC}"
fi
if [[ -n "$LOG_FILE" ]]; then
    echo -e "Log file: ${YELLOW}$LOG_FILE${NC}"
fi
echo ""

# Run pre-flight checks
run_preflight_checks

# Check write permissions (using atomic test)
parent_for_write=$(dirname "$INSTALL_DIR")
write_test_file=""

if [[ -d "$INSTALL_DIR" ]]; then
    # Directory exists, test write permission atomically
    write_test_file="$INSTALL_DIR/.write_test_$$"
    if ! touch "$write_test_file" 2>/dev/null; then
        log_error "No write permission for $INSTALL_DIR"
        exit 1
    fi
    rm -f "$write_test_file" 2>/dev/null
else
    # Directory doesn't exist, test parent write permission
    if [[ ! -d "$parent_for_write" ]]; then
        log_error "Parent directory does not exist: $parent_for_write"
        exit 1
    fi
    write_test_file="$parent_for_write/.write_test_$$"
    if ! touch "$write_test_file" 2>/dev/null; then
        log_error "No write permission to create $INSTALL_DIR"
        exit 1
    fi
    rm -f "$write_test_file" 2>/dev/null
fi

# Confirmation prompt (skip if --force)
if [[ "$FORCE_INSTALL" != true ]]; then
    if [[ "$UPDATE_MODE" = true ]]; then
        echo -e "${YELLOW}This will update SuperClaude in $INSTALL_DIR${NC}"
    else
        echo -e "${YELLOW}This will install SuperClaude in $INSTALL_DIR${NC}"
    fi
    echo -n "Are you sure you want to continue? (y/n): "
    read -r confirm_install
    if [ "$confirm_install" != "y" ]; then
        echo "Installation cancelled."
        exit 0
    fi
fi
echo ""

# Check if we're in SuperClaude directory
if [ ! -f "CLAUDE.md" ] || [ ! -d ".claude/commands" ]; then
    echo -e "${RED}Error: This script must be run from the SuperClaude directory${NC}"
    echo ""
    echo "Expected files not found. Please ensure you are in the root SuperClaude directory."
    echo "Missing: $([ ! -f "CLAUDE.md" ] && echo "CLAUDE.md ")$([ ! -d ".claude/commands" ] && echo ".claude/commands/")"
    echo ""
    echo "Solution: cd to the SuperClaude directory and run: ./install.sh"
    exit 1
fi

# Get version information
SUPERCLAUDE_VERSION="unknown"
if [[ -f "VERSION" ]] && [[ -r "VERSION" ]]; then
    SUPERCLAUDE_VERSION=$(< VERSION) || SUPERCLAUDE_VERSION="unknown"
fi
log_verbose "SuperClaude version: $SUPERCLAUDE_VERSION"

# Check existing installation version
if [[ -f "$INSTALL_DIR/VERSION" ]] && [[ -r "$INSTALL_DIR/VERSION" ]]; then
    INSTALLED_VERSION=$(< "$INSTALL_DIR/VERSION") || INSTALLED_VERSION="unknown"
    log_verbose "Installed version: $INSTALLED_VERSION"
    
    if [[ "$UPDATE_MODE" = true ]]; then
        echo "Current version: $INSTALLED_VERSION"
        echo "New version: $SUPERCLAUDE_VERSION"
        echo ""
    fi
fi

# Check if existing directory exists and has files
if [ -d "$INSTALL_DIR" ] && [ "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]; then
    echo -e "${YELLOW}Existing configuration found at $INSTALL_DIR${NC}"
    
    # In update mode, always backup
    if [[ "$UPDATE_MODE" = true ]] || [[ "$FORCE_INSTALL" = true ]]; then
        backup_choice="y"
    else
        echo -n "Backup existing configuration? (y/n): "
        read -r backup_choice
    fi
    
    if [ "$backup_choice" = "y" ]; then
        # Create backup directory with secure random suffix
        backup_timestamp=$(date +%Y%m%d_%H%M%S)
        backup_random=$(head -c 8 /dev/urandom 2>/dev/null | od -An -tx1 | tr -d ' \n' || echo "$$")
        BACKUP_DIR="$(dirname "$INSTALL_DIR")/superclaude-backup.${backup_timestamp}.${backup_random}"
        mkdir -p "$BACKUP_DIR"
        
        # Backup ALL existing files
        echo "Backing up all existing files..."
        
        # Copy everything except backup directories
        for item in "$INSTALL_DIR"/*; do
            basename_item=$(basename "$item")
            # Skip backup directories to avoid nested backups
            if [[ ! "$basename_item" =~ ^backup\. ]]; then
                if [ -e "$item" ]; then
                    cp -r "$item" "$BACKUP_DIR/"
                fi
            fi
        done
        
        echo -e "${GREEN}Backed up existing files to: $BACKUP_DIR${NC}"
    fi
elif [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Directory $INSTALL_DIR exists but is empty${NC}"
fi

# In update mode, clean up obsolete files before copying new ones
if [[ "$UPDATE_MODE" = true ]] && [[ -d "$INSTALL_DIR" ]]; then
    echo ""
    echo "Checking for obsolete files..."
    
    # Find obsolete files
    obsolete_files=$(find_obsolete_files "." "$INSTALL_DIR")
    
    if [[ -n "$obsolete_files" ]]; then
        cleanup_obsolete_files "$INSTALL_DIR" "$obsolete_files"
    else
        echo "No obsolete files found."
    fi
fi

echo ""
if [[ "$UPDATE_MODE" = true ]]; then
    echo "Updating SuperClaude..."
else
    echo "Installing SuperClaude..."
fi

# Create directory structure dynamically based on source
if [[ "$DRY_RUN" != true ]]; then
    echo "Creating directory structure..."
    # Find all directories in source and create them in destination
    find . -type d \
        -not -path "./.git*" \
        -not -path "./backup.*" \
        -not -name "." \
        | while read -r dir; do
        mkdir -p "$INSTALL_DIR/${dir#./}"
    done
else
    echo "Would create directory structure..."
fi

# Function to copy files with update mode handling and integrity verification
copy_with_update_check() {
    local src_file="$1"
    local dest_file="$2"
    local basename_file=$(basename "$src_file")
    local copy_performed=false
    local target_file="$dest_file"
    
    if [[ "$UPDATE_MODE" = true ]] && [[ -f "$dest_file" ]]; then
        # Check if file differs from source
        if ! cmp -s "$src_file" "$dest_file"; then
            # Check if it's a main config file that might be customized
            local is_customizable=false
            for config in "${CUSTOMIZABLE_CONFIGS[@]}"; do
                if [[ "$basename_file" == "$config" ]]; then
                    is_customizable=true
                    break
                fi
            done
            
            if [[ "$is_customizable" = true ]]; then
                echo "  Preserving customized $basename_file (new version: $basename_file.new)"
                if [[ "$DRY_RUN" != true ]]; then
                    cp "$src_file" "$dest_file.new"
                    target_file="$dest_file.new"
                    copy_performed=true
                fi
            else
                if [[ "$DRY_RUN" != true ]]; then
                    cp "$src_file" "$dest_file"
                    copy_performed=true
                fi
            fi
        else
            if [[ "$DRY_RUN" != true ]]; then
                cp "$src_file" "$dest_file"
                copy_performed=true
            fi
        fi
    else
        if [[ "$DRY_RUN" != true ]]; then
            cp "$src_file" "$dest_file"
            copy_performed=true
        fi
    fi
    
    # Verify integrity after copy
    if [[ "$copy_performed" = true ]] && [[ "$DRY_RUN" != true ]]; then
        if ! verify_file_integrity "$src_file" "$target_file"; then
            log_error "Integrity verification failed for $basename_file"
            ((VERIFICATION_FAILURES++))
            return 1
        fi
        log_verbose "Integrity verified for $basename_file"
    fi
    
    return 0
}

# Copy all files dynamically
echo "Copying files..."
# Get total file count for progress tracking
total_files=$(get_source_files "." | wc -l)
current_file=0
copied_count=0
preserved_count=0

# Process files with progress tracking
while IFS= read -r file; do
    if [[ -n "$file" ]]; then
        ((current_file++))
        src_file="./$file"
        dest_file="$INSTALL_DIR/$file"
        
        # Show progress
        if [[ "$VERBOSE" = true ]] || [[ $((current_file % 10)) -eq 0 ]]; then
            printf "\r  Progress: [%3d/%3d] Processing: %-50s" "$current_file" "$total_files" "${file:0:50}"
        fi
        
        # Create parent directory if needed
        dest_dir=$(dirname "$dest_file")
        if [[ "$DRY_RUN" != true ]]; then
            mkdir -p "$dest_dir"
        fi
        
        # Check if this is a preserved user file
        if is_preserve_file "$file" && [[ -f "$dest_file" ]]; then
            log_verbose "Preserving user file: $file"
            ((preserved_count++))
        else
            # Copy the file
            if [[ "$DRY_RUN" != true ]]; then
                copy_with_update_check "$src_file" "$dest_file"
                
                # Make scripts executable
                if [[ "$file" == *.sh ]]; then
                    chmod +x "$dest_file"
                fi
            fi
            ((copied_count++))
        fi
    fi
done < <(get_source_files ".")

# Clear progress line and show summary
printf "\r%-80s\r" " "
echo "  Files copied: $copied_count"
echo "  Files preserved: $preserved_count"


# Verify installation
echo ""
echo "Verifying installation..."

# Report verification failures from copy operations
if [[ $VERIFICATION_FAILURES -gt 0 ]]; then
    echo -e "${RED}Warning: $VERIFICATION_FAILURES file(s) failed integrity verification during copy${NC}"
fi

# Generate checksums for installed files
if command -v sha256sum &> /dev/null && [[ "$DRY_RUN" != true ]]; then
    echo "Generating checksums for installed files..."
    checksums_file="$INSTALL_DIR/.checksums"
    
    # Create checksums file
    > "$checksums_file"
    
    # Generate checksums for all installed files
    cd "$INSTALL_DIR" || exit 1
    find . -type f -not -path "./backup.*" -not -name ".checksums" | sort | while read -r file; do
        # Skip empty files
        if [[ -s "$file" ]]; then
            checksum=$(sha256sum "$file" 2>/dev/null | awk '{print $1}')
            if [[ -n "$checksum" ]]; then
                echo "$checksum  $file" >> "$checksums_file"
            fi
        fi
    done
    cd "$ORIGINAL_DIR" || { log_error "Failed to return to original directory"; exit 1; }
    
    log_verbose "Generated checksums file at $checksums_file"
else
    log_verbose "sha256sum not available or dry run mode, skipping checksum generation"
fi

# Get expected files from source
expected_files=$(get_source_files "." | wc -l)
actual_files=$(get_installed_files "$INSTALL_DIR" | wc -l)

# Count files by category for detailed report
main_files=$(find "$INSTALL_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)
command_files=$(find "$INSTALL_DIR/commands" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)
shared_yml=$(find "$INSTALL_DIR/commands/shared" -name "*.yml" -type f 2>/dev/null | wc -l)
shared_scripts=$(find "$INSTALL_DIR/commands/shared" -name "*.sh" -type f 2>/dev/null | wc -l)
claude_shared=$(find "$INSTALL_DIR/shared" -name "*.yml" -type f 2>/dev/null | wc -l)

echo -e "Total files: ${GREEN}$actual_files${NC} (expected: $expected_files)"
echo ""
echo "File breakdown:"
echo -e "  Main config files: ${GREEN}$main_files${NC}"
echo -e "  Command files: ${GREEN}$command_files${NC}"
echo -e "  Shared YML files: ${GREEN}$shared_yml${NC}"
echo -e "  Shared scripts: ${GREEN}$shared_scripts${NC}"
echo -e "  Claude shared files: ${GREEN}$claude_shared${NC}"

# Verify critical files exist
critical_files_ok=true
for critical_file in "CLAUDE.md" ".claude/commands" ".claude/shared"; do
    if [[ ! -e "$INSTALL_DIR/$critical_file" ]]; then
        echo -e "${YELLOW}Warning: Critical file/directory missing: $critical_file${NC}"
        critical_files_ok=false
    fi
done

# Check if installation was successful
if [ "$actual_files" -ge "$expected_files" ] && [ "$critical_files_ok" = true ] && [ $VERIFICATION_FAILURES -eq 0 ]; then
    echo ""
    if [[ "$UPDATE_MODE" = true ]]; then
        echo -e "${GREEN}✓ SuperClaude updated successfully!${NC}"
        echo ""
        # Check for .new files
        new_files=$(find "$INSTALL_DIR" -name "*.new" 2>/dev/null)
        if [[ -n "$new_files" ]]; then
            echo -e "${YELLOW}Note: The following files have updates available:${NC}"
            echo "$new_files" | while read -r file; do
                echo "  - $file"
            done
            echo ""
            echo "To review changes: diff <file> <file>.new"
            echo "To apply update: mv <file>.new <file>"
            echo ""
        fi
    else
        echo -e "${GREEN}✓ SuperClaude installed successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Open any project with Claude Code"
        echo "2. Try a command: /analyze --code"
        echo "3. Activate a persona: /analyze --persona-architect"
        echo ""
    fi
    if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}Note: Your previous configuration was backed up to:${NC}"
        echo "$BACKUP_DIR"
        echo ""
    fi
    echo "For more information, see README.md"
else
    echo ""
    echo -e "${RED}✗ Installation may be incomplete${NC}"
    echo ""
    echo "Expected vs Actual file counts:"
    echo "  Total files: $actual_files/$expected_files$([ "$actual_files" -lt "$expected_files" ] && echo " ❌" || echo " ✓")"
    if [ $VERIFICATION_FAILURES -gt 0 ]; then
        echo "  Integrity failures: $VERIFICATION_FAILURES ❌"
    fi
    echo ""
    
    # List missing files if any
    if [ "$actual_files" -lt "$expected_files" ]; then
        echo "Missing files:"
        comm -23 <(get_source_files "." | sort) <(get_installed_files "$INSTALL_DIR" | sort) | head -10 | while read -r file; do
            echo "  - $file"
        done
        echo ""
    fi
    
    echo "Troubleshooting steps:"
    echo "1. Check for error messages above"
    echo "2. Ensure you have write permissions to $INSTALL_DIR"
    echo "3. Verify all source files exist in the current directory"
    echo "4. Try running with sudo if permission errors occur"
    echo ""
    echo "For manual installation, see README.md"
    exit 1
fi