#!/usr/bin/env python3
"""
SuperClaude Framework Management Hub
Entry point when running as: python -m superclaude

This module delegates to the modern typer-based CLI.
"""

import sys
from superclaude.cli.app import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
