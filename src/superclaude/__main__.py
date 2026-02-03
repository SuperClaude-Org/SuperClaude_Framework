"""
Allow running as: python -m superclaude

This module enables the package to be executed directly via:
    python -m superclaude [command]

Which is equivalent to:
    superclaude [command]
"""

from superclaude.cli.main import main

if __name__ == "__main__":
    main()
