# SuperClaude PowerShell Installer Script
# Installs SuperClaude configuration framework to enhance Claude Code
# Version: 2.0.0
# License: MIT
# Repository: https://github.com/NomenAK/SuperClaude

param(
    [string]$InstallDir = "$env:USERPROFILE\.claude",
    [switch]$Force,
    [switch]$Update,
    [switch]$Uninstall,
    [switch]$VerifyChecksums,
    [switch]$Verbose,
    [switch]$DryRun,
    [string]$LogFile = "",
    [string]$ConfigFile = "",
    [switch]$NoRollback,
    [switch]$CheckUpdate,
    [switch]$Help
)

# Script version
$SCRIPT_VERSION = "2.0.0"

# Constants
$REQUIRED_SPACE_MB = 50
$CHECKSUM_FILE = ".checksums"
$CONFIG_FILE = ".superclaude.conf"

# Configuration patterns
$CUSTOMIZABLE_CONFIGS = @("CLAUDE.md", "RULES.md", "PERSONAS.md", "MCP.md")

# Default settings
$FORCE_INSTALL = $Force
$UPDATE_MODE = $Update
$UNINSTALL_MODE = $Uninstall
$VERIFY_MODE = $VerifyChecksums
$VERBOSE_MODE = $Verbose
$DRY_RUN_MODE = $DryRun
$VERIFICATION_FAILURES = 0
$ROLLBACK_ON_FAILURE = -not $NoRollback
$BACKUP_DIR = ""
$INSTALLATION_PHASE = $false

# Error/Warning tracking
$ERROR_COUNT = 0
$WARNING_COUNT = 0
$ERROR_DETAILS = @()
$WARNING_DETAILS = @()

# Exception patterns - files/patterns to never delete during cleanup
$EXCEPTION_PATTERNS = @(
    "*.custom",
    "*.local",
    "*.new",
    "backup.*",
    ".git*",
    "CLAUDE.md",
    "RULES.md",
    "PERSONAS.md",
    "MCP.md"
)

# User data files that should NEVER be deleted or overwritten
$PRESERVE_FILES = @(
    ".credentials.json",
    "settings.json",
    "settings.local.json",
    ".claude\todos",
    ".claude\statsig",
    ".claude\projects",
    ".claude\local",
    ".claude\local\*"
)

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    if ($Host.UI.RawUI.ForegroundColor) {
        Write-Host $Message -ForegroundColor $Color
    } else {
        Write-Host $Message
    }
}

function Write-Error-Custom {
    param(
        [string]$Message,
        [string]$Context = "unknown"
    )
    
    $script:ERROR_COUNT++
    $script:ERROR_DETAILS += "[$Context] $Message"
    
    if ($LogFile) {
        Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [ERROR] [$Context] $Message"
    }
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Write-Warning-Custom {
    param(
        [string]$Message,
        [string]$Context = "unknown"
    )
    
    $script:WARNING_COUNT++
    $script:WARNING_DETAILS += "[$Context] $Message"
    
    if ($LogFile) {
        Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [WARNING] [$Context] $Message"
    }
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Verbose-Custom {
    param([string]$Message)
    
    if ($LogFile) {
        Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [VERBOSE] $Message"
    }
    if ($VERBOSE_MODE) {
        Write-ColorOutput "[VERBOSE] $Message" "Blue"
    }
}

function Write-Log {
    param([string]$Message)
    
    if ($LogFile) {
        Add-Content -Path $LogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    }
    Write-Host $Message
}

function Show-Usage {
    Write-Host "SuperClaude Installer v$SCRIPT_VERSION"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -InstallDir <directory>  Install to custom directory (default: $env:USERPROFILE\.claude)"
    Write-Host "  -Force                   Skip confirmation prompts (for automation)"
    Write-Host "  -Update                  Update existing installation (preserves customizations)"
    Write-Host "  -Uninstall               Remove SuperClaude from specified directory"
    Write-Host "  -VerifyChecksums         Verify integrity of an existing installation"
    Write-Host "  -Verbose                 Show detailed output during installation"
    Write-Host "  -DryRun                  Preview changes without making them"
    Write-Host "  -LogFile <file>          Save installation log to file"
    Write-Host "  -ConfigFile <file>       Load configuration from file"
    Write-Host "  -NoRollback              Disable automatic rollback on failure"
    Write-Host "  -CheckUpdate             Check for SuperClaude updates"
    Write-Host "  -Help                    Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                               # Install to default location"
    Write-Host "  .\install.ps1 -InstallDir 'C:\Claude'       # Install to C:\Claude"
    Write-Host "  .\install.ps1 -Force                        # Install without prompts"
    Write-Host "  .\install.ps1 -Update                       # Update existing installation"
    Write-Host "  .\install.ps1 -Uninstall                    # Remove SuperClaude"
    Write-Host "  .\install.ps1 -VerifyChecksums              # Verify existing installation"
    Write-Host "  .\install.ps1 -DryRun -Verbose              # Preview with detailed output"
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-DiskSpace {
    param([string]$Path)
    
    try {
        $drive = (Get-Item $Path).PSDrive
        $freeSpace = $drive.Free / 1MB
        
        if ($freeSpace -lt $REQUIRED_SPACE_MB) {
            Write-Error-Custom "Insufficient disk space. Need at least ${REQUIRED_SPACE_MB}MB free." "disk-space-check"
            return $false
        }
        return $true
    }
    catch {
        Write-Warning-Custom "Could not check disk space: $_" "disk-space-check"
        return $true  # Continue if we can't check
    }
}

function Get-FileHash-Safe {
    param([string]$FilePath)
    
    try {
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
        return $hash.Hash
    }
    catch {
        Write-Error-Custom "Failed to calculate hash for $FilePath`: $_" "integrity-check"
        return $null
    }
}

function Test-FileIntegrity {
    param(
        [string]$SourceFile,
        [string]$DestinationFile
    )
    
    if (-not (Test-Path $SourceFile)) {
        Write-Error-Custom "Source file does not exist: $SourceFile" "integrity-check"
        return $false
    }
    
    if (-not (Test-Path $DestinationFile)) {
        Write-Error-Custom "Destination file does not exist: $DestinationFile" "integrity-check"
        return $false
    }
    
    $srcHash = Get-FileHash-Safe $SourceFile
    $destHash = Get-FileHash-Safe $DestinationFile
    
    if (-not $srcHash -or -not $destHash) {
        return $false
    }
    
    if ($srcHash -ne $destHash) {
        Write-Error-Custom "Checksum mismatch: $DestinationFile" "integrity-check"
        return $false
    }
    
    Write-Verbose-Custom "File integrity verified: $DestinationFile"
    return $true
}

function Get-SourceFiles {
    param([string]$SourceRoot)
    
    $files = @()
    
    # Get files from .claude directory
    if (Test-Path "$SourceRoot\.claude") {
        $claudeFiles = Get-ChildItem -Path "$SourceRoot\.claude" -Recurse -File | 
                      Where-Object { 
                          $_.FullName -notmatch '\.git' -and
                          $_.FullName -notmatch 'backup\.' -and
                          $_.Name -ne 'settings.local.json'
                      } |
                      ForEach-Object { $_.FullName.Replace("$SourceRoot\.claude\", "").Replace("\", "/") }
        $files += $claudeFiles
    }
    
    # Include CLAUDE.md from root if it exists
    if (Test-Path "$SourceRoot\CLAUDE.md") {
        $files += "CLAUDE.md"
    }
    
    return $files
}

function Test-PreserveFile {
    param([string]$FilePath)
    
    foreach ($preserve in $PRESERVE_FILES) {
        if ($FilePath -like "*$preserve*") {
            return $true
        }
    }
    return $false
}

function Test-ExceptionFile {
    param([string]$FilePath)
    
    $fileName = Split-Path $FilePath -Leaf
    foreach ($pattern in $EXCEPTION_PATTERNS) {
        if ($fileName -like $pattern) {
            return $true
        }
    }
    return $false
}

function Invoke-Rollback {
    if (-not $BACKUP_DIR -or -not (Test-Path $BACKUP_DIR)) {
        Write-Error-Custom "No backup available for rollback" "rollback"
        return $false
    }
    
    Write-ColorOutput "Rolling back installation..." "Yellow"
    
    try {
        if (Test-Path $InstallDir) {
            Remove-Item -Path $InstallDir -Recurse -Force
        }
        
        Move-Item -Path $BACKUP_DIR -Destination $InstallDir
        Write-ColorOutput "Installation rolled back successfully" "Green"
        return $true
    }
    catch {
        Write-Error-Custom "Rollback failed: $_" "rollback"
        return $false
    }
}

function New-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $random = Get-Random -Minimum 1000 -Maximum 9999
    $backupName = "superclaude-backup.$timestamp.$random"
    $script:BACKUP_DIR = Join-Path (Split-Path $InstallDir -Parent) $backupName
    
    if (-not $DRY_RUN_MODE) {
        try {
            Copy-Item -Path $InstallDir -Destination $BACKUP_DIR -Recurse
            Write-ColorOutput "Backed up existing files to: $BACKUP_DIR" "Green"
            return $true
        }
        catch {
            Write-Error-Custom "Failed to create backup: $_" "backup"
            return $false
        }
    }
    return $true
}

function Copy-WithUpdateCheck {
    param(
        [string]$SourceFile,
        [string]$DestinationFile
    )
    
    $fileName = Split-Path $SourceFile -Leaf
    $destDir = Split-Path $DestinationFile -Parent
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    if ($UPDATE_MODE -and (Test-Path $DestinationFile)) {
        # Check if file differs from source
        $filesEqual = $false
        try {
            $filesEqual = (Compare-Object (Get-Content $SourceFile) (Get-Content $DestinationFile)) -eq $null
        }
        catch {
            $filesEqual = $false
        }
        
        if (-not $filesEqual) {
            # Check if it's a customizable config file
            $isCustomizable = $CUSTOMIZABLE_CONFIGS -contains $fileName
            
            if ($isCustomizable) {
                Write-Host "  Preserving customized $fileName (new version: $fileName.new)"
                if (-not $DRY_RUN_MODE) {
                    Copy-Item -Path $SourceFile -Destination "$DestinationFile.new" -Force
                }
            }
            else {
                if (-not $DRY_RUN_MODE) {
                    Copy-Item -Path $SourceFile -Destination $DestinationFile -Force
                }
            }
        }
        else {
            if (-not $DRY_RUN_MODE) {
                Copy-Item -Path $SourceFile -Destination $DestinationFile -Force
            }
        }
    }
    else {
        if (-not $DRY_RUN_MODE) {
            Copy-Item -Path $SourceFile -Destination $DestinationFile -Force
        }
    }
}

# Main script logic starts here

if ($Help) {
    Show-Usage
    exit 0
}

if ($CheckUpdate) {
    Write-Host "Update checking not implemented in PowerShell version yet."
    exit 0
}

# Handle uninstall mode
if ($UNINSTALL_MODE) {
    Write-ColorOutput "SuperClaude Uninstaller" "Green"
    Write-Host "========================"
    Write-ColorOutput "Target directory: $InstallDir" "Yellow"
    Write-Host ""
    
    if (-not (Test-Path $InstallDir)) {
        Write-ColorOutput "Error: SuperClaude not found at $InstallDir" "Red"
        exit 1
    }
    
    if (-not $FORCE_INSTALL) {
        Write-ColorOutput "This will remove SuperClaude from $InstallDir" "Yellow"
        $confirm = Read-Host "Are you sure you want to continue? (y/n)"
        if ($confirm -ne "y") {
            Write-Host "Uninstall cancelled."
            exit 0
        }
    }
    
    Write-Host "Removing SuperClaude files while preserving user data..."
    
    try {
        $removedCount = 0
        $preservedCount = 0
        
        $installedFiles = Get-ChildItem -Path $InstallDir -Recurse -File
        foreach ($file in $installedFiles) {
            $relativePath = $file.FullName.Replace("$InstallDir\", "")
            
            if (Test-PreserveFile $relativePath) {
                Write-Host "  Preserving: $relativePath"
                $preservedCount++
            }
            else {
                if (-not $DRY_RUN_MODE) {
                    Remove-Item -Path $file.FullName -Force
                    Write-Host "  Removing: $relativePath"
                }
                else {
                    Write-Host "  Would remove: $relativePath"
                }
                $removedCount++
            }
        }
        
        # Remove empty directories
        if (-not $DRY_RUN_MODE) {
            Get-ChildItem -Path $InstallDir -Directory -Recurse | 
                Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 } |
                Remove-Item -Force
            
            if ((Get-ChildItem $InstallDir).Count -eq 0) {
                Remove-Item -Path $InstallDir -Force
                Write-ColorOutput "✓ SuperClaude uninstalled completely!" "Green"
            }
            else {
                Write-ColorOutput "✓ SuperClaude uninstalled successfully!" "Green"
                Write-ColorOutput "Note: User data files preserved in $InstallDir" "Yellow"
            }
        }
        
        Write-Host ""
        Write-Host "Summary:"
        Write-Host "  Files removed: $removedCount"
        Write-Host "  Files preserved: $preservedCount"
    }
    catch {
        Write-Error-Custom "Uninstall failed: $_" "uninstall"
        exit 1
    }
    
    exit 0
}

# Handle verify mode
if ($VERIFY_MODE) {
    Write-ColorOutput "SuperClaude Verification" "Green"
    Write-Host "========================="
    Write-ColorOutput "Target directory: $InstallDir" "Yellow"
    Write-Host ""
    
    if (-not (Test-Path $InstallDir)) {
        Write-ColorOutput "Error: SuperClaude not found at $InstallDir" "Red"
        exit 1
    }
    
    Write-Host "Verifying installation integrity..."
    
    $sourceFiles = Get-SourceFiles "."
    $verificationFailures = 0
    $filesChecked = 0
    $filesMissing = 0
    
    foreach ($file in $sourceFiles) {
        $filesChecked++
        $srcFile = if ($file -eq "CLAUDE.md") { ".\$file" } else { ".\.claude\$file" }
        $destFile = Join-Path $InstallDir $file
        
        if (-not (Test-Path $destFile)) {
            Write-Host "  Missing: $file"
            $filesMissing++
        }
        elseif (-not (Test-FileIntegrity $srcFile $destFile)) {
            Write-Host "  Mismatch: $file"
            $verificationFailures++
        }
        else {
            Write-Verbose-Custom "  Verified: $file"
        }
    }
    
    Write-Host ""
    Write-Host "Summary:"
    Write-Host "  Files checked: $filesChecked"
    Write-Host "  Files missing: $filesMissing"
    Write-Host "  Checksum mismatches: $verificationFailures"
    Write-Host ""
    
    if ($filesMissing -eq 0 -and $verificationFailures -eq 0) {
        Write-ColorOutput "✓ Installation verified successfully!" "Green"
        Write-Host "All files match the source."
    }
    else {
        Write-ColorOutput "✗ Verification failed" "Red"
        if ($filesMissing -gt 0) {
            Write-Host "Some files are missing from the installation."
        }
        if ($verificationFailures -gt 0) {
            Write-Host "Some files differ from the source (may have been customized)."
        }
        exit 1
    }
    
    exit 0
}

# Main installation logic
Write-ColorOutput "SuperClaude Installer" "Green"
Write-Host "======================"
Write-ColorOutput "Installation directory: $InstallDir" "Yellow"

if ($DRY_RUN_MODE) {
    Write-ColorOutput "Mode: DRY RUN (no changes will be made)" "Blue"
}
if ($VERBOSE_MODE) {
    Write-ColorOutput "Mode: VERBOSE" "Blue"
}
if ($LogFile) {
    Write-ColorOutput "Log file: $LogFile" "Yellow"
}
Write-Host ""

# Pre-flight checks
Write-Verbose-Custom "Running pre-flight checks..."

# Check if running as administrator for system directories
if ($InstallDir -match "^[A-Z]:\\Program Files" -and -not (Test-Administrator)) {
    Write-Error-Custom "Administrator privileges required for installation to Program Files" "permissions"
    exit 1
}

# Check required PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 3) {
    Write-Error-Custom "PowerShell 3.0 or higher required" "powershell-version"
    exit 1
}

# Check disk space
if (-not $DRY_RUN_MODE) {
    $parentDir = Split-Path $InstallDir -Parent
    if ($parentDir -and (Test-Path $parentDir)) {
        if (-not (Test-DiskSpace $parentDir)) {
            exit 1
        }
    }
}

# Check write permissions
if (-not $DRY_RUN_MODE) {
    $parentDir = Split-Path $InstallDir -Parent
    if (Test-Path $InstallDir) {
        try {
            $testFile = Join-Path $InstallDir ".write_test_$(Get-Random)"
            New-Item -ItemType File -Path $testFile -Force | Out-Null
            Remove-Item -Path $testFile -Force
        }
        catch {
            Write-Error-Custom "No write permission for $InstallDir" "permissions"
            exit 1
        }
    }
    elseif ($parentDir) {
        if (-not (Test-Path $parentDir)) {
            Write-Error-Custom "Parent directory does not exist: $parentDir" "directory"
            exit 1
        }
        try {
            $testFile = Join-Path $parentDir ".write_test_$(Get-Random)"
            New-Item -ItemType File -Path $testFile -Force | Out-Null
            Remove-Item -Path $testFile -Force
        }
        catch {
            Write-Error-Custom "No write permission to create $InstallDir" "permissions"
            exit 1
        }
    }
}

# Confirmation prompt
if (-not $FORCE_INSTALL) {
    if ($UPDATE_MODE) {
        Write-ColorOutput "This will update SuperClaude in $InstallDir" "Yellow"
    }
    else {
        Write-ColorOutput "This will install SuperClaude in $InstallDir" "Yellow"
    }
    $confirm = Read-Host "Are you sure you want to continue? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "Installation cancelled."
        exit 0
    }
}
Write-Host ""

# Check if we're in SuperClaude directory
if (-not (Test-Path "CLAUDE.md") -or -not (Test-Path ".claude") -or -not (Test-Path ".claude\commands")) {
    Write-ColorOutput "Error: This script must be run from the SuperClaude directory" "Red"
    Write-Host ""
    Write-Host "Expected files not found. Please ensure you are in the root SuperClaude directory."
    $missing = @()
    if (-not (Test-Path "CLAUDE.md")) { $missing += "CLAUDE.md" }
    if (-not (Test-Path ".claude")) { $missing += ".claude\" }
    if (-not (Test-Path ".claude\commands")) { $missing += ".claude\commands\" }
    Write-Host "Missing: $($missing -join ' ')"
    Write-Host ""
    Write-Host "Solution: cd to the SuperClaude directory and run: .\install.ps1"
    exit 1
}

# Get version information
$SUPERCLAUDE_VERSION = "unknown"
if (Test-Path "VERSION") {
    try {
        $SUPERCLAUDE_VERSION = Get-Content "VERSION" -Raw | ForEach-Object { $_.Trim() }
    }
    catch {
        $SUPERCLAUDE_VERSION = "unknown"
    }
}
Write-Verbose-Custom "SuperClaude version: $SUPERCLAUDE_VERSION"

# Check existing installation
if (Test-Path "$InstallDir\VERSION") {
    try {
        $INSTALLED_VERSION = Get-Content "$InstallDir\VERSION" -Raw | ForEach-Object { $_.Trim() }
        Write-Verbose-Custom "Installed version: $INSTALLED_VERSION"
        
        if ($UPDATE_MODE) {
            Write-Host "Current version: $INSTALLED_VERSION"
            Write-Host "New version: $SUPERCLAUDE_VERSION"
            Write-Host ""
        }
    }
    catch {
        Write-Warning-Custom "Could not read installed version" "version-check"
    }
}

# Handle existing directory
if ((Test-Path $InstallDir) -and (@(Get-ChildItem $InstallDir).Count -gt 0)) {
    Write-ColorOutput "Existing configuration found at $InstallDir" "Yellow"
    
    $backupChoice = "n"
    if ($UPDATE_MODE -or $FORCE_INSTALL) {
        $backupChoice = "y"
    }
    else {
        $backupChoice = Read-Host "Backup existing configuration? (y/n)"
    }
    
    if ($backupChoice -eq "y") {
        if (-not (New-Backup)) {
            exit 1
        }
    }
}
elseif (Test-Path $InstallDir) {
    Write-ColorOutput "Directory $InstallDir exists but is empty" "Yellow"
}

Write-Host ""
if ($UPDATE_MODE) {
    Write-Host "Updating SuperClaude..."
}
else {
    Write-Host "Installing SuperClaude..."
}

# Mark installation phase
$script:INSTALLATION_PHASE = $true

# Create directory structure
if (-not $DRY_RUN_MODE) {
    Write-Host "Creating directory structure..."
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
}

# Copy files
Write-Host "Copying files..."
$sourceFiles = Get-SourceFiles "."
$totalFiles = $sourceFiles.Count
$currentFile = 0
$copiedCount = 0
$preservedCount = 0

foreach ($file in $sourceFiles) {
    if ($file) {
        $currentFile++
        Write-Verbose-Custom "Processing file $currentFile/$totalFiles`: $file"
        
        $srcFile = if ($file -eq "CLAUDE.md") { ".\$file" } else { ".\.claude\$file" }
        $destFile = Join-Path $InstallDir $file
        
        if ($VERBOSE_MODE) {
            Write-Host "  Progress: [$currentFile/$totalFiles] Processing: $file"
        }
        
        if ((Test-PreserveFile $file) -and (Test-Path $destFile)) {
            Write-Verbose-Custom "Preserving user file: $file"
            $preservedCount++
        }
        else {
            try {
                Copy-WithUpdateCheck $srcFile $destFile
                Write-Verbose-Custom "  Copied: $file"
                $copiedCount++
            }
            catch {
                Write-Error-Custom "  Copy failed: $srcFile -> $destFile`: $_" "file-copy"
            }
        }
    }
}

Write-Host "  Files copied: $copiedCount"
Write-Host "  Files preserved: $preservedCount"

# Verification
Write-Host ""
Write-Host "Verifying installation..."

$sourceFiles = Get-SourceFiles "."
$expectedFiles = $sourceFiles.Count
$actualFiles = 0

foreach ($file in $sourceFiles) {
    $destFile = Join-Path $InstallDir $file
    if (Test-Path $destFile) {
        $actualFiles++
    }
}

Write-ColorOutput "Total files: $actualFiles (expected: $expectedFiles)" "Green"

# Check critical files
$criticalFilesOk = $true
$criticalFiles = @("CLAUDE.md", "commands", "shared")
foreach ($criticalFile in $criticalFiles) {
    $criticalPath = Join-Path $InstallDir $criticalFile
    if (-not (Test-Path $criticalPath)) {
        Write-ColorOutput "Warning: Critical file/directory missing: $criticalFile" "Yellow"
        $criticalFilesOk = $false
    }
}

# Final status
if ($actualFiles -ge $expectedFiles -and $criticalFilesOk -and $VERIFICATION_FAILURES -eq 0) {
    $script:INSTALLATION_PHASE = $false
    
    Write-Host ""
    if ($UPDATE_MODE) {
        Write-ColorOutput "✓ SuperClaude updated successfully!" "Green"
        
        # Check for .new files
        $newFiles = Get-ChildItem -Path $InstallDir -Filter "*.new" -Recurse
        if ($newFiles) {
            Write-Host ""
            Write-ColorOutput "Note: The following files have updates available:" "Yellow"
            foreach ($file in $newFiles) {
                Write-Host "  - $($file.FullName)"
            }
            Write-Host ""
            Write-Host "To review changes: Compare-Object (Get-Content <file>) (Get-Content <file>.new)"
            Write-Host "To apply update: Move-Item <file>.new <file>"
        }
    }
    else {
        Write-ColorOutput "✓ SuperClaude installed successfully!" "Green"
        Write-Host ""
        Write-Host "Next steps:"
        Write-Host "1. Open any project with Claude Code"
        Write-Host "2. Try a command: /analyze --code"
        Write-Host "3. Activate a persona: /analyze --persona-architect"
    }
    
    if ($BACKUP_DIR -and (Test-Path $BACKUP_DIR)) {
        Write-Host ""
        Write-ColorOutput "Note: Your previous configuration was backed up to:" "Yellow"
        Write-Host "$BACKUP_DIR"
    }
    
    Write-Host ""
    Write-Host "For more information, see README.md"
}
else {
    Write-Host ""
    Write-ColorOutput "✗ Installation may be incomplete" "Red"
    Write-Host ""
    Write-Host "Expected vs Actual file counts:"
    $status = if ($actualFiles -lt $expectedFiles) { " ❌" } else { " ✓" }
    Write-Host "  Total files: $actualFiles/$expectedFiles$status"
    
    if ($VERIFICATION_FAILURES -gt 0) {
        Write-Host "  Integrity failures: $VERIFICATION_FAILURES ❌"
    }
    
    Write-Host ""
    Write-Host "Troubleshooting steps:"
    Write-Host "1. Check for error messages above"
    Write-Host "2. Ensure you have write permissions to $InstallDir"
    Write-Host "3. Verify all source files exist in the current directory"
    Write-Host "4. Try running as Administrator if permission errors occur"
    Write-Host ""
    Write-Host "For manual installation, see README.md"
    exit 1
}