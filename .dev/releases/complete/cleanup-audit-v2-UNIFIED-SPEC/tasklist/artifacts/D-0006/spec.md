# D-0006 Spec: Real Credential Scanning with Redaction

## Module
`src/superclaude/cli/audit/credential_scanner.py`

## Detection Patterns
aws_access_key, aws_secret_key, github_token, github_classic_token, generic_api_key, generic_token, generic_password, private_key, slack_token, stripe_key

## Exclusion Patterns
${VAR_NAME}, <YOUR_*>, xxx/XXX/placeholder/PLACEHOLDER/changeme, process.env.*, os.environ.get(), os.getenv()

## Redaction
All detected secrets replaced with `[REDACTED]` via `redact_output()`.
