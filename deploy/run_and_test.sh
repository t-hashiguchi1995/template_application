#!/usr/bin/env bash
# デプロイの実行と動作確認（テスト）をまとめて実行
# 使い方:
#   ./deploy/run_and_test.sh           … テストのみ（既にデプロイ済みの場合）
#   ./deploy/run_and_test.sh --deploy … デプロイしてからテスト
# 実行: リポジトリルートから ./deploy/run_and_test.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ---- .env 読み込み ----
if [[ -f ".env" ]]; then
  set -a
  . ./.env
  set +a
fi

PROJECT_ID="${PROJECT_ID:? .env に PROJECT_ID=... を設定してください}"
REGION="${REGION:-asia-northeast1}"
SERVICE_BACKEND="${SERVICE_BACKEND:-my-app-backend}"
PROXY_PORT="${PROXY_PORT:-8080}"

export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
gcloud config set project "$PROJECT_ID" --quiet

do_deploy=false
for arg in "$@"; do
  if [[ "$arg" == "--deploy" ]]; then
    do_deploy=true
    break
  fi
done

if [[ "$do_deploy" == true ]]; then
  echo "=== デプロイ実行 ==="
  "$SCRIPT_DIR/deploy_cloudrun.sh"
  echo ""
fi

echo "=== 動作確認（テスト）==="

echo ""
echo "1. サービス URL"
URL=$(gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)
if [[ -z "$URL" ]]; then
  echo "   Cloud Run サービスが見つかりません。先に ./deploy/deploy_cloudrun.sh を実行してください。"
  exit 1
fi
echo "   $URL"

echo ""
echo "2. ヘルスチェック（認証付き）"
TOKEN=$(gcloud auth print-identity-token 2>/dev/null)
if curl -sf -H "Authorization: Bearer $TOKEN" "$URL/health" >/dev/null; then
  RESP=$(curl -s -H "Authorization: Bearer $TOKEN" "$URL/health")
  echo "   OK: $RESP"
else
  echo "   失敗: /health にアクセスできませんでした。"
  exit 1
fi

echo ""
echo "3. ブラウザで確認する場合"
echo "   以下を別ターミナルで実行し、ブラウザで http://localhost:${PROXY_PORT}/ を開いてください。"
echo "   gcloud run services proxy $SERVICE_BACKEND --region $REGION --port $PROXY_PORT"
echo ""
echo "   - ヘルス: http://localhost:${PROXY_PORT}/health"
echo "   - API ドキュメント: http://localhost:${PROXY_PORT}/docs"
echo ""
echo "=== テスト完了 ==="
