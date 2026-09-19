---
name: check-deadlines
description: Show what's due soon across calendar, Canvas, and tasks. Use when the user asks "what's due", "what do I have this week", "check my deadlines", or similar.
---

# Check deadlines

Gather what's coming up from every source that's configured, and merge into one list sorted by date:

1. Call the `calendar` tool `list_upcoming_events` (default 7 days; use a longer window if the user asks for one).
2. Call the `canvas` tool `list_upcoming_assignments` (default 14 days — assignments usually need more lead time than calendar events).
3. Call the `tasks` tool `list_tasks` and include any with a due date inside the window.

If a source isn't configured (its tool returns a "not set up yet" message), skip it silently rather than making the user feel bad about it — just work with what's available. Only mention what's missing if literally nothing is configured.

Merge everything into one chronological list. Group by day if there's more than a handful of items. Keep it scannable — this should be quick to read, not a wall of text.
