# D-0044 Evidence: AC1-AC20 Validation Suite

## Test Execution

```
$ uv run pytest tests/audit/test_ac_validation.py -v

tests/audit/test_ac_validation.py::TestAC1Classification::test_v2_actions_cover_five_categories PASSED
tests/audit/test_ac_validation.py::TestAC1Classification::test_classify_finding_returns_valid_result PASSED
tests/audit/test_ac_validation.py::TestAC1Classification::test_report_completeness_mandated_sections PASSED
tests/audit/test_ac_validation.py::TestAC2Coverage::test_coverage_tracker_produces_artifact PASSED
tests/audit/test_ac_validation.py::TestAC3Checkpointing::test_checkpoint_write_and_read PASSED
tests/audit/test_ac_validation.py::TestAC3Checkpointing::test_resume_controller PASSED
tests/audit/test_ac_validation.py::TestAC4EvidenceDelete::test_delete_with_evidence_passes PASSED
tests/audit/test_ac_validation.py::TestAC4EvidenceDelete::test_delete_without_evidence_fails PASSED
tests/audit/test_ac_validation.py::TestAC5EvidenceKeep::test_keep_tier1_with_imports_passes PASSED
tests/audit/test_ac_validation.py::TestAC5EvidenceKeep::test_keep_tier1_without_imports_fails PASSED
tests/audit/test_ac_validation.py::TestAC6SpotCheck::test_validation_result_has_consistency_rate PASSED
tests/audit/test_ac_validation.py::TestAC6SpotCheck::test_spot_check_validate_runs PASSED
tests/audit/test_ac_validation.py::TestAC7CredentialScanning::test_real_credential_flagged PASSED
tests/audit/test_ac_validation.py::TestAC7CredentialScanning::test_template_not_flagged PASSED
tests/audit/test_ac_validation.py::TestAC8Gitignore::test_gitignore_inconsistency_flagged PASSED
tests/audit/test_ac_validation.py::TestAC8Gitignore::test_consistent_files_pass PASSED
tests/audit/test_ac_validation.py::TestAC9Budget::test_budget_enforcement_warn_at_75pct PASSED
tests/audit/test_ac_validation.py::TestAC9Budget::test_budget_enforcement_halt_at_100pct PASSED
tests/audit/test_ac_validation.py::TestAC10ReportDepth::test_summary_mode PASSED
tests/audit/test_ac_validation.py::TestAC10ReportDepth::test_detailed_mode PASSED
tests/audit/test_ac_validation.py::TestAC11ScannerSchema::test_valid_phase1_output PASSED
tests/audit/test_ac_validation.py::TestAC11ScannerSchema::test_invalid_phase1_missing_field PASSED
tests/audit/test_ac_validation.py::TestAC12DependencyGraph::test_graph_with_edges_has_nodes PASSED
tests/audit/test_ac_validation.py::TestAC12DependencyGraph::test_empty_graph PASSED
tests/audit/test_ac_validation.py::TestAC13ColdStart::test_cold_start_detected PASSED
tests/audit/test_ac_validation.py::TestAC13ColdStart::test_auto_config_has_budget_and_batch_size PASSED
tests/audit/test_ac_validation.py::TestAC14DocsAudit::test_broken_link_detected PASSED
tests/audit/test_ac_validation.py::TestAC14DocsAudit::test_full_docs_audit_5_sections PASSED
tests/audit/test_ac_validation.py::TestAC15BackwardCompat::test_map_to_v1_works PASSED
tests/audit/test_ac_validation.py::TestAC15BackwardCompat::test_all_v1_categories_covered PASSED
tests/audit/test_ac_validation.py::TestAC16DirectoryAssessment::test_large_directory_gets_assessment PASSED
tests/audit/test_ac_validation.py::TestAC16DirectoryAssessment::test_identify_large_directories PASSED
tests/audit/test_ac_validation.py::TestAC17InvestigateCap::test_escalation_detects_signals PASSED
tests/audit/test_ac_validation.py::TestAC17InvestigateCap::test_escalation_module_importable PASSED
tests/audit/test_ac_validation.py::TestAC18FailureHandling::test_anti_lazy_flags_uniform_batch PASSED
tests/audit/test_ac_validation.py::TestAC18FailureHandling::test_anti_lazy_passes_mixed_batch PASSED
tests/audit/test_ac_validation.py::TestAC19DryRun::test_dry_run_produces_estimates PASSED
tests/audit/test_ac_validation.py::TestAC19DryRun::test_budget_caveat_present PASSED
tests/audit/test_ac_validation.py::TestAC20RunIsolation::test_batch_decomposer_produces_unique_ids PASSED
tests/audit/test_ac_validation.py::TestAC20RunIsolation::test_known_issues_registry_per_run PASSED

============================== 40 passed in 0.05s ==============================
```

## AC Count Verification

40 tests across 20 test classes, each named `TestAC{N}*`, covering AC1 through AC20.
All tests pass. Self-contained fixtures, no external repos needed.
