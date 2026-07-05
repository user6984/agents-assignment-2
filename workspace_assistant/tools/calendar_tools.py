"""
Option A: Calendar Assistant Tools
Implements 5 tools for Google Calendar operations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta, timezone
from typing import Optional

from auth import get_calendar_service


def list_upcoming_events(max_results: int = 10, days_ahead: int = 7) -> dict:
    """List upcoming calendar events within a specified number of days.

    Args:
        max_results: Maximum number of events to return (default 10).
        days_ahead: Number of days ahead to look for events (default 7).

    Returns:
        dict with 'status' and 'events' keys. Each event includes
        summary, start time, end time, and event id.
    """
    try:
        service = get_calendar_service()
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days_ahead)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=end.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        formatted = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            end_time = e["end"].get("dateTime", e["end"].get("date"))
            formatted.append(
                {
                    "id": e["id"],
                    "summary": e.get("summary", "No title"),
                    "start": start,
                    "end": end_time,
                    "location": e.get("location", ""),
                }
            )

        return {"status": "success", "events": formatted, "count": len(formatted)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[str] = None,
) -> dict:
    """Create a new calendar event.

    Args:
        summary: Title of the event.
        start_datetime: Start time in ISO format (e.g. '2025-07-10T14:00:00').
        end_datetime: End time in ISO format (e.g. '2025-07-10T15:00:00').
        description: Optional description or agenda for the event.
        location: Optional location of the event.
        attendees: Optional comma-separated list of attendee email addresses.

    Returns:
        dict with 'status' and created event details including the event id.
    """
    try:
        service = get_calendar_service()

        event = {
            "summary": summary,
            "start": {"dateTime": start_datetime, "timeZone": "UTC"},
            "end": {"dateTime": end_datetime, "timeZone": "UTC"},
        }

        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            emails = [e.strip() for e in attendees.split(",")]
            event["attendees"] = [{"email": em} for em in emails]

        created = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
                sendUpdates="all" if attendees else "none",
            )
            .execute()
        )

        return {
            "status": "success",
            "message": f"Event '{summary}' created successfully.",
            "event_id": created["id"],
            "link": created.get("htmlLink", ""),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_conflicts(start_datetime: str, end_datetime: str) -> dict:
    """Check for scheduling conflicts in a given time range.

    Args:
        start_datetime: Start of the time range in ISO format
            (e.g. '2025-07-10T14:00:00').
        end_datetime: End of the time range in ISO format
            (e.g. '2025-07-10T15:00:00').

    Returns:
        dict with 'status', 'has_conflicts' boolean, and any
        conflicting events found.
    """
    try:
        service = get_calendar_service()

        body = {
            "timeMin": start_datetime,
            "timeMax": end_datetime,
            "items": [{"id": "primary"}],
        }

        result = service.freebusy().query(body=body).execute()
        busy = result.get("calendars", {}).get("primary", {}).get("busy", [])

        return {
            "status": "success",
            "has_conflicts": len(busy) > 0,
            "conflicts": busy,
            "message": (
                f"Found {len(busy)} conflict(s) in that time slot."
                if busy
                else "No conflicts found — time slot is free."
            ),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def find_available_slots(
    duration_minutes: int = 60,
    days_ahead: int = 5,
    start_hour: int = 9,
    end_hour: int = 17,
) -> dict:
    """Find available time slots for a meeting within working hours.

    Args:
        duration_minutes: Duration of the meeting in minutes (default 60).
        days_ahead: Number of days ahead to search (default 5).
        start_hour: Start of working hours in 24h format (default 9).
        end_hour: End of working hours in 24h format (default 17).

    Returns:
        dict with 'status' and 'available_slots' list of free windows.
    """
    try:
        service = get_calendar_service()
        now = datetime.now(timezone.utc)
        slots = []

        for day_offset in range(days_ahead):
            day = now + timedelta(days=day_offset)
            work_start = day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            work_end = day.replace(hour=end_hour, minute=0, second=0, microsecond=0)

            if work_end < now:
                continue

            body = {
                "timeMin": work_start.isoformat(),
                "timeMax": work_end.isoformat(),
                "items": [{"id": "primary"}],
            }
            result = service.freebusy().query(body=body).execute()
            busy = result.get("calendars", {}).get("primary", {}).get("busy", [])

            # Walk working hours, skip busy blocks
            current = max(work_start, now)
            for busy_block in busy:
                busy_start = datetime.fromisoformat(
                    busy_block["start"].replace("Z", "+00:00")
                )
                if (busy_start - current).seconds >= duration_minutes * 60:
                    slots.append(
                        {
                            "start": current.isoformat(),
                            "end": (
                                current + timedelta(minutes=duration_minutes)
                            ).isoformat(),
                        }
                    )
                current = datetime.fromisoformat(
                    busy_block["end"].replace("Z", "+00:00")
                )

            if (work_end - current).seconds >= duration_minutes * 60:
                slots.append(
                    {
                        "start": current.isoformat(),
                        "end": (
                            current + timedelta(minutes=duration_minutes)
                        ).isoformat(),
                    }
                )

        return {
            "status": "success",
            "available_slots": slots[:10],
            "count": min(len(slots), 10),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_event(event_id: str) -> dict:
    """Delete a calendar event by its ID.

    Args:
        event_id: The unique ID of the event to delete. Use
            list_upcoming_events to find event IDs.

    Returns:
        dict with 'status' and confirmation message.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {
            "status": "success",
            "message": f"Event {event_id} deleted successfully.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


calendar_tools = [
    list_upcoming_events,
    create_event,
    check_conflicts,
    find_available_slots,
    delete_event,
]
