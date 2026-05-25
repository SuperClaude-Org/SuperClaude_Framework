# KNOWLEDGE.md — accumulated insights and debugging patterns

Project-level lessons captured during development. Add to this file when an
issue's root cause or fix is non-obvious enough that a future contributor
(or future you) would benefit from finding it documented.

Format per entry: short title, one-paragraph context, the rule/pattern,
and a pointer to the originating work (commit, tasklist, RCA).

---

## Freshness system insights (2026-05-13, freshness-system v1)

Captured during the freshness-system tasklist (`.dev/releases/current/freshness-system/`).
Each item below cost ≥30 minutes of debugging — log them now so the next person
doesn't re-pay.

### F1 — Claude Code `FileChanged` is not a filesystem watcher

**Context:** the `phase5.1-context-refresh-design.md` design assumed `FileChanged`
fired on any modification to any file, with a regex matcher. Live probing
(T02.05) captured zero events.

**Rule:** Per [official docs](https://code.claude.com/docs/en/hooks):

- Matcher is `|`-separated **literal filenames** in CWD (e.g., `.env|.envrc`).
  No regex. No globs. `*` ≠ "match all".
- Stdin fields are `file_path` (absolute) and `event` ("change"/"add"/"unlink"),
  not `path` and `change_type`.
- No decision control — FileChanged cannot block anything.
- Dynamic watching via `hookSpecificOutput.watchPaths`, documented for
  CwdChanged/FileChanged responses; unverified from other events.

If a freshness/watch design needs "every file Claude has Read," the only
documented approach is to emit `watchPaths` from the watch-emitting events.
Whether `PostToolUse(Read)` can also emit `watchPaths` is an open probe.

**Source:** `.dev/releases/current/freshness-system/artifacts/D-0008/probe-finding.md`.

### F2 — `grep -c . 2>/dev/null || echo 0` double-counts when nothing matches

**Context:** the UserPromptSubmit hook used this idiom to count entries in a
file. When the file was empty, grep printed `0` AND exited 1 (no matches),
triggering the OR which printed another `0`. The captured value was `0\n0`,
which broke `[ "$count" -gt 0 ]` arithmetic comparison.

**Rule:** Don't use `grep -c | exit-1 fallback`. Either:

```bash
count=$(grep -v '^$' file | wc -l | tr -d ' ')
[ -z "$count" ] && count=0
```

…or capture and validate:

```bash
count=$(grep -c . file 2>/dev/null)
[ -z "$count" ] && count=0
```

**Source:** Phase 2 dry-runs (`CP-P02-END.md` F1).

### F3 — `flock -w N <fd> || true` falls through to unlocked critical section

**Context:** the subagent counter and post-read tracker used `flock -w 1 9 || true`,
expecting that if the lock timed out we'd just skip. Reality: under
`xargs -P 10` contention, several invocations timed out on the 1s wait and
ran the critical section WITHOUT the lock, producing duplicate `tool_call_idx`
values and lost counter updates.

**Rule:** For microsecond-scale critical sections, drop the timeout and
fail-open only on flock binary absence:

```bash
flock <fd> 2>/dev/null || exit 0
```

This blocks indefinitely (no deadlock risk if critical section is brief),
or exits cleanly if `flock` itself isn't on the host (fail-open per NFR-3).

**Source:** Phase 2 concurrency tests (`CP-P02-END.md` F2).

### F4 — Counter-increment and counter-read must share one locked section

**Context:** `freshness-post-read.sh` initially incremented the tool-call-counter
inside a flocked subshell, exited the subshell, then re-read the counter outside
the lock to get the new value. Under `-P 20` parallelism, 4/100 reads got
duplicate `tool_call_idx` because another process incremented between the lock
release and the re-read.

**Rule:** Either do the whole "increment + use" inside one lock:

```bash
(
    flock 9
    new=$(($(cat $COUNTER) + 1))
    echo "$new" > $COUNTER
    # …use $new directly inside the lock, e.g. append to log…
)
```

…or write the locked-section's value to a per-PID tempfile and read it from
there outside the lock:

```bash
TMP=$(mktemp)
(
    flock 9
    new=$(($(cat $COUNTER) + 1))
    echo "$new" > $COUNTER
    echo "$new" > $TMP
)
NEW_IDX=$(cat $TMP)
rm -f $TMP
```

Validated at -P 20 (100 unique idx) and -P 40 (200 unique idx).

**Source:** Phase 2 concurrency stress (`CP-P02-END.md` F3, F4).

### F5 — Fresh Claude Code sessions have empty `reads.jsonl` per-session

**Context:** `freshness-pre-edit.sh` filters `reads.jsonl` by both `path` and
`session_id`. A new session has no rows for itself, so EVERY first-Edit-against-a-file
blocks with `no_prior_read` — even for files the agent created earlier in a
different session.

**Rule:** This is correct behavior (each session validates its own world view).
But it means:

- Workflow is "Read first, then Edit" for every file in every session, no
  exceptions.
- For brand-new files (target path doesn't exist), use Bash heredocs (`cat > new <<EOF`)
  — the gate doesn't run on Bash.

A future v1.5 refinement may "allow Write if target path doesn't exist on disk."
Tracked in `CHANGELOG.md` under "v1.5 work items".

**Source:** Multiple organic catches during this session's own work
(`CP-P05-T05.01.md` Addendum + F10).

---

## Adding new entries

When a debugging session takes >30 minutes and the root cause is non-obvious,
add an entry here in the same format. Keep entries terse — long-form lives in
the originating doc (RCA, checkpoint, finding). This file is a fast-lookup
table that points you AT the long-form when you hit a similar symptom.

Topical sections grow as the project does (e.g., `## MCP integration insights`,
`## Pytest plugin insights`).

---

## Fix B Merged — Anti-Instinct Gate Mechanism-Signature Refactor (2026-05-25)

**Problem framing.** `integration_contracts.py` previously conflated lexical
evidence (raw line text) with semantic mechanism identity (the integration
point itself). This produced three symptoms of one design flaw: over-capture
of bare "dispatch" mentions, per-evidence-line dedup that didn't collapse
semantically-identical contracts, and narrow FR-MOD2.7 coverage that required
literal mechanism-term substrings valid roadmaps may not contain. Per
merged-output.md §1, the fix was a single coherent abstraction, not three
patches.

**Key abstraction.** Introduced `mechanism_signature: tuple[str, frozenset[str]]`
on `IntegrationContract` — a normalized `(mechanism_kind, identifier_set)`
tuple that routes both deduplication and Layer 3 stem-fallback coverage
matching through the same semantic primitive. A new `_signature_subsumed`
helper collapses contracts whose `(mechanism, identifier-set)` is identical
or a subset of an already-seen signature with ≥1 shared identifier.

**Load-bearing detail.** The empty-identifier branch in `_signature_subsumed`
(`if not idents: return sig in seen`) preserves the existing
`test_duplicate_lines_deduplicated` test's exact-match semantics. Without
it, identical evidence lines lacking UPPER_SNAKE/PascalCase identifiers
would no longer dedup.

**Spec-vs-implementation deviations.** Two deviations from merged-output.md
verbatim were necessary because the spec was internally inconsistent in two
places: (1) `PROGRAMMATIC_RUNNERS` had to be added as an explicit alternation
to `DISPATCH_PATTERNS[0]` because `\bRUNNERS\b` and `\b_RUNNERS\b` don't
match inside `PROGRAMMATIC_RUNNERS` (no word boundary at `_`); without this
addition, `TestCliPortifyRegression.*` regressed despite §4 asserting they
would pass. (2) Bare `priority` had to be removed from both §2.2 extraction
and §2.4 Layer 1 `dispatch_family` regexes because Layer 1 matched
"Implement priority dispatch for logging events" and short-circuited before
Layer 3's identifier-overlap guard — directly contradicting t7's design
intent. Both deviations are documented in the task's deviation log.

**Documented limitation.** When a spec's context contains only
single-PascalCase identifiers like `Interactive`/`Bulk` that
`_extract_identifiers` doesn't capture (it requires UPPER_SNAKE
`[A-Z][A-Z0-9_]{2,}` or multi-cap `[A-Z][a-z]+(?:[A-Z][a-z]+)+`),
the Layer 3 identifier-overlap guard short-circuits to an "empty
set = match" branch. Out of scope for this fix; logged as a Follow-Up
Item per merged-output.md §6 secondary counter-argument.

**End-to-end target.** Live re-run against
`/config/workspace/TUIBBS-scp/.dev/releases/current/v1-MVP/{epics,roadmap}.md`
(BEFORE the Fix A workaround in roadmap.md is reverted) yielded
`total=5 uncovered=0` — confirming the merged Fix B alone is sufficient.

**Files touched:** src/superclaude/cli/roadmap/integration_contracts.py, tests/roadmap/test_integration_contracts.py
