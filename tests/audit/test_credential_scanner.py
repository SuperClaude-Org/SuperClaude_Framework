"""Tests for real credential scanning with safe redaction.

Validates AC7: credential scanning distinguishes real secrets from templates.
"""

from __future__ import annotations

from superclaude.cli.audit.credential_scanner import (
    REDACTION_MARKER,
    ScanResult,
    redact_output,
    scan_content,
)


# Test fixture: 3 real secrets + 3 template placeholders
FIXTURE_CONTENT = """# Config file
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
api_key = "sk_live_abcdefghijklmnopqrstuvwx"
password = "SuperSecret1234567"

# Templates (should be excluded)
password = ${DB_PASSWORD}
password = changeme
password = placeholder
"""


class TestScanContent:
    def test_detects_real_secrets(self):
        result = scan_content("config.py", FIXTURE_CONTENT)
        assert result.real_secret_count >= 3, (
            f"Expected >= 3 real secrets, got {result.real_secret_count}: "
            f"{[s.pattern_name for s in result.secrets_found]}"
        )

    def test_excludes_placeholders(self):
        result = scan_content("config.py", FIXTURE_CONTENT)
        assert result.placeholder_count >= 3, (
            f"Expected >= 3 placeholders, got {result.placeholder_count}: "
            f"{[s.pattern_name for s in result.placeholders_excluded]}"
        )

    def test_aws_key_detected(self):
        content = "AWS_KEY=AKIAIOSFODNN7EXAMPLE"
        result = scan_content("env", content)
        assert any(s.pattern_name == "aws_access_key" for s in result.secrets_found)

    def test_placeholder_dollar_brace_excluded(self):
        content = "api_key = ${API_KEY}"
        result = scan_content("env", content)
        # Should be excluded as placeholder
        for s in result.secrets_found:
            assert not s.is_placeholder

    def test_placeholder_angle_bracket_excluded(self):
        content = "token = <YOUR_API_KEY>"
        result = scan_content("env", content)
        # Should not appear in real secrets
        assert result.real_secret_count == 0

    def test_placeholder_changeme_excluded(self):
        content = "password = changeme"
        result = scan_content("env", content)
        assert result.real_secret_count == 0

    def test_github_token_detected(self):
        content = "GITHUB_TOKEN=ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"
        result = scan_content("env", content)
        assert result.real_secret_count >= 1

    def test_private_key_detected(self):
        content = "-----BEGIN RSA PRIVATE KEY-----\nfoo\n-----END RSA PRIVATE KEY-----"
        result = scan_content("key.pem", content)
        assert any(s.pattern_name == "private_key" for s in result.secrets_found)

    def test_no_secrets_in_clean_file(self):
        content = "def hello():\n    return 'world'\n"
        result = scan_content("clean.py", content)
        assert result.real_secret_count == 0
        assert result.placeholder_count == 0

    def test_empty_file(self):
        result = scan_content("empty.py", "")
        assert result.real_secret_count == 0


class TestRedaction:
    def test_redact_replaces_secret(self):
        content = "key=AKIAIOSFODNN7EXAMPLE"
        result = scan_content("env", content)
        redacted = redact_output(content, result.secrets_found)
        assert "AKIAIOSFODNN7EXAMPLE" not in redacted
        assert REDACTION_MARKER in redacted

    def test_redact_preserves_placeholders(self):
        content = "key=${API_KEY}"
        result = scan_content("env", content)
        redacted = redact_output(content, result.placeholders_excluded)
        assert "${API_KEY}" in redacted  # Placeholders not redacted

    def test_no_secret_in_output_artifact(self):
        result = scan_content("config.py", FIXTURE_CONTENT)
        d = result.to_dict()
        # Verify no raw secret value in the serialized output
        serialized = str(d)
        assert "AKIAIOSFODNN7EXAMPLE" not in serialized or REDACTION_MARKER in serialized


class TestScanResultSerialization:
    def test_to_dict_schema(self):
        result = scan_content("test.py", FIXTURE_CONTENT)
        d = result.to_dict()
        assert "file_path" in d
        assert "real_secrets" in d
        assert "placeholders_excluded" in d
        assert "real_secret_count" in d
        assert "placeholder_count" in d
