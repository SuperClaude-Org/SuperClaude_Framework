# Finding Profile Templates

## Purpose
Mandatory per-file profile formats for Pass 2 and Pass 3. **ALL fields are MANDATORY. Reports with missing fields are FAILED.**

---

## Pass 2 Profile (8 Mandatory Fields)

```markdown
### `filepath`

| Field | Value |
|-------|-------|
| **What it does** | {1-2 sentence plain-English explanation} |
| **Nature** | {script / test / doc / config / source code / data / asset / migration / one-time artifact} |
| **References** | {Who/what references this file? Grep results with files + line numbers. "None found" must be stated explicitly with grep command used} |
| **CI/CD usage** | {Called by any automation? Check workflows, compose files, Makefile, package.json, Dockerfiles. State "None" with evidence if not used} |
| **Superseded by / duplicates** | {Is there a newer/better version? Check for _v2, _enhanced, _new variants. State "No superseding file found" if none} |
| **Risk notes** | {Runtime/CI/test/doc impact if removed or moved} |
| **Recommendation** | {KEEP / MOVE / DELETE / FLAG} — {finding type if applicable} — {brief reason} |
| **Verification notes** | {Explicit list of what was checked — prevents lazy KEEP} |
```

### Pass 2 Validation Rules
- All 8 fields must be present and non-empty
- "N/A" is only acceptable for **Superseded by / duplicates** when explicitly checked
- **References** must include the grep command used, even if result is "None found"
- **Verification notes** must list at least 2 specific checks performed
- Missing or empty fields → report FAILED → must regenerate

---

## Pass 3 Profile (7 Mandatory Fields)

```markdown
### `filepath`

| Field | Value |
|-------|-------|
| **What it does** | {1-2 sentence explanation} |
| **Nature** | {file type classification} |
| **References** | {Grep results with files + line numbers} |
| **Similar files** | {Other files serving same/overlapping purpose; quantify % overlap or key differences. "No similar files found" is valid} |
| **Superseded?** | {Newer/better version exists? Evidence required} |
| **Currently used?** | {Referenced by running app, CI/CD, build? Evidence required — cite specific references} |
| **Recommendation** | {DELETE / CONSOLIDATE (with what) / MOVE / FLAG / KEEP} — {reason} |
```

### Pass 3 Validation Rules
- All 7 fields must be present and non-empty
- **Similar files** must include comparison methodology (how similarity was determined)
- **Currently used?** must cite specific evidence, not just "yes" or "no"
- For CONSOLIDATE: **Similar files** must include overlap percentage
- Missing or empty fields → report FAILED → must regenerate

---

## Common Validation Failures

| Failure | Example | Fix |
|---------|---------|-----|
| Missing grep evidence | "No references" without command | Add: `grep -r "filename" . → 0 matches` |
| Lazy KEEP | "Seems important" | Add specific reference: `imported by src/app.js:42` |
| Empty verification notes | Field left blank | List: "Checked: imports, CI workflows, package.json" |
| Unquantified overlap | "Similar to other file" | Add: "85% overlap, differs in lines 42-58" |
| Missing nature classification | Field says "file" | Use taxonomy: script / test / doc / config / source code / data / asset |
