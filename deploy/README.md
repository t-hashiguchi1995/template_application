# GCP Cloud Run デプロイ

このディレクトリは、このアプリを GCP Cloud Run にデプロイするためのスクリプトと Terraform を格納しています。

## 前提

- リポジトリルートに `.env` を用意する（`PROJECT_ID`、`GEMINI_API_KEY` または `GOOGLE_API_KEY` など）
- `gcloud` CLI がインストール済みで、対象プロジェクトにログイン済みであること

## 手順

### 1. Terraform でインフラを用意（初回または変更時）

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars   # 必要に応じて編集
terraform init
terraform plan
terraform apply
```

これで以下が作成されます。

- 必要な GCP API の有効化（Cloud Run, Cloud Build, Artifact Registry, IAM Credentials, Storage 等）
- Artifact Registry の Docker リポジトリ
- **オプション** `terraform.tfvars` で `cloud_run_sa_id` と `gcs_bucket_name` を指定した場合:
  - Cloud Run 用サービスアカウント
  - GCS バケット（CORS 設定済み）
  - 上記 SA への Storage 権限・Token Creator 権限（Signed URL 用）

### 2. リポジトリルートで .env を設定

```bash
# リポジトリルートの .env 例
PROJECT_ID=your-gcp-project-id
REGION=asia-northeast1
REPO=app-repo
SERVICE_BACKEND=my-app-backend

GEMINI_API_KEY=your-gemini-api-key
# または GOOGLE_API_KEY=...

# Terraform で SA と GCS を作成した場合（任意）
# CLOUD_RUN_SA_ID=pdf-redacted
# または CLOUD_RUN_SERVICE_ACCOUNT=pdf-redacted@PROJECT_ID.iam.gserviceaccount.com
# GCS_BUCKET=pdf-redacted-your-gcp-project-id
```

- `REPO` は Terraform の `artifact_registry_repo` と同一にしてください（デフォルトは `app-repo`）。
- GCS と専用 SA を使う場合は、Terraform で `cloud_run_sa_id` / `gcs_bucket_name` を設定し、`.env` に `CLOUD_RUN_SA_ID`（または `CLOUD_RUN_SERVICE_ACCOUNT`）と `GCS_BUCKET` を設定してください。

### 3. デプロイ実行

```bash
# リポジトリルートから実行
./deploy/deploy_cloudrun.sh
```

- `.env` を読み込み、バックエンドをビルドして Cloud Run にデプロイします。
- サービスはデフォルトで非公開です。ローカルから確認する例:
  `gcloud run services proxy my-app-backend --region asia-northeast1 --port 8080`

## 構成

- `deploy_cloudrun.sh` … .env を読み込み、Cloud Build でビルドし Cloud Run にデプロイするスクリプト
- `terraform/` … GCP の API 有効化と Artifact Registry を管理する Terraform
