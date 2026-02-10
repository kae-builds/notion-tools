# notion-tools

Notion API直接連携の Claude Code プラグイン。

MCP不要で Notion ページの取得・検索・コメント・プロパティ更新・DB クエリが可能。

## インストール

```bash
# マーケットプレイス追加（初回のみ）
/plugin marketplace add <your-marketplace>

# インストール
/plugin install notion-tools@<marketplace-name>
```

開発中のテスト:

```bash
claude --plugin-dir ~/dev/projects/notion-tools
```

## セットアップ

プロジェクトの `.claude/settings.local.json` に `NOTION_TOKEN` を設定:

```json
{
  "env": {
    "NOTION_TOKEN": "ntn_xxxxx"
  }
}
```

トークンは [Notion Integrations](https://www.notion.so/my-integrations) から取得。

## 使い方

Claude Code 上で Notion URL を共有するか、以下のようなリクエストをすると自動でスキルが発動:

- 「このNotionページ読んで」
- 「Notionで○○を検索して」
- 「Notionにコメント投稿して」
- 「ステータスを完了に更新して」

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| `page <url>` | ページ全体（プロパティ + 本文 + コメント） |
| `props <url>` | プロパティのみ |
| `blocks <url>` | 本文ブロックのみ |
| `comments <url>` | コメントのみ |
| `search "query"` | キーワード検索 |
| `comment <url> "text"` | コメント投稿 |
| `update <url> '{json}'` | プロパティ更新 |
| `db <id> [filter]` | データベースクエリ |

## プラグイン構造

```
notion-tools/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── notion-api/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── notion_api.py
│       └── references/
│           ├── api-endpoints.md
│           └── property-types.md
└── README.md
```

## ライセンス

MIT
