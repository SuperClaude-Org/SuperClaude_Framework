"""Unit tests for the MCP server registry used by `superclaude mcp`."""

import json
from pathlib import Path

from superclaude.cli.install_mcp import MCP_SERVERS

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
