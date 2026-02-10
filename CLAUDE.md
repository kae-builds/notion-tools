# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Notion API直接連携のClaude Codeプラグイン。MCP不要でNotionページの取得・検索・コメント投稿・プロパティ更新・DBクエリが可能。Python stdlib のみで動作（外部依存なし）。

## Architecture

```
.claude-plugin/plugin.json  → プラグインマニフェスト
skills/notion-api/
  SKILL.md                  → スキル定義（トリガー条件・ワークフロー）
  scripts/notion_api.py     → CLI本体（全APIコマンド実装）
  references/
    api-endpoints.md        → Notion API エンドポイントリファレンス
    property-types.md       → プロパティ型・ブロック型の読み書きフォーマット
```

CLIフロー: Claude Codeがスキルトリガー → `notion_api.py` をコマンド実行 → Notion REST API呼び出し → 結果をマークダウン風テキストで返却

## Commands

```bash
# ページ全体（プロパティ+ブロック+コメント）
python3 skills/notion-api/scripts/notion_api.py page <url_or_id>

# 個別取得
python3 skills/notion-api/scripts/notion_api.py props <url_or_id>
python3 skills/notion-api/scripts/notion_api.py blocks <url_or_id>
python3 skills/notion-api/scripts/notion_api.py comments <url_or_id>

# 検索・投稿・更新
python3 skills/notion-api/scripts/notion_api.py search "query"
python3 skills/notion-api/scripts/notion_api.py comment <url_or_id> "text"
python3 skills/notion-api/scripts/notion_api.py update <url_or_id> '{"Status":{"status":{"name":"Done"}}}'
python3 skills/notion-api/scripts/notion_api.py db <database_id> [filter_json]
```

## Development

```bash
# ローカルテスト（プラグインとしてロード）
claude --plugin-dir ~/dev/projects/notion-tools

# 直接スクリプト実行テスト
NOTION_TOKEN=ntn_xxx python3 skills/notion-api/scripts/notion_api.py search "test"
```

ビルド・lint・テストのステップはなし。Python 3 stdlibのみ使用。

## Key Conventions

- **認証**: `NOTION_TOKEN`環境変数（`.claude/settings.local.json`の`env`で設定）
- **Notion API Version**: `2022-06-28`（`notion_api.py`内にハードコード）
- **ID処理**: Notion URL / 32文字hex / UUID形式すべて受け付け、自動正規化
- **MCP fallback**: MCP Notionツールが利用可能な場合はそちらを優先、不可時にこのスクリプトで代替
- **プロパティ更新フォーマット**: `references/property-types.md`に各型のJSON形式を記載
