---
name: slack
description: Use when reading, searching, or posting to Slack via the `claude.ai Slack` MCP connector - pasted Slack links (<workspace>.slack.com/archives/...), "check Slack", "read that thread", "search Slack for X", or drafting a Slack message/reply.
---

# Slack (claude.ai MCP connector)

Tools are namespaced `mcp__claude_ai_Slack__*` and load on demand via ToolSearch (`select:mcp__claude_ai_Slack__<name>`).

## Connector is user-managed, not Claude-managed

The connector is enabled per-user in claude.ai connector settings, not something Claude Code can turn on. If the tools are missing (they'll show under "requires authentication" in the deferred-tools reminder), tell the user to enable/authorize it there - don't try workarounds.

## Parsing a Slack link

A pasted link looks like:

```
https://your-workspace.slack.com/archives/C0123456789/p1700000000123456
```

- `channel_id` = the archives segment verbatim (`C0123456789`)
- `message_ts` = the `p<digits>` segment with a decimal point inserted 6 digits from the right: `p1700000000123456` → `1700000000.123456`

## Picking a tool

| Need | Tool |
|---|---|
| Parent message + all replies from a link | `slack_read_thread` (channel_id, message_ts) |
| Recent channel history, no specific message | `slack_read_channel` |
| Don't know the channel ID, only a name | `slack_search_channels` first |
| Don't know a user's ID, only a name/handle | `slack_search_users` |
| Find messages/threads by content, don't have a link | `slack_search_public` (public channels) or `slack_search_public_and_private` (also searches private channels you're in) |
| A reply references a "Forwarded message" stub | The stub gives you the original channel/ts - re-fetch it with `slack_read_thread`/`slack_read_channel` if you need the full content, don't assume the stub is the whole message |

## Posting is draft-only by default

Same rule as GitHub: never call `slack_send_message`, `slack_schedule_message`, `slack_add_reaction`, `slack_create_canvas`, `slack_update_canvas`, or `slack_create_conversation` without the user's explicit go-ahead for that specific message. Use `slack_send_message_draft` to prepare something for review instead.

## Token efficiency

`slack_read_thread`/`slack_read_channel` already return clean structured text (sender, timestamp, reactions, forwarded-message stubs deduped) rather than raw JSON - no extra summarization step needed before showing results to the user.
