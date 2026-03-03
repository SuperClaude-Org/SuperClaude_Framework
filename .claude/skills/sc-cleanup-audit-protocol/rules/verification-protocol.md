# Universal Verification Protocol

## Purpose
Defines evidence requirements for every recommendation type and the cross-reference checklist used by all audit passes.

## Unified Classification Taxonomy (Priority-Ordered)

| Priority | Category | Reversibility | Actor |
|----------|----------|--------------|-------|
| 1 | DELETE | Git recoverable | Any developer |
| 2 | CONSOLIDATE | Git recoverable | Developer with domain knowledge |
| 3 | MOVE | Git recoverable | Any developer |
| 4 | FLAG | Requires code changes | Developer with context |
| 5 | KEEP | No action | N/A |
| 6 | BROKEN REF | Varies | Developer with context |

## Evidence Requirements by Recommendation Type

### DELETE (4 checklist items)
- [ ] Grep confirms zero active references (cite the grep command and results with pattern + count)
- [ ] File is not dynamically loaded (check all 5 patterns from dynamic-use-checklist.md)
- [ ] No CI/CD pipeline references it (check workflows, Makefile, package.json, Dockerfile)
- [ ] A successor/replacement exists, OR the functionality is no longer needed, OR the file is a transient artifact (cache/log/tmp/demo) — transient type eliminates the successor requirement

### KEEP (5 checklist items)
- [ ] At least one active reference found (cite file + line number)
- [ ] File is in a sensible location for its type
- [ ] File naming follows project conventions
- [ ] For configs: referenced by build/CI/runtime system
- [ ] For tests: in a test-runner-discovered path with proper patterns

### CONSOLIDATE (3 checklist items)
- [ ] Both files identified with full paths
- [ ] Overlap quantified (% identical, key differences listed)
- [ ] Recommendation for which to keep and what unique parts to merge

### FLAG (4 checklist items)
- [ ] The issue is clearly described
- [ ] The required action is specific enough to execute
- [ ] Impact scope is estimated (which files/systems affected)
- [ ] A minimal verification checklist states: "what evidence would settle this?"

### MOVE (2 checklist items)
- [ ] Clear target location rationale
- [ ] List of references to update

## Cross-Reference Checklist (7 Reference Sources)

Every file audit must check these reference sources:

1. [ ] **Source code imports/requires**: `grep -r "filename" --include="*.{ts,tsx,py,js,jsx,go,rs,java,rb}"`
2. [ ] **CI/CD workflows**: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`
3. [ ] **Docker/Compose files**: `docker-compose*.yml`, `Dockerfile*`
4. [ ] **Package managers**: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`
5. [ ] **Build systems**: `Makefile`, `*.sh`, `*.ps1`, `Justfile`, `Taskfile.yml`
6. [ ] **Documentation**: `*.md`, `docs/`, `README*`
7. [ ] **Infrastructure manifests**: Kubernetes, Helm, Terraform (if present)

## Documentation Claim Verification

For documentation files, verify 3-5 technical claims against actual implementation:
- Check that referenced file paths exist
- Check that described API endpoints are current
- Check that configuration values match actual defaults
- Check that version numbers are accurate
- **Highest-value finding**: "this README/doc describes things that don't exist"

## 16 Reusable Cleanup Principles

1. **Read-only by default**: Audit output only; no repo edits during the audit
2. **Evidence over assumption**: Every recommendation must cite specific grep results, line numbers, or config references. "Probably unused" is not evidence
3. **Conservative default**: When in doubt, FLAG rather than DELETE. A false negative (missed dead code) is cheaper than a false positive (deleted active code)
4. **Read before judging**: A file named `old-deploy.sh` might be the only deploy script that works. Read it and trace its references
5. **Proof standards rise each pass**: Pass 1 quick triage → Pass 2 per-file proof → Pass 3 cross-cutting diff/overlap proof
6. **Escalating depth**: Start broad and shallow, then narrow and deep
7. **Mandatory evidence**: Every KEEP/DELETE needs verifiable anchors (references + file:line)
8. **Profile everything**: Even KEEP items get profiles. Prevents re-auditing and creates institutional knowledge
9. **Incremental saves**: Context windows are finite. Save every 5-10 files. Never risk losing work
10. **Scope discipline**: Cap files per agent; state explicit exclusions; prevent "audit the world"
11. **Orchestrated batching**: Priority-first batches, parallel where independent, special fast-path for binary/asset directories
12. **Noise control (dedup across passes)**: Each pass receives known issues from previous passes. Re-flagging wastes reviewer time
13. **Completion criteria and Remaining list**: Transparency beats pretending completeness
14. **Output schema as a quality gate**: Reports must be machine-checkable (consistent, mandatory fields)
15. **Verify documentation claims**: The highest-value finding class is "this README/doc describes things that don't exist"
16. **Check the test infrastructure**: Tests targeting dead code, using wrong paths, or permanently skipped are a common source of hidden debt
