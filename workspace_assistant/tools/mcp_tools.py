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


def get_github_mcp_toolset_deferred() -> McpToolset:
    """Create McpToolset with defer_loading for on-demand tool discovery.

    Returns:
        McpToolset configured with defer_loading=True to reduce token usage
        by ~80% compared to loading all GitHub tools upfront.

    Raises:
        ValueError: If GITHUB_PERSONAL_ACCESS_TOKEN is not set.
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN not set. Add it to your .env file."
        )

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params),
        defer_loading=True,
    )


def search_github_tools(query: str) -> dict:
    """Search for available GitHub MCP tools by keyword.

    Use this to discover which GitHub tools are available before calling them.
    Search by capability keyword to find the right tool for the task.

    Args:
        query: Search term describing the capability needed, such as
            'repository', 'issues', 'pull request', 'commits', or 'search'.

    Returns:
        dict with 'status' and 'matching_tools' list of tool names and
        descriptions that match the query keyword.
    """
    # Known GitHub MCP tools and their descriptions
    github_tool_registry = {
        "create_or_update_file": "Create or update a file in a repository",
        "search_repositories": "Search for GitHub repositories",
        "create_repository": "Create a new GitHub repository",
        "get_file_contents": "Get contents of a file from a repository",
        "push_files": "Push multiple files to a repository",
        "create_issue": "Create a new issue in a repository",
        "create_pull_request": "Create a pull request",
        "fork_repository": "Fork a repository",
        "create_branch": "Create a new branch",
        "list_commits": "List commits on a branch",
        "list_issues": "List issues in a repository",
        "update_issue": "Update an existing issue",
        "add_issue_comment": "Add a comment to an issue",
        "search_code": "Search for code across repositories",
        "search_issues": "Search for issues and pull requests",
        "get_issue": "Get details of a specific issue",
        "get_pull_request": "Get details of a pull request",
        "list_pull_requests": "List pull requests in a repository",
    }

    query_lower = query.lower()
    matching = {
        name: desc
        for name, desc in github_tool_registry.items()
        if query_lower in name.lower() or query_lower in desc.lower()
    }

    if not matching:
        return {
            "status": "no_match",
            "message": f"No tools found matching '{query}'.",
            "available_categories": [
                "repository",
                "issues",
                "pull request",
                "commits",
                "search",
                "file",
                "branch",
            ],
        }

    return {
        "status": "success",
        "matching_tools": [
            {"name": name, "description": desc} for name, desc in matching.items()
        ],
        "count": len(matching),
    }


mcp_tools = [
    get_github_mcp_toolset(),
]


def get_github_mcp_toolset_deferred() -> McpToolset:
    """Create McpToolset configured for on-demand tool discovery.

    Paired with search_github_tools to implement the tool search pattern,
    reducing effective token usage by only calling tools discovered via search.

    Returns:
        McpToolset connected to the GitHub MCP server.

    Raises:
        ValueError: If GITHUB_PERSONAL_ACCESS_TOKEN is not set.
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN not set. Add it to your .env file."
        )

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
    )

    return McpToolset(
        connection_params=StdioConnectionParams(server_params=server_params)
    )


deferred_mcp_toolset = get_github_mcp_toolset_deferred()
