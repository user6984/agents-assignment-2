"""
Part 2: GitHub MCP Integration

Configures McpToolset to connect to the GitHub MCP server.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

MCP_CONFIG_PATH = Path(__file__).parent.parent / "config" / "mcp_servers.json"


def get_github_mcp_toolset() -> McpToolset:
    """Create and return a McpToolset configured for the GitHub MCP server.

    Reads the GITHUB_PERSONAL_ACCESS_TOKEN from the environment and
    configures the GitHub MCP server via npx. Raises a clear error if
    the token is missing.

    Returns:
        McpToolset connected to the GitHub MCP server.

    Raises:
        ValueError: If GITHUB_PERSONAL_ACCESS_TOKEN is not set in .env
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN not set. "
            "Add it to your .env file: GITHUB_PERSONAL_ACCESS_TOKEN=ghp_..."
        )

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params)
    )


def get_github_mcp_toolset_from_config() -> McpToolset:
    """Load McpToolset configuration from config/mcp_servers.json.

    Alternative to get_github_mcp_toolset() using file-based config.

    Returns:
        McpToolset connected to the GitHub MCP server.

    Raises:
        FileNotFoundError: If mcp_servers.json does not exist.
        ValueError: If GITHUB_PERSONAL_ACCESS_TOKEN is not set.
    """
    config = load_mcp_config()
    github = config["mcpServers"]["github"]

    token = github["env"].get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN not set. Add it to your .env file."
        )

    server_params = StdioServerParameters(
        command=github["command"], args=github["args"], env=github["env"]
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params)
    )


def load_mcp_config() -> dict:
    """Load MCP server configuration from JSON file."""
    if not MCP_CONFIG_PATH.exists():
        raise FileNotFoundError(f"MCP config not found: {MCP_CONFIG_PATH}")

    with open(MCP_CONFIG_PATH) as f:
        config = json.load(f)

    github_config = config.get("mcpServers", {}).get("github", {})
    env = github_config.get("env", {})
    for key, value in env.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env[key] = os.getenv(env_var, "")

    return config


mcp_tools = [
    get_github_mcp_toolset(),
]
