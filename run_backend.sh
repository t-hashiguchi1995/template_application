#!/bin/bash
# バックエンドサーバーを起動するスクリプト

# 環境変数を読み込む
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# バックエンドを起動
uv run uvicorn backend.main:app --reload --port 8800 --host 0.0.0.0

