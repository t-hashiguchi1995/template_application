# バックエンド用Dockerfile
FROM python:3.11-slim

# uvをインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルとアプリケーションコードをコピー
COPY pyproject.toml ./
COPY backend/ ./backend/

# 依存関係をインストール（プロジェクトも含めてインストール）
RUN uv sync

# 環境変数（Cloud Run は PORT=8080 を渡す。未設定時は 8800）
ENV PYTHONPATH=/app
ENV PORT=8800

# ポートを公開
EXPOSE 8800

# アプリケーションを起動（PORT を参照して Cloud Run 互換に）
CMD ["sh", "-c", "uv run uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8800}"]
