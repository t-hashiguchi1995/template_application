output "project_id" {
  description = "GCP プロジェクト ID"
  value       = var.project_id
}

output "region" {
  description = "リージョン"
  value       = var.region
}

output "artifact_registry_repo" {
  description = "Artifact Registry リポジトリ名"
  value       = google_artifact_registry_repository.app_repo.name
}

output "artifact_registry_location" {
  description = "イメージのフルパス（例: asia-northeast1-docker.pkg.dev/PROJECT/REPO）"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}"
}

output "cloud_run_service_account_email" {
  description = "Cloud Run 用サービスアカウントのメール（cloud_run_sa_id を設定した場合のみ）"
  value       = var.cloud_run_sa_id != "" ? google_service_account.cloud_run[0].email : null
}

output "gcs_bucket_name" {
  description = "作成した GCS バケット名（gcs_bucket_name を設定した場合のみ）"
  value       = var.gcs_bucket_name != "" ? google_storage_bucket.app[0].name : null
}
