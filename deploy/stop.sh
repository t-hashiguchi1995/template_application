#!/usr/bin/env bash
# デプロイしたリソースを停止・削除する
# 使い方:
#   ./deploy/stop.sh              … Cloud Run サービスのみ削除
#   ./deploy/stop.sh --terraform  … Cloud Run 削除のあと Terraform リソースも削除
#   ./deploy/stop.sh --yes       … 確認プロンプトをスキップ（CI 等用）
# 実行: リポジトリルートから ./deploy/stop.sh
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

export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
gcloud config set project "$PROJECT_ID" --quiet

do_terraform=false
skip_confirm=false
for arg in "$@"; do
  case "$arg" in
    --terraform) do_terraform=true ;;
    --yes)        skip_confirm=true ;;
  esac
done

confirm() {
  if [[ "$skip_confirm" == true ]]; then
    return 0
  fi
  echo -n "$1 (y/N): "
  read -r r
  [[ "$r" == "y" || "$r" == "Y" ]]
}

echo "=== リソースの停止・削除 ==="
echo "  プロジェクト: $PROJECT_ID"
echo "  リージョン:   $REGION"
echo "  サービス:     $SERVICE_BACKEND"
echo ""

# --- Cloud Run サービスの削除 ---
if gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" &>/dev/null; then
  if confirm "Cloud Run サービス '$SERVICE_BACKEND' を削除しますか？"; then
    gcloud run services delete "$SERVICE_BACKEND" --region "$REGION" --quiet
    echo "  Cloud Run サービスを削除しました。"
  else
    echo "  Cloud Run の削除をスキップしました。"
  fi
else
  echo "  Cloud Run サービス '$SERVICE_BACKEND' は存在しません。スキップします。"
fi

# --- Terraform リソースの削除（オプション）---
if [[ "$do_terraform" == true ]]; then
  echo ""
  if confirm "Terraform で作成したリソース（Artifact Registry 等）も削除しますか？"; then
    cd "$SCRIPT_DIR/terraform"
    if [[ "$skip_confirm" == true ]]; then
      terraform destroy -auto-approve
    else
      terraform destroy
    fi
    echo "  Terraform リソースを削除しました。"
  else
    echo "  Terraform の削除をスキップしました。"
  fi
fi

echo ""
echo "=== 停止処理完了 ==="
echo "  確認: Cloud Run https://console.cloud.google.com/run?project=$PROJECT_ID"
echo "  請求: https://console.cloud.google.com/billing"
