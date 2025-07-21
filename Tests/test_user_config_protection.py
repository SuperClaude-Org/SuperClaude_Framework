#!/usr/bin/env python3
"""
Integration test for user configuration protection mechanism
"""

import tempfile
import shutil
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from setup.components.core import CoreComponent
from setup.utils.logger import setup_logging


def create_sample_user_config() -> str:
    """Create a sample user CLAUDE.md configuration"""
    return """# My Personal Claude Configuration

This is my custom configuration for Claude Code.

## My Custom Rules
- Always use TypeScript for new projects
- Prefer functional programming patterns
- Use specific naming conventions for APIs

## My Custom Tools and Preferences
- ESLint with custom rules
- Prettier with 2-space indentation
- Jest for testing framework

## Personal Workflow
- Code review checklist
- Documentation standards
- Error handling patterns
"""


def create_sample_framework_config() -> str:
    """Create a sample SuperClaude framework CLAUDE.md"""
    return """# SuperClaude Entry Point

@COMMANDS.md
@FLAGS.md
@PRINCIPLES.md
@RULES.md
@MCP.md
@PERSONAS.md
@ORCHESTRATOR.md
@MODES.md

# User Configuration Integration
@USER.md
"""


def test_scenario_1_no_existing_config():
    """Test Case 1: No existing CLAUDE.md file"""
    print("\n=== Test Case 1: No existing CLAUDE.md ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "claude"
        test_dir.mkdir()
        
        print(f"Test directory: {test_dir}")
        
        # Initialize core component
        core = CoreComponent(test_dir)
        
        # Test protection mechanism
        result = core._protect_user_configuration()
        
        print(f"✅ Protection result: {result} (expected: False)")
        assert result == False, "Should return False when no existing config"
        
        # Verify no USER.md was created
        user_md = test_dir / "USER.md"
        assert not user_md.exists(), "USER.md should not exist"
        print("✅ No USER.md created (correct)")


def test_scenario_2_user_config_exists():
    """Test Case 2: Existing user CLAUDE.md file"""
    print("\n=== Test Case 2: Existing user CLAUDE.md ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "claude"
        test_dir.mkdir()
        
        print(f"Test directory: {test_dir}")
        
        # Create user CLAUDE.md
        claude_md = test_dir / "CLAUDE.md"
        user_content = create_sample_user_config()
        with open(claude_md, 'w') as f:
            f.write(user_content)
        
        print("✅ Created sample user CLAUDE.md")
        
        # Initialize core component
        core = CoreComponent(test_dir)
        
        # Test protection mechanism
        result = core._protect_user_configuration()
        
        print(f"✅ Protection result: {result} (expected: True)")
        assert result == True, "Should return True when user config exists"
        
        # Verify CLAUDE.md was moved to USER.md
        user_md = test_dir / "USER.md"
        assert user_md.exists(), "USER.md should exist"
        assert not claude_md.exists(), "Original CLAUDE.md should be gone"
        
        # Verify content was preserved
        with open(user_md, 'r') as f:
            preserved_content = f.read()
        
        assert "My Personal Claude Configuration" in preserved_content, "User content should be preserved"
        print("✅ User configuration preserved correctly")


def test_scenario_3_framework_config_exists():
    """Test Case 3: Existing SuperClaude framework CLAUDE.md"""
    print("\n=== Test Case 3: Existing SuperClaude framework CLAUDE.md ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "claude"
        test_dir.mkdir()
        
        print(f"Test directory: {test_dir}")
        
        # Create framework CLAUDE.md
        claude_md = test_dir / "CLAUDE.md"
        framework_content = create_sample_framework_config()
        with open(claude_md, 'w') as f:
            f.write(framework_content)
        
        print("✅ Created sample framework CLAUDE.md")
        
        # Initialize core component
        core = CoreComponent(test_dir)
        
        # Test protection mechanism
        result = core._protect_user_configuration()
        
        print(f"✅ Protection result: {result} (expected: False)")
        assert result == False, "Should return False for framework files"
        
        # Verify CLAUDE.md still exists and wasn't moved
        assert claude_md.exists(), "Framework CLAUDE.md should still exist"
        
        user_md = test_dir / "USER.md"
        assert not user_md.exists(), "USER.md should not be created"
        print("✅ Framework file correctly detected and not moved")


def test_scenario_4_user_md_reference_handling():
    """Test Case 4: USER.md reference handling in CLAUDE.md"""
    print("\n=== Test Case 4: USER.md reference handling ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "claude"
        test_dir.mkdir()
        
        print(f"Test directory: {test_dir}")
        
        # Create framework CLAUDE.md with USER.md reference
        claude_md = test_dir / "CLAUDE.md"
        framework_content = create_sample_framework_config()
        with open(claude_md, 'w') as f:
            f.write(framework_content)
        
        # Initialize core component
        core = CoreComponent(test_dir)
        
        # Test with user config preserved (True)
        print("\n--- Testing with user config preserved = True ---")
        core._update_claude_md_user_reference(True)
        
        with open(claude_md, 'r') as f:
            content = f.read()
        
        assert "@USER.md" in content and not content.count("# @USER.md"), "USER.md reference should be active"
        print("✅ USER.md reference activated correctly")
        
        # Test with no user config (False)
        print("\n--- Testing with user config preserved = False ---")
        # Reset the file
        with open(claude_md, 'w') as f:
            f.write(framework_content)
        
        core._update_claude_md_user_reference(False)
        
        with open(claude_md, 'r') as f:
            content = f.read()
        
        assert "# @USER.md" in content, "USER.md reference should be commented out"
        print("✅ USER.md reference commented out correctly")


def test_scenario_5_error_handling():
    """Test Case 5: Error handling and edge cases"""
    print("\n=== Test Case 5: Error handling ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "claude"
        test_dir.mkdir()
        
        print(f"Test directory: {test_dir}")
        
        # Test with permission issues (simulate by using read-only directory)
        readonly_dir = test_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        core = CoreComponent(readonly_dir)
        
        # This should handle the error gracefully
        result = core._protect_user_configuration()
        print(f"✅ Handled read-only directory gracefully: {result}")
        
        # Clean up
        readonly_dir.chmod(0o755)


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Starting User Configuration Protection Integration Tests")
    print("=" * 60)
    
    # Setup logging for tests
    setup_logging("test_integration", console_level=20)  # INFO level
    
    try:
        test_scenario_1_no_existing_config()
        test_scenario_2_user_config_exists()
        test_scenario_3_framework_config_exists()
        test_scenario_4_user_md_reference_handling()
        test_scenario_5_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All integration tests passed!")
        print("✅ User configuration protection mechanism is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_integration_tests()