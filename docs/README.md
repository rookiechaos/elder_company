# Elder Company - Documentation Hub

Welcome to the Elder Company documentation hub. This directory contains all development, feature, testing, deployment, and compliance documentation.

## Documentation Structure

```
docs/
├── README.md                    # This file (documentation index)
├── development/                 # Development docs
│   ├── CODING_PLAN.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── CODE_DESIGN_IMPROVEMENTS.md
│   └── ...
├── features/                    # Feature docs
│   ├── FEATURE_COMPLETE.md
│   ├── PRODUCT_FEATURES.md
│   ├── ACTIVITY_FEATURES.md
│   └── ...
├── testing/                     # Testing docs
│   ├── TESTING.md
│   ├── STRESS_TEST_GUIDE.md
│   └── ...
├── architecture/                # Architecture docs
│   ├── CLOUD_ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   └── ...
├── api/                         # API docs
│   ├── API_ACTIVITIES.md
│   ├── API_CLOUD.md
│   ├── API_CLIENT.md            # App–cloud interaction (errors, Sync, 401)
│   └── ...
├── security/                    # Security docs
│   ├── APPLICATION_SECURITY.md
│   ├── SECURITY_AUDIT.md
│   └── ...
├── deployment/                  # Deployment docs
│   ├── DEPLOYMENT.md
│   ├── SETUP.md
│   └── ...
├── compliance/                  # Compliance docs
│   ├── PRODUCT_NON_MEDICAL.md
│   └── AUTH_REGISTRATION_LOGIN_STATUS.md
└── business/                    # Business docs
    ├── 事業計画書.md
    ├── PRESENTATION_JP.md
    └── ...
```

## Quick Navigation

### New Users
- [Project README](../README.md) — Project overview
- [Setup Guide](deployment/SETUP.md) — Environment configuration
- [Product Features](features/PRODUCT_FEATURES.md) — Feature list

### Developers
- [Coding Plan](development/CODING_PLAN.md) — Development plan and progress
- [Development Roadmap](development/DEVELOPMENT_ROADMAP.md) — Feature roadmap
- [Code Design Improvements](development/CODE_DESIGN_IMPROVEMENTS.md) — Code conventions

### QA / Testers
- [Testing Guide](testing/TESTING.md) — Testing methods
- [tests/README.md](../tests/README.md) — Test layout and commands
- [Stress Test Guide](testing/STRESS_TEST_GUIDE.md) — Stress testing
- [Internal Testing Guide](testing/README_INTERNAL_TESTING.md) — Internal API testing

### Operations
- [Deployment Guide](deployment/DEPLOYMENT.md) — Production deployment
- [Cloud Architecture](architecture/CLOUD_ARCHITECTURE.md) — Architecture overview
- [Performance Optimization](architecture/PERFORMANCE_OPTIMIZATION.md) — Performance tuning

### Product / Business
- [Product Vision](../VISION.md) — Product philosophy
- [Business Plan (JP)](business/事業計画書.md) — Business plan (Japanese)
- [Presentation (JP)](business/PRESENTATION_JP.md) — Client presentation (Japanese)

## Category Descriptions

### Development
Plans, roadmaps, code improvements, and other development-process documentation.

### Features
Feature completion reports, product capabilities, and feature analysis.

### Testing
Testing guides, results, and reports. Run tests from the repo root — see [tests/README.md](../tests/README.md).

### Architecture
System architecture, database design, and performance optimization.

### API
Module-level API documentation. See also [api/API_CLIENT.md](api/API_CLIENT.md) for app–cloud interaction conventions (error responses, Sync, 401 handling).

### Security
Security audits, improvements, and summaries.

### Deployment
Environment setup, deployment guides, and upgrade guides. Local secrets and data live in [do-not-upload/](../do-not-upload/README.md).

### Compliance
Product disclaimers, auth requirements, and regulatory boundaries.

### Business
Business plans, presentations, and market analysis.

## Documentation Updates

Documentation is updated as the project evolves.

- **Last updated**: 2026-01-20
- **Maintained by**: Elder Company development team

## Contributing to Documentation

To add or update documentation:

1. Place the file in the appropriate category directory
2. Update this index
3. Update the root [DOCS_INDEX.md](../DOCS_INDEX.md)

---

**Note**: The documentation tree was reorganized on 2026-01-20 for clearer management.

---

# Elder Company - ドキュメントハブ

Elder Company プロジェクトのドキュメントハブへようこそ。開発、機能、テスト、デプロイ、コンプライアンスに関するすべてのドキュメントがここに集約されています。

## ドキュメント構成

```
docs/
├── README.md                    # 本ファイル（ドキュメント索引）
├── development/                 # 開発ドキュメント
├── features/                    # 機能ドキュメント
├── testing/                     # テストドキュメント
├── architecture/                # アーキテクチャドキュメント
├── api/                         # API ドキュメント
├── security/                    # セキュリティドキュメント
├── deployment/                  # デプロイドキュメント
├── compliance/                  # コンプライアンスドキュメント
└── business/                    # ビジネスドキュメント
```

## クイックナビゲーション

### 新規ユーザー
- [プロジェクト README](../README.md) — プロジェクト概要
- [セットアップガイド](deployment/SETUP.md) — 環境構築
- [プロダクト機能](features/PRODUCT_FEATURES.md) — 機能一覧

### 開発者
- [開発計画](development/CODING_PLAN.md) — 開発計画と進捗
- [開発ロードマップ](development/DEVELOPMENT_ROADMAP.md) — 機能開発ロードマップ
- [コード設計改善](development/CODE_DESIGN_IMPROVEMENTS.md) — コード規約

### テスト担当
- [テストガイド](testing/TESTING.md) — テスト方法
- [tests/README.md](../tests/README.md) — テスト構成とコマンド
- [負荷テストガイド](testing/STRESS_TEST_GUIDE.md) — 負荷テスト
- [内部テストガイド](testing/README_INTERNAL_TESTING.md) — 内部 API テスト

### 運用担当
- [デプロイガイド](deployment/DEPLOYMENT.md) — 本番環境デプロイ
- [クラウドアーキテクチャ](architecture/CLOUD_ARCHITECTURE.md) — アーキテクチャ概要
- [パフォーマンス最適化](architecture/PERFORMANCE_OPTIMIZATION.md) — パフォーマンスチューニング

### プロダクト / ビジネス
- [プロダクトビジョン](../VISION.md) — プロダクト理念
- [事業計画書](business/事業計画書.md) — 事業計画（日本語）
- [プレゼン資料](business/PRESENTATION_JP.md) — 顧客向けプレゼン（日本語）

## カテゴリ説明

### Development（開発）
開発計画、ロードマップ、コード改善など。

### Features（機能）
機能完了レポート、プロダクト特性、機能分析。

### Testing（テスト）
テストガイド、結果、レポート。テストはリポジトリルートから実行 — [tests/README.md](../tests/README.md) を参照。

### Architecture（アーキテクチャ）
システムアーキテクチャ、データベース設計、パフォーマンス最適化。

### API
各モジュールの API ドキュメント。[api/API_CLIENT.md](api/API_CLIENT.md) にはアプリとクラウドの連携規約（エラーレスポンス、Sync、401 処理）も記載。

### Security（セキュリティ）
セキュリティ監査、改善、まとめ。

### Deployment（デプロイ）
環境構築、デプロイガイド、アップグレードガイド。ローカル秘密情報とデータは [do-not-upload/](../do-not-upload/README.md) に配置。

### Compliance（コンプライアンス）
プロダクト免責事項、認証要件、規制上の境界。

### Business（ビジネス）
事業計画、プレゼン資料、市場分析。

## ドキュメント更新

プロジェクトの進展に合わせて継続的に更新されます。

- **最終更新**: 2026-01-20
- **メンテナンス**: Elder Company 開発チーム

## ドキュメントへの貢献

ドキュメントを追加・更新する場合:

1. 適切なカテゴリディレクトリに配置
2. 本索引を更新
3. ルートの [DOCS_INDEX.md](../DOCS_INDEX.md) を更新

---

**注記**: ドキュメントツリーは 2026-01-20 に再編成され、管理しやすくなりました。
