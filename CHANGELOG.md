# Changelog

All notable changes to SuperClaude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Commands now use `/sc:` namespace to avoid conflicts with user custom commands
- Commands are now installed in `~/.claude/commands/sc/` subdirectory
- All 16 commands updated: `/analyze` � `/sc:analyze`, `/build` � `/sc:build`, etc.
- Automatic migration from old command locations to new `sc/` subdirectory

### Added
- **NEW COMMAND**: `/sc:implement` for feature and code implementation (addresses v2 user feedback)
- **NEW COMMAND**: `/sc:i18n` for super-simple language switching 
- **NEW**: Complete i18n system with 10 language translations (English, 简体中文, 繁體中文, 日本語, 한국어, Русский, Español, Deutsch, Français, العربية)
- **NEW**: 100% offline language switching - no network connection required
- **NEW**: Instant language switching with `/sc:i18n switch zh_CN` command
- **NEW**: Traditional Chinese (zh_TW) translation with 118 high-quality translation items
- Migration logic to move existing commands to new namespace automatically
- Enhanced uninstaller to handle both old and new command locations
- Improved command conflict prevention
- Better command organization and discoverability
- Localized command descriptions that update dynamically based on selected language

### Technical Details
- Commands now accessible as `/sc:analyze`, `/sc:build`, `/sc:improve`, etc.
- Migration preserves existing functionality while preventing naming conflicts
- Installation process detects and migrates existing commands automatically
- Tab completion support for `/sc:` prefix to discover all SuperClaude commands
- **i18n Architecture**: Uses Python's `importlib.resources` for reliable package-based translation access
- **Language Configuration**: Stored in `~/.claude/i18n/config.json` with persistence across sessions
- **Translation Management**: Dual-layer system - simple user commands vs. developer translation workflow
- **Quality Assurance**: Translation quality scoring and MD5-based incremental update system

## [3.0.0] - 2025-07-14

### Added
- Initial release of SuperClaude v3.0
- 15 specialized slash commands for development tasks
- Smart persona auto-activation system
- MCP server integration (Context7, Sequential, Magic, Playwright)
- Unified CLI installer with multiple installation profiles
- Comprehensive documentation and user guides
- Token optimization framework
- Task management system

### Features
- **Commands**: analyze, build, cleanup, design, document, estimate, explain, git, improve, index, load, spawn, task, test, troubleshoot
- **Personas**: architect, frontend, backend, analyzer, security, mentor, refactorer, performance, qa, devops, scribe
- **MCP Servers**: Official library documentation, complex analysis, UI components, browser automation
- **Installation**: Quick, minimal, and developer profiles with component selection