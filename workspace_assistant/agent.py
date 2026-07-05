"""
Google Workspace Assistant - Main Agent Definition
"""

import os
import sys
from pathlib import Path

# Make imports work both as a package (adk web) and directly (test runner)
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

from config.settings import Settings
from tools.calendar_tools import calendar_tools
from tools.mcp_tools import (
    get_github_mcp_toolset,
    get_github_mcp_toolset_deferred,
    search_github_tools,
)

try:
    from .config.settings import Settings
    from .tools.calendar_tools import calendar_tools
    from .tools.mcp_tools import (
        get_github_mcp_toolset,
        get_github_mcp_toolset_deferred,
        search_github_tools,
    )
except ImportError:
    from config.settings import Settings
    from tools.calendar_tools import calendar_tools
    from tools.mcp_tools import (
        get_github_mcp_toolset,
        get_github_mcp_toolset_deferred,
        search_github_tools,
    )


def create_agent() -> LlmAgent:
    """Create the Workspace Assistant agent."""
    settings = Settings()

    instruction = """You are a helpful Google Workspace assistant that helps 
    users manage their calendar and GitHub repositories.

    CALENDAR CAPABILITIES:
    - List upcoming events: show the user their scheduled meetings and events
    - Create events: schedule new meetings with title, time, location, and attendees
    - Check conflicts: detect scheduling conflicts before booking a meeting
    - Find available slots: suggest free time windows for meetings
    - Delete events: remove events by their event ID

    GITHUB CAPABILITIES:
    - List repositories: show the user's GitHub repositories
    - Show issues: display open issues in a specific repository
    - Create issues: add a new issue to a repository

    BEHAVIORAL GUIDELINES:
    - Always confirm with the user before creating, modifying, or deleting anything
    - When creating an event, ask for all required details (title, date, time, 
      duration) before proceeding
    - When a time slot has conflicts, proactively suggest alternatives using 
      find_available_slots
    - Display dates and times in a human-friendly format
    - If a tool returns an error, explain it clearly and suggest how to fix it
    - For GitHub operations, always clarify which repository the user means if 
      it is ambiguous
    """

    github_toolset = get_github_mcp_toolset()

    return LlmAgent(
        name="workspace_assistant",
        model=settings.model_name,
        instruction=instruction,
        tools=calendar_tools + [github_toolset],
    )


def create_agent_with_tool_search() -> LlmAgent:
    """BONUS: Create agent with defer_loading for tool search.

    Uses defer_loading=True on McpToolset so GitHub tools are loaded
    on-demand rather than all upfront, reducing token usage by ~80%.
    A search_github_tools function is provided so the agent can
    discover available tools before calling them.
    """
    settings = Settings()

    instruction = """You are a helpful Google Workspace assistant that helps 
    users manage their calendar and GitHub repositories.

    CALENDAR CAPABILITIES:
    - List upcoming events: show the user their scheduled meetings and events
    - Create events: schedule new meetings with title, time, location, and attendees
    - Check conflicts: detect scheduling conflicts before booking a meeting
    - Find available slots: suggest free time windows for meetings
    - Delete events: remove events by their event ID

    GITHUB CAPABILITIES:
    - Use search_github_tools first to find the right GitHub tool for a task
    - List repositories, show issues, create issues, manage pull requests
    - Always search for the right tool before attempting a GitHub operation

    BEHAVIORAL GUIDELINES:
    - Always confirm with the user before creating, modifying, or deleting anything
    - For GitHub operations, use search_github_tools to find the right tool first
    - Display dates and times in a human-friendly format
    - If a tool returns an error, explain it clearly and suggest how to fix it
    """

    from tools.mcp_tools import deferred_mcp_toolset, search_github_tools

    return LlmAgent(
        name="workspace_assistant_with_tool_search",
        model=settings.model_name,
        instruction=instruction,
        tools=calendar_tools + [search_github_tools, deferred_mcp_toolset],
    )


# Required by ADK web UI
root_agent = create_agent()
# Bonus: agent with deferred tool loading
root_agent_with_tool_search = create_agent_with_tool_search()
