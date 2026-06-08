"""
Tests for MCP Server Installation Module

Tests MCP server installation and management functionality.
"""

import subprocess
from unittest.mock import MagicMock, patch


class TestMCPServerRegistry:
    """Tests for MCP server registry"""

    def test_mcp_servers_registry_exists(self):
        """Test MCP_SERVERS registry is defined"""
        from superclaude.cli.install_mcp import MCP_SERVERS

        assert isinstance(MCP_SERVERS, dict)
        assert len(MCP_SERVERS) > 0

    def test_airis_gateway_defined(self):
        """Test AIRIS gateway configuration exists"""
        from superclaude.cli.install_mcp import AIRIS_GATEWAY

        assert isinstance(AIRIS_GATEWAY, dict)
        assert "name" in AIRIS_GATEWAY
        assert "endpoint" in AIRIS_GATEWAY
        assert "transport" in AIRIS_GATEWAY

    def test_server_has_required_fields(self):
        """Test each server has required fields"""
        from superclaude.cli.install_mcp import MCP_SERVERS

        required_fields = ["name", "description", "transport", "command"]

        for server_key, server_info in MCP_SERVERS.items():
            for field in required_fields:
                assert field in server_info, f"{server_key} missing {field}"

    def test_server_transport_types(self):
        """Test servers use valid transport types"""
        from superclaude.cli.install_mcp import MCP_SERVERS

        valid_transports = ["stdio", "sse", "websocket"]

        for server_key, server_info in MCP_SERVERS.items():
            assert server_info["transport"] in valid_transports, (
                f"{server_key} has invalid transport: {server_info['transport']}"
            )


class TestCheckDockerAvailable:
    """Tests for check_docker_available function"""

    @patch("superclaude.cli.install_mcp._run_command")
    def test_docker_available(self, mock_run):
        """Test docker available detection"""
        from superclaude.cli.install_mcp import check_docker_available

        mock_run.return_value = MagicMock(returncode=0)

        result = check_docker_available()

        assert result is True

    @patch("superclaude.cli.install_mcp._run_command")
    def test_docker_not_available(self, mock_run):
        """Test docker not available detection"""
        from superclaude.cli.install_mcp import check_docker_available

        mock_run.return_value = MagicMock(returncode=1)

        result = check_docker_available()

        assert result is False

    @patch("superclaude.cli.install_mcp._run_command")
    def test_docker_timeout(self, mock_run):
        """Test docker check handles timeout"""
        from superclaude.cli.install_mcp import check_docker_available

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="docker", timeout=10)

        result = check_docker_available()

        assert result is False


class TestCheckPrerequisites:
    """Tests for check_prerequisites function"""

    @patch("superclaude.cli.install_mcp._run_command")
    def test_prerequisites_all_pass(self, mock_run):
        """Test all prerequisites pass"""
        from superclaude.cli.install_mcp import check_prerequisites

        # Mock successful claude and node checks
        mock_run.return_value = MagicMock(returncode=0, stdout="v20.0.0")

        success, errors = check_prerequisites()

        assert success is True
        assert len(errors) == 0

    @patch("superclaude.cli.install_mcp._run_command")
    def test_prerequisites_missing_claude(self, mock_run):
        """Test missing Claude CLI detected"""
        from superclaude.cli.install_mcp import check_prerequisites

        def side_effect(cmd, **kwargs):
            if "claude" in cmd:
                raise FileNotFoundError()
            return MagicMock(returncode=0, stdout="v20.0.0")

        mock_run.side_effect = side_effect

        success, errors = check_prerequisites()

        assert success is False
        assert any("Claude CLI" in e for e in errors)

    @patch("superclaude.cli.install_mcp._run_command")
    def test_prerequisites_old_node_version(self, mock_run):
        """Test old Node.js version detected"""
        from superclaude.cli.install_mcp import check_prerequisites

        def side_effect(cmd, **kwargs):
            if "node" in cmd:
                return MagicMock(returncode=0, stdout="v16.0.0")
            return MagicMock(returncode=0, stdout="")

        mock_run.side_effect = side_effect

        success, errors = check_prerequisites()

        assert success is False
        assert any("version 18+" in e for e in errors)


class TestCheckMCPServerInstalled:
    """Tests for check_mcp_server_installed function"""

    @patch("superclaude.cli.install_mcp._run_command")
    def test_server_installed(self, mock_run):
        """Test installed server detection"""
        from superclaude.cli.install_mcp import check_mcp_server_installed

        mock_run.return_value = MagicMock(
            returncode=0, stdout="tavily\ncontext7\nplaywright"
        )

        assert check_mcp_server_installed("tavily") is True

    @patch("superclaude.cli.install_mcp._run_command")
    def test_server_not_installed(self, mock_run):
        """Test uninstalled server detection"""
        from superclaude.cli.install_mcp import check_mcp_server_installed

        mock_run.return_value = MagicMock(returncode=0, stdout="tavily\ncontext7")

        assert check_mcp_server_installed("unknown-server") is False

    @patch("superclaude.cli.install_mcp._run_command")
    def test_server_check_handles_error(self, mock_run):
        """Test server check handles errors gracefully"""
        from superclaude.cli.install_mcp import check_mcp_server_installed

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)

        result = check_mcp_server_installed("any-server")

        assert result is False


class TestInstallMCPServer:
    """Tests for install_mcp_server function"""

    @patch("superclaude.cli.install_mcp.check_mcp_server_installed")
    @patch("superclaude.cli.install_mcp._run_command")
    def test_install_already_installed(self, mock_run, mock_check):
        """Test skips installation if already installed"""
        from superclaude.cli.install_mcp import MCP_SERVERS, install_mcp_server

        mock_check.return_value = True

        server_info = MCP_SERVERS["tavily"]
        result = install_mcp_server(server_info)

        assert result is True
        # _run_command should not be called for installation
        # (may be called by check_mcp_server_installed)

    @patch("superclaude.cli.install_mcp.check_mcp_server_installed")
    @patch("superclaude.cli.install_mcp._run_command")
    def test_install_dry_run(self, mock_run, mock_check):
        """Test dry run doesn't execute commands"""
        from superclaude.cli.install_mcp import MCP_SERVERS, install_mcp_server

        mock_check.return_value = False

        # Use a server without API key requirement for dry run test
        server_info = MCP_SERVERS["context7"]
        result = install_mcp_server(server_info, dry_run=True)

        assert result is True

    @patch("superclaude.cli.install_mcp.check_mcp_server_installed")
    @patch("superclaude.cli.install_mcp._run_command")
    def test_install_success(self, mock_run, mock_check):
        """Test successful installation"""
        from superclaude.cli.install_mcp import MCP_SERVERS, install_mcp_server

        mock_check.return_value = False
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        server_info = MCP_SERVERS["context7"]
        result = install_mcp_server(server_info)

        assert result is True

    @patch("superclaude.cli.install_mcp.check_mcp_server_installed")
    @patch("superclaude.cli.install_mcp._run_command")
    def test_install_failure(self, mock_run, mock_check):
        """Test installation failure handling"""
        from superclaude.cli.install_mcp import MCP_SERVERS, install_mcp_server

        mock_check.return_value = False
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="Installation failed"
        )

        server_info = MCP_SERVERS["context7"]
        result = install_mcp_server(server_info)

        assert result is False


class TestInstallMCPServers:
    """Tests for install_mcp_servers main function"""

    @patch("superclaude.cli.install_mcp.check_prerequisites")
    def test_install_fails_prerequisites(self, mock_prereq):
        """Test installation fails if prerequisites not met"""
        from superclaude.cli.install_mcp import install_mcp_servers

        mock_prereq.return_value = (False, ["Missing Claude CLI"])

        success, message = install_mcp_servers(selected_servers=["tavily"])

        assert success is False
        assert "Prerequisites" in message

    @patch("superclaude.cli.install_mcp.check_prerequisites")
    @patch("superclaude.cli.install_mcp.install_airis_gateway")
    def test_install_gateway_selection(self, mock_gateway, mock_prereq):
        """Test AIRIS gateway installation"""
        from superclaude.cli.install_mcp import install_mcp_servers

        mock_prereq.return_value = (True, [])
        mock_gateway.return_value = True

        success, message = install_mcp_servers(
            selected_servers=["airis-mcp-gateway"], dry_run=True
        )

        assert success is True

    @patch("superclaude.cli.install_mcp.check_prerequisites")
    @patch("superclaude.cli.install_mcp.install_mcp_server")
    def test_install_selected_servers(self, mock_install, mock_prereq):
        """Test installation of selected servers"""
        from superclaude.cli.install_mcp import install_mcp_servers

        mock_prereq.return_value = (True, [])
        mock_install.return_value = True

        success, message = install_mcp_servers(
            selected_servers=["tavily", "context7"], dry_run=True
        )

        assert success is True

    @patch("superclaude.cli.install_mcp.check_prerequisites")
    def test_install_invalid_servers(self, mock_prereq):
        """Test handling of invalid server names"""
        from superclaude.cli.install_mcp import install_mcp_servers

        mock_prereq.return_value = (True, [])

        success, message = install_mcp_servers(selected_servers=["invalid-server-xyz"])

        assert success is False
        assert "No valid servers" in message


class TestAirisGatewayInstall:
    """Tests for AIRIS gateway installation"""

    @patch("superclaude.cli.install_mcp.check_docker_available")
    def test_gateway_requires_docker(self, mock_docker):
        """Test gateway installation requires Docker"""
        from superclaude.cli.install_mcp import install_airis_gateway

        mock_docker.return_value = False

        result = install_airis_gateway()

        assert result is False

    @patch("superclaude.cli.install_mcp.check_docker_available")
    def test_gateway_dry_run(self, mock_docker):
        """Test gateway dry run"""
        from superclaude.cli.install_mcp import install_airis_gateway

        mock_docker.return_value = True

        result = install_airis_gateway(dry_run=True)

        assert result is True
