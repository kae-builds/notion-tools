#!/usr/bin/env python3
"""Notion API CLI - Claude Code notion-tools plugin.

Usage:
    python notion_api.py page <url_or_id>          # Fetch page properties + body + comments
    python notion_api.py blocks <url_or_id>        # Fetch page blocks only
    python notion_api.py comments <url_or_id>      # Fetch comments only
    python notion_api.py props <url_or_id>         # Fetch properties only
    python notion_api.py search <query>            # Search workspace
    python notion_api.py comment <url_or_id> <text> # Post a comment
    python notion_api.py update <url_or_id> <json>  # Update page properties
    python notion_api.py db <database_id> [filter_json] # Query database

Token is auto-discovered from Notion plugin cache or NOTION_TOKEN env var.
"""

import json
import os
import re
import sys
import glob
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


def find_token():
    """Auto-discover Notion token from .mcp.json or environment.

    Search order:
      1. NOTION_TOKEN environment variable
      2. Project .mcp.json (walk up from CWD)
      3. ~/.claude/mcp.json (global)
      4. Notion plugin cache (fallback)
    """
    token = os.environ.get("NOTION_TOKEN")
    if token:
        return token

    def extract_from_mcp_json(path):
        """Extract Notion token from an .mcp.json file."""
        try:
            with open(path) as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            for name, cfg in servers.items():
                if "notion" in name.lower():
                    t = cfg.get("env", {}).get("NOTION_TOKEN")
                    if t:
                        return t
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
        return None

    # 1. Walk up from CWD looking for .mcp.json
    cwd = os.getcwd()
    while True:
        mcp_path = os.path.join(cwd, ".mcp.json")
        t = extract_from_mcp_json(mcp_path)
        if t:
            return t
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent

    # 2. Global ~/.claude/mcp.json
    t = extract_from_mcp_json(os.path.expanduser("~/.claude/mcp.json"))
    if t:
        return t

    # 3. Notion plugin cache (fallback)
    for path in sorted(glob.glob(
        os.path.expanduser("~/.claude/plugins/cache/claude-plugins-official/Notion/*/.mcp.json")
    ), reverse=True):
        t = extract_from_mcp_json(path)
        if t:
            return t

    print("Error: Notion token not found.", file=sys.stderr)
    print("Add notion server to .mcp.json or set NOTION_TOKEN env var.", file=sys.stderr)
    sys.exit(1)


def extract_page_id(url_or_id):
    """Extract page ID from Notion URL or raw ID."""
    url_or_id = url_or_id.strip()
    # Already a UUID
    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', url_or_id):
        return url_or_id
    # 32-char hex without dashes
    if re.match(r'^[0-9a-f]{32}$', url_or_id):
        s = url_or_id
        return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"
    # Notion URL
    m = re.search(r'([0-9a-f]{32})(?:\?|$|#)', url_or_id)
    if m:
        s = m.group(1)
        return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"
    print(f"Error: Cannot extract page ID from: {url_or_id}", file=sys.stderr)
    sys.exit(1)


def api_request(method, endpoint, token, data=None):
    """Make Notion API request."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            err = json.loads(error_body)
            print(f"API Error {e.code}: {err.get('message', error_body)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def extract_text(rich_text_array):
    """Extract plain text from rich_text array."""
    return "".join(t.get("plain_text", "") for t in rich_text_array)


def render_property(name, prop):
    """Render a single property to readable text."""
    ptype = prop.get("type", "")
    if ptype == "title":
        return f"{name}: {extract_text(prop.get('title', []))}"
    elif ptype == "rich_text":
        return f"{name}: {extract_text(prop.get('rich_text', []))}"
    elif ptype == "select":
        sel = prop.get("select")
        return f"{name}: {sel['name'] if sel else '(empty)'}"
    elif ptype == "multi_select":
        return f"{name}: {', '.join(s['name'] for s in prop.get('multi_select', []))}"
    elif ptype == "status":
        st = prop.get("status")
        return f"{name}: {st['name'] if st else '(empty)'}"
    elif ptype == "date":
        d = prop.get("date")
        if d:
            end = f" → {d['end']}" if d.get("end") else ""
            return f"{name}: {d.get('start', '')}{end}"
        return f"{name}: (empty)"
    elif ptype == "people":
        return f"{name}: {', '.join(p.get('name', '?') for p in prop.get('people', []))}"
    elif ptype == "number":
        return f"{name}: {prop.get('number', '(empty)')}"
    elif ptype == "checkbox":
        return f"{name}: {'✓' if prop.get('checkbox') else '✗'}"
    elif ptype == "url":
        return f"{name}: {prop.get('url', '(empty)')}"
    elif ptype == "email":
        return f"{name}: {prop.get('email', '(empty)')}"
    elif ptype == "phone_number":
        return f"{name}: {prop.get('phone_number', '(empty)')}"
    elif ptype == "relation":
        rels = prop.get("relation", [])
        return f"{name}: {len(rels)} relation(s)"
    elif ptype == "rollup":
        return f"{name}: (rollup)"
    elif ptype == "formula":
        f = prop.get("formula", {})
        ftype = f.get("type", "")
        return f"{name}: {f.get(ftype, '(empty)')}"
    elif ptype == "unique_id":
        uid = prop.get("unique_id", {})
        prefix = uid.get("prefix", "")
        num = uid.get("number", "")
        return f"{name}: {prefix}{num}" if prefix else f"{name}: {num}"
    elif ptype in ("created_time", "last_edited_time"):
        return f"{name}: {prop.get(ptype, '')}"
    elif ptype in ("created_by", "last_edited_by"):
        user = prop.get(ptype, {})
        return f"{name}: {user.get('name', '?')}"
    else:
        return f"{name}: ({ptype})"


def render_block(block, indent=0):
    """Render a block to readable text."""
    btype = block.get("type", "")
    prefix = "  " * indent
    lines = []

    type_map = {
        "heading_1": ("# ", "heading_1"),
        "heading_2": ("## ", "heading_2"),
        "heading_3": ("### ", "heading_3"),
    }

    if btype in type_map:
        marker, key = type_map[btype]
        text = extract_text(block[key].get("rich_text", []))
        lines.append(f"{prefix}{marker}{text}")
    elif btype == "paragraph":
        text = extract_text(block["paragraph"].get("rich_text", []))
        lines.append(f"{prefix}{text}" if text else "")
    elif btype == "bulleted_list_item":
        text = extract_text(block["bulleted_list_item"].get("rich_text", []))
        lines.append(f"{prefix}- {text}")
    elif btype == "numbered_list_item":
        text = extract_text(block["numbered_list_item"].get("rich_text", []))
        lines.append(f"{prefix}1. {text}")
    elif btype == "to_do":
        text = extract_text(block["to_do"].get("rich_text", []))
        mark = "x" if block["to_do"].get("checked") else " "
        lines.append(f"{prefix}[{mark}] {text}")
    elif btype == "toggle":
        text = extract_text(block["toggle"].get("rich_text", []))
        lines.append(f"{prefix}▸ {text}")
    elif btype == "divider":
        lines.append(f"{prefix}---")
    elif btype == "callout":
        text = extract_text(block["callout"].get("rich_text", []))
        icon = block["callout"].get("icon", {})
        emoji = icon.get("emoji", "") if icon else ""
        lines.append(f"{prefix}{emoji} {text}")
    elif btype == "quote":
        text = extract_text(block["quote"].get("rich_text", []))
        lines.append(f"{prefix}> {text}")
    elif btype == "code":
        text = extract_text(block["code"].get("rich_text", []))
        lang = block["code"].get("language", "")
        lines.append(f"{prefix}```{lang}")
        lines.append(f"{prefix}{text}")
        lines.append(f"{prefix}```")
    elif btype == "table":
        lines.append(f"{prefix}[Table: {block['table'].get('table_width', 0)} columns]")
    elif btype == "image":
        img = block.get("image", {})
        if img.get("type") == "external":
            lines.append(f"{prefix}[Image: {img['external']['url']}]")
        else:
            lines.append(f"{prefix}[Image: uploaded file]")
    elif btype == "bookmark":
        url = block.get("bookmark", {}).get("url", "")
        lines.append(f"{prefix}[Bookmark: {url}]")
    elif btype == "embed":
        url = block.get("embed", {}).get("url", "")
        lines.append(f"{prefix}[Embed: {url}]")
    elif btype == "child_page":
        title = block.get("child_page", {}).get("title", "")
        lines.append(f"{prefix}[Child page: {title}]")
    elif btype == "child_database":
        title = block.get("child_database", {}).get("title", "")
        lines.append(f"{prefix}[Child database: {title}]")
    else:
        lines.append(f"{prefix}[{btype}]")

    return "\n".join(lines)


def fetch_all_blocks(page_id, token):
    """Fetch all blocks including children recursively."""
    blocks = []
    cursor = None
    while True:
        endpoint = f"blocks/{page_id}/children?page_size=100"
        if cursor:
            endpoint += f"&start_cursor={cursor}"
        data = api_request("GET", endpoint, token)
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return blocks


def cmd_page(page_id, token):
    """Fetch and display full page: properties + body + comments."""
    # Properties
    page = api_request("GET", f"pages/{page_id}", token)
    icon = page.get("icon", {})
    icon_str = icon.get("emoji", "") + " " if icon and icon.get("emoji") else ""

    # Find title
    title = ""
    for name, prop in page.get("properties", {}).items():
        if prop.get("type") == "title":
            title = extract_text(prop.get("title", []))
            break

    print(f"{'=' * 60}")
    print(f"{icon_str}{title}")
    print(f"{'=' * 60}")
    print(f"ID: {page['id']}")
    print(f"Created: {page.get('created_time', '')}")
    print(f"Updated: {page.get('last_edited_time', '')}")
    print()

    print("## Properties")
    for name, prop in sorted(page.get("properties", {}).items()):
        if prop.get("type") == "title":
            continue
        rendered = render_property(name, prop)
        if rendered:
            print(f"  {rendered}")
    print()

    # Body
    print("## Content")
    blocks = fetch_all_blocks(page_id, token)
    for block in blocks:
        rendered = render_block(block)
        if rendered is not None:
            print(rendered)
    print()

    # Comments
    print("## Comments")
    data = api_request("GET", f"comments?block_id={page_id}", token)
    comments = data.get("results", [])
    if not comments:
        print("  (no comments)")
    else:
        for c in comments:
            created = c.get("created_time", "")[:16].replace("T", " ")
            user = c.get("created_by", {})
            user_name = user.get("name", user.get("id", "unknown")[:8])
            text = extract_text(c.get("rich_text", []))
            print(f"  [{created}] {user_name}:")
            for line in text.split("\n"):
                print(f"    {line}")
            print()


def cmd_blocks(page_id, token):
    """Fetch and display blocks only."""
    blocks = fetch_all_blocks(page_id, token)
    for block in blocks:
        rendered = render_block(block)
        if rendered is not None:
            print(rendered)


def cmd_comments(page_id, token):
    """Fetch and display comments only."""
    data = api_request("GET", f"comments?block_id={page_id}", token)
    comments = data.get("results", [])
    if not comments:
        print("(no comments)")
        return
    for c in comments:
        created = c.get("created_time", "")[:16].replace("T", " ")
        user = c.get("created_by", {})
        user_name = user.get("name", user.get("id", "unknown")[:8])
        text = extract_text(c.get("rich_text", []))
        print(f"[{created}] {user_name}:")
        for line in text.split("\n"):
            print(f"  {line}")
        print()


def cmd_props(page_id, token):
    """Fetch and display properties only."""
    page = api_request("GET", f"pages/{page_id}", token)
    for name, prop in sorted(page.get("properties", {}).items()):
        print(render_property(name, prop))


def cmd_search(query, token):
    """Search Notion workspace."""
    data = api_request("POST", "search", token, {
        "query": query,
        "page_size": 20,
    })
    results = data.get("results", [])
    if not results:
        print("No results found.")
        return

    for r in results:
        obj_type = r.get("object", "")
        rid = r.get("id", "")
        icon = r.get("icon", {})
        emoji = icon.get("emoji", "") + " " if icon and icon.get("emoji") else ""

        title = ""
        if obj_type == "page":
            for prop in r.get("properties", {}).values():
                if prop.get("type") == "title":
                    title = extract_text(prop.get("title", []))
                    break
        elif obj_type == "database":
            title = extract_text(r.get("title", []))

        url = r.get("url", "")
        print(f"{emoji}[{obj_type}] {title}")
        print(f"  ID: {rid}")
        print(f"  URL: {url}")
        print()


def cmd_comment(page_id, token, text):
    """Post a comment to a page."""
    data = api_request("POST", "comments", token, {
        "parent": {"page_id": page_id},
        "rich_text": [{"type": "text", "text": {"content": text}}],
    })
    print(f"Comment posted: {data.get('id', '')}")
    print(f"Time: {data.get('created_time', '')}")


def cmd_update(page_id, token, props_json):
    """Update page properties."""
    props = json.loads(props_json)
    data = api_request("PATCH", f"pages/{page_id}", token, {"properties": props})
    print(f"Page updated: {data.get('id', '')}")
    print(f"Updated at: {data.get('last_edited_time', '')}")


def cmd_db(db_id, token, filter_json=None):
    """Query a database."""
    body = {"page_size": 50}
    if filter_json:
        body["filter"] = json.loads(filter_json)
    data = api_request("POST", f"databases/{db_id}/query", token, body)
    results = data.get("results", [])
    print(f"Found {len(results)} result(s)")
    print()

    for r in results:
        # Find title
        title = ""
        for name, prop in r.get("properties", {}).items():
            if prop.get("type") == "title":
                title = extract_text(prop.get("title", []))
                break
        icon = r.get("icon", {})
        emoji = icon.get("emoji", "") + " " if icon and icon.get("emoji") else ""
        print(f"{emoji}{title}")
        print(f"  ID: {r['id']}")
        for name, prop in sorted(r.get("properties", {}).items()):
            if prop.get("type") == "title":
                continue
            rendered = render_property(name, prop)
            if rendered and "(empty)" not in rendered and "0 relation" not in rendered:
                print(f"  {rendered}")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    token = find_token()

    if cmd == "page" and len(sys.argv) >= 3:
        cmd_page(extract_page_id(sys.argv[2]), token)
    elif cmd == "blocks" and len(sys.argv) >= 3:
        cmd_blocks(extract_page_id(sys.argv[2]), token)
    elif cmd == "comments" and len(sys.argv) >= 3:
        cmd_comments(extract_page_id(sys.argv[2]), token)
    elif cmd == "props" and len(sys.argv) >= 3:
        cmd_props(extract_page_id(sys.argv[2]), token)
    elif cmd == "search" and len(sys.argv) >= 3:
        cmd_search(" ".join(sys.argv[2:]), token)
    elif cmd == "comment" and len(sys.argv) >= 4:
        cmd_comment(extract_page_id(sys.argv[2]), token, " ".join(sys.argv[3:]))
    elif cmd == "update" and len(sys.argv) >= 4:
        cmd_update(extract_page_id(sys.argv[2]), token, sys.argv[3])
    elif cmd == "db" and len(sys.argv) >= 3:
        filt = sys.argv[3] if len(sys.argv) >= 4 else None
        cmd_db(extract_page_id(sys.argv[2]), token, filt)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
