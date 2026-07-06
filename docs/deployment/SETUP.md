# Elder Company - Setup Guide

> **About this document**: Detailed installation and configuration instructions.

**Last updated**: 2026-01-20

---

## Table of Contents

- [Quick Start](#quick-start)
- [Backend Setup](#1-backend-setup)
- [Frontend Setup](#2-frontend-setup)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Supported Languages](#supported-languages)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Backend Setup

```bash
cd elder_company/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example ../do-not-upload/env/.env
# Or: cp env.example .env (legacy)
```

For first-time local setup, run from the repo root:

```bash
./scripts/setup_local_dirs.sh
```

See [do-not-upload/README.md](../../do-not-upload/README.md) for local data layout.

### 2. Configure API Keys

Edit `do-not-upload/env/.env` (or `backend/.env`) and add your API keys:

```env
# Choose AI provider (openai, claude, gemini)
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Google (Gemini)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-pro

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server port
PORT=8000
```

**Important**: Configure at least one AI provider API key.

### 3. Start the Backend

```bash
# From backend/
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### 4. Frontend Setup

```bash
cd elder_company/frontend

npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Configuration

Environment templates live in `backend/env.example`. Secrets and local overrides belong in `do-not-upload/env/.env`.

---

## API Endpoints

### Translation

**POST** `/api/translate`

Request:

```json
{
  "text": "こんにちは",
  "source_language": "ja",
  "target_language": "en",
  "context": "caregiving scenario"
}
```

Response:

```json
{
  "original_text": "こんにちは",
  "translated_text": "Hello",
  "source_language": "ja",
  "target_language": "en",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Chat Translation

**POST** `/api/chat`

Request:

```json
{
  "message": "おはようございます",
  "source_language": "ja",
  "target_language": "en",
  "conversation_id": "optional-id"
}
```

### Health Check

- **GET** `/health`
- **GET** `/api/ai/provider` — Current AI provider info

---

## Supported Languages

- `ja` — Japanese
- `en` — English
- `ko` — Korean

---

## Troubleshooting

### Backend won't start

1. Verify `.env` exists and is configured correctly
2. Confirm API keys are valid
3. Check whether port 8000 is already in use

### Translation fails

1. Verify API keys
2. Check network connectivity
3. Review backend logs in `do-not-upload/logs/`
4. Confirm the selected AI provider is available

### Frontend can't reach backend

1. Confirm the backend is running
2. Check proxy settings in `vite.config.js`
3. Verify CORS configuration

---

## Development Tips

- Start the backend with `--reload` for hot reload
- Frontend uses Vite HMR
- Check the browser console and backend terminal for errors
- Run tests from the repo root: see [tests/README.md](../../tests/README.md)

---

# Elder Company - セットアップガイド

> **本ドキュメントについて**: 詳細なインストールと設定手順を提供します。

**最終更新**: 2026-01-20

---

## 目次

- [クイックスタート](#クイックスタート)
- [バックエンド設定](#1-バックエンド設定)
- [フロントエンド設定](#2-フロントエンド設定)
- [設定](#設定)
- [API エンドポイント](#api-エンドポイント)
- [対応言語](#対応言語)
- [トラブルシューティング](#トラブルシューティング)

---

## クイックスタート

### 1. バックエンド設定

```bash
cd elder_company/backend

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp env.example ../do-not-upload/env/.env
# または: cp env.example .env（レガシー）
```

初回ローカルセットアップはリポジトリルートから:

```bash
./scripts/setup_local_dirs.sh
```

ローカルデータ構成は [do-not-upload/README.md](../../do-not-upload/README.md) を参照。

### 2. API キーの設定

`do-not-upload/env/.env`（または `backend/.env`）を編集し、API キーを追加:

```env
# AI プロバイダーを選択 (openai, claude, gemini)
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4  # または gpt-3.5-turbo

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Google (Gemini)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-pro

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# サーバーポート
PORT=8000
```

**重要**: 少なくとも 1 つの AI プロバイダー API キーを設定してください。

### 3. バックエンドの起動

```bash
# backend/ から
uvicorn main:app --reload
```

バックエンドは `http://localhost:8000` で起動します。

### 4. フロントエンド設定

```bash
cd elder_company/frontend

npm install
npm run dev
```

フロントエンドは `http://localhost:3000` で起動します。

---

## 設定

環境変数テンプレートは `backend/env.example` にあります。秘密情報とローカル上書きは `do-not-upload/env/.env` に配置してください。

---

## API エンドポイント

### 翻訳

**POST** `/api/translate`

リクエスト:

```json
{
  "text": "こんにちは",
  "source_language": "ja",
  "target_language": "en",
  "context": "介護シーン"
}
```

レスポンス:

```json
{
  "original_text": "こんにちは",
  "translated_text": "Hello",
  "source_language": "ja",
  "target_language": "en",
  "timestamp": "2024-01-01T00:00:00"
}
```

### チャット翻訳

**POST** `/api/chat`

リクエスト:

```json
{
  "message": "おはようございます",
  "source_language": "ja",
  "target_language": "en",
  "conversation_id": "optional-id"
}
```

### ヘルスチェック

- **GET** `/health`
- **GET** `/api/ai/provider` — 現在の AI プロバイダー情報

---

## 対応言語

- `ja` — 日本語
- `en` — 英語
- `ko` — 韓国語

---

## トラブルシューティング

### バックエンドが起動しない

1. `.env` が存在し、正しく設定されているか確認
2. API キーが有効か確認
3. ポート 8000 が使用中でないか確認

### 翻訳が失敗する

1. API キーを確認
2. ネットワーク接続を確認
3. `do-not-upload/logs/` のバックエンドログを確認
4. 選択した AI プロバイダーが利用可能か確認

### フロントエンドがバックエンドに接続できない

1. バックエンドが起動しているか確認
2. `vite.config.js` のプロキシ設定を確認
3. CORS 設定を確認

---

## 開発のヒント

- バックエンドは `--reload` でホットリロード
- フロントエンドは Vite HMR を使用
- ブラウザコンソールとバックエンドターミナルでエラーを確認
- テストはリポジトリルートから実行: [tests/README.md](../../tests/README.md) を参照
