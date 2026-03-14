"""CLI subcommand package for cli-portify pipeline.

Portifies inference-based SuperClaude workflows into programmatic
CLI pipelines with sprint-style supervised execution.

This module provides the ``superclaude cli-portify`` command group.
"""

from .cli import cli_portify_group

__all__ = ["cli_portify_group"]
