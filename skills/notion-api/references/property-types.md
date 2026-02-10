# Notion Property Types Reference

## Reading Properties

Each property has a `type` field. Extract values based on type:

| Type | Value Path | Example |
|------|-----------|---------|
| `title` | `prop["title"][*]["plain_text"]` | Page title |
| `rich_text` | `prop["rich_text"][*]["plain_text"]` | Text fields |
| `number` | `prop["number"]` | `42` |
| `select` | `prop["select"]["name"]` | `"High"` |
| `multi_select` | `prop["multi_select"][*]["name"]` | `["Tag1", "Tag2"]` |
| `status` | `prop["status"]["name"]` | `"In Progress"` |
| `date` | `prop["date"]["start"]`, `["end"]` | `"2026-02-10"` |
| `people` | `prop["people"][*]["name"]` | `["Alice", "Bob"]` |
| `checkbox` | `prop["checkbox"]` | `true` |
| `url` | `prop["url"]` | `"https://..."` |
| `email` | `prop["email"]` | `"a@b.com"` |
| `phone_number` | `prop["phone_number"]` | `"+81..."` |
| `relation` | `prop["relation"][*]["id"]` | Related page IDs |
| `rollup` | Depends on rollup config | Computed value |
| `formula` | `prop["formula"][type_value]` | Computed value |
| `unique_id` | `prop["unique_id"]["prefix"]` + `["number"]` | `"TASK-123"` |
| `created_time` | `prop["created_time"]` | ISO datetime |
| `last_edited_time` | `prop["last_edited_time"]` | ISO datetime |
| `created_by` | `prop["created_by"]["name"]` | User name |
| `last_edited_by` | `prop["last_edited_by"]["name"]` | User name |

## Writing Properties

### title / rich_text
```json
{"Title": {"title": [{"text": {"content": "New Title"}}]}}
{"Description": {"rich_text": [{"text": {"content": "Text here"}}]}}
```

### number
```json
{"Score": {"number": 95}}
```

### select / multi_select
```json
{"Priority": {"select": {"name": "High"}}}
{"Tags": {"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]}}
```

### status
```json
{"Status": {"status": {"name": "Done"}}}
```

### date
```json
{"Due": {"date": {"start": "2026-02-10"}}}
{"Period": {"date": {"start": "2026-02-10", "end": "2026-02-20"}}}
```

### checkbox
```json
{"Done": {"checkbox": true}}
```

### url / email / phone
```json
{"Website": {"url": "https://example.com"}}
{"Email": {"email": "a@b.com"}}
{"Phone": {"phone_number": "+81-90-1234-5678"}}
```

### people
```json
{"Assignee": {"people": [{"id": "user-uuid"}]}}
```

### relation
```json
{"Parent": {"relation": [{"id": "page-uuid"}]}}
```

## Block Types

| Type | Content Key | Notes |
|------|------------|-------|
| `heading_1` | `heading_1.rich_text` | H1 |
| `heading_2` | `heading_2.rich_text` | H2 |
| `heading_3` | `heading_3.rich_text` | H3 |
| `paragraph` | `paragraph.rich_text` | Regular text |
| `bulleted_list_item` | `bulleted_list_item.rich_text` | Bullet |
| `numbered_list_item` | `numbered_list_item.rich_text` | Numbered |
| `to_do` | `to_do.rich_text` + `.checked` | Checkbox |
| `toggle` | `toggle.rich_text` | Collapsible |
| `code` | `code.rich_text` + `.language` | Code block |
| `quote` | `quote.rich_text` | Blockquote |
| `callout` | `callout.rich_text` + `.icon` | Callout box |
| `divider` | (none) | Horizontal rule |
| `table` | `table.table_width` | Table container |
| `table_row` | `table_row.cells` | Table row |
| `image` | `image.file.url` or `.external.url` | Image |
| `bookmark` | `bookmark.url` | Web bookmark |
| `embed` | `embed.url` | Embedded content |
| `child_page` | `child_page.title` | Sub-page |
| `child_database` | `child_database.title` | Inline DB |
