

---
high_severity_count: 1
medium_severity_count: 7
low_severity_count: 3
total_deviations: 11
validation_complete: true
tasklist_ready: false
---

## Deviation Report

### DEV-001
- **ID**: DEV-001
- **Severity**: HIGH
- **Deviation**: Roadmap omits `TargetInputType` enum from data models milestone. The spec defines a 5-value enum (`COMMAND_NAME`, `COMMAND_PATH`, `SKILL_DIR`, `SKILL_NAME`, `SKILL_FILE`) as a first-class type used by `ResolvedTarget.input_type`. The roadmap's Milestone 1.1 lists `ResolvedTarget` with `target_type: str` instead of `input_type: TargetInputType`.
- **Spec Quote**: `class TargetInputType(Enum): COMMAND_NAME = "command_name" COMMAND_PATH = "command_path" SKILL_DIR = "skill_dir" SKILL_NAME = "skill_name" SKILL_FILE = "skill_file"` (Section 4.5) and `input_type: TargetInputType  # Enum classification` in `ResolvedTarget`
- **Roadmap Quote**: `Define ResolvedTarget dataclass with command_path: Path | None, skill_dir: Path | None, project_root: Path, target_type: str` (Milestone 1.1, item 1)
- **Impact**: Implementers will use a raw string instead of a typed enum, losing type safety and the ability to exhaustively match input forms. The field name also differs (`target_type` vs `input_type`), which would cause misalignment with downstream code referencing the spec's field name.
- **Recommended Correction**: Add `TargetInputType` enum to Milestone 1.1. Change `target_type: str` to `input_type: TargetInputType` in the `ResolvedTarget` definition. Note: the roadmap uses `target_type` consistently (including in `ValidateConfigResult`), so either align all to `input_type` per spec or explicitly document the rename as a deliberate deviation.

### DEV-002
- **ID**: DEV-002
- **Severity**: MEDIUM
- **Deviation**: Roadmap omits several `ResolvedTarget` fields specified in the spec. The spec defines `input_form: str`, `commands_dir: Path`, `skills_dir: Path`, `agents_dir: Path` on `ResolvedTarget`. The roadmap's Milestone 1.1 only mentions `command_path`, `skill_dir`, `project_root`, `target_type`.
- **Spec Quote**: `@dataclass class ResolvedTarget: input_form: str  # What the user typed / input_type: TargetInputType / command_path: Path | None / skill_dir: Path | None / project_root: Path / commands_dir: Path / skills_dir: Path / agents_dir: Path` (Section 4.5)
- **Roadmap Quote**: `Define ResolvedTarget dataclass with command_path: Path | None, skill_dir: Path | None, project_root: Path, target_type: str` (Milestone 1.1, item 1)
- **Impact**: Missing directory fields (`commands_dir`, `skills_dir`, `agents_dir`) and `input_form` means the resolution algorithm cannot pass directory overrides downstream as designed. Implementers may omit these fields.
- **Recommended Correction**: Expand Milestone 1.1 item 1 to list all 8 fields from the spec's `ResolvedTarget` dataclass.

### DEV-003
- **ID**: DEV-003
- **Severity**: MEDIUM
- **Deviation**: Roadmap omits `PortifyConfig` extensions from data models milestone. The spec defines significant additions to `PortifyConfig` (~10 new fields) and an augmented `derive_cli_name()` method. Neither appears in any roadmap milestone.
- **Spec Quote**: `@dataclass class PortifyConfig(PipelineConfig): ... # NEW -- populated after resolution / target_input: str = "" / target_type: str = "" / command_path: Path | None = None / commands_dir: Path | None = None / skills_dir: Path | None = None / agents_dir: Path | None = None / project_root: Path | None = None / include_agents: list[str] = field(default_factory=list) / save_manifest_path: Path | None = None / component_tree: ComponentTree | None = None` (Section 4.5)
- **Roadmap Quote**: [MISSING] — No milestone explicitly addresses `PortifyConfig` extension or `derive_cli_name()` augmentation.
- **Impact**: Without explicit tasking, `PortifyConfig` extensions may be missed or inconsistently implemented. The `derive_cli_name()` augmentation (prefer command name when available) is a behavioral change that needs explicit implementation.
- **Recommended Correction**: Add `PortifyConfig` extension as an explicit item in Milestone 1.1 (data models) or Milestone 2.3 (CLI & Config). Include `derive_cli_name()` augmentation.

### DEV-004
- **ID**: DEV-004
- **Severity**: MEDIUM
- **Deviation**: Roadmap places `--include-agent` deduplication test in Milestone 2.3 (CLI) but the implementation logic is in Milestone 2.1 (Discovery). The spec places deduplication logic in Step R3 of the resolution algorithm, not in the CLI layer.
- **Spec Quote**: `Deduplication rule: All agents — both auto-discovered and manually injected — are deduplicated by name. If --include-agent specifies an agent already discovered from SKILL.md: The manually specified entry takes precedence (overwrites auto-discovered)` (Section 4.5, Step R3)
- **Roadmap Quote**: SC-7: `--include-agent dedup` mapped to Phase `2.3` (Success Criteria table). But Milestone 2.1 item 4: `Implement --include-agent deduplication with referenced_in="cli-override" precedence`
- **Impact**: Contradictory phase assignment — SC-7 says test in 2.3 but implementation is in 2.1. Minor confusion for implementers about where dedup logic lives.
- **Recommended Correction**: Align SC-7 test phase to 2.1 where the implementation occurs, or clarify that 2.3 tests CLI-level invocation while 2.1 tests the dedup algorithm.

### DEV-005
- **ID**: DEV-005
- **Severity**: MEDIUM
- **Deviation**: Roadmap omits the spec's explicit `ValidateConfigResult.to_dict()` update requirement. The spec provides an explicit updated `to_dict()` method with specific fields and warns that omitting them causes "silent data loss in pipeline telemetry."
- **Spec Quote**: `The to_dict() method MUST be updated to include all new fields: ... "warnings": self.warnings, ... "command_path": self.command_path, "skill_dir": self.skill_dir, "target_type": self.target_type, "agent_count": self.agent_count` (Section 4.5)
- **Roadmap Quote**: Milestone 3.1 item 3: `Extend to_dict() with new fields` — mentioned but without the spec's emphasis on completeness or the downstream consumption warning.
- **Impact**: Low risk since the roadmap does mention it, but the spec's MUST emphasis and downstream data loss warning are not carried through.
- **Recommended Correction**: Add a note in Milestone 3.1 that `to_dict()` must include all new fields per spec, as downstream `contract.py` and `resume.py` consume them.

### DEV-006
- **ID**: DEV-006
- **Severity**: MEDIUM
- **Deviation**: Roadmap omits the spec's artifact enrichment details. The spec lists 4 new sections for `component-inventory.md` and specific new frontmatter fields. The roadmap's Milestone 3.2 is a single line.
- **Spec Quote**: `The component-inventory.md artifact is enriched with: ## Command section (Tier 0 metadata), ## Agents section (Tier 2 agent table), ## Cross-Tier Data Flow section (directory references), ## Resolution Log section (how components were discovered)` and frontmatter: `source_command: roadmap / source_skill: sc-roadmap-protocol / component_count: 14 / total_lines: 2847 / agent_count: 3 / has_command: true / has_skill: true / duration_seconds: 0.0312` (Section 4.4)
- **Roadmap Quote**: `Enrich component-inventory.md with Command section, Agents table, Cross-Tier Data Flow, Resolution Log, extended frontmatter (FR-017)` (Milestone 3.2)
- **Impact**: While the roadmap lists the sections by name, it lacks the specific frontmatter fields. Implementers may miss `source_command`, `has_command`, `has_skill`, `duration_seconds` fields.
- **Recommended Correction**: Expand Milestone 3.2 to enumerate the required frontmatter fields.

### DEV-007
- **ID**: DEV-007
- **Severity**: MEDIUM
- **Deviation**: Roadmap references "FR-001" through "FR-018" numbering scheme that does not exist in the spec. The spec uses `FR-PORTIFY-WORKFLOW.1`, `.2`, `.3` as requirement IDs. The roadmap invents its own numbering.
- **Spec Quote**: `FR-PORTIFY-WORKFLOW.1: Multi-Form Target Resolution`, `FR-PORTIFY-WORKFLOW.2: Full Component Tree Discovery`, `FR-PORTIFY-WORKFLOW.3: Extended Subprocess Scoping` (Section 3)
- **Roadmap Quote**: `(FR-001, NFR-001)` (Milestone 1.2 item 1), `(FR-002)` (item 3), `(FR-008)` (Milestone 2.1 item 1), `(FR-017)` (Milestone 3.2)
- **Impact**: Traceability between roadmap and spec is broken. "FR-008" cannot be traced to any spec requirement ID. An auditor cannot verify coverage.
- **Recommended Correction**: Replace roadmap's FR-NNN references with the spec's actual requirement IDs (FR-PORTIFY-WORKFLOW.1, .2, .3) and specific acceptance criteria bullet references.

### DEV-008
- **ID**: DEV-008
- **Severity**: MEDIUM
- **Deviation**: Roadmap adds two "Open Items" (OI-5 and OI-6) in the Deferred Items section that do not exist in the spec's Open Items (OI-1 through OI-4).
- **Spec Quote**: `OI-1: Should agent-to-agent refs be recursively resolved? / OI-2: Should manifest loading be supported as input? / OI-3: Should --exclude-component be supported? / OI-4: Quality scores for this spec` (Section 11)
- **Roadmap Quote**: `4. Multi-source agent tracking (OI-5) — current: first source wins / 5. Configurable consolidation threshold (OI-6) — current: hardcoded cap at 10` (Deferred Items)
- **Impact**: Introduces unspecified scope items. While both are reasonable deferrals, they are not in the spec and could cause confusion about what was agreed upon.
- **Recommended Correction**: Either add OI-5 and OI-6 to the spec via a spec amendment, or remove them from the roadmap's deferred items and note them as roadmap-originated observations.

### DEV-009
- **ID**: DEV-009
- **Severity**: LOW
- **Deviation**: Roadmap states "23 requirements (18 functional, 5 non-functional)" in the Executive Summary. The spec defines 3 functional requirements (FR-PORTIFY-WORKFLOW.1, .2, .3) with acceptance criteria sub-items, and 5 NFRs. The "18 functional" count appears to be the total acceptance criteria bullets, not requirement count.
- **Spec Quote**: 3 FRs with multiple acceptance criteria each (Section 3); 5 NFRs (Section 6)
- **Roadmap Quote**: `23 requirements (18 functional, 5 non-functional)` (Executive Summary)
- **Impact**: Minor confusion about requirement granularity. Does not affect implementation correctness.
- **Recommended Correction**: Clarify whether "18 functional" refers to acceptance criteria or requirements. Align terminology.

### DEV-010
- **ID**: DEV-010
- **Severity**: LOW
- **Deviation**: Roadmap describes the consolidation algorithm's Tier 2 as "select top 10 by component count" but the spec says to also check a 3x file-count constraint before replacing with parent directories.
- **Spec Quote**: `Replace groups sharing a common parent with the common parent directory, provided the parent directory contains no more than 3x the total file count of its constituent directories. If consolidation still exceeds 10 directories, use only the top 10 by component count` (Section 4.5)
- **Roadmap Quote**: `Tier 1: os.path.commonpath() to merge directories sharing common ancestors / Tier 2: If still over cap after Tier 1, select top 10 by component count` (Milestone 2.2)
- **Impact**: The roadmap omits the 3x file-count guard on Tier 1 consolidation. This could lead to over-scoping if a common parent contains many unrelated files.
- **Recommended Correction**: Add the 3x file-count constraint to the Tier 1 description in Milestone 2.2.

### DEV-011
- **ID**: DEV-011
- **Severity**: LOW
- **Deviation**: Roadmap states regex patterns should be defined as "compiled `re.Pattern` constants at module level in `discover_components.py`" but the spec defines them in the resolution algorithm section and the `AGENT_PATTERNS` list uses raw strings, not compiled patterns.
- **Spec Quote**: `AGENT_PATTERNS = [r'...', r'...', ...]` defined in Step R3 of the resolution algorithm (Section 4.5)
- **Roadmap Quote**: `Define the 6 agent-extraction patterns as compiled re.Pattern constants at module level in discover_components.py` (Architectural Recommendations, item 3)
- **Impact**: Minor discrepancy about where patterns live (resolution.py per spec's algorithm vs discover_components.py per roadmap) and whether they're raw strings or compiled. Does not affect correctness.
- **Recommended Correction**: Clarify that patterns should live in `resolution.py` (where the resolution algorithm is) per spec, or explicitly document the decision to place them in `discover_components.py` with rationale.

---

## Summary

**Severity Distribution**: 1 HIGH, 7 MEDIUM, 3 LOW (11 total)

The roadmap is a well-structured implementation plan that correctly captures the spec's architectural intent, phasing, and risk profile. However, it has one high-severity gap: the omission of the `TargetInputType` enum and field name mismatch (`target_type` vs `input_type`) in the data model milestone, which would cause type safety loss and API misalignment.

The 7 medium-severity deviations cluster around **incomplete data model transcription** (DEV-002, DEV-003), **requirement traceability** (DEV-007), and **detail omissions** in validation and artifact enrichment (DEV-005, DEV-006). The most impactful pattern is that the roadmap summarizes spec data models at too high a level — `ResolvedTarget` is missing 4 fields, `PortifyConfig` extensions are entirely absent, and `ValidateConfigResult.to_dict()` lacks the spec's emphasis on completeness.

The roadmap is **not tasklist-ready** due to the HIGH severity deviation. Resolving DEV-001 (add `TargetInputType` enum, align field naming) and addressing the medium-severity data model gaps (DEV-002, DEV-003) would bring the roadmap to tasklist-ready status.
