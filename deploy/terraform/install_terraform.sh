#!/usr/bin/env bash
# Terraform 公式リポジトリを使ったインストール（Debian / Ubuntu / WSL2 想定）
# APT が他リポジトリのエラーで失敗する場合は公式バイナリでフォールバック
# 実行: ./deploy/terraform/install_terraform.sh  または  cd deploy/terraform && ./install_terraform.sh
set -euo pipefail

# 公式バイナリでインストール（APT が使えない場合のフォールバック）
install_linux_binary() {
  if ! command -v unzip &>/dev/null; then
    echo "unzip をインストールしています..."
    sudo apt-get update -qq 2>/dev/null || true
    sudo apt-get install -y -qq unzip 2>/dev/null || true
    if ! command -v unzip &>/dev/null; then
      echo "unzip が必要です。手動で apt-get install unzip を実行してください。"
      return 1
    fi
  fi

  local arch
  case "$(uname -m)" in
    x86_64|amd64) arch="amd64" ;;
    aarch64|arm64) arch="arm64" ;;
    *) echo "未対応のアーキテクチャ: $(uname -m)"; return 1 ;;
  esac

  local version="${TERRAFORM_VERSION:-1.9.6}"
  local url="https://releases.hashicorp.com/terraform/${version}/terraform_${version}_linux_${arch}.zip"
  local tmpdir
  tmpdir="$(mktemp -d)"

  echo "公式バイナリでインストールしています（${version}, linux_${arch}）..."
  if ! wget -q --show-progress -O "$tmpdir/terraform.zip" "$url"; then
    echo "ダウンロードに失敗しました: $url"
    rm -rf "$tmpdir"
    return 1
  fi
  unzip -q -o "$tmpdir/terraform.zip" -d "$tmpdir"
  sudo mv "$tmpdir/terraform" /usr/local/bin/terraform
  sudo chmod +x /usr/local/bin/terraform
  rm -rf "$tmpdir"
}

install_linux_apt() {
  if ! command -v lsb_release &>/dev/null; then
    echo "lsb_release が見つかりません。"
    return 1
  fi

  local dist
  dist="$(lsb_release -cs 2>/dev/null)"
  if [[ -z "$dist" ]]; then
    echo "ディストリビューションを検出できませんでした。"
    return 1
  fi

  echo "HashiCorp 公式 APT リポジトリを追加しています..."
  sudo apt-get update -qq 2>/dev/null || true
  sudo apt-get install -y -qq gpg wget ca-certificates unzip 2>/dev/null || true

  wget -qO- https://apt.releases.hashicorp.com/gpg |
    sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $dist main" |
    sudo tee /etc/apt/sources.list.d/hashicorp.list >/dev/null

  echo "Terraform をインストールしています（APT）..."
  # 他リポジトリ（例: Chrome）の GPG エラーで update が失敗することがあるため、続行を許容
  sudo apt-get update -qq 2>/dev/null || true
  if sudo apt-get install -y -qq terraform 2>/dev/null; then
    return 0
  fi
  echo "APT からインストールできませんでした（他リポジトリのエラーが原因の可能性）。公式バイナリで試します。"
  return 1
}

check_version() {
  if ! command -v terraform &>/dev/null; then
    echo "Terraform がインストールされていません。"
    return 1
  fi
  local ver
  ver=$(terraform version -json 2>/dev/null | sed -n 's/.*"terraform_version":"\([^"]*\)".*/\1/p' || terraform version | head -1)
  echo "インストール済み: terraform $ver"
  return 0
}

main() {
  if command -v terraform &>/dev/null; then
    if terraform version -json &>/dev/null; then
      local v
      v=$(terraform version -json | sed -n 's/.*"terraform_version":"\([^"]*\)".*/\1/p')
      if [[ -n "$v" ]]; then
        echo "Terraform は既にインストールされています: $v"
        terraform version
        exit 0
      fi
    fi
    echo "Terraform は既にインストールされています: $(terraform version | head -1)"
    exit 0
  fi

  case "$(uname -s)" in
    Linux)
      if [[ -f /etc/debian_version ]] || grep -qEi "ubuntu|debian" /etc/os-release 2>/dev/null; then
        if ! install_linux_apt; then
          install_linux_binary
        fi
        check_version
        echo ""
        echo "次のステップ: cd deploy/terraform && cp terraform.tfvars.example terraform.tfvars && terraform init && terraform apply"
      else
        echo "このスクリプトは Debian/Ubuntu（および WSL2 上のそれら）向けです。"
        echo "他の Linux では https://developer.hashicorp.com/terraform/install を参照してください。"
        exit 1
      fi
      ;;
    Darwin)
      echo "macOS の場合は Homebrew でインストールしてください:"
      echo "  brew install terraform"
      exit 1
      ;;
    *)
      echo "未対応の OS です。公式ドキュメントを参照してください:"
      echo "  https://developer.hashicorp.com/terraform/install"
      exit 1
      ;;
  esac
}

main "$@"
