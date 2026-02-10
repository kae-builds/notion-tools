---
name: Notion API
description: >-
  This skill should be used when the user shares a Notion URL, asks to "check a Notion page",
  "read Notion", "fetch from Notion", "search Notion", "post a comment on Notion",
  "update Notion status", "query Notion database", or references any notion.so link.
  Also trigger when Notion MCP tools are unavailable and direct API access is needed.
version: 1.0.0
---

# Notion API Integration

Direct Notion API access via Python CLI. Works independently of Notion MCP server availability.

## Quick Start

The script at `scripts/notion_api.py` handles all Notion API operations. Token is auto-discovered
from the Notion plugin cache (`~/.claude/plugins/cache/claude-plugins-official/Notion/*/.mcp.json`)
or `NOTION_TOKEN` environment variable.

## Commands

### Read Operations

```bash
# Full page (properties + content + comments)
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py page <url_or_id>

# Individual sections
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py props <url_or_id>
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py blocks <url_or_id>
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py comments <url_or_id>
```

### Search

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py search "query text"
```

### Write Operations

```bash
# Post comment
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py comment <url_or_id> "Comment text"

# Update properties (JSON format)
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py update <url_or_id> '{"ステータス":{"status":{"name":"完了"}}}'
```

### Database Query

```bash
# All records
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py db <database_id>

# With filter
python ${CLAUDE_PLUGIN_ROOT}/skills/notion-api/scripts/notion_api.py db <database_id> '{"property":"Status","status":{"equals":"Done"}}'
```

## URL Handling

The script accepts Notion URLs, 32-char hex IDs, or formatted UUIDs:
- `https://www.notion.so/Page-Title-abc123...` → auto-extracts ID
- `abc123def456...` (32 hex chars) → auto-formats to UUID
- `abc123de-f456-...` (UUID) → used directly

## Workflow

### When user shares a Notion URL

1. Run `page` command to fetch full content
2. Summarize properties (status, assignees, dates)
3. Present body content in readable format
4. Include relevant comments

### When searching for a task

1. Run `search` command with keywords
2. Present results with titles, IDs, and URLs
3. Offer to fetch full details of specific results

### When posting comments

1. Confirm comment content with user before posting
2. Run `comment` command
3. Verify success from output

### When updating properties

1. First run `props` to see current values
2. Confirm changes with user
3. Run `update` with property JSON
4. Refer to `references/property-types.md` for JSON format

## MCP Fallback Strategy

When Notion MCP tools (`mcp__plugin_Notion_notion__*`) are available, prefer those.
Fall back to this script when:
- MCP tools return errors or are not loaded
- Session startup failed to connect Notion MCP
- Direct API control is needed (e.g., raw property updates)

## Additional Resources

### Reference Files

- **`references/api-endpoints.md`** — Full API endpoint reference, auth details, query patterns
- **`references/property-types.md`** — Property type reading/writing formats, block types

### Known User IDs (moneycharger project)

For mention-capable comments, user IDs can be discovered via the `people` properties
in page responses. Cache discovered IDs for the session.
