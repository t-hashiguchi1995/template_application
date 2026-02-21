# GCP プロジェクトで Cloud Run デプロイに必要な API と Artifact Registry を用意する
# デプロイ本体は deploy/deploy_cloudrun.sh で実行

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 必要な API の有効化
resource "google_project_service" "apis" {
  for_each = toset(var.enable_apis)
  project  = var.project_id
  service  = each.value
  # 無効化時の destroy で API を無効にしない（他サービスで利用中の可能性）
  disable_on_destroy = false
}

# Artifact Registry（Docker イメージ用）
resource "google_artifact_registry_repository" "app_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Cloud Run 用 Docker イメージ"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}

# --- オプション: Cloud Run 用サービスアカウント ---
resource "google_service_account" "cloud_run" {
  count        = var.cloud_run_sa_id != "" ? 1 : 0
  project      = var.project_id
  account_id   = var.cloud_run_sa_id
  display_name = "Cloud Run 用サービスアカウント"
  description  = "Cloud Run がこの ID で GCS 等にアクセスする"
}

# --- オプション: GCS バケット（CORS 付き）---
resource "google_storage_bucket" "app" {
  count         = var.gcs_bucket_name != "" ? 1 : 0
  project       = var.project_id
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = false

  # ブラウザからの直接 PUT 用 CORS
  cors {
    origin          = ["*"]
    method          = ["GET", "PUT", "POST", "OPTIONS"]
    response_header = ["Content-Type", "Content-Length", "x-goog-resumable"]
    max_age_seconds = 3600
  }
}

# SA にバケットの Storage 権限を付与（SA とバケットの両方がある場合）
resource "google_storage_bucket_iam_member" "sa_object_admin" {
  count  = var.cloud_run_sa_id != "" && var.gcs_bucket_name != "" ? 1 : 0
  bucket = google_storage_bucket.app[0].name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run[0].email}"
}

# Signed URL 生成用: SA に Token Creator を付与（自分用）
resource "google_project_iam_member" "sa_token_creator" {
  count   = var.cloud_run_sa_id != "" ? 1 : 0
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.cloud_run[0].email}"
}
