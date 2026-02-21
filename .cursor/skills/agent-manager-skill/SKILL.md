---
name: agent-manager-skill
description: "Cursorで扱えるエージェント群の運用ガイド。サブエージェント（generalPurpose, explore, shell, e2e-tester）の起動・使い分け、MCP・スキルの選択、並列実行とresume。"
risk: safe
source: community
---

# Agent Manager Skill（Cursor 用）

Cursor 内で利用できるエージェント・ツール群を整理し、タスクに応じて適切に振り分け・並列実行するためのガイドです。

## When to use

このスキルを参照する場面:

- 複数タスクをサブエージェントに振り分けたい（並列・継続実行）
- コードベース探索・シェル実行・E2E テストなど役割ごとにエージェントを選びたい
- MCP やスキルを「どのエージェントで使うか」を決めたい
- タスクの進め方（単体 vs サブエージェント、resume）を決めたい

## Cursor で扱えるエージェント群

| 種別 | 役割 | 主な用途 |
|------|------|----------|
| **メインエージェント** | このチャット | 全体の判断・統合・直接編集・ツール呼び出し |
| **サブエージェント** (mcp_task) | 自律的に細かいタスクを実行 | 探索・シェル・E2E・汎用の切り出し |

### サブエージェントの種類（subagent_type）

| タイプ | 用途 | 使う場面 |
|--------|------|----------|
| `explore` | コードベースの探索 | ファイル検索、キーワード検索、構成把握。**広く浅く**の調査向け。 |
| `shell` | シェルコマンド実行 | git、ビルド、npm/pip、CI などターミナル作業。 |
| `generalPurpose` | 汎用（調査・実装・複合） | キーワード検索、多段階タスク、サブエージェントで任せたい汎用作業。 |
| `e2e-tester` | E2E テスト | ブラウザでアプリを起動し、ユーザーフロー検証・リグレッション確認。 |

### 使い分けの目安

- **メインで完結させる**: 1〜2ステップ、ファイルパスが分かっている、変更が少ない → メインエージェントのみで対応。
- **サブエージェントに任せる**: 探索範囲が広い、シェルを多用する、E2E を走らせる、**並列で複数タスク**を進めたい → `mcp_task` で `description` と `subagent_type` を指定。
- **並列実行**: 依存のない複数タスクは、**同じターンで複数 `mcp_task` を同時に呼ぶ**（最大4並列の目安）。各呼び出しに `description` と希望する `subagent_type` を書く。
- **継続実行**: 同じサブエージェントに続きをさせたい場合は、`resume` に前回の agent ID を渡す。

## 運用ルール（要約）

1. **探索は explore**: コードベースの「どこに何があるか」は `explore`。必要なら thoroughness を `quick` / `medium` / `very thorough` で指定。
2. **シェルは shell**: git / ビルド / パッケージマネージャは `shell` に任せる。
3. **E2E は e2e-tester**: ブラウザ起動・操作・検証は `e2e-tester`。実機ブラウザで動作確認したいときだけ使う。
4. **曖昧なときは generalPurpose**: キーワード検索や「ファイルを探して編集」など、役割がはっきりしない複合タスクは `generalPurpose`。
5. **resume**: 長いタスクを分割するときは、返ってきた agent ID を `resume` に渡して同じサブエージェントを継続させる。
6. **readonly**: 読み取り専用で試したいときは `readonly: true` を指定する。

## MCP とスキル

- **MCP サーバー**: ブラウザ操作・Notion・Linear・Figma・GitHub などはメインエージェントが `call_mcp_tool` で利用。サブエージェントには MCP コンテキストは渡らないため、MCP が必要な作業はメインで行う。
- **スキル**: `@skill-name` やチャットでの言及でメインエージェントに読み込まれる。サブエージェント起動時は、タスク説明（`prompt`）に「どのスキルに従うか」を書くとよい。

## 外部の tmux ベース運用（オプション）

複数 CLI エージェントを tmux セッションで並列運用したい場合は、別リポジトリのスクリプトを利用できます（Cursor 標準のサブエージェントとは独立）:

```bash
git clone https://github.com/fractalmind-ai/agent-manager-skill.git
# 利用時は python3 agent-manager/scripts/main.py を参照
```

- 要 tmux と python3。エージェント定義は `agents/` 以下を参照。

## まとめ

- **Cursor 内**: メインエージェント + mcp_task（explore / shell / generalPurpose / e2e-tester）で役割分担と並列・継続実行。
- **MCP・スキル**: メインで選択して利用。サブエージェントには `prompt` で指示を明示。
- **tmux 運用**: 必要なら上記リポジトリを別途クローンして利用。
