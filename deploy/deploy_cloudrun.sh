#!/usr/bin/env bash
# GCP Cloud Run デプロイスクリプト（このリポジトリ構成用）
# 実行: リポジトリルートで ./deploy/deploy_cloudrun.sh
# 事前に Terraform でインフラを用意しておく: cd deploy/terraform && terraform init && terraform apply
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ---- .env 読み込み ----
if [[ -f ".env" ]]; then
  set -a
  # shellcheck source=../.env
  . ./.env
  set +a
fi

# APIキー（バックエンド用）
: "${GEMINI_API_KEY:=${GOOGLE_API_KEY:-}}"
: "${GEMINI_API_KEY:? .env に GEMINI_API_KEY=... または GOOGLE_API_KEY=... を設定してください}"

# ---- 設定（.env で上書き可）----
PROJECT_ID="${PROJECT_ID:? .env に PROJECT_ID=... を設定してください}"
REGION="${REGION:-asia-northeast1}"
REPO="${REPO:-app-repo}"
SERVICE_BACKEND="${SERVICE_BACKEND:-my-app-backend}"

# オプション: Terraform で作成した SA と GCS を使う場合
# CLOUD_RUN_SERVICE_ACCOUNT=template-app-sa@PROJECT_ID.iam.gserviceaccount.com または
# CLOUD_RUN_SA_ID=template-app-sa で SA のみ指定可能
CLOUD_RUN_SERVICE_ACCOUNT="${CLOUD_RUN_SERVICE_ACCOUNT:-}"
CLOUD_RUN_SA_ID="${CLOUD_RUN_SA_ID:-}"
GCS_BUCKET="${GCS_BUCKET:-}"
# SA を ID だけで指定した場合はメール形式に変換
if [[ -n "$CLOUD_RUN_SA_ID" && -z "$CLOUD_RUN_SERVICE_ACCOUNT" ]]; then
  CLOUD_RUN_SERVICE_ACCOUNT="${CLOUD_RUN_SA_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
fi

export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Terraform で有効化済み想定（未適用の場合は deploy/terraform を先に apply）
# 必要ならここで API 有効化も可能:
# gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --quiet

IMAGE_BACKEND="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend"
TAG="$(date +%Y%m%d%H%M%S)-${RANDOM}"
FULL_IMAGE="${IMAGE_BACKEND}:${TAG}"

# ---- バックエンドビルド（ルートを context、backend/Dockerfile を指定）----
echo "Building backend image: $FULL_IMAGE"
cat > /tmp/cloudbuild-backend.yaml <<YAML
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-t', '${FULL_IMAGE}', '-f', 'backend/Dockerfile', '.']
images:
- '${FULL_IMAGE}'
YAML

gcloud builds submit \
  --config /tmp/cloudbuild-backend.yaml \
  .

# ---- Cloud Run デプロイ（非公開）----
BACKEND_ENV_FILE="/tmp/run-env-backend.yaml"
# GCS を使う場合は GCS_BUCKET を .env に設定（Terraform の gcs_bucket_name と一致させる）
{
  echo "GEMINI_API_KEY: \"${GEMINI_API_KEY}\""
  echo "GOOGLE_API_KEY: \"${GOOGLE_API_KEY:-}\""
  echo "GOOGLE_GENAI_USE_VERTEXAI: \"${GOOGLE_GENAI_USE_VERTEXAI:-0}\""
  echo "GOOGLE_CLOUD_PROJECT: \"${PROJECT_ID}\""
  [[ -n "${GCS_BUCKET}" ]] && echo "GCS_BUCKET: \"${GCS_BUCKET}\""
} > "$BACKEND_ENV_FILE"

# 過去に allUsers で公開していた場合は外す（失敗しても続行）
gcloud run services remove-iam-policy-binding "$SERVICE_BACKEND" \
  --region "$REGION" \
  --member="allUsers" \
  --role="roles/run.invoker" 2>/dev/null || true

DEPLOY_ARGS=(
  --image "$FULL_IMAGE"
  --region "$REGION"
  --no-allow-unauthenticated
  --env-vars-file "$BACKEND_ENV_FILE"
  --execution-environment gen2
  --cpu 1
  --memory 2Gi
  --timeout 300
  --max-instances 3
  --concurrency 20
)
[[ -n "${CLOUD_RUN_SERVICE_ACCOUNT}" ]] && DEPLOY_ARGS+=(--service-account "${CLOUD_RUN_SERVICE_ACCOUNT}")

gcloud run deploy "$SERVICE_BACKEND" "${DEPLOY_ARGS[@]}"

BACKEND_URL=$(gcloud run services describe "$SERVICE_BACKEND" --region "$REGION" --format='value(status.url)')
echo ""
echo "Backend URL: $BACKEND_URL"
echo "（非公開のため）ローカルからプロキシ: gcloud run services proxy $SERVICE_BACKEND --region $REGION --port 8080"
