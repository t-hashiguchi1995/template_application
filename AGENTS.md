# AGENTS.md — スキル呼び出しガイド

> このドキュメントは、エージェント（AI）が現在登録されている **Skills** を適切に選択・呼び出すためのガイドです。  
> タスクやユーザーの発話に応じて、どのスキルを参照すべきかを判断する際に使用してください。

---

## 1. 使い方

- **スキルの参照**: 該当するスキルは `@skill-name` で参照するか、チャットでスキル名に言及して読み込む。
- **PROACTIVELY**: 説明に「Use PROACTIVELY」とあるスキルは、該当タスクでは**こちらから積極的に**参照する。
- **複数該当**: タスクが複数領域にまたがる場合は、必要なスキルを複数参照してよい。
- **サブエージェント**: 探索・シェル・E2E・並列タスクの振り分けは **agent-manager-skill** に従う。

---

## 2. カテゴリ別スキル一覧

### 2.1 フロントエンド・UI/UX

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| React / Next.js の実装・コンポーネント・データ取得・パフォーマンス | **frontend-dev-guidelines** | Suspense-first、feature-based、MUI v7、TanStack Router 等の標準に従う |
| React/Next.js のパフォーマンス最適化・バンドル・ウォーターフォール | **vercel-react-best-practices** (Vercel) | 書き方・レビュー・リファクタ時に参照 |
| UI/UX デザイン・スタイル・パレット・フォント・チャート・スタック選定 | **ui-ux-pro-max** | plan / build / create 等のアクション |
| Figma デザインの実装・コード生成・コンポーネント対応 | **implement-design** (Figma) | Figma URL や「デザインを実装して」に使用 |
| Figma とコードのコンポーネント対応づけ | **code-connect-components** (Figma) | Code Connect 用 |
| デザインシステムルールの生成 | **create-design-system-rules** (Figma) | プロジェクト固有のルール |

### 2.2 セキュリティ

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| バックエンドのセキュリティ・入力検証・認証・API 保護 | **backend-security-coder** | PROACTIVELY 使用推奨 |
| フロントエンドのセキュリティ・XSS・サニタイズ・クライアント側保護 | **frontend-security-coder** | PROACTIVELY 使用推奨 |
| API の認証・認可・レート制限・脆弱性対策 | **api-security-best-practices** | API 設計・実装時 |
| スキルの監査・プロンプトインジェクション・悪意あるコードのスキャン | **skill-scanner** | .cursor/skills の追加・変更・監査時 |

### 2.3 API・バックエンド設計

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| REST / GraphQL API の設計・仕様レビュー・方針策定 | **api-design-principles** | 新規 API 設計・レビュー |
| Pydantic モデル・API スキーマ・DB モデル・バリデーション | **pydantic-models-py** | Base / Create / Update / Response / InDB パターン |

### 2.4 コード品質・レビュー

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| コードレビュー・品質保証・静的解析・セキュリティスキャン・設定レビュー | **code-reviewer** | PROACTIVELY 使用推奨 |

### 2.5 デプロイ・CI/CD・インフラ

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| CI/CD 設計・GitOps・デプロイ自動化・ゼロダウンタイム | **deployment-engineer** | PROACTIVELY 使用推奨 |
| マルチステージパイプライン・承認ゲート・デプロイオーケストレーション | **deployment-pipeline-design** | ワークフロー設計時 |
| 本番デプロイの考え方・ロールバック・検証 | **deployment-procedures** | 手順・判断の指針 |
| 設定の検証・テスト・スキーマ・設定の正しさの保証 | **deployment-validation-config-validate** | 設定管理 |
| Terraform / OpenTofu・IaC・ステート・マルチクラウド・GitOps | **terraform-specialist** | PROACTIVELY 使用推奨 |
| Vercel へのデプロイ・プレビュー・本番デプロイ | **vercel-deploy-claimable** | 「デプロイして」「Vercel に上げて」等 |
| Serverless ブラウザ自動化のデプロイ・スケジュール・Webhook | **functions** (Browserbase) | Browserbase Functions |

### 2.6 Git・PR・Issue

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| rebase / cherry-pick / bisect / worktree / reflog 等の高度な Git | **git-advanced-workflows** | 履歴の整理・復旧 |
| PR の品質向上・説明文・レビュー自動化 | **git-pr-workflows-pr-enhance** | PR 作成・改善 |
| オンボーディング・ナレッジ転移・リモートチーム統合 | **git-pr-workflows-onboard** | 新規メンバー・引き継ぎ |
| Sentry 流の PR 作成・説明・レビュー準備 | **create-pr** | PR を開く・説明を書く |
| メモ・ログ・音声メモ・スクショから GitHub Issue 作成 | **github-issue-creator** | バグ報告・Issue 化 |

### 2.7 3D・WebGL・ゲーム

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| Web 上の 3D 体験全般（プラットフォーム選定含む） | **game-development** | プラットフォーム別に振り分け |
| Three.js で 3D シーン・ビジュアル・インタラクション | **threejs-skills** | 3D/WebGL/ビジュアル表現 |
| React Three Fiber・Spline・3D ポートフォリオ・没入サイト | **3d-web-experience** | プロダクトコンフィグ等 |
| 2D ゲーム（スプライト・タイルマップ・物理・カメラ） | **game-development/2d-games** | |
| 3D ゲーム（レンダリング・シェーダ・物理・カメラ） | **game-development/3d-games** | |
| Web ブラウザゲーム・WebGPU・PWA | **game-development/web-games** | |
| モバイルゲーム・タッチ・バッテリー・ストア | **game-development/mobile-games** | |
| PC/コンソール・エンジン選定・最適化 | **game-development/pc-games** | |
| マルチプレイ・ネットワーク・同期 | **game-development/multiplayer** | |
| VR/AR・快適性・インタラクション・パフォーマンス | **game-development/vr-ar** | |
| ゲームデザイン・GDD・バランス・進行 | **game-development/game-design** | |
| ゲームアート・ビジュアル・アセット・アニメーション | **game-development/game-art** | |
| ゲームオーディオ・BGM・適応オーディオ | **game-development/game-audio** | |

### 2.8 プロンプト・スキル・ルール・設定

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| プロンプトの改善・戦略・デバッグ | **prompt-engineering** | プロンプト設計・学習 |
| 新規スキルの作成・SKILL.md の形式・ベストプラクティス | **create-skill** | スキル作成・執筆 |
| ルール作成・. cursor/rules・AGENTS.md・コーディング規約 | **create-rule** | ルール・規約の追加・変更 |
| Cursor/VSCode の settings.json 変更 | **update-cursor-settings** | エディタ設定・テーマ・キーバインド |

### 2.9 エージェント・タスク振り分け

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| サブエージェントの起動・explore / shell / e2e-tester / generalPurpose の使い分け・並列・resume | **agent-manager-skill** | 探索・シェル・E2E・並列実行の判断 |

### 2.10 ブラウザ自動化・テスト

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| ブラウザ操作・フォーム入力・スクリーンショット・データ取得 | **browser-use** | サイト操作・テスト・情報取得 |

### 2.11 ビジネス・Notion・Figma・ストア

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| Notion テンプレートのビジネス・販売・価格・マーケットプレイス | **notion-template-business** | テンプレートを製品として運用 |
| App Store / Google Play の ASO・リサーチ・最適化・トラッキング | **app-store-optimization** | アプリのストア最適化 |
| Discord のメッセージ・チャンネル・ロール・Webhook・リアクション自動化 | **discord-automation** | Rube MCP (Composio) 利用時はツールスキーマを確認 |

### 2.12 Notion（MCP 連携スキル）

| シナリオ・キーワード | 推奨スキル | 備考 |
|----------------------|------------|------|
| Notion でページ・DB を検索 | **search** / **find** | キーワード・自然言語検索 |
| データベースのクエリ・フィルタ・ソート | **database-query** | 構造化結果 |
| 新規ページ作成（会議メモ・プロジェクト等） | **create-page** | タイプに応じた構造 |
| データベースに行追加 | **create-database-row** | プロパティのマッピング |
| タスク作成（期日・ステータス・オーナー・プロジェクト） | **create-task** | タスクDB向け |
| 会議の事前資料・アジェンダ・リサーチ | **meeting-intelligence** | Notion 連携 |
| 議論・会話の構造化ドキュメント化 | **knowledge-capture** | ナレッジ蓄積 |
| 複数ページの調査・リサーチドキュメント作成 | **research-documentation** | 引用・インサイト |
| 仕様・スペックから実装タスクへ分解 | **spec-to-implementation** | Notion タスク化 |
| タスクボードのセットアップ | **tasks-setup** | テンプレート or 既存ボード接続 |
| タスクからの実装プラン作成 | **tasks-plan** | ステップ・見積もり・依存 |
| タスク URL から実装・ステータス更新 | **tasks-build** | Notion と連携した実装 |
| コード変更の説明ドキュメントを Notion に作成 | **tasks-explain-diff** | 差分の説明 |

---

## 3. クイック参照（キーワード → スキル）

- **React / Next / フロント** → frontend-dev-guidelines, vercel-react-best-practices  
- **UI/UX / デザイン** → ui-ux-pro-max, implement-design (Figma)  
- **セキュリティ（バックエンド）** → backend-security-coder  
- **セキュリティ（フロント）** → frontend-security-coder  
- **API 設計** → api-design-principles, api-security-best-practices  
- **Pydantic / スキーマ** → pydantic-models-py  
- **コードレビュー** → code-reviewer  
- **デプロイ / CI/CD** → deployment-engineer, deployment-pipeline-design, deployment-procedures  
- **Terraform / IaC** → terraform-specialist  
- **Vercel デプロイ** → vercel-deploy-claimable  
- **Git 上級** → git-advanced-workflows  
- **PR / Issue** → create-pr, git-pr-workflows-pr-enhance, github-issue-creator  
- **3D / WebGL** → threejs-skills, 3d-web-experience  
- **ゲーム** → game-development（必要に応じて 2d/3d/web/mobile 等）  
- **プロンプト** → prompt-engineering  
- **スキル・ルール作成** → create-skill, create-rule  
- **サブエージェント・並列** → agent-manager-skill  
- **ブラウザ操作** → browser-use  
- **スキル監査** → skill-scanner  
- **Notion** → search, find, database-query, create-page, create-task, tasks-* 等  

---

## 4. 注意事項

- スキルは**読んでから**従う。言及するだけでなく、必要に応じて `Read` で SKILL.md を開く。
- 複数スキルが該当する場合は、タスクの性質に合わせて組み合わせて使用する。
- MCP が必要な作業（Notion・Figma・GitHub 等）はメインエージェントで行い、サブエージェントに任せる場合は `prompt` で使用するスキルを明示する。
