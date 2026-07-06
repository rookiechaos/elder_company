# Elder Company - Project Structure

**Last updated**: 2026-01-20

## Project Directory Layout

```
elder_company/
├── README.md                    # Main project README
├── CHANGELOG.md                 # Version changelog
├── VISION.md                    # Product vision
├── DOCS_INDEX.md                # Documentation index
├── PROJECT_STRUCTURE.md         # This file
├── pytest.ini                   # pytest configuration (repo root)
│
├── services/                    # Business logic (repo root)
│   ├── auth_service.py
│   ├── task_service.py
│   ├── schedule_service.py
│   ├── emotion_service.py
│   ├── rag_service.py
│   ├── family_service.py
│   └── ...
│
├── tests/                       # Test suite (repo root)
│   ├── README.md
│   ├── conftest.py
│   ├── integration/
│   └── test_*.py
│
├── scripts/                     # Utility scripts (repo root)
│   ├── setup_local_dirs.sh
│   ├── run_test_in_chatbot.sh
│   ├── migrate_v1_to_v2.py
│   └── ...
│
├── do-not-upload/               # Local-only data (not committed)
│   ├── README.md
│   ├── env/.env                 # Secrets and local config
│   ├── data/                    # SQLite database
│   ├── logs/                    # Application logs
│   ├── storage/                 # Uploaded media
│   └── cache/                   # Generated caches
│
├── backend/                     # Backend application code
│   ├── README.md
│   ├── main.py                  # FastAPI entry point
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── env.example
│   │
│   ├── api/                     # API routes
│   │   ├── auth_routes.py
│   │   ├── task_routes.py
│   │   ├── schedule_routes.py
│   │   └── ...
│   │
│   ├── models/                  # Data models
│   │   ├── database.py
│   │   └── ...
│   │
│   ├── config/                  # Configuration
│   │   ├── settings.py
│   │   └── database.py
│   │
│   ├── middleware/              # Middleware
│   │   ├── error_handler.py
│   │   ├── rate_limit.py
│   │   └── ...
│   │
│   └── utils/                   # Utilities
│       └── security.py
│
├── frontend/                    # Frontend application
│   ├── README.md
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── public/
│
├── game/                        # Game module
│   ├── README.md
│   ├── DESIGN.md
│   ├── GAME_SPECS.md
│   ├── SECURITY.md
│   ├── backend/
│   └── frontend/
│
└── docs/                        # Documentation (all markdown docs)
    ├── README.md
    ├── development/
    ├── features/
    ├── testing/
    ├── architecture/
    ├── api/
    ├── security/
    ├── deployment/
    ├── compliance/
    └── business/
```

## Directory Descriptions

### Application Code

- **services/** — Business logic at the repo root; imported by `backend/` routes
- **backend/** — FastAPI application: routes, models, middleware, config
- **frontend/** — React application code
- **game/** — Collaborative game module with its own backend and frontend

### Tests and Scripts

- **tests/** — pytest suite; run from the repo root (see `pytest.ini`)
- **scripts/** — Setup, migration, and test helper scripts

### Local Data

- **do-not-upload/** — Secrets, database, logs, uploads, and caches. See [do-not-upload/README.md](./do-not-upload/README.md). Not committed to version control.

### Documentation (`docs/`)

All development, testing, deployment, and compliance markdown docs are organized by category:

- **development/** — Plans, roadmaps, code improvements
- **features/** — Feature reports and product capabilities
- **testing/** — Testing guides and reports
- **architecture/** — Architecture, database, performance
- **api/** — API reference
- **security/** — Security audits and improvements
- **deployment/** — Setup and deployment guides
- **compliance/** — Product disclaimers and auth requirements
- **business/** — Business plans and presentations

### Root-Level Files

The repo root keeps only the most important entry points:

- `README.md` — Project overview
- `CHANGELOG.md` — Version history
- `VISION.md` — Product vision
- `DOCS_INDEX.md` — Full documentation index
- `PROJECT_STRUCTURE.md` — This file
- `pytest.ini` — Test configuration

## Design Principles

1. **Separate code and docs** — Application directories contain code; docs live in `docs/`
2. **Services at repo root** — Shared business logic in `services/`; API layer in `backend/`
3. **Local data isolated** — Machine-specific files in `do-not-upload/`, never committed
4. **Clear categories** — Documentation grouped by purpose for easy discovery
5. **Maintainable layout** — Structure supports growth without clutter

## Finding Documentation

- [DOCS_INDEX.md](./DOCS_INDEX.md) — Complete documentation index
- [docs/README.md](./docs/README.md) — Documentation hub with category details

---

**Structure reorganized**: 2026-01-20

---

# Elder Company - プロジェクト構成

**最終更新**: 2026-01-20

## プロジェクトディレクトリ構成

```
elder_company/
├── README.md                    # メインプロジェクト README
├── CHANGELOG.md                 # バージョン更新履歴
├── VISION.md                    # プロダクトビジョン
├── DOCS_INDEX.md                # ドキュメント索引
├── PROJECT_STRUCTURE.md         # 本ファイル
├── pytest.ini                   # pytest 設定（リポジトリルート）
│
├── services/                    # ビジネスロジック（リポジトリルート）
├── tests/                       # テストスイート（リポジトリルート）
├── scripts/                     # ユーティリティスクリプト（リポジトリルート）
├── do-not-upload/               # ローカル専用データ（コミット対象外）
├── backend/                     # バックエンドアプリケーション
├── frontend/                    # フロントエンドアプリケーション
├── game/                        # ゲームモジュール
└── docs/                        # ドキュメント（すべての markdown）
```

## ディレクトリ説明

### アプリケーションコード

- **services/** — リポジトリルートのビジネスロジック。`backend/` ルートから import
- **backend/** — FastAPI アプリケーション：ルート、モデル、ミドルウェア、設定
- **frontend/** — React アプリケーションコード
- **game/** — 協働ゲームモジュール（専用 backend / frontend）

### テストとスクリプト

- **tests/** — pytest スイート。リポジトリルートから実行（`pytest.ini` 参照）
- **scripts/** — セットアップ、マイグレーション、テスト補助スクリプト

### ローカルデータ

- **do-not-upload/** — 秘密情報、DB、ログ、アップロード、キャッシュ。[do-not-upload/README.md](./do-not-upload/README.md) を参照。バージョン管理対象外。

### ドキュメント（`docs/`）

開発、テスト、デプロイ、コンプライアンス関連の markdown をカテゴリ別に整理:

- **development/** — 計画、ロードマップ、コード改善
- **features/** — 機能レポートとプロダクト特性
- **testing/** — テストガイドとレポート
- **architecture/** — アーキテクチャ、DB、パフォーマンス
- **api/** — API リファレンス
- **security/** — セキュリティ監査と改善
- **deployment/** — セットアップとデプロイガイド
- **compliance/** — プロダクト免責事項と認証要件
- **business/** — 事業計画とプレゼン資料

### ルートレベルファイル

リポジトリルートには主要なエントリポイントのみを配置:

- `README.md` — プロジェクト概要
- `CHANGELOG.md` — バージョン履歴
- `VISION.md` — プロダクトビジョン
- `DOCS_INDEX.md` — ドキュメント完全索引
- `PROJECT_STRUCTURE.md` — 本ファイル
- `pytest.ini` — テスト設定

## 設計原則

1. **コードとドキュメントの分離** — アプリディレクトリはコード、`docs/` にドキュメント
2. **services をルートに配置** — 共有ビジネスロジックは `services/`、API 層は `backend/`
3. **ローカルデータの分離** — マシン固有ファイルは `do-not-upload/` に、コミットしない
4. **明確なカテゴリ分け** — 目的別にドキュメントを整理
5. **保守しやすい構成** — 拡張しても散らからない構造

## ドキュメントの探し方

- [DOCS_INDEX.md](./DOCS_INDEX.md) — ドキュメント完全索引
- [docs/README.md](./docs/README.md) — カテゴリ別ドキュメントハブ

---

**構成再編成日**: 2026-01-20
