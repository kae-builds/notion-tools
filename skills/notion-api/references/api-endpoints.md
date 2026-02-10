# Notion API Endpoints Reference

## Authentication

All requests require:
- `Authorization: Bearer <token>`
- `Notion-Version: 2022-06-28`

Token auto-discovery order:
1. `NOTION_TOKEN` environment variable
2. `~/.claude/plugins/cache/claude-plugins-official/Notion/*/.mcp.json`

## Endpoints

### Pages

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Get page | GET | `/v1/pages/{page_id}` |
| Update page | PATCH | `/v1/pages/{page_id}` |
| Create page | POST | `/v1/pages` |

### Blocks (Page Content)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Get children | GET | `/v1/blocks/{block_id}/children?page_size=100` |
| Append children | PATCH | `/v1/blocks/{block_id}/children` |
| Get block | GET | `/v1/blocks/{block_id}` |
| Update block | PATCH | `/v1/blocks/{block_id}` |
| Delete block | DELETE | `/v1/blocks/{block_id}` |

### Comments

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Get comments | GET | `/v1/comments?block_id={page_id}` |
| Create comment | POST | `/v1/comments` |

### Databases

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Query database | POST | `/v1/databases/{database_id}/query` |
| Get database | GET | `/v1/databases/{database_id}` |

### Search

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Search | POST | `/v1/search` |

## Page ID Extraction

Notion URLs contain the page ID as a 32-character hex string at the end:
```
https://www.notion.so/Page-Title-{32_hex_chars}?params
```

Convert to UUID format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## Common Property Update Patterns

### Update status
```json
{"properties": {"ステータス": {"status": {"name": "完了"}}}}
```

### Update select
```json
{"properties": {"カテゴリ": {"select": {"name": "バグ修正"}}}}
```

### Update rich text
```json
{"properties": {"メモ": {"rich_text": [{"text": {"content": "テキスト"}}]}}}
```

### Update number
```json
{"properties": {"工数": {"number": 5}}}
```

## Comment with Mentions

To mention a user in a comment:
```json
{
  "parent": {"page_id": "xxx"},
  "rich_text": [
    {"type": "mention", "mention": {"user": {"id": "user-uuid"}}},
    {"type": "text", "text": {"content": " コメント本文"}}
  ]
}
```

## Database Query Filters

### Text contains
```json
{"filter": {"property": "Name", "title": {"contains": "keyword"}}}
```

### Status equals
```json
{"filter": {"property": "Status", "status": {"equals": "In Progress"}}}
```

### Compound filter (AND)
```json
{"filter": {"and": [
  {"property": "Status", "status": {"equals": "Done"}},
  {"property": "Assignee", "people": {"contains": "user-id"}}
]}}
```

### Sort
```json
{"sorts": [{"property": "Created", "direction": "descending"}]}
```
