# SuperClaude Installation CLI Improvements

**Date**: 2025-10-17
**Status**: Proposed Enhancement
**Goal**: Replace interactive prompts with efficient CLI flags for better developer experience

## 🎯 Objectives

1. **Speed**: One-command installation without interactive prompts
2. **Scriptability**: CI/CD and automation-friendly
3. **Clarity**: Clear, self-documenting flags
4. **Flexibility**: Support both simple and advanced use cases
5. **Backward Compatibility**: Keep interactive mode as fallback

## 🚨 Current Problems

### Problem 1: Slow Interactive Flow
```bash
# Current: Interactive (slow, manual)
$ uv run superclaude install

Stage 1: MCP Server Selection (Optional)
  Select MCP servers to configure:
  1. [ ] sequential-thinking
  2. [ ] context7
  ...
  > [user must manually select]

Stage 2: Framework Component Selection
  Select components (Core is recommended):
  1. [ ] core
  2. [ ] modes
  ...
  > [user must manually select again]

# Total time: ~60 seconds of clicking
# Automation: Impossible (requires human interaction)
```

### Problem 2: Ambiguous Recommendations
```bash
Stage 2: "Select components (Core is recommended):"

User Confusion:
  - Does "Core" include everything needed?
  - What about mcp_docs? Is it needed?
  - Should I select "all" instead?
  - What's the difference between "recommended" and "Core"?
```

### Problem 3: No Quick Profiles
```bash
# User wants: "Just install everything I need to get started"
# Current solution: Select ~8 checkboxes manually across 2 stages
# Better solution: `--recommended` flag
```

## ✅ Proposed Solution

### New CLI Flags

```bash
# Installation Profiles (Quick Start)
--minimal           # Minimal installation (core only)
--recommended       # Recommended for most users (complete working setup)
--all               # Install everything (all components + all MCP servers)

# Explicit Component Selection
--components NAMES  # Specific components (space-separated)
--mcp-servers NAMES # Specific MCP servers (space-separated)

# Interactive Override
--interactive       # Force interactive mode (default if no flags)
--yes, -y           # Auto-confirm (skip confirmation prompts)

# Examples
uv run superclaude install --recommended
uv run superclaude install --minimal
uv run superclaude install --all
uv run superclaude install --components core modes --mcp-servers airis-mcp-gateway
```

## 📋 Profile Definitions

### Profile 1: Minimal
```yaml
Profile: minimal
Purpose: Testing, development, minimal footprint
Components:
  - core
MCP Servers:
  - None
Use Cases:
  - Quick testing
  - CI/CD pipelines
  - Minimal installations
  - Development environments
Estimated Size: ~5 MB
Estimated Tokens: ~50K
```

### Profile 2: Recommended (DEFAULT for --recommended)
```yaml
Profile: recommended
Purpose: Complete working installation for most users
Components:
  - core
  - modes (7 behavioral modes)
  - commands (slash commands)
  - agents (15 specialized agents)
  - mcp_docs (documentation for MCP servers)
MCP Servers:
  - airis-mcp-gateway (dynamic tool loading, zero-token baseline)
Use Cases:
  - First-time installation
  - Production use
  - Recommended for 90% of users
Estimated Size: ~30 MB
Estimated Tokens: ~150K
Rationale:
  - Complete PM Agent functionality (sub-agent delegation)
  - Zero-token baseline with airis-mcp-gateway
  - All essential features included
  - No missing dependencies
```

### Profile 3: Full
```yaml
Profile: full
Purpose: Install everything available
Components:
  - core
  - modes
  - commands
  - agents
  - mcp
  - mcp_docs
MCP Servers:
  - airis-mcp-gateway
  - sequential-thinking
  - context7
  - magic
  - playwright
  - serena
  - morphllm-fast-apply
  - tavily
  - chrome-devtools
Use Cases:
  - Power users
  - Comprehensive installations
  - Testing all features
Estimated Size: ~50 MB
Estimated Tokens: ~250K
```

## 🔧 Implementation Changes

### File: `setup/cli/commands/install.py`

#### Change 1: Add Profile Arguments
```python
# Line ~64 (after --components argument)

parser.add_argument(
    "--minimal",
    action="store_true",
    help="Minimal installation (core only, no MCP servers)"
)

parser.add_argument(
    "--recommended",
    action="store_true",
    help="Recommended installation (core + modes + commands + agents + mcp_docs + airis-mcp-gateway)"
)

parser.add_argument(
    "--all",
    action="store_true",
    help="Install all components and all MCP servers"
)

parser.add_argument(
    "--mcp-servers",
    type=str,
    nargs="+",
    help="Specific MCP servers to install (space-separated list)"
)

parser.add_argument(
    "--interactive",
    action="store_true",
    help="Force interactive mode (default if no profile flags)"
)
```

#### Change 2: Profile Resolution Logic
```python
# Add new function after line ~172

def resolve_profile(args: argparse.Namespace) -> tuple[List[str], List[str]]:
    """
    Resolve installation profile from CLI arguments

    Returns:
        (components, mcp_servers)
    """

    # Check for conflicting profiles
    profile_flags = [args.minimal, args.recommended, args.all]
    if sum(profile_flags) > 1:
        raise ValueError("Only one profile flag can be specified: --minimal, --recommended, or --all")

    # Minimal profile
    if args.minimal:
        return ["core"], []

    # Recommended profile (default for --recommended)
    if args.recommended:
        return (
            ["core", "modes", "commands", "agents", "mcp_docs"],
            ["airis-mcp-gateway"]
        )

    # Full profile
    if args.all:
        components = ["core", "modes", "commands", "agents", "mcp", "mcp_docs"]
        mcp_servers = [
            "airis-mcp-gateway",
            "sequential-thinking",
            "context7",
            "magic",
            "playwright",
            "serena",
            "morphllm-fast-apply",
            "tavily",
            "chrome-devtools"
        ]
        return components, mcp_servers

    # Explicit component selection
    if args.components:
        components = args.components if isinstance(args.components, list) else [args.components]
        mcp_servers = args.mcp_servers if args.mcp_servers else []

        # Auto-include mcp_docs if any MCP servers selected
        if mcp_servers and "mcp_docs" not in components:
            components.append("mcp_docs")
            logger.info("Auto-included mcp_docs for MCP server documentation")

        # Auto-include mcp component if MCP servers selected
        if mcp_servers and "mcp" not in components:
            components.append("mcp")
            logger.info("Auto-included mcp component for MCP server support")

        return components, mcp_servers

    # No profile specified: return None to trigger interactive mode
    return None, None
```

#### Change 3: Update `get_components_to_install`
```python
# Modify function at line ~126

def get_components_to_install(
    args: argparse.Namespace, registry: ComponentRegistry, config_manager: ConfigService
) -> Optional[List[str]]:
    """Determine which components to install"""
    logger = get_logger()

    # Try to resolve from profile flags first
    components, mcp_servers = resolve_profile(args)

    if components is not None:
        # Profile resolved, store MCP servers in config
        if not hasattr(config_manager, "_installation_context"):
            config_manager._installation_context = {}
        config_manager._installation_context["selected_mcp_servers"] = mcp_servers

        logger.info(f"Profile selected: {len(components)} components, {len(mcp_servers)} MCP servers")
        return components

    # No profile flags: fall back to interactive mode
    if args.interactive or not (args.minimal or args.recommended or args.all or args.components):
        return interactive_component_selection(registry, config_manager)

    # Should not reach here
    return None
```

## 📖 Updated Documentation

### README.md Installation Section
```markdown
## Installation

### Quick Start (Recommended)
```bash
# One-command installation with everything you need
uv run superclaude install --recommended
```

This installs:
- Core framework
- 7 behavioral modes
- SuperClaude slash commands
- 15 specialized AI agents
- airis-mcp-gateway (zero-token baseline)
- Complete documentation

### Installation Profiles

**Minimal** (testing/development):
```bash
uv run superclaude install --minimal
```

**Recommended** (most users):
```bash
uv run superclaude install --recommended
```

**Full** (power users):
```bash
uv run superclaude install --all
```

### Custom Installation

Select specific components:
```bash
uv run superclaude install --components core modes commands
```

Select specific MCP servers:
```bash
uv run superclaude install --components core mcp_docs --mcp-servers airis-mcp-gateway context7
```

### Interactive Mode

If you prefer the guided installation:
```bash
uv run superclaude install --interactive
```

### Automation (CI/CD)

For automated installations:
```bash
uv run superclaude install --recommended --yes
```

The `--yes` flag skips confirmation prompts.
```

### CONTRIBUTING.md Developer Quickstart
```markdown
## Developer Setup

### Quick Setup
```bash
# Clone repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Install development dependencies
uv sync

# Run tests
pytest tests/ -v

# Install SuperClaude (recommended profile)
uv run superclaude install --recommended
```

### Testing Different Profiles

```bash
# Test minimal installation
uv run superclaude install --minimal --install-dir /tmp/test-minimal

# Test recommended installation
uv run superclaude install --recommended --install-dir /tmp/test-recommended

# Test full installation
uv run superclaude install --all --install-dir /tmp/test-full
```

### Performance Benchmarking

```bash
# Run installation performance benchmarks
pytest tests/performance/test_installation_performance.py -v --benchmark

# Compare profiles
pytest tests/performance/test_installation_performance.py::test_compare_profiles -v
```
```

## 🎯 User Experience Improvements

### Before (Current)
```bash
$ uv run superclaude install
[Interactive Stage 1: MCP selection]
[User clicks through options]
[Interactive Stage 2: Component selection]
[User clicks through options again]
[Confirmation prompt]
[Installation starts]

Time: ~60 seconds of user interaction
Scriptable: No
Clear expectations: Ambiguous ("Core is recommended" unclear)
```

### After (Proposed)
```bash
$ uv run superclaude install --recommended
[Installation starts immediately]
[Progress bar shown]
[Installation complete]

Time: 0 seconds of user interaction
Scriptable: Yes
Clear expectations: Yes (documented profile)
```

### Comparison Table
| Aspect | Current (Interactive) | Proposed (CLI Flags) |
|--------|----------------------|---------------------|
| **User Interaction Time** | ~60 seconds | 0 seconds |
| **Scriptable** | No | Yes |
| **CI/CD Friendly** | No | Yes |
| **Clear Expectations** | Ambiguous | Well-documented |
| **One-Command Install** | No | Yes |
| **Automation** | Impossible | Easy |
| **Profile Comparison** | Manual | Benchmarked |

## 🧪 Testing Plan

### Unit Tests
```python
# tests/test_install_cli_flags.py

def test_profile_minimal():
    """Test --minimal flag"""
    args = parse_args(["install", "--minimal"])
    components, mcp_servers = resolve_profile(args)

    assert components == ["core"]
    assert mcp_servers == []

def test_profile_recommended():
    """Test --recommended flag"""
    args = parse_args(["install", "--recommended"])
    components, mcp_servers = resolve_profile(args)

    assert "core" in components
    assert "modes" in components
    assert "commands" in components
    assert "agents" in components
    assert "mcp_docs" in components
    assert "airis-mcp-gateway" in mcp_servers

def test_profile_full():
    """Test --all flag"""
    args = parse_args(["install", "--all"])
    components, mcp_servers = resolve_profile(args)

    assert len(components) == 6  # All components
    assert len(mcp_servers) >= 5  # All MCP servers

def test_profile_conflict():
    """Test conflicting profile flags"""
    with pytest.raises(ValueError):
        args = parse_args(["install", "--minimal", "--recommended"])
        resolve_profile(args)

def test_explicit_components_auto_mcp_docs():
    """Test auto-inclusion of mcp_docs when MCP servers selected"""
    args = parse_args([
        "install",
        "--components", "core", "modes",
        "--mcp-servers", "airis-mcp-gateway"
    ])
    components, mcp_servers = resolve_profile(args)

    assert "core" in components
    assert "modes" in components
    assert "mcp_docs" in components  # Auto-included
    assert "mcp" in components  # Auto-included
    assert "airis-mcp-gateway" in mcp_servers
```

### Integration Tests
```python
# tests/integration/test_install_profiles.py

def test_install_minimal_profile(tmp_path):
    """Test full installation with --minimal"""
    install_dir = tmp_path / "minimal"

    result = subprocess.run(
        ["uv", "run", "superclaude", "install", "--minimal", "--install-dir", str(install_dir), "--yes"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert (install_dir / "CLAUDE.md").exists()
    assert (install_dir / "core").exists() or len(list(install_dir.glob("*.md"))) > 0

def test_install_recommended_profile(tmp_path):
    """Test full installation with --recommended"""
    install_dir = tmp_path / "recommended"

    result = subprocess.run(
        ["uv", "run", "superclaude", "install", "--recommended", "--install-dir", str(install_dir), "--yes"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert (install_dir / "CLAUDE.md").exists()

    # Verify key components installed
    assert any(p.match("*MODE_*.md") for p in install_dir.glob("**/*.md"))  # Modes
    assert any(p.match("MCP_*.md") for p in install_dir.glob("**/*.md"))  # MCP docs
```

### Performance Tests
```bash
# Use existing benchmark suite
pytest tests/performance/test_installation_performance.py -v

# Expected results:
# - minimal: ~5 MB, ~50K tokens
# - recommended: ~30 MB, ~150K tokens (3x minimal)
# - full: ~50 MB, ~250K tokens (5x minimal)
```

## 📋 Migration Path

### Phase 1: Add CLI Flags (Backward Compatible)
```yaml
Changes:
  - Add --minimal, --recommended, --all flags
  - Add --mcp-servers flag
  - Keep interactive mode as default
  - No breaking changes

Testing:
  - Run all existing tests (should pass)
  - Add new tests for CLI flags
  - Performance benchmarks

Release: v4.2.0 (minor version bump)
```

### Phase 2: Update Documentation
```yaml
Changes:
  - Update README.md with new flags
  - Update CONTRIBUTING.md with quickstart
  - Add installation guide (docs/installation-guide.md)
  - Update examples

Release: v4.2.1 (patch)
```

### Phase 3: Promote CLI Flags (Optional)
```yaml
Changes:
  - Make --recommended default if no args
  - Keep interactive available via --interactive flag
  - Update CLI help text

Testing:
  - User feedback collection
  - A/B testing (if possible)

Release: v4.3.0 (minor version bump)
```

## 🎯 Success Metrics

### Quantitative Metrics
```yaml
Installation Time:
  Current (Interactive): ~60 seconds of user interaction
  Target (CLI Flags): ~0 seconds of user interaction
  Goal: 100% reduction in manual interaction time

Scriptability:
  Current: 0% (requires human interaction)
  Target: 100% (fully scriptable)

CI/CD Adoption:
  Current: Not possible
  Target: >50% of automated deployments use CLI flags
```

### Qualitative Metrics
```yaml
User Satisfaction:
  Survey question: "How satisfied are you with the installation process?"
  Target: >90% satisfied or very satisfied

Clarity:
  Survey question: "Did you understand what would be installed?"
  Target: >95% clear understanding

Recommendation:
  Survey question: "Would you recommend this installation method?"
  Target: >90% would recommend
```

## 🚀 Next Steps

1. ✅ Document CLI improvements proposal (this file)
2. ⏳ Implement profile resolution logic
3. ⏳ Add CLI argument parsing
4. ⏳ Write unit tests for profile resolution
5. ⏳ Write integration tests for installations
6. ⏳ Run performance benchmarks (minimal, recommended, full)
7. ⏳ Update documentation (README, CONTRIBUTING, installation guide)
8. ⏳ Gather user feedback
9. ⏳ Prepare Pull Request with evidence

## 📊 Pull Request Checklist

Before submitting PR:

- [ ] All new CLI flags implemented
- [ ] Profile resolution logic added
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests written and passing
- [ ] Performance benchmarks run (results documented)
- [ ] Documentation updated (README, CONTRIBUTING, installation guide)
- [ ] Backward compatibility maintained (interactive mode still works)
- [ ] No breaking changes
- [ ] User feedback collected (if possible)
- [ ] Examples tested manually
- [ ] CI/CD pipeline tested

## 📚 Related Documents

- [Installation Process Analysis](./install-process-analysis.md)
- [Performance Benchmark Suite](../../tests/performance/test_installation_performance.py)
- [PM Agent Parallel Architecture](./pm-agent-parallel-architecture.md)

---

**Conclusion**: CLI flags will dramatically improve the installation experience, making it faster, scriptable, and more suitable for CI/CD workflows. The recommended profile provides a clear, well-documented default that works for 90% of users while maintaining flexibility for advanced use cases.

**User Benefit**: One-command installation (`--recommended`) with zero interaction time, clear expectations, and full scriptability for automation.
