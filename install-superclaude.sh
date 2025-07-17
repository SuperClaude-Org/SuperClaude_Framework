#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
ORANGE='\033[38;2;255;140;0m'
NC='\033[0m' # No Color

print_message() {
    local level=$1
    local message=$2
    local color=""

    case $level in
        info) color="${GREEN}" ;;
        warning) color="${YELLOW}" ;;
        error) color="${RED}" ;;
    esac

    echo -e "${color}${message}${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        # Check if it's Python 3
        if python --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="python"
        else
            print_message error "Python 3 is required but not found. Please install Python 3.7 or higher."
            exit 1
        fi
    else
        print_message error "Python is not installed. Please install Python 3.7 or higher."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 7 ]]; then
        print_message error "Python 3.7 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi

    print_message info "Found Python: $PYTHON_VERSION"
}

# Check if pip is installed
check_pip() {
    # First try python -m pip
    if $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        PIP_CMD="$PYTHON_CMD -m pip"
        return 0
    fi
    
    # Try pip3
    if command -v pip3 >/dev/null 2>&1; then
        PIP_CMD="pip3"
        return 0
    fi
    
    # Try pip
    if command -v pip >/dev/null 2>&1; then
        # Check if it's for Python 3
        if pip --version 2>&1 | grep -q "python 3"; then
            PIP_CMD="pip"
            return 0
        fi
    fi
    
    print_message error "pip is not installed. Please install pip for Python 3."
    print_message info "You can install pip with one of these methods:"
    print_message info "  - $PYTHON_CMD -m ensurepip --upgrade"
    print_message info "  - sudo apt-get install python3-pip (on Ubuntu/Debian)"
    print_message info "  - curl https://bootstrap.pypa.io/get-pip.py | $PYTHON_CMD"
    exit 1
}

# Check if SuperClaude is already installed
check_existing_installation() {
    # Skip prompts if FORCE_INSTALL is set
    if [ "${FORCE_INSTALL:-false}" = true ]; then
        return 1  # Always proceed with installation
    fi
    
    # Check pipx first
    if command -v pipx >/dev/null 2>&1 && pipx list 2>/dev/null | grep -q "SuperClaude"; then
        INSTALLED_VERSION=$(pipx list --json 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('venvs', {}).get('superclaude', {}).get('metadata', {}).get('main_package', {}).get('package_version', 'unknown'))" 2>/dev/null || echo "unknown")
        print_message info "SuperClaude is already installed via pipx (version: ${YELLOW}$INSTALLED_VERSION${GREEN})"
        
        read -p "Do you want to upgrade to the latest version? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message info "Keeping existing installation."
            return 0
        fi
        return 1
    fi
    
    # Check regular pip installation
    if $PIP_CMD show SuperClaude >/dev/null 2>&1; then
        INSTALLED_VERSION=$($PIP_CMD show SuperClaude | grep Version | awk '{print $2}')
        print_message info "SuperClaude is already installed (version: ${YELLOW}$INSTALLED_VERSION${GREEN})"
        
        read -p "Do you want to upgrade to the latest version? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message info "Keeping existing installation."
            return 0
        fi
        return 1
    fi
    return 1
}

# Install or upgrade SuperClaude
install_superclaude() {
    print_message info "Installing ${ORANGE}SuperClaude${GREEN}..."
    
    # Check if we're in an externally managed environment
    # First, try a simple pip install to check for the error
    if ! $PIP_CMD install --dry-run SuperClaude >/dev/null 2>&1; then
        # If it failed, check if it's due to externally managed environment
        ERROR_MSG=$($PIP_CMD install --dry-run SuperClaude 2>&1 || true)
        if echo "$ERROR_MSG" | grep -q "externally-managed-environment"; then
            print_message warning "Detected externally managed Python environment"
            print_message info "Using pipx for isolated installation..."
            
            # Check if pipx is installed
            if ! command -v pipx >/dev/null 2>&1; then
                print_message info "Installing pipx..."
                if command -v apt-get >/dev/null 2>&1; then
                    sudo apt-get update && sudo apt-get install -y pipx || {
                        print_message error "Failed to install pipx"
                        print_message info "Try: sudo apt-get install pipx"
                        exit 1
                    }
                else
                    # Try installing via pip with break-system-packages flag
                    $PIP_CMD install --user --break-system-packages pipx || {
                        print_message error "Failed to install pipx"
                        exit 1
                    }
                fi
                
                # Ensure pipx bin is in PATH
                export PATH="$HOME/.local/bin:$PATH"
                pipx ensurepath
            fi
            
            # Install/upgrade SuperClaude using pipx
            if pipx install SuperClaude --force; then
                print_message info "${GREEN}SuperClaude installed successfully via pipx!${NC}"
                print_message info "Note: SuperClaude is installed in an isolated environment"
            else
                print_message error "Failed to install SuperClaude via pipx"
                exit 1
            fi
        else
            # Other pip error - try traditional install anyway
            if $PIP_CMD install --upgrade SuperClaude; then
                print_message info "${GREEN}SuperClaude installed successfully!${NC}"
            else
                print_message error "Failed to install SuperClaude"
                print_message error "Error: $ERROR_MSG"
                exit 1
            fi
        fi
    else
        # Traditional pip install (dry-run succeeded)
        if $PIP_CMD install --upgrade SuperClaude; then
            print_message info "${GREEN}SuperClaude installed successfully!${NC}"
        else
            print_message error "Failed to install SuperClaude"
            exit 1
        fi
    fi
}

# Setup PATH and run SuperClaude component installation
setup_and_configure() {
    local SUPERCLAUDE_CMD=""
    
    # Find the SuperClaude command
    if command -v superclaude >/dev/null 2>&1; then
        SUPERCLAUDE_CMD="superclaude"
    elif command -v SuperClaude >/dev/null 2>&1; then
        SUPERCLAUDE_CMD="SuperClaude"
    elif [ -f "$HOME/.local/bin/superclaude" ]; then
        SUPERCLAUDE_CMD="$HOME/.local/bin/superclaude"
    elif [ -f "/config/.local/bin/superclaude" ]; then
        SUPERCLAUDE_CMD="/config/.local/bin/superclaude"
    else
        print_message error "Could not find SuperClaude executable after installation"
        exit 1
    fi
    
    print_message info "Running SuperClaude component installation..."
    
    # Create expect script for automated installation
    cat > /tmp/superclaude_auto_install.expect << 'EOF'
#!/usr/bin/expect -f
set timeout 30
set superclaude_cmd [lindex $argv 0]

spawn $superclaude_cmd install

# Wait for installation type prompt
expect {
    "Enter your choice (1-3):" {
        send "1\r"
    }
    timeout {
        puts "Timeout waiting for installation type prompt"
        exit 1
    }
}

# Wait for existing installation prompt
expect {
    "Continue and update existing installation?" {
        send "y\r"
    }
    "Proceed with installation?" {
        # No existing installation, continue
    }
    timeout {
        puts "Timeout waiting for installation confirmation"
        exit 1
    }
}

# Wait for final installation prompt
expect {
    "Proceed with installation?" {
        send "y\r"
    }
    "Next steps:" {
        # Installation already complete
        exit 0
    }
    timeout {
        puts "Timeout waiting for final confirmation"
        exit 1
    }
}

# Wait for completion
expect {
    "Next steps:" {
        exit 0
    }
    eof {
        exit 0
    }
    timeout {
        puts "Timeout waiting for installation completion"
        exit 1
    }
}
EOF
    
    chmod +x /tmp/superclaude_auto_install.expect
    
    # Check if expect is installed
    if ! command -v expect >/dev/null 2>&1; then
        print_message info "Installing expect for automated setup..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y expect
        else
            print_message warning "Cannot install expect automatically. Running manual installation..."
            # Fallback to manual command with instructions
            print_message info ""
            print_message info "Please run the following command manually and select option 1 for Quick Installation:"
            print_message info "${YELLOW}$SUPERCLAUDE_CMD install${NC}"
            return
        fi
    fi
    
    # Run automated installation
    if /tmp/superclaude_auto_install.expect "$SUPERCLAUDE_CMD"; then
        print_message info "${GREEN}SuperClaude components installed successfully!${NC}"
    else
        print_message warning "Automated installation may have had issues. You can run manually:"
        print_message info "${YELLOW}$SUPERCLAUDE_CMD install${NC}"
    fi
    
    # Cleanup
    rm -f /tmp/superclaude_auto_install.expect
}

# Update PATH configuration
update_path_config() {
    local PATH_ADDED=false
    
    # For the current session
    export PATH="$HOME/.local/bin:$PATH"
    export PATH="/config/.local/bin:$PATH"
    
    # Determine which PATH to add based on where SuperClaude is installed
    local PATH_TO_ADD=""
    if [ -f "/config/.local/bin/superclaude" ]; then
        PATH_TO_ADD="/config/.local/bin"
    else
        PATH_TO_ADD="$HOME/.local/bin"
    fi
    
    # Update shell configuration files
    for rcfile in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "/config/.bashrc"; do
        if [ -f "$rcfile" ]; then
            if ! grep -q "$PATH_TO_ADD" "$rcfile"; then
                echo "" >> "$rcfile"
                echo "# Added by SuperClaude installer" >> "$rcfile"
                echo "export PATH=\"$PATH_TO_ADD:\$PATH\"" >> "$rcfile"
                PATH_ADDED=true
                print_message info "Updated PATH in $rcfile"
            fi
        fi
    done
    
    if [ "$PATH_ADDED" = true ]; then
        print_message info "PATH has been updated in your shell configuration"
    fi
}

# Main installation flow
main() {
    print_message info "Starting SuperClaude installation..."
    
    # Check prerequisites
    check_python
    check_pip
    
    # Force installation/upgrade without prompting
    FORCE_INSTALL=true
    
    # Check for existing installation but don't prompt
    if command -v pipx >/dev/null 2>&1 && pipx list 2>/dev/null | grep -q "SuperClaude"; then
        INSTALLED_VERSION=$(pipx list --json 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('venvs', {}).get('superclaude', {}).get('metadata', {}).get('main_package', {}).get('package_version', 'unknown'))" 2>/dev/null || echo "unknown")
        print_message info "Found existing SuperClaude installation (version: ${YELLOW}$INSTALLED_VERSION${GREEN})"
        print_message info "Upgrading to latest version..."
    elif $PIP_CMD show SuperClaude >/dev/null 2>&1; then
        INSTALLED_VERSION=$($PIP_CMD show SuperClaude | grep Version | awk '{print $2}')
        print_message info "Found existing SuperClaude installation (version: ${YELLOW}$INSTALLED_VERSION${GREEN})"
        print_message info "Upgrading to latest version..."
    fi
    
    # Install or upgrade
    install_superclaude
    
    # Update PATH configuration
    update_path_config
    
    # Post-installation message
    print_message info ""
    print_message info "${GREEN}SuperClaude package installation complete!${NC}"
    print_message info ""
    
    # Setup and configure SuperClaude components
    setup_and_configure
    
    print_message info ""
    print_message info "${GREEN}Full installation completed successfully!${NC}"
    print_message info ""
    print_message info "SuperClaude is now ready to use with Claude Code."
    print_message info "The framework files are available in ~/.claude"
    print_message info ""
    print_message info "You may need to restart your shell or run:"
    print_message info "${YELLOW}source ~/.bashrc${NC}"
}

# Run main function
main
