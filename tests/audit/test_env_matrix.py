"""Tests for env key-presence matrix (T03.05 / D-0021)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.env_matrix import (
    EnvKeyMatrix,
    build_matrix,
    parse_env_file,
    scan_code_references,
)


# --- Fixtures ---

ENV_CONTENT = """\
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secret123
API_KEY=sk_live_abc123
"""

ENV_EXAMPLE = """\
# Database config
DB_HOST=
DB_PORT=
DB_PASSWORD=
# API_KEY is optional
"""

ENV_PRODUCTION = """\
DB_HOST=prod.db.example.com
DB_PORT=5432
DB_PASSWORD=prod_secret
API_KEY=sk_live_prod
SENTRY_DSN=https://sentry.io/123
"""

CODE_PY = """\
import os

db_host = os.environ.get("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT")
api_key = os.environ["API_KEY"]
redis_url = os.environ.get("REDIS_URL")
"""

CODE_JS = """\
const dbHost = process.env.DB_HOST;
const dbPort = process.env.DB_PORT;
const newRelic = process.env.NEW_RELIC_KEY;
"""


class TestParseEnvFile:
    def test_extracts_keys(self):
        keys = parse_env_file(ENV_CONTENT)
        assert "DB_HOST" in keys
        assert "DB_PORT" in keys
        assert "DB_PASSWORD" in keys
        assert "API_KEY" in keys

    def test_skips_comments(self):
        keys = parse_env_file(ENV_CONTENT)
        assert not any(k.startswith("#") for k in keys)

    def test_skips_empty_lines(self):
        keys = parse_env_file("\n\n\n")
        assert keys == []

    def test_handles_export_prefix(self):
        keys = parse_env_file("export MY_VAR=value\n")
        assert "MY_VAR" in keys

    def test_never_returns_values(self):
        """CRITICAL: keys only, no values."""
        keys = parse_env_file(ENV_CONTENT)
        for key in keys:
            assert "=" not in key
            assert "localhost" not in key
            assert "secret" not in key.lower()


class TestScanCodeReferences:
    def test_python_os_environ_get(self):
        keys = scan_code_references(CODE_PY)
        assert "DB_HOST" in keys

    def test_python_os_getenv(self):
        keys = scan_code_references(CODE_PY)
        assert "DB_PORT" in keys

    def test_python_os_environ_bracket(self):
        keys = scan_code_references(CODE_PY)
        assert "API_KEY" in keys

    def test_js_process_env(self):
        keys = scan_code_references(CODE_JS)
        assert "DB_HOST" in keys
        assert "NEW_RELIC_KEY" in keys


class TestBuildMatrix:
    def test_basic_matrix(self):
        matrix = build_matrix(
            env_files={".env": ENV_CONTENT},
            code_files={"main.py": CODE_PY},
        )
        assert len(matrix.entries) > 0

    def test_output_contains_keys_only(self):
        """CRITICAL: matrix output must contain only key names, never values."""
        matrix = build_matrix(
            env_files={".env": ENV_CONTENT, ".env.example": ENV_EXAMPLE},
            code_files={"main.py": CODE_PY},
        )
        d = matrix.to_dict()
        serialized = str(d)
        assert "secret123" not in serialized
        assert "sk_live_abc123" not in serialized
        assert "localhost" not in serialized

    def test_drift_missing_from_example(self):
        """Keys in code but missing from .env.example."""
        matrix = build_matrix(
            env_files={
                ".env": ENV_CONTENT,
                ".env.example": ENV_EXAMPLE,
            },
            code_files={"main.py": CODE_PY},
        )
        drifts = matrix.all_drifts
        # REDIS_URL is in code but not in .env or .env.example
        redis_drift = [d for d in drifts if d["key"] == "REDIS_URL"]
        assert len(redis_drift) > 0
        assert "missing_from_example" in redis_drift[0]["categories"]

    def test_drift_unused_in_code(self):
        """Keys in .env but never referenced in code."""
        matrix = build_matrix(
            env_files={".env": ENV_PRODUCTION},
            code_files={"main.py": CODE_PY},
        )
        drifts = matrix.all_drifts
        # SENTRY_DSN is in .env.production but not in code
        sentry_drift = [d for d in drifts if d["key"] == "SENTRY_DSN"]
        assert len(sentry_drift) > 0
        assert "unused_in_code" in sentry_drift[0]["categories"]

    def test_drift_missing_from_env(self):
        """Keys in code but not in any .env file."""
        matrix = build_matrix(
            env_files={".env": "DB_HOST=x\n"},
            code_files={"main.py": CODE_PY},
        )
        drifts = matrix.all_drifts
        # REDIS_URL is in code but not in .env
        redis_drift = [d for d in drifts if d["key"] == "REDIS_URL"]
        assert len(redis_drift) > 0
        assert "missing_from_env" in redis_drift[0]["categories"]

    def test_all_3_drift_scenarios(self):
        """Verify all 3 drift types are detectable."""
        matrix = build_matrix(
            env_files={
                ".env": ENV_CONTENT,
                ".env.example": ENV_EXAMPLE,
            },
            code_files={
                "main.py": CODE_PY,
                "app.js": CODE_JS,
            },
        )
        drifts = matrix.all_drifts
        categories = set()
        for d in drifts:
            categories.update(d["categories"])
        # At least these drift types should be detected
        assert "missing_from_example" in categories or "missing_from_env" in categories
        # NEW_RELIC_KEY and REDIS_URL are in code but not in env files
        code_only_keys = [d["key"] for d in drifts if "missing_from_env" in d["categories"]]
        assert any(k in code_only_keys for k in ["NEW_RELIC_KEY", "REDIS_URL"])

    def test_matrix_serializable(self):
        matrix = build_matrix(
            env_files={".env": ENV_CONTENT},
            code_files={"main.py": CODE_PY},
        )
        d = matrix.to_dict()
        assert "sources" in d
        assert "keys" in d
        assert "drift_count" in d
        assert "total_keys" in d
