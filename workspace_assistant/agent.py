"""
Google Workspace Assistant - Main Agent Definition
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

from .config.settings import Settings
from .tools.calendar_tools import calendar_tools
from .tools.mcp_tools import get_github_mcp_toolset


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
    """BONUS: Create agent with defer_loading for tool search."""
    raise NotImplementedError("Bonus: Implement tool search pattern")


# Required by ADK web UI
root_agent = create_agent()
