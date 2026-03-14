# D-0003: Test Matrix

## Existing Test Coverage (505 tests passing)

| Test File | Count | Coverage Area |
|-----------|-------|---------------|
| test_config.py | 8 | PortifyConfig validation, derive_cli_name |
| test_contracts.py | varies | Contract builder |
| test_validate_config.py | 8 | Step 1 validate-config |
| test_discover_components.py | varies | Step 2 discover-components |
| test_process.py | varies | Orchestration engine |
| integration/test_orchestration.py | 30+ | End-to-end pipeline |

## Coverage Gaps for New Resolution Paths

| Input Form | Test Needed | Target File |
|------------|-------------|-------------|
| F1: Command Name ("roadmap") | test_resolve_command_name | test_resolution.py |
| F2: Command Path ("/path/to/roadmap.md") | test_resolve_command_path | test_resolution.py |
| F3: Skill Dir ("/path/to/sc-roadmap-protocol/") | test_resolve_skill_dir | test_resolution.py |
| F4: Skill Name ("sc-roadmap-protocol") | test_resolve_skill_name | test_resolution.py |
| F5: Skill File ("/path/to/SKILL.md") | test_resolve_skill_file | test_resolution.py |
| F6: sc: Prefixed ("sc:roadmap") | test_resolve_sc_prefix | test_resolution.py |
| ERR: Empty/None/Whitespace | test_empty_target_raises | test_resolution.py |
| ERR: sc: with empty remainder | test_sc_prefix_empty_raises | test_resolution.py |
| ERR: Ambiguous target | test_ambiguous_target | test_resolution.py |
| ERR: Not found target | test_not_found_target | test_resolution.py |
| Edge: Standalone command | test_standalone_command | test_resolution.py |
| Edge: Standalone skill | test_standalone_skill | test_resolution.py |
| Edge: Multi-skill command | test_multi_skill_command | test_resolution.py |
| Model: TargetInputType enum | test_enum_membership | test_models.py |
| Model: ResolvedTarget construction | test_resolved_target | test_models.py |
| Model: ComponentTree properties | test_component_tree | test_models.py |
| Model: to_flat_inventory() | test_flat_inventory_roundtrip | test_models.py |
| Model: Error constants | test_error_constants | test_models.py |
