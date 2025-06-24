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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dir <directory>    Install to custom directory (default: $HOME/.claude)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Install to default location"
    echo "  $0 --dir /opt/claude        # Install to /opt/claude"
    echo "  $0 --dir ./local-claude     # Install to ./local-claude"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dir)
            INSTALL_DIR="$2"
            shift 2
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
    INSTALL_DIR="$(cd "$(dirname "$INSTALL_DIR")" && pwd)/$(basename "$INSTALL_DIR")"
fi

echo -e "${GREEN}SuperClaude Installer${NC}"
echo "======================"
echo -e "Installation directory: ${YELLOW}$INSTALL_DIR${NC}"
echo ""

# Confirmation prompt
echo -e "${YELLOW}This will install SuperClaude in $INSTALL_DIR${NC}"
echo -n "Are you sure you want to continue? (y/n): "
read -r confirm_install
if [ "$confirm_install" != "y" ]; then
    echo "Installation cancelled."
    exit 0
fi
echo ""

# Check if we're in SuperClaude directory
if [ ! -f "CLAUDE.md" ] || [ ! -d ".claude/commands" ]; then
    echo -e "${RED}Error: This script must be run from the SuperClaude directory${NC}"
    echo "Please cd into the SuperClaude directory and try again."
    exit 1
fi

# Check if existing directory exists and has files
if [ -d "$INSTALL_DIR" ] && [ "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]; then
    echo -e "${YELLOW}Existing configuration found at $INSTALL_DIR${NC}"
    echo -n "Backup existing configuration? (y/n): "
    read -r backup_choice
    if [ "$backup_choice" = "y" ]; then
        # Create backup directory inside installation directory
        backup_dir="$INSTALL_DIR/backup.$(date +%Y%m%d_%H%M%S)"
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
echo "Installing SuperClaude..."

# Create directory structure
echo "Creating directories..."
mkdir -p "$INSTALL_DIR/commands/shared"

# Copy main configuration files
echo "Copying configuration files..."
cp CLAUDE.md RULES.md PERSONAS.md MCP.md "$INSTALL_DIR/"

# Copy command files
echo "Copying slash commands..."
cp .claude/commands/*.md "$INSTALL_DIR/commands/" 2>/dev/null || true

# Copy shared resources
echo "Copying shared resources..."
cp .claude/commands/shared/*.yml "$INSTALL_DIR/commands/shared/"

# Verify installation
echo ""
echo "Verifying installation..."

# Count installed files
main_files=$(ls -1 "$INSTALL_DIR/"*.md 2>/dev/null | wc -l)
command_files=$(ls -1 "$INSTALL_DIR/commands/"*.md 2>/dev/null | wc -l)
shared_files=$(ls -1 "$INSTALL_DIR/commands/shared/"*.yml 2>/dev/null | wc -l)

echo -e "Main config files: ${GREEN}$main_files${NC} (expected: 4)"
echo -e "Command files: ${GREEN}$command_files${NC} (expected: 19)"
echo -e "Shared resources: ${GREEN}$shared_files${NC} (expected: 31)"

# Check if installation was successful
if [ "$main_files" -ge 4 ] && [ "$command_files" -ge 19 ] && [ "$shared_files" -ge 31 ]; then
    echo ""
    echo -e "${GREEN}✓ SuperClaude installed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Open any project with Claude Code"
    echo "2. Try a command: /user:analyze --code"
    echo "3. Activate a persona: /persona:architect"
    echo ""
    if [ -n "$backup_dir" ] && [ -d "$backup_dir" ]; then
        echo -e "${YELLOW}Note: Your previous configuration was backed up to:${NC}"
        echo "$backup_dir"
        echo ""
    fi
    echo "For more information, see README.md"
else
    echo ""
    echo -e "${RED}✗ Installation may be incomplete${NC}"
    echo "Please check the error messages above or install manually."
    echo "See README.md for manual installation instructions."
    exit 1
fi