# フロントエンド用Dockerfile（マルチステージビルド）

# ビルドステージ
FROM node:20-alpine AS builder

WORKDIR /app

# 依存関係ファイルをコピー
COPY package.json package-lock.json* ./

# 依存関係をインストール
# package-lock.jsonが存在する場合はnpm ci、存在しない場合はnpm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# ソースコードをコピー
COPY . .

# アプリケーションをビルド
# ビルド時に環境変数を設定（ARGで受け取り、ENVで設定）
ARG VITE_API_URL=http://localhost:8800
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# 本番ステージ
FROM node:20-alpine

# wgetをインストール（ヘルスチェック用）
RUN apk add --no-cache wget

WORKDIR /app

# ビルド成果物をコピー
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

# ポートを公開
EXPOSE 5173

# プレビューサーバーを起動
# プロキシ設定はvite.config.tsのpreview.proxyで設定
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]

