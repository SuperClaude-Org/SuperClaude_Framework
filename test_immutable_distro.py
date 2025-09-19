#!/usr/bin/env python3
"""
Test script for immutable distro home directory detection
Tests the new get_home_directory() function
"""

import os
import sys
from pathlib import Path

# Add setup to path for testing
sys.path.insert(0, str(Path(__file__).parent / "setup"))

from setup.utils.environment import get_home_directory

def test_home_directory_detection():
    """Test home directory detection with various scenarios"""

    print("🧪 Testing SuperClaude home directory detection")
    print("=" * 50)

    # Test 1: Standard detection
    home = get_home_directory()
    print(f"Detected home directory: {home}")
    print(f"Home exists: {home.exists()}")
    print(f"Home is directory: {home.is_dir()}")

    # Test 2: Environment variables
    print(f"\n🔍 Environment variables:")
    print(f"$HOME: {os.environ.get('HOME', 'Not set')}")
    print(f"$USER: {os.environ.get('USER', 'Not set')}")
    print(f"$USERNAME: {os.environ.get('USERNAME', 'Not set')}")

    # Test 3: Check for immutable distro patterns
    print(f"\n🐧 Immutable distro check:")
    username = os.environ.get('USER') or os.environ.get('USERNAME')
    if username:
        var_home_path = Path(f'/var/home/{username}')
        regular_home_path = Path(f'/home/{username}')

        print(f"/var/home/{username} exists: {var_home_path.exists()}")
        print(f"/home/{username} exists: {regular_home_path.exists()}")

        if var_home_path.exists():
            print("✅ Immutable distro pattern detected!")
        elif regular_home_path.exists():
            print("✅ Standard Linux pattern detected!")

    # Test 4: SuperClaude installation directory
    claude_dir = home / ".claude"
    print(f"\n📁 SuperClaude directory:")
    print(f"Expected location: {claude_dir}")
    print(f"Would create at: {claude_dir}")

    # Test 5: Compare with standard Path.home()
    try:
        standard_home = Path.home()
        print(f"\n🔍 Comparison:")
        print(f"Standard Path.home(): {standard_home}")
        print(f"Our get_home_directory(): {home}")
        print(f"Same result: {standard_home == home}")
    except Exception as e:
        print(f"\n⚠️ Standard Path.home() failed: {e}")

    print(f"\n✅ Test completed successfully!")
    return home

if __name__ == "__main__":
    try:
        test_home_directory_detection()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)