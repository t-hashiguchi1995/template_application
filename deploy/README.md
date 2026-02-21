# GCP Cloud Run デプロイ

このディレクトリは、このアプリを GCP Cloud Run にデプロイするためのスクリプトと Terraform を格納しています。

## 前提

- リポジトリルートに `.env` を用意する（`PROJECT_ID`、`GEMINI_API_KEY` または `GOOGLE_API_KEY` など）
- `gcloud` CLI がインストール済みであること
- **GCP プロジェクトに請求（ビリング）がリンクされていること**  
  Cloud Run / Artifact Registry / Cloud Build は、無料枠利用でも「請求を有効にする」必要があります。  
  [コンソール → お支払い](https://console.cloud.google.com/billing) でプロジェクトに請求アカウントをリンクしてください。未リンクだと `Billing account for project ... is not found` で Terraform が失敗します。

### 認証とプロジェクトの指定（Terraform / デプロイ前に行う）

Terraform や `deploy_cloudrun.sh` は **Application Default Credentials (ADC)** を使います。未設定だと `No credentials loaded` になります。

1. **ログイン（ブラウザが開きます）**
   ```bash
   gcloud auth application-default login
   ```
2. **利用するプロジェクトを指定**
   ```bash
   gcloud config set project your-gcp-project-id
   ```
3. **Terraform の `terraform.tfvars` で同じプロジェクト ID を指定**
   - `project_id = "your-gcp-project-id"` のように設定

**ログイン状態の確認**

| 確認項目 | コマンド | 期待する結果 |
|----------|----------|--------------|
| gcloud でログイン済みか | `gcloud auth list` | アクティブなアカウント（`*`）が表示される |
| デフォルトプロジェクト | `gcloud config get-value project` | 使うプロジェクト ID（例: your-gcp-project-id） |
| Terraform 用 ADC | `gcloud auth application-default print-access-token` | トークンが表示される（長い文字列） |

ADC が未設定のときは `ERROR: Your default credentials were not found` と出ます。その場合はもう一度 `gcloud auth application-default login` を実行してください。

## 手順

### 0. Terraform のインストール（未導入の場合）

Terraform がまだ入っていない場合は、以下いずれかで導入してください。

#### Linux（Debian / Ubuntu / WSL2）

**方法 A: リポジトリ内スクリプト（推奨）**

```bash
# リポジトリルートから
./deploy/terraform/install_terraform.sh
```

公式 HashiCorp APT リポジトリを追加し、`terraform` をインストールします。既にインストール済みの場合は何もしません。

**方法 B: 手動（apt）**

```bash
# 必要なツール
sudo apt-get update && sudo apt-get install -y gpg wget

# HashiCorp の GPG キーとリポジトリ追加（Ubuntu 22.04 の例）
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt-get update && sudo apt-get install -y terraform
terraform version
```

#### macOS

```bash
brew install terraform
terraform version
```

#### Windows

- [Terraform 公式ダウンロード](https://developer.hashicorp.com/terraform/install) から Windows 用バイナリを取得するか、Chocolatey で `choco install terraform` を実行してください。
- WSL2 を使っている場合は、上記「Linux」手順を WSL 内で実行しても構いません。

#### 動作確認

```bash
terraform version
# Terraform v1.x.x 以上が表示されれば OK
```

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
# CLOUD_RUN_SA_ID=template-app-sa
# または CLOUD_RUN_SERVICE_ACCOUNT=template-app-sa@PROJECT_ID.iam.gserviceaccount.com
# GCS_BUCKET=template-app-your-gcp-project-id
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

## 動作確認（テスト実行）

プロジェクトとリージョンは `.env` の `PROJECT_ID` / `REGION` に合わせてください。サービス名は `SERVICE_BACKEND` の値（デフォルト `my-app-backend`）です。

### 1. URL の確認

```bash
gcloud run services describe my-app-backend --region asia-northeast1 --format='value(status.url)'
```

### 2. ローカルからプロキシでブラウザアクセス（非公開のまま）

```bash
gcloud run services proxy my-app-backend --region asia-northeast1 --port 8080
```

ブラウザで http://localhost:8080 を開く。例: http://localhost:8080/health （ヘルスチェック）、http://localhost:8080/docs （API ドキュメント）。

### 3. ヘルスチェック（curl）

プロキシを別ターミナルで起動した状態で:

```bash
curl -s http://localhost:8080/health
# 期待: {"status":"healthy"}
```

または、認証付きで直接 Cloud Run URL にアクセス:

```bash
URL=$(gcloud run services describe my-app-backend --region asia-northeast1 --format='value(status.url)')
TOKEN=$(gcloud auth print-identity-token)
curl -s -H "Authorization: Bearer $TOKEN" "$URL/health"
```

---

## リソースの停止

### Cloud Run サービスの削除（デプロイしたアプリのみ停止）

請求を止めたい場合は、Cloud Run サービスを削除します。最小インスタンス 0 のためトラフィックがなければ課金はほぼ発生しませんが、削除すれば完全に停止できます。

```bash
gcloud config set project your-gcp-project-id   # 必要に応じてプロジェクト ID に変更
gcloud run services delete my-app-backend --region asia-northeast1
# 確認プロンプトで y
```

### Terraform で作成したリソースの削除（API 有効化・Artifact Registry 等）

Artifact Registry のリポジトリや、Terraform で管理しているリソースをまとめて削除する場合:

```bash
cd deploy/terraform
terraform destroy
# 確認で yes
```

- **注意**: `terraform destroy` は API の「無効化」は行いません（`disable_on_destroy = false` のため）。Artifact Registry リポジトリなどは削除されます。Cloud Run サービスは Terraform で作っていないため、上記の `gcloud run services delete` で別途削除してください。

### 作業後の確認

- Cloud Run: [コンソール → Cloud Run](https://console.cloud.google.com/run) でサービス一覧を確認
- 請求: [お支払い](https://console.cloud.google.com/billing) で利用状況を確認

## 実行・テスト／停止のまとめスクリプト

| スクリプト | 内容 |
|------------|------|
| **`run_and_test.sh`** | 動作確認（URL 表示・ヘルスチェック）。`--deploy` を付けるとデプロイしてからテスト。 |
| **`stop.sh`** | Cloud Run サービスの削除。`--terraform` で Terraform リソースも削除。`--yes` で確認スキップ。 |

```bash
# テストのみ（デプロイ済みが前提）
./deploy/run_and_test.sh

# デプロイしてからテスト
./deploy/run_and_test.sh --deploy

# Cloud Run だけ停止
./deploy/stop.sh

# Cloud Run + Terraform リソースを停止
./deploy/stop.sh --terraform
```

## 構成

- `deploy_cloudrun.sh` … .env を読み込み、Cloud Build でビルドし Cloud Run にデプロイするスクリプト
- `run_and_test.sh` … デプロイ＋動作確認を一括実行（`--deploy` でデプロイを含む）
- `stop.sh` … Cloud Run 削除、オプションで Terraform destroy
- `terraform/` … GCP の API 有効化と Artifact Registry を管理する Terraform
  - `install_terraform.sh` … Terraform 未導入時用のインストールスクリプト（Debian/Ubuntu/WSL2）
