"""Unit tests for the MCP server registry used by `superclaude mcp`."""

import json
from pathlib import Path
from unittest.mock import patch

from superclaude.cli.install_mcp import (
    AIRIS_GATEWAY,
    MCP_SERVERS,
    _provision_compose_mounts,
    install_airis_gateway,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Environment variables `@21st-dev/magic` reads its API key from
# (dist/index.js: TWENTY_FIRST_API_KEY, API_KEY_21ST, API_KEY).
MAGIC_ACCEPTED_ENV_VARS = {"TWENTY_FIRST_API_KEY", "API_KEY_21ST", "API_KEY"}


class TestMagicServerRegistry:
    """The registry must hand the 21st.dev key to magic under a name it reads.

    Regression test for #578: the installer used `TWENTYFIRST_API_KEY`
    (no underscore), which the package never looks at, so every install
    failed with "Not authenticated" even with a valid key.
    """

    def test_api_key_env_is_one_the_package_reads(self):
        assert MCP_SERVERS["magic"]["api_key_env"] in MAGIC_ACCEPTED_ENV_VARS

    def test_bundled_configs_use_the_same_env_var(self):
        expected = MCP_SERVERS["magic"]["api_key_env"]
        for config in (
            REPO_ROOT / "src" / "superclaude" / "mcp" / "configs" / "magic.json",
            REPO_ROOT / "plugins" / "superclaude" / "mcp" / "configs" / "magic.json",
        ):
            env = json.loads(config.read_text())["magic"]["env"]
            assert list(env) == [expected], config


class TestAirisGatewayRegistry:
    """The AIRIS MCP Gateway configuration must point to active upstream assets.

    Regression test for #564: upstream renamed docker-compose.dist.yml to compose.yaml,
    causing 404 download errors.
    """

    def test_compose_url_points_to_valid_compose_yaml(self):
        url = AIRIS_GATEWAY["docker_compose_url"]
        assert url.endswith("/compose.yaml")
        assert "docker-compose.dist.yml" not in url

    def test_gateway_registry_has_required_fields(self):
        for field in (
            "name",
            "transport",
            "endpoint",
            "docker_compose_url",
            "mcp_config_url",
        ):
            assert field in AIRIS_GATEWAY
            assert AIRIS_GATEWAY[field]


class TestProvisionComposeMounts:
    """Relative bind mount paths in compose files must be provisioned before container startup.

    Regression test for #564: missing bind mount paths on the host get auto-created by the
    Docker daemon as root-owned directories, causing 'not a directory' mount failures.
    """

    def test_provision_mounts_creates_files_and_directories(self, tmp_path):
        compose_file = tmp_path / "docker-compose.yml"
        compose_content = """
services:
  api:
    volumes:
      - ./mcp-config.json:/app/mcp-config.json:ro
      - ./routing-table.json:/app/routing-table.json:ro
      - ./config/gateway-config.yaml:/app/config/gateway-config.yaml:ro
      - ./catalogs/airis-catalog.yaml:/catalogs/airis-catalog.yaml:ro
      - ./profiles:/app/profiles:rw
"""
        compose_file.write_text(compose_content, encoding="utf-8")

        _provision_compose_mounts(compose_file, tmp_path)

        assert (tmp_path / "routing-table.json").is_file()
        assert (tmp_path / "config" / "gateway-config.yaml").is_file()
        assert (tmp_path / "catalogs" / "airis-catalog.yaml").is_file()
        assert (tmp_path / "profiles").is_dir()

    def test_provision_mounts_handles_missing_compose_file(self, tmp_path):
        # Should not raise when compose file does not exist
        missing_file = tmp_path / "nonexistent.yml"
        _provision_compose_mounts(missing_file, tmp_path)

    @patch("superclaude.cli.install_mcp.check_docker_available", return_value=True)
    def test_install_airis_gateway_dry_run(self, mock_docker):
        assert install_airis_gateway(dry_run=True) is True

