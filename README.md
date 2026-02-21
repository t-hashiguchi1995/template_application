# Gemini API テンプレートアプリケーション

Python (FastAPI, uv) と TypeScript (React + Vite) を使用した、Gemini APIの機能を網羅したテンプレートアプリケーションです。

## 機能

このアプリケーションは以下のGemini API機能を実装しています：

- **テキスト生成**: テキストの生成とチャット機能
- **画像生成**: Nano Bananaを使用した画像生成
- **画像理解**: 画像の分析と説明
- **動画生成**: Veo 3.1を使用した動画生成
- **音声生成**: TTS（Text-to-Speech）機能
- **音声理解**: 音声の文字起こし
- **エンベディング**: テキストのベクトル化
- **関数呼び出し**: 外部関数との連携
- **構造化出力**: JSON形式での構造化された出力
- **ドキュメント理解**: PDF、DOCX等のドキュメント分析
- **エージェント**: ツールを使用したエージェント機能

## プロジェクト構造

```
template_application/
├── backend/              # FastAPI バックエンド
│   ├── main.py          # メインアプリケーション
│   ├── config.py        # 設定管理
│   ├── client.py        # Gemini API クライアント
│   └── routers/         # API ルーター
│       ├── text.py
│       ├── image.py
│       ├── video.py
│       ├── audio.py
│       ├── embedding.py
│       ├── function_calling.py
│       ├── structured_output.py
│       ├── document.py
│       └── agent.py
├── frontend/            # React + Vite フロントエンド
│   ├── src/
│   │   ├── pages/       # ページコンポーネント
│   │   ├── api/         # API クライアント
│   │   └── App.tsx      # メインアプリケーション
│   ├── Dockerfile       # フロントエンド用Dockerfile
│   └── package.json
├── backend/
│   └── Dockerfile       # バックエンド用Dockerfile
├── deploy/              # GCP Cloud Run デプロイ用
│   ├── deploy_cloudrun.sh
│   ├── README.md
│   └── terraform/       # API 有効化・Artifact Registry 等
├── docker-compose.yml   # Docker Compose設定
├── Makefile            # 便利なMakeコマンド
├── pyproject.toml       # Python 依存関係
├── .env.example         # 環境変数テンプレート
├── .dockerignore        # Docker無視ファイル
├── run_backend.sh       # バックエンド起動スクリプト
├── run_frontend.sh      # フロントエンド起動スクリプト
└── README.md
```

## セットアップ

### 方法1: Docker Composeを使用（推奨）

最も簡単な方法です。DockerとDocker Composeがインストールされている必要があります。

#### 1. 前提条件

- Docker 20.10以上
- Docker Compose 2.0以上
- Gemini API キー

#### 2. Gemini API キーの取得

1. [Google AI Studio](https://ai.google.dev/) にアクセス
2. API キーを取得
3. `.env` ファイルを作成し、API キーを設定

```bash
cp .env.example .env
# .env ファイルを編集して GEMINI_API_KEY を設定
```

#### 3. Docker Composeで起動

```bash
# コンテナをビルドして起動
docker-compose up --build

# バックグラウンドで起動する場合
docker-compose up -d --build

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

**Makefileを使用する場合（推奨）:**

```bash
# ヘルプを表示
make help

# コンテナをビルド
make build

# コンテナを起動
make up

# ログを表示しながら起動
make up-logs

# ログを表示
make logs

# バックエンドのログのみ表示
make logs-backend

# フロントエンドのログのみ表示
make logs-frontend

# コンテナを停止
make down

# コンテナを再起動
make restart

# コンテナとイメージを削除
make clean

# 再ビルドして起動
make rebuild
```

アプリケーションは以下のURLでアクセスできます：
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8800
- API ドキュメント: http://localhost:8800/docs

### 方法2: ローカル環境でセットアップ

#### 1. 前提条件

- Python 3.11以上
- Node.js 18以上
- uv (Pythonパッケージマネージャー)
- Gemini API キー

#### 2. Gemini API キーの取得

1. [Google AI Studio](https://ai.google.dev/) にアクセス
2. API キーを取得
3. `.env` ファイルを作成し、API キーを設定

```bash
cp .env.example .env
# .env ファイルを編集して GEMINI_API_KEY を設定
```

#### 3. バックエンドのセットアップ

```bash
# uv をインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# バックエンドを起動
uv run uvicorn backend.main:app --reload --port 8800

# または起動スクリプトを使用
./run_backend.sh
```

#### 4. フロントエンドのセットアップ

```bash
cd frontend

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev

# または起動スクリプトを使用（プロジェクトルートから）
./run_frontend.sh
```

## 使用方法

1. バックエンドとフロントエンドの両方を起動
2. ブラウザで `http://localhost:5173` にアクセス
3. ナビゲーションメニューから各機能を選択して使用

## API エンドポイント

### テキスト生成
- `POST /api/text/generate` - テキスト生成
- `POST /api/text/chat` - チャット形式のテキスト生成

### 画像
- `POST /api/image/generate` - 画像生成
- `POST /api/image/analyze` - 画像分析

### 動画
- `POST /api/video/generate` - 動画生成

### 音声
- `POST /api/audio/generate` - 音声生成（TTS）
- `POST /api/audio/transcribe` - 音声の文字起こし

### エンベディング
- `POST /api/embedding/generate` - エンベディング生成
- `POST /api/embedding/batch` - バッチエンベディング生成

### 関数呼び出し
- `POST /api/function-calling/call` - 関数呼び出し

### 構造化出力
- `POST /api/structured-output/generate` - 構造化出力生成

### ドキュメント
- `POST /api/document/analyze` - ドキュメント分析

### エージェント
- `POST /api/agent/chat` - エージェントチャット

## 開発

### Docker Composeを使用する場合

#### 本番環境（ビルド済み）

```bash
# コンテナを起動
docker-compose up

# バックエンドのログを確認
docker-compose logs -f backend

# フロントエンドのログを確認
docker-compose logs -f frontend

# コンテナを再ビルド
docker-compose up --build
```

#### 開発環境（ホットリロード有効）

```bash
# 開発用設定で起動（コード変更が自動反映）
docker-compose -f docker-compose.dev.yml up --build

# バックグラウンドで起動
docker-compose -f docker-compose.dev.yml up -d --build
```

### ローカル環境で開発する場合

#### バックエンドの開発

```bash
# 開発サーバーを起動（ホットリロード有効）
uv run uvicorn backend.main:app --reload --port 8800

# API ドキュメントを確認
# http://localhost:8800/docs
```

#### フロントエンドの開発

```bash
cd frontend
npm run dev
```

### Dockerイメージの個別ビルド

```bash
# バックエンドのみビルド（コンテキストはリポジトリルート）
docker build -f backend/Dockerfile -t gemini-backend .

# フロントエンドのみビルド
docker build -f frontend/Dockerfile -t gemini-frontend ./frontend
```

## GCP Cloud Run へのデプロイ

- デプロイ手順・Terraform（API 有効化・Artifact Registry）は [deploy/README.md](deploy/README.md) を参照してください。
- リポジトリルートの `.env` に `PROJECT_ID` と `GEMINI_API_KEY`（または `GOOGLE_API_KEY`）を設定したうえで、`./deploy/deploy_cloudrun.sh` を実行します。

## 参考資料

- [Gemini API ドキュメント](https://ai.google.dev/gemini-api/docs?hl=ja)
- [Agent Development Kit ドキュメント](https://google.github.io/adk-docs/)
- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [React ドキュメント](https://react.dev/)
- [Vite ドキュメント](https://vite.dev/)

## ライセンス

MIT
