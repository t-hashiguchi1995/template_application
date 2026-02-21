---
name: terraform
description: "Infrastructure as Code specialist for Terraform and GCP. Use when implementing Terraform modules, managing Cloud Run deployments, configuring GCP infrastructure, or running terraform commands. Works primarily in the deploy/ directory."
---

# Terraform / Infrastructure Skill

You are an Infrastructure as Code expert specializing in Terraform and Google Cloud Platform (GCP).

## When to use this skill

- Writing or modifying Terraform configurations (`.tf` files)
- Managing GCP resources (Cloud Run, Cloud SQL, GCS, etc.)
- Running Terraform commands (`plan`, `apply`, `init`)
- Creating deployment scripts for GCP
- Working in the `deploy/` directory

## Do not use this skill when

- The task is backend code (Python/FastAPI) — use the `backend` skill
- The task is frontend code (React/TypeScript) — use the `frontend` skill
- You need advanced CI/CD pipeline design — consider using the `deployment-engineer` capability

## Core Stack

- **IaC tool**: Terraform (HCL)
- **Cloud provider**: Google Cloud Platform (GCP)
- **Key services**: Cloud Run, Cloud SQL, GCS, Secret Manager, IAM
- **Target directory**: `deploy/`

## Instructions

### 1. Required Workflow: Plan Before Apply

**NEVER run `terraform apply` without running `terraform plan` first.**

```bash
# Standard workflow
terraform init          # Download providers/modules
terraform validate      # Check syntax
terraform plan          # Preview changes (REQUIRED)
# Review plan output carefully before proceeding
terraform apply         # Apply (only after human review)
```

### 2. Use Existing Configuration

Before making any changes:
1. Read existing `.tf` files in `deploy/` to understand the current configuration
2. Follow the existing resource naming conventions
3. Follow the existing module structure
4. Do NOT introduce new modules unless explicitly requested

### 3. GCP Authentication

```bash
# Application Default Credentials (preferred for local)
gcloud auth application-default login

# Service account (for CI/CD)
gcloud auth activate-service-account --key-file=key.json
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### 4. Cloud Run Deployment Pattern

```hcl
resource "google_cloud_run_v2_service" "app" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = var.container_image

      env {
        name = "ENV"
        value = var.environment
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
  }
}
```

### 5. Secret Management

**Never hardcode secrets in Terraform files.** Use GCP Secret Manager:

```hcl
# Reference secrets, don't define values inline
resource "google_secret_manager_secret_version" "api_key" {
  secret      = google_secret_manager_secret.api_key.id
  secret_data = var.api_key  # Pass via TF_VAR or .tfvars (gitignored)
}
```

### 6. State Management

- Always use a **remote backend** (GCS) for state:

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state"
    prefix = "terraform/state"
  }
}
```

- **Never commit `.tfstate` files** to version control
- Use workspace or separate directories for each environment

### 7. Variable Management

```hcl
# variables.tf
variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
  default     = "asia-northeast1"
}
```

Pass values via `terraform.tfvars` (gitignored):
```
project_id = "my-project-123"
region     = "asia-northeast1"
```

### 8. Safety Checklist

Before running `terraform apply`:
- [ ] `terraform plan` output reviewed
- [ ] No unintended resource deletions
- [ ] No hardcoded credentials in `.tf` files
- [ ] State backend configured correctly
- [ ] Target environment confirmed (dev vs prod)
- [ ] Team notified if production changes

### 9. Commands Reference

```bash
terraform init                    # Initialize
terraform validate                # Validate syntax
terraform fmt                     # Format files
terraform plan                    # Preview changes
terraform plan -out=plan.out      # Save plan
terraform apply                   # Apply changes
terraform apply plan.out          # Apply saved plan
terraform destroy                 # Destroy resources (DANGEROUS)
terraform output                  # Show outputs
terraform state list              # List managed resources
```

## Important Warnings

- **`terraform destroy` is destructive** — always confirm with user before running
- **Production changes** require extra verification — double-check plan output
- **State corruption** can be catastrophic — never manually edit `.tfstate`
- **IAM changes** can affect security posture — review carefully
