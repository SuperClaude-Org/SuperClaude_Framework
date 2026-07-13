---
name: identify-risk
description: "Standardized code-risk assessment across 7 dimensions (security, reliability, complexity, performance, correctness, dependency, change-hotspot); local by default, optional Bluelink integration via --bluelink / --submit"
category: workflow
complexity: advanced
mcp-servers: []
personas: [security-engineer, backend-architect, performance-engineer, quality-engineer]
---

# /sc:identify-risk - Code Risk Assessment

> **Context Framework Note**: Activates when users type `/sc:identify-risk`. Runs a
> standardized, evidence-based code-risk assessment using the built-in R1–R7 rubric below.
> **Fully local by default** — no MCP or network needed. **Bluelink is opt-in**: `--bluelink`
> adds read context (sync a shared template, resolve the service, show the delta vs the previous
> run) and `--submit` persists the run to Bluelink for org/squad rollups. Bluelink is **never
> auto-activated** — contacted ONLY when `--bluelink`/`--submit` is explicitly present, **not**
> enabled by `--all-mcp`, and disabled by `--no-mcp`. All Bluelink use auto-degrades to the local
> rubric when unavailable — it never blocks the assessment.

> **Scoring convention**: scores are **0-100 where HIGHER = riskier**. Per dimension: a
> deterministic severity-weighted **base**, plus a **bounded LLM adjustment of ±15**, gives
> the **final**. Rollups at squad/org level are **worst-case (max)**.

## Usage
```
/sc:identify-risk [target] [--path <subdir>] [--service <name>] [--bluelink] [--submit]
```

**Arguments:**
- `target` / `--path <subdir>` — analyze the repo root, or a specific subdirectory
- `--service <name>` — override the target service name; default: auto-match from git remote
- `--bluelink` — *(optional)* use the Bluelink MCP for read context: sync a shared
  `_templates/risk-assessment.md`, resolve the service's meta-spec, and show the delta vs the
  previous run. Off by default; requires a configured Bluelink MCP server (see `mcp/MCP_Bluelink.md`).
- `--submit` — *(optional, implies `--bluelink`)* persist the assessment to Bluelink (upsert the
  service, write the meta-spec `risk-assessment.md`, link it in the README). Off by default.

Without `--bluelink`/`--submit` the command produces an inline report only and writes nothing.

## Triggers
- Request to assess code risk, quality, or "what could cause an incident here"
- Pre-release / pre-merge health check of a service
- Periodic risk review

## Behavioral Flow

### Step 1 — Acquire the rubric
Use the built-in R1–R7 rubric (Steps 3–5). If `--bluelink` is set, try to read
`_templates/risk-assessment.md` from Bluelink for the latest shared schema / `template_version`;
on any failure, fall back to the built-in rubric and note it — never STOP.

### Step 2 — (only with `--bluelink`/`--submit`) resolve the service
Read the git remote (`git remote get-url origin`) and `commit_sha` (`git rev-parse HEAD`).
If Bluelink is reachable, resolve the service's meta-spec (`doc_type: service-meta-spec` matching
this repo by `repository`/`service_name`) to capture `service_name`, `squad`, `repository`, `tier`,
and `meta_spec_path`. Prompt to disambiguate multiple matches; with `--submit` and no match, create
a stub meta-spec. If Bluelink is unavailable, skip and continue local-only (note it).

### Step 3 — Analyze all 7 dimensions (evidence-based)
Every finding MUST cite `file:line` and a one-sentence rationale.

| # | Dimension | How |
|---|---|---|
| R1 | Security / vulnerability | Static reasoning (security-engineer): injection, authn/z, secrets, unsafe patterns |
| R2 | Reliability / downtime | Static reasoning: SPOF, missing timeouts/retries, blast radius, leaks, circular deps |
| R3 | Complexity / maintainability | Static + structural: deep nesting, god-files, duplication, coupling |
| R4 | Performance | Static reasoning (performance-engineer): N+1, unbounded loops, sync-in-hot-path, memory |
| R5 | Correctness / defects | Static reasoning: NPE risk, wrong/empty error handling, unchecked returns |
| R6 | Dependency / supply-chain | Run `osv-scanner --format json` over lockfiles; map CVSS → severity. Fall back to manifests + web CVE lookup if OSV unavailable |
| R7 | Change-hotspot | `git log` churn × R3 complexity; flag high-churn complex files. Requires a real git repo |

If OSV-Scanner is not installed, note it and degrade R6 to manifest-only.

### Step 4 — Score
Per dimension: `base` = severity-weighted (Critical 40 / High 20 / Medium 8 / Low 2, capped at
100). `final = clamp(base + llm_adj, 0, 100)` with `llm_adj ∈ [-15, +15]` — adjust only for context
the static count misses; never exceed ±15.
- `overall = round(0.6·max(final) + 0.4·weighted_mean(final))` — weights: Security 1.3,
  Reliability 1.3, Correctness 1.1, others 1.0.
- `driver_dimension = argmax(final)`.

### Step 5 — Render the report (always)
Emit: summary table, dimension-score table, findings grouped by severity (most-severe first).
This inline report is the primary output regardless of Bluelink/flags.

### Step 6 — (only with `--bluelink`) delta vs previous run
If Bluelink is reachable, fetch the service's latest prior run and show **new / fixed / regressed**
— a dimension counts as regressed only if its score rose **> 15 points**. Skip with a note otherwise.

### Step 7 — (only with `--submit`) persist to Bluelink
Call the Bluelink `risk_submit` MCP tool (service, commit_sha, repository, squad, tier,
meta_spec_path, template_version, dimensions, overall_score, driver_dimension, findings[],
report_markdown). Supply only the meta-spec *folder* — the server derives + validates the file path.
Then link `risk-assessment.md` in the service README's Sub-documents table (idempotent).
**Auto-degrade**: if Bluelink is unreachable, print the report and append
`[ℹ️ Bluelink unreachable — report not persisted]`.

## Tool Coordination
- **Read/Grep/Glob**: source analysis for R1-R5
- **Bash**: `git remote/rev-parse/log` (R7) and `osv-scanner` (R6)
- **Bluelink MCP** *(optional)*: read context (`--bluelink`) and persistence (`--submit`); degrades gracefully
- **AskUserQuestion**: service disambiguation (Step 2)
- **TodoWrite**: track the 7-dimension sweep on large repos

## Output Format
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️  Code Risk Assessment — <service> @ <sha>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall : <score>/100   (higher = riskier)
Driver  : <dimension>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[dimension table] · [findings by severity] · [Δ vs previous, with --bluelink]
<with --submit & persisted>  Persisted: <run_id> → <meta_spec_path>/risk-assessment.md
<otherwise>                  Local only — add --bluelink/--submit to sync with Bluelink
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Examples
```bash
# Local assessment — inline report, no MCP, nothing written
/sc:identify-risk

# Assess a subdirectory of a specific service (still local)
/sc:identify-risk --service booking-api --path src/payments

# Use Bluelink for shared template + prior-run delta (read-only)
/sc:identify-risk --bluelink

# Assess AND persist to Bluelink for org/squad rollup
/sc:identify-risk --submit
```

## Boundaries

**Will:**
- Assess all 7 dimensions with evidence-based findings (every item cites file:line + rationale)
- Run fully local by default with a built-in rubric — no MCP required
- Use Bluelink only when `--bluelink`/`--submit` is passed, and auto-degrade if it is unavailable
- Produce a deterministic base score with a bounded (±15) LLM adjustment

**Will NOT:**
- Touch Bluelink or any network without `--bluelink`/`--submit`
- Invent a scoring schema or exceed the ±15 adjustment band
- Fabricate findings or scores without file:line evidence
- Modify the analyzed code (assessment only — use `/sc:improve` to fix)

**Output**: Inline ranked report always; with `--submit`, also a persisted run + meta-spec
`risk-assessment.md` in Bluelink.

**Next Step**: Use `/sc:improve --focus <dimension>` to remediate top findings, then re-run
`/sc:identify-risk` to confirm the score dropped.
