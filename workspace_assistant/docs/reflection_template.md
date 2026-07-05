# Assignment 2 Reflection

**Name:** Rami Kabbani
**Option:** A - Calendar
**Date:** July 5, 2026

---

## Tool Design Decisions

### Tools Implemented
1. **list_upcoming_events**: Lists calendar events within a configurable number of days ahead, returning summary, start/end times, location, and event ID.
2. **create_event**: Creates a new calendar event with title, start/end datetime, optional description, location, and attendees.
3. **check_conflicts**: Uses the Calendar freebusy API to detect scheduling conflicts in a given time range before booking.
4. **find_available_slots**: Searches working hours across upcoming days to find free windows of a specified duration.
5. **delete_event**: Removes a calendar event by its ID, which is surfaced by list_upcoming_events.

### Why These Tools?
These five tools cover the full lifecycle of calendar management: reading (list_upcoming_events), planning (find_available_slots, check_conflicts), writing (create_event), and cleanup (delete_event). The conflict-checking and slot-finding tools work together — when a user asks to schedule something, the agent can proactively check for conflicts and suggest alternatives without the user having to ask separately.

### Description Strategy
Each tool's docstring describes its purpose in plain language, names its parameters with concrete examples (e.g. ISO format datetime strings), and describes the return value structure. ADK reads these docstrings to build the tool schema, so precision matters. Action verbs in the function names (list, create, check, find, delete) help the LLM select the right tool based on the user's intent.

---

## Challenges Encountered

### Challenge 1: Module import errors with ADK web
- **Problem:** ADK loads the agent as a package from the parent directory, so absolute imports like `from config.settings import Settings` failed with `ModuleNotFoundError`.
- **Solution:** Switched all intra-package imports to relative imports (e.g. `from .config.settings import Settings`), which resolve correctly regardless of which directory ADK is launched from.

### Challenge 2: ADK requires `root_agent`, not just `create_agent()`
- **Problem:** ADK's web UI looks for a module-level variable called `root_agent` rather than calling a factory function automatically, so the agent wasn't loading.
- **Solution:** Added `root_agent = create_agent()` at the bottom of `agent.py` to expose the instantiated agent at module level.

### Challenge 3: Model availability and quota
- **Problem:** `gemini-2.0-flash` was deprecated and free tier quotas were exhausted, causing 404 and 429 errors.
- **Solution:** Listed available models programmatically via the API and switched to `gemini-2.5-flash`, which is stable and available on the billing-enabled account.

---

## Error Handling Approach

Every tool wraps its Google API call in a try/except block and returns a dict with `status: "error"` and a `message` field on failure. This means the agent always receives structured output it can interpret and relay to the user in plain language, rather than crashing or receiving a raw Python exception. Anticipated error types include: expired OAuth tokens (handled by the auth helper's automatic refresh), missing credentials files, invalid datetime formats passed by the user, and event IDs that no longer exist.

---

## Ideas for Improvement

1. Add a `reschedule_event` tool that combines finding a new slot, checking conflicts, and updating the existing event in one step rather than requiring the user to coordinate three separate tool calls.
2. Improve the `find_available_slots` tool to accept a timezone parameter so results are returned in the user's local time rather than UTC.
3. Add a `search_events` tool that finds events by keyword in the title or description, useful for locating a specific meeting without knowing its exact date.

---

## Key Learnings

Building with ADK taught me that the boundary between agent behavior and tool design is more important than it initially appears. A well-named, well-documented tool function shapes what the agent can do as much as the system instruction does — ADK reads the docstrings to build the tool schema, so vague descriptions lead to the agent picking wrong tools or constructing bad arguments. Writing tool descriptions as if explaining to a careful colleague who will decide when to use the tool, rather than as API documentation, produced noticeably better agent behavior.

The MCP integration for GitHub highlighted an important architectural difference between custom tools and MCP toolsets: custom tools give you full control over the interface the agent sees, while MCP tools expose whatever the server provides. The GitHub MCP server has 15+ tools with its own naming conventions, and the agent sometimes needed more specific prompting to navigate them correctly. This pointed toward the value of the defer_loading pattern — rather than loading all 15 tools into the context upfront, a production system would benefit from on-demand tool discovery to reduce token usage and improve selection accuracy.

The most practically valuable lesson was about environment and dependency management. Several hours of debugging traced back to Python version mismatches, stale virtual environment activations, and missing API keys — none of which were problems with the agent code itself. In a team setting, these setup issues multiply quickly, which is why pinning Python versions, committing `.env.example` files with clear documentation, and scripting the setup process are worth the upfront investment.