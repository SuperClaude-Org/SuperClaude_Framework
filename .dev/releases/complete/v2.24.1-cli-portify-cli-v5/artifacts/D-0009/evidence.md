# D-0009: Updated derive_cli_name() Evidence

- When command_path=None: returns workflow-derived name (backward compat)
- When command_path=Path("roadmap.md"): returns "roadmap" (new behavior)
- Existing test_config.py tests pass unchanged
- 505 total tests pass
