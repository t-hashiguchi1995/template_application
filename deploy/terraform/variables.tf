# GCP Cloud Run デプロイ用 Terraform 変数
# 値は .tfvars または環境変数 TF_VAR_* で指定

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "region" {
  description = "デプロイ先リージョン（Cloud Run / Artifact Registry）"
  type        = string
  default     = "asia-northeast1"
}

variable "artifact_registry_repo" {
  description = "Artifact Registry のリポジトリ名"
  type        = string
  default     = "app-repo"
}

variable "enable_apis" {
  description = "有効化する GCP API の一覧"
  type        = list(string)
  default = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "storage.googleapis.com",
    "storage-api.googleapis.com"
  ]
}

# --- Cloud Run 用サービスアカウント・GCS（任意）---
variable "cloud_run_sa_id" {
  description = "Cloud Run が使用するサービスアカウントの ID（空の場合はデフォルト SA）。"
  type        = string
  default     = ""
}

variable "gcs_bucket_name" {
  description = "Cloud Run から利用する GCS バケット名（空の場合は作成しない）。"
  type        = string
  default     = ""
}
