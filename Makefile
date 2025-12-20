.PHONY: help build up down logs clean dev-build dev-up dev-down dev-restart dev-rebuild

help: ## このヘルプメッセージを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Dockerイメージをビルド（本番用）
	docker-compose build

up: ## コンテナを起動（本番用）
	docker-compose up -d

up-logs: ## コンテナを起動してログを表示（本番用）
	docker-compose up

down: ## コンテナを停止
	docker-compose down

logs: ## ログを表示
	docker-compose logs -f

logs-backend: ## バックエンドのログを表示
	docker-compose logs -f backend

logs-frontend: ## フロントエンドのログを表示
	docker-compose logs -f frontend

restart: ## コンテナを再起動（本番用）
	docker-compose restart

clean: ## コンテナとイメージを削除
	docker-compose down -v --rmi all

rebuild: ## コンテナを再ビルドして起動（本番用）
	docker-compose up --build -d

# 開発環境用コマンド
dev-build: ## 開発環境のDockerイメージをビルド
	docker-compose -f docker-compose.dev.yml build

dev-up: ## 開発環境のコンテナを起動（ホットリロード有効）
	docker-compose -f docker-compose.dev.yml up -d

dev-up-logs: ## 開発環境のコンテナを起動してログを表示
	docker-compose -f docker-compose.dev.yml up

dev-down: ## 開発環境のコンテナを停止
	docker-compose -f docker-compose.dev.yml down

dev-restart: ## 開発環境のコンテナを再起動
	docker-compose -f docker-compose.dev.yml restart

dev-rebuild: ## 開発環境のコンテナを再ビルドして起動（コード変更を反映）
	docker-compose -f docker-compose.dev.yml up --build -d

dev-logs: ## 開発環境のログを表示
	docker-compose -f docker-compose.dev.yml logs -f

dev-logs-backend: ## 開発環境のバックエンドのログを表示
	docker-compose -f docker-compose.dev.yml logs -f backend

dev-logs-frontend: ## 開発環境のフロントエンドのログを表示
	docker-compose -f docker-compose.dev.yml logs -f frontend

