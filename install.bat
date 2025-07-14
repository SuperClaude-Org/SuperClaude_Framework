@echo off
setlocal enabledelayedexpansion

REM SuperClaude Batch Installer Script
REM Installs SuperClaude configuration framework to enhance Claude Code
REM Version: 2.0.0
REM License: MIT
REM Repository: https://github.com/NomenAK/SuperClaude

set "SCRIPT_VERSION=2.0.0"
set "INSTALL_DIR=%USERPROFILE%\.claude"
set "FORCE_INSTALL=false"
set "UPDATE_MODE=false"
set "UNINSTALL_MODE=false"
set "VERBOSE_MODE=false"
set "DRY_RUN_MODE=false"
set "HELP_MODE=false"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--dir" (
    set "INSTALL_DIR=%~2"
    shift /1
    shift /1
    goto parse_args
)
if /i "%~1"=="--force" (
    set "FORCE_INSTALL=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="--update" (
    set "UPDATE_MODE=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="--uninstall" (
    set "UNINSTALL_MODE=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set "VERBOSE_MODE=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="--dry-run" (
    set "DRY_RUN_MODE=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="--help" (
    set "HELP_MODE=true"
    shift /1
    goto parse_args
)
if /i "%~1"=="-h" (
    set "HELP_MODE=true"
    shift /1
    goto parse_args
)
echo Unknown option: %~1
goto show_usage

:args_done

if "%HELP_MODE%"=="true" goto show_usage

REM Check if we're in the correct directory
if not exist "CLAUDE.md" (
    echo Error: This script must be run from the SuperClaude directory
    echo.
    echo Expected files not found. Please ensure you are in the root SuperClaude directory.
    echo Missing: CLAUDE.md
    echo.
    echo Solution: cd to the SuperClaude directory and run: install.bat
    exit /b 1
)

if not exist ".claude" (
    echo Error: .claude directory not found
    echo Please ensure you are in the root SuperClaude directory.
    exit /b 1
)

if not exist ".claude\commands" (
    echo Error: .claude\commands directory not found
    echo Please ensure you are in the root SuperClaude directory.
    exit /b 1
)

REM Handle uninstall mode
if "%UNINSTALL_MODE%"=="true" goto uninstall_mode

REM Handle main installation
echo SuperClaude Installer
echo ======================
echo Installation directory: %INSTALL_DIR%

if "%DRY_RUN_MODE%"=="true" (
    echo Mode: DRY RUN (no changes will be made)
)
if "%VERBOSE_MODE%"=="true" (
    echo Mode: VERBOSE
)
echo.

REM Check if target directory exists
if exist "%INSTALL_DIR%" (
    dir /b "%INSTALL_DIR%" 2>nul | findstr . >nul
    if not errorlevel 1 (
        echo Existing configuration found at %INSTALL_DIR%
        if "%FORCE_INSTALL%"=="false" (
            set /p "backup_choice=Backup existing configuration? (y/n): "
        ) else (
            set "backup_choice=y"
        )
        
        if /i "!backup_choice!"=="y" (
            call :create_backup
        )
    )
)

echo.
if "%UPDATE_MODE%"=="true" (
    echo Updating SuperClaude...
) else (
    echo Installing SuperClaude...
)

REM Create installation directory if it doesn't exist
if "%DRY_RUN_MODE%"=="false" (
    if not exist "%INSTALL_DIR%" (
        echo Creating directory structure...
        mkdir "%INSTALL_DIR%" 2>nul
        if errorlevel 1 (
            echo Error: Failed to create installation directory
            exit /b 1
        )
    )
)

REM Copy files
echo Copying files...
set "copied_count=0"
set "preserved_count=0"

REM Copy CLAUDE.md from root
if exist "CLAUDE.md" (
    call :copy_file "CLAUDE.md" "%INSTALL_DIR%\CLAUDE.md"
)

REM Copy files from .claude directory
call :copy_directory ".claude" "%INSTALL_DIR%"

echo   Files copied: !copied_count!
echo   Files preserved: !preserved_count!

REM Verification
echo.
echo Verifying installation...

REM Count files
set "actual_files=0"
if exist "%INSTALL_DIR%" (
    for /r "%INSTALL_DIR%" %%f in (*) do (
        set /a actual_files+=1
    )
)

echo Total files: !actual_files!

REM Check critical files
set "critical_files_ok=true"
if not exist "%INSTALL_DIR%\CLAUDE.md" (
    echo Warning: Critical file missing: CLAUDE.md
    set "critical_files_ok=false"
)
if not exist "%INSTALL_DIR%\commands" (
    echo Warning: Critical directory missing: commands
    set "critical_files_ok=false"
)
if not exist "%INSTALL_DIR%\shared" (
    echo Warning: Critical directory missing: shared
    set "critical_files_ok=false"
)

if "%critical_files_ok%"=="true" (
    echo.
    if "%UPDATE_MODE%"=="true" (
        echo [92m✓ SuperClaude updated successfully![0m
    ) else (
        echo [92m✓ SuperClaude installed successfully![0m
        echo.
        echo Next steps:
        echo 1. Open any project with Claude Code
        echo 2. Try a command: /analyze --code
        echo 3. Activate a persona: /analyze --persona-architect
    )
    echo.
    echo For more information, see README.md
) else (
    echo.
    echo [91m✗ Installation may be incomplete[0m
    echo.
    echo Troubleshooting steps:
    echo 1. Check for error messages above
    echo 2. Ensure you have write permissions to %INSTALL_DIR%
    echo 3. Verify all source files exist in the current directory
    echo 4. Try running as Administrator if permission errors occur
    echo.
    echo For manual installation, see README.md
    exit /b 1
)

goto end

:uninstall_mode
echo SuperClaude Uninstaller
echo ========================
echo Target directory: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" (
    echo Error: SuperClaude not found at %INSTALL_DIR%
    exit /b 1
)

if "%FORCE_INSTALL%"=="false" (
    echo This will remove SuperClaude from %INSTALL_DIR%
    set /p "confirm=Are you sure you want to continue? (y/n): "
    if /i not "!confirm!"=="y" (
        echo Uninstall cancelled.
        exit /b 0
    )
)

echo Removing SuperClaude files while preserving user data...

if "%DRY_RUN_MODE%"=="true" (
    echo Would remove SuperClaude installation files
) else (
    REM Remove known SuperClaude files while preserving user data
    if exist "%INSTALL_DIR%\CLAUDE.md" del /q "%INSTALL_DIR%\CLAUDE.md" 2>nul
    if exist "%INSTALL_DIR%\commands" rmdir /s /q "%INSTALL_DIR%\commands" 2>nul
    if exist "%INSTALL_DIR%\shared" rmdir /s /q "%INSTALL_DIR%\shared" 2>nul
    if exist "%INSTALL_DIR%\.checksums" del /q "%INSTALL_DIR%\.checksums" 2>nul
    
    REM Check if directory is empty
    dir /b "%INSTALL_DIR%" 2>nul | findstr . >nul
    if errorlevel 1 (
        rmdir "%INSTALL_DIR%" 2>nul
        echo [92m✓ SuperClaude uninstalled completely![0m
    ) else (
        echo [92m✓ SuperClaude uninstalled successfully![0m
        echo [93mNote: User data files preserved in %INSTALL_DIR%[0m
    )
)

goto end

:copy_directory
set "source_dir=%~1"
set "dest_dir=%~2"

if "%VERBOSE_MODE%"=="true" (
    echo Copying directory: %source_dir% to %dest_dir%
)

for /r "%source_dir%" %%f in (*) do (
    set "rel_path=%%f"
    set "rel_path=!rel_path:%source_dir%\=!"
    set "dest_file=%dest_dir%\!rel_path!"
    call :copy_file "%%f" "!dest_file!"
)
goto :eof

:copy_file
set "source_file=%~1"
set "dest_file=%~2"
set "dest_dir=%~dp2"

REM Create destination directory if it doesn't exist
if "%DRY_RUN_MODE%"=="false" (
    if not exist "%dest_dir%" (
        mkdir "%dest_dir%" 2>nul
    )
)

REM Check if it's a preserve file (basic check)
echo %dest_file% | findstr /i "settings.local.json .credentials.json" >nul
if not errorlevel 1 (
    if exist "%dest_file%" (
        if "%VERBOSE_MODE%"=="true" (
            echo Preserving user file: %dest_file%
        )
        set /a preserved_count+=1
        goto :eof
    )
)

REM Copy the file
if "%DRY_RUN_MODE%"=="true" (
    if "%VERBOSE_MODE%"=="true" (
        echo Would copy: %source_file% to %dest_file%
    )
) else (
    copy "%source_file%" "%dest_file%" >nul 2>&1
    if errorlevel 1 (
        echo Error copying: %source_file% to %dest_file%
    ) else (
        if "%VERBOSE_MODE%"=="true" (
            echo Copied: %source_file%
        )
        set /a copied_count+=1
    )
)
goto :eof

:create_backup
set "timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "random_num=%random%"
for %%d in ("%INSTALL_DIR%") do set "parent_dir=%%~dpd"
set "backup_dir=%parent_dir%superclaude-backup.%timestamp%.%random_num%"

if "%DRY_RUN_MODE%"=="false" (
    echo Creating backup...
    xcopy "%INSTALL_DIR%" "%backup_dir%\" /e /i /q >nul 2>&1
    if errorlevel 1 (
        echo Error: Failed to create backup
        exit /b 1
    ) else (
        echo Backed up existing files to: %backup_dir%
    )
)
goto :eof

:show_usage
echo SuperClaude Installer v%SCRIPT_VERSION%
echo.
echo Usage: install.bat [OPTIONS]
echo.
echo Options:
echo   --dir ^<directory^>    Install to custom directory (default: %USERPROFILE%\.claude)
echo   --force              Skip confirmation prompts (for automation)
echo   --update             Update existing installation (preserves customizations)
echo   --uninstall          Remove SuperClaude from specified directory
echo   --verbose            Show detailed output during installation
echo   --dry-run            Preview changes without making them
echo   -h, --help           Show this help message
echo.
echo Examples:
echo   install.bat                           # Install to default location
echo   install.bat --dir "C:\Claude"         # Install to C:\Claude
echo   install.bat --force                   # Install without prompts
echo   install.bat --update                  # Update existing installation
echo   install.bat --uninstall               # Remove SuperClaude
echo   install.bat --dry-run --verbose       # Preview with detailed output
echo.
echo Note: This batch script provides basic installation functionality.
echo For advanced features, use the PowerShell installer (install.ps1).
goto end

:end
endlocal