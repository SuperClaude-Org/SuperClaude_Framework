# Release Review Matrix: v2.10–v2.20

## Scope

This matrix summarizes releases **v2.10 through v2.20** using the same evidence base as the full narrative report:
- **git commit messages** as the primary source of truth
- **high-level release specs/docs** only where explicitly mapped by the user
- **quick, shallow parallel review** for each release section

## Evidence basis legend

| Label | Meaning |
|------|---------|
| Commit-derived | Backed directly by git log / commit messages and shallow diff context |
| Spec-derived | Backed by release-level spec/findings docs explicitly provided or mapped |
| Shallow review | Quick parallel pass; not deep code or runtime verification |

---

## Release matrix

| Release | Mapped Release / Artifact | Evidence Basis | What Changed | What It Accomplished | Confidence | Caveats |
|---|---|---|---|---|---|---|
| **v2.10** | spec-panel-v2 / roadmap-v4 archive | Commit-derived, shallow review | Archived roadmap-v4 artifacts from `current` to `complete`; mostly file moves/renames | Reduced clutter in active release directories and preserved historical roadmap-v4 materials | Moderate | Archive/path-oriented evidence only; possible release-label drift in destination path |
| **v2.11** | `unified-audit-gating-v1.2.1` | Spec-derived, shallow review | Introduced runner-owned completion tracking, per-task subprocesses, TurnLedger reimbursement, trailing gates, deferred remediation, conflict review, diagnostic-chain logic | Reduced false-success sprint outcomes and moved completion authority from agent self-reporting to the runner | Moderate | Spec-derived only; no direct v2.11 commit match in initial log scan |
| **v2.12** | `cleanup-audit-v2-UNIFIED-SPEC` | Spec-derived, shallow review | Defined 5-phase cleanup-audit v2 architecture, richer classification, coverage tracking, checkpoint/resume, known-issues handling, docs audit, dependency analysis, credential scanning | Closed gaps between cleanup-audit v1 promises and actual behavior; made audit flow more structured and repeatable | Moderate | Spec-derived only; not tied to a direct v2.12 commit message |
| **v2.13** | CLI Runner / Pipeline Unification | Commit-derived, shallow review | Added pipeline unification modules and integrations across pipeline, roadmap, sprint, and audit flows; landed with expanded test coverage | Consolidated shared workflow infrastructure and improved reuse across CLI subsystems | Moderate | Merge commit bundled broader archival/framework changes |
| **v2.14** | `unified-audit-gating-v2` | Spec-derived, shallow review | Raised `max_turns` 50→100 and `reimbursement_rate` 0.5→0.8; aligned defaults across pipeline, sprint, roadmap CLI, shell scripts, tests | Improved sprint budget sustainability, increased turn headroom, reduced config drift | Moderate | Spec-derived only; no direct v2.14 commit match in initial log scan |
| **v2.15** | `v2.15-cli-portify` | Spec-derived with limited commit corroboration, shallow review | Reviewed original cli-portify workflow/spec, identified structural issues, produced refactored spec, investigated gate failures, ran layered root-cause analysis | Reframed cli-portify as a more contract-driven, operationally grounded portification workflow | Medium | Mostly doc/spec-derived; limited commit corroboration |
| **v2.16** | unified audit gating v2 fix | Commit-derived, shallow review | Merge-level fix/release touching supporting command/skill content, CLI-portify references, release/refactor/audit artifact packaging | Likely advanced or stabilized unified audit gating workflow and packaged supporting material | Medium-low to medium | Merge commit too terse for precise behavioral claims |
| **v2.17** | roadmap-reliability | Commit-derived, shallow review | Archived v2.17 release bundle from `current` to `complete`; pure move/rename across roadmap/tasklists/checkpoints/results/artifacts | Marked v2.17 complete and preserved the evidence trail | High | Archive-only change based on available evidence |
| **v2.18** | cli-portify-v2 | Commit-derived, shallow review | Added a full persisted release bundle including roadmap, tasklists, execution logs, checkpoints, results, artifacts, and docs | Preserved end-to-end cli-portify-v2 planning and execution evidence in a structured release directory | Medium | Scope confirmed, but semantic correctness of outputs not verified |
| **v2.19** | roadmap-validate | Commit-derived, shallow review | Added `roadmap validate` workflow, 7 validation dimensions, single-agent and multi-agent modes, spec/extraction/roadmap/test-strategy/tasklists/adversarial artifacts; later archived to `complete` | Formalized roadmap validation as a first-class workflow with explicit validation dimensions and release evidence | Medium-high | Strong at release/artifact level; code-level implementation not deeply verified |
| **v2.20** | Workflow Evolution | Commit-derived, shallow review | Added forensic diagnostic backlog/release area with agent reports, adversarial validation, failure theories; later added benchmark baseline corpus with fixtures, comparison scripts, outputs, validation reports, scenario summaries | Created a durable evidence base and repeatable benchmark scenarios for workflow failure analysis | High | Intent and scope are clear; underlying docs were not deeply evaluated |

---

## Theme matrix

| Theme | Releases | Notes |
|---|---|---|
| **Archival / release hygiene** | v2.10, v2.17 | Primarily movement of completed release bundles from `current` to `complete` |
| **Runner reliability / gating / budget control** | v2.11, v2.14, v2.16 | Focus on completion truth, reimbursement math, turn budgets, and gating stabilization |
| **Pipeline and workflow architecture** | v2.13, v2.19 | Reusable pipeline unification and dedicated roadmap validation workflow |
| **Cleanup-audit system expansion** | v2.12 | Large spec-driven expansion from light audit to phased, evidence-backed audit pipeline |
| **CLI portification and workflow forensics** | v2.15, v2.18, v2.20 | Portification design work, stored run artifacts, and later forensic/benchmark analysis |

---

## Confidence summary

| Confidence Band | Releases | Reason |
|---|---|---|
| **High** | v2.17, v2.20 | Clear archive/benchmark intent from commit messages and shallow diff context |
| **Medium-high** | v2.19 | Strong release/artifact evidence and explicit commit messaging |
| **Moderate / Medium** | v2.10, v2.13, v2.15, v2.18 | Good top-level evidence, but not deep implementation verification |
| **Moderate but spec-bound** | v2.11, v2.12, v2.14 | Well-supported by mapped release specs, but not by explicit commit-title matches |
| **Lowest confidence** | v2.16 | Merge commit too terse; impact inferred from shallow diff context |

---

## Key takeaway

From **v2.10 to v2.20**, the repo’s release history shows a progression from archive hygiene and workflow infrastructure work toward explicit validation, stronger execution controls, cleanup-audit redesign, CLI portification, and finally forensic workflow analysis backed by benchmark corpora.
