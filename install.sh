#!/bin/bash

# SuperClaude Installer Script
# Installs SuperClaude configuration framework to enhance Claude Code

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default installation directory
INSTALL_DIR="$HOME/.claude"
FORCE_INSTALL=false
UPDATE_MODE=false
UNINSTALL_MODE=false

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dir <directory>    Install to custom directory (default: $HOME/.claude)"
    echo "  --force              Skip confirmation prompts (for automation)"
    echo "  --update             Update existing installation (preserves customizations)"
    echo "  --uninstall          Remove SuperClaude from specified directory"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Install to default location"
    echo "  $0 --dir /opt/claude        # Install to /opt/claude"
    echo "  $0 --dir ./local-claude     # Install to ./local-claude"
    echo "  $0 --force                  # Install without prompts"
    echo "  $0 --update                 # Update existing installation"
    echo "  $0 --uninstall              # Remove SuperClaude"
}

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
    INSTALL_DIR="$(cd "$parent_dir" && pwd)/$(basename "$INSTALL_DIR")"
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
    
    echo "Removing SuperClaude..."
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓ SuperClaude uninstalled successfully!${NC}"
    exit 0
fi

echo -e "${GREEN}SuperClaude Installer${NC}"
echo "======================"
echo -e "Installation directory: ${YELLOW}$INSTALL_DIR${NC}"
echo ""

# Check write permissions
parent_for_write=$(dirname "$INSTALL_DIR")
if [[ -d "$INSTALL_DIR" ]]; then
    # Directory exists, check if we can write to it
    if [[ ! -w "$INSTALL_DIR" ]]; then
        echo -e "${RED}Error: No write permission for $INSTALL_DIR${NC}"
        exit 1
    fi
elif [[ ! -w "$parent_for_write" ]]; then
    # Directory doesn't exist, check if we can create it
    echo -e "${RED}Error: No write permission to create $INSTALL_DIR${NC}"
    exit 1
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
        # Create backup directory in parent directory to avoid conflicts
        backup_dir="$(dirname "$INSTALL_DIR")/superclaude-backup.$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Backup ALL existing files
        echo "Backing up all existing files..."
        
        # Copy everything except backup directories
        for item in "$INSTALL_DIR"/*; do
            basename_item=$(basename "$item")
            # Skip backup directories to avoid nested backups
            if [[ ! "$basename_item" =~ ^backup\. ]]; then
                if [ -e "$item" ]; then
                    cp -r "$item" "$backup_dir/"
                fi
            fi
        done
        
        echo -e "${GREEN}Backed up existing files to: $backup_dir${NC}"
    fi
elif [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Directory $INSTALL_DIR exists but is empty${NC}"
fi

echo ""
if [[ "$UPDATE_MODE" = true ]]; then
    echo "Updating SuperClaude..."
else
    echo "Installing SuperClaude..."
fi

# Create directory structure
echo "Creating directories..."
mkdir -p "$INSTALL_DIR/commands/shared"

# Copy main configuration files
echo "Copying configuration files..."
if [[ "$UPDATE_MODE" = true ]]; then
    # In update mode, preserve user modifications
    for file in CLAUDE.md RULES.md PERSONAS.md MCP.md; do
        if [[ -f "$INSTALL_DIR/$file" ]]; then
            # Check if file differs from source
            if ! cmp -s "$file" "$INSTALL_DIR/$file"; then
                echo "  Preserving customized $file (new version: $file.new)"
                cp "$file" "$INSTALL_DIR/$file.new"
            else
                cp "$file" "$INSTALL_DIR/"
            fi
        else
            cp "$file" "$INSTALL_DIR/"
        fi
    done
else
    cp CLAUDE.md RULES.md PERSONAS.md MCP.md "$INSTALL_DIR/"
fi

# Copy command files
echo "Copying slash commands..."
cp .claude/commands/*.md "$INSTALL_DIR/commands/" 2>/dev/null || true

# Copy shared resources
echo "Copying shared resources..."
cp .claude/commands/shared/*.yml "$INSTALL_DIR/commands/shared/"
cp .claude/commands/shared/*.md "$INSTALL_DIR/commands/shared/" 2>/dev/null || true
cp .claude/commands/shared/*.sh "$INSTALL_DIR/commands/shared/" 2>/dev/null || true

# Make scripts executable
chmod +x "$INSTALL_DIR/commands/shared/"*.sh 2>/dev/null || true

# Expand @ references in command files
echo "Expanding references in command files..."
if [[ -f "$INSTALL_DIR/commands/shared/expand-references.sh" ]]; then
    cd "$INSTALL_DIR/commands/shared" && ./expand-references.sh >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        echo -e "  ${GREEN}✓ References expanded successfully${NC}"
    else
        echo -e "  ${YELLOW}⚠ Reference expansion completed with warnings${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Reference expansion script not found${NC}"
fi

# Verify installation
echo ""
echo "Verifying installation..."

# Count installed files
main_files=$(ls -1 "$INSTALL_DIR/"*.md 2>/dev/null | wc -l)
command_files=$(ls -1 "$INSTALL_DIR/commands/"*.md 2>/dev/null | wc -l)
shared_files=$(find "$INSTALL_DIR/commands/shared/" -name "*.yml" -o -name "*.md" -o -name "*.sh" 2>/dev/null | wc -l)

echo -e "Main config files: ${GREEN}$main_files${NC} (expected: 4)"
echo -e "Command files: ${GREEN}$command_files${NC} (expected: 21)"
echo -e "Shared resources: ${GREEN}$shared_files${NC} (expected: 25)"

# Check if installation was successful
if [ "$main_files" -ge 4 ] && [ "$command_files" -ge 21 ] && [ "$shared_files" -ge 25 ]; then
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
        echo "3. Activate a persona: /persona:architect"
        echo ""
    fi
    if [ -n "$backup_dir" ] && [ -d "$backup_dir" ]; then
        echo -e "${YELLOW}Note: Your previous configuration was backed up to:${NC}"
        echo "$backup_dir"
        echo ""
    fi
    echo "For more information, see README.md"
else
    echo ""
    echo -e "${RED}✗ Installation may be incomplete${NC}"
    echo ""
    echo "Expected vs Actual file counts:"
    echo "  Main config files: $main_files/4$([ "$main_files" -lt 4 ] && echo " ❌" || echo " ✓")"
    echo "  Command files: $command_files/21$([ "$command_files" -lt 21 ] && echo " ❌" || echo " ✓")"
    echo "  Shared resources: $shared_files/25$([ "$shared_files" -lt 25 ] && echo " ❌" || echo " ✓")"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check for error messages above"
    echo "2. Ensure you have write permissions to $INSTALL_DIR"
    echo "3. Verify all source files exist in the current directory"
    echo "4. Try running with sudo if permission errors occur"
    echo ""
    echo "For manual installation, see README.md"
    exit 1
fi