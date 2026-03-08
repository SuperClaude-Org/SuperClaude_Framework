# D-0002: Regex Validation — Frontmatter vs Horizontal Rules

## Summary

The regex pattern requires at least one `key: value` line between `---` delimiters, which distinguishes valid YAML frontmatter from markdown horizontal rules.

## Mechanism

The inner capture group `((?:[ \t]*\w[\w\s]*:.*\n)+)` requires:
1. At least one line (`+` quantifier)
2. Each line must contain a word-character key followed by `:`
3. Pattern: `\w[\w\s]*:` — key starts with word char, may contain word chars/spaces, then colon

## Rejected Inputs

- `---\n---` (empty between delimiters) → No match (no key:value line)
- `---\nplain text\n---` → No match (no colon in "plain text")
- `---\n\n---` → No match (blank lines don't match `\w[\w\s]*:`)

## Accepted Inputs

- `---\ntitle: Test\n---` → Match (has key:value)
- `---\ntitle: \n---` → Match (empty value is valid, key present)

## Verification

Test `test_horizontal_rule_rejected` confirms this behavior.
