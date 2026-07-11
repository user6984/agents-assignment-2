## Grade: 100 / 100

**Assignment:** Google Workspace Assistant + GitHub MCP (ADK)  
**Attempt:** 1 of 2  ·  **Graded:** 2026-07-11  ·  Commit `b4a220d`

### Score breakdown
| Criterion | Max | Earned | Notes |
|-----------|-----|--------|-------|
| tool_design | 18 | 18 | Option A implemented with 5 plain-function tools (list_upcoming_events, create_event, check_conflicts, find_available_slots, delete_event), all with action-verb names, complete Args/Returns docstrings, typed parameters, and collected into the calendar_tools list (lines 260-266). Exceeds the 3-tool minimum. (`workspace_assistant/tools/calendar_tools.py:260`) |
| agent_instructions | 14 | 14 | System instruction is clear and scoped: enumerates calendar and GitHub capabilities and gives behavioral guidelines including 'Always confirm before creating, modifying, or deleting' (line 66) and proactively suggesting alternatives via find_available_slots (lines 69-70). (`workspace_assistant/agent.py:50`) |
| error_handling | 14 | 13 | Every one of the 5 tools wraps its API call in try/except and returns a structured {status, message} dict on failure (e.g. lines 62-63). All-day events handled via .get('date') fallback (line 49). Minor: failures are caught generically as str(e) rather than differentiating error types (invalid datetime, 404 event). (`workspace_assistant/tools/calendar_tools.py:62`) |
| functionality | 14 | 13 | Correct Google Calendar API usage via get_calendar_service: events().list with singleEvents/orderBy (line 33), events().insert with proper body (line 104), freebusy().query for conflicts (line 146), events().delete (line 251). Minor static bug in find_available_slots: uses timedelta.seconds instead of total_seconds() (lines 207, 220), which undercounts gaps spanning >1 day. (`workspace_assistant/tools/calendar_tools.py:33`) |
| code_quality | 10 | 8 | Code is readable, organized, and well-documented, and tools are wired into an LlmAgent via create_agent() (agent.py:79). Deductions: get_github_mcp_toolset_deferred is defined twice (lines 100 and 200) — the second silently shadows the first — and module-level side effects call get_github_mcp_toolset() at import (lines 195-197, 229), requiring a token just to import the module. (`workspace_assistant/tools/mcp_tools.py:200`) |
| mcp_configured | 10 | 10 | McpToolset correctly configured for the GitHub MCP server using StdioConnectionParams/StdioServerParameters and npx @modelcontextprotocol/server-github (lines 41-49), and attached to the agent via tools=calendar_tools + [github_toolset] (agent.py:83). (`workspace_assistant/tools/mcp_tools.py:47`) |
| github_queries | 15 | 13 | GitHub operations are wired through the MCP toolset attached to the agent (line 83) and guided by the instruction's GitHub capabilities (list repos, show/create issues, lines 60-63). A search_github_tools registry documents the expected repo/issue/PR queries (mcp_tools.py:143-162). Reflection discusses the 15+ GitHub tools exposed via MCP. No hardcoded queries, which is the correct MCP pattern; slightly generic on specific query wiring. (`workspace_assistant/agent.py:83`) |
| mcp_error_handling | 5 | 5 | Missing GITHUB_PERSONAL_ACCESS_TOKEN raises a clear, actionable ValueError with remediation guidance (lines 34-39), repeated in the deferred and config-based variants. (`workspace_assistant/tools/mcp_tools.py:34`) |
| _bonus_ | +25 | +22 | |
| Integrity deduction | — | 0 | Provided files unmodified |
| **Total** | **100** | **100** | |

### What went well
- Full calendar lifecycle covered by 5 well-named tools (read/plan/write/cleanup) with complete docstrings and typed parameters, all collected into calendar_tools (calendar_tools.py:260).
- Consistent error handling: every tool returns a structured {status, message} dict so the agent always gets interpretable output (e.g. calendar_tools.py:62).
- Clear, safety-oriented agent instruction that mandates confirmation before mutations and proactive conflict handling (agent.py:66-70).
- All three bonus features attempted with a thoughtful reflection quantifying the defer_loading token savings (reflection_template.md:70-74).

### What to improve (actionable)
- Remove the duplicate get_github_mcp_toolset_deferred definition (mcp_tools.py:200): the second copy shadows the first and drops defer_loading=True, so the deferred_mcp_toolset actually used by create_agent_with_tool_search never gets the flag — the bonus feature is inert at runtime.
- Avoid module-level side effects that require a token at import time (mcp_tools.py:195-197 and :229 call the toolset factory on import); build toolsets lazily inside the agent factory instead.
- In find_available_slots, use timedelta.total_seconds() instead of .seconds (calendar_tools.py:207, 220) so gaps longer than a day are measured correctly.
- Differentiate error handling beyond generic str(e) — surface user-friendly messages for common cases like invalid datetime strings or a missing/expired event ID.

### Automated checks
- ✅ All required files implemented
- ✅ Provided files unmodified
- ✅ 0/0 output artifacts committed
- ✅ Reflection 968 words

### Resubmission
You may resubmit **once**. Push fixes to this repo, then notify the instructor; we'll re-grade as **Attempt 2 (final)**. This is attempt 1 of 2.

---
*Graded automatically with Claude Code against the course rubric. Questions → contact the instructor.*


---
<sub>🔎 **Autograder record** — attempt 1 of 2 · graded at commit `b4a220d` · delivered 2026-07-11T18:01:35Z. Commits pushed to `main` after this timestamp are treated as a resubmission.</sub>
