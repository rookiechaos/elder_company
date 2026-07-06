# Elder Company — Enterprise Product Features

> **Document purpose**: Product features and API reference.

**Version**: 2.1.2 — Enterprise Enhanced (code quality & security improvements)  
**Last updated**: 2026-01-20

---

## Product Positioning

Elder Company AI Translator is an enterprise product for care facilities, supporting multi-tenant management, usage analytics, and personalized configuration.

---

## Core Enterprise Features

### 1. Organization Management (Multi-Tenant)

- Multiple care facilities with isolated data and configuration
- Org-level user management and permissions

**API**: `POST/GET/PUT /api/organizations`, `GET /{org_id}/users`, `GET /{org_id}/statistics?days=30`

**Config**: name, address, default language, custom terminology, care scenarios, subscription plan, user/translation limits

---

### 2. Enhanced Care Terminology Library

- 50+ professional care terms across categories
- Search, translation, scenario templates

**API**: `GET /api/care-terms`, `GET /care-terms/search?q=...`, `GET /care-terms/translate`, `GET /care-terms/scenarios`

**Categories**: daily_care, medical, facilities, conditions, communication, equipment

---

### 3. Usage Statistics & Reporting

- Org and user-level stats; language pair distribution; daily trends
- Metrics: total translations, active users, avg translation time, character counts

---

### 4. Personalized Translation (Three-Tier Config)

1. **Organization**: default language, org terminology, scenarios
2. **User**: style preferences, personal terms, scenarios
3. **Request**: temporary context (highest priority)

Merge order: org → user → request

---

### 5. Enterprise Logging & Monitoring

- Structured logs: translation events, API requests, errors, performance
- Log files: `do-not-upload/logs/app.log`, `do-not-upload/logs/error.log`

---

### 6. Usage Limits & Quotas

| Plan | Max Users | Translations/Month |
|------|-----------|-------------------|
| Basic | 10 | 1,000 |
| Professional | 50 | 10,000 |
| Enterprise | Unlimited | Unlimited |

Automatic quota checks with friendly errors.

---

## Data Models

- `organizations` — org info, subscription, usage summary
- `user_profiles` — user info, org link, personalization
- `translation_history` — records, performance, org link
- `usage_statistics` — daily stats, language pairs

---

## Security & Privacy

- Org data isolation; role-based access (caregiver/admin/manager)

---

## Deployment Recommendations

- **Database**: PostgreSQL for production; connection pooling; backups
- **Logs**: rotation, aggregation (ELK), retention policy
- **Monitoring**: API performance, error alerts, usage tracking
- **Scale**: horizontal scaling, load balancing, Redis cache
- **Local dev data**: `do-not-upload/` (DB, logs, storage)

---

## Business Value

1. **Communication efficiency** — reduce language barriers, improve care quality
2. **Data-driven decisions** — usage reports, scenario identification
3. **Standardization** — unified terminology, care workflows, training
4. **Cost control** — subscription tiers, usage monitoring

---

## Upgrade Path (1.0 → 2.0)

### Database Migration ✅
- `config/database.py::init_database()`
- Migration script: `scripts/migrate_v1_to_v2.py`
- Creates default org, migrates users and translation history

### Configuration ✅
```env
DEFAULT_ORG_ID=default_org
ORG_SUBSCRIPTION_PLAN=basic
ORG_MAX_USERS=10
ORG_MONTHLY_TRANSLATION_LIMIT=1000
```

### API Compatibility ✅
- All 1.0 APIs remain; `org_id` optional on translate/profile endpoints
- New org endpoints in `backend/api/organization_routes.py`

### Quick Upgrade
```bash
cp do-not-upload/elder_company.db do-not-upload/elder_company.db.backup
cd backend && python3 scripts/migrate_v1_to_v2.py
```

---

## Code Quality (v2.1.2)

| Area | Implementation |
|------|----------------|
| Error handling | Custom exceptions (`NotFoundError`, `AuthenticationError`, etc.) |
| Refactoring | `BaseService`, reduced router duplication |
| Type hints | Full public method annotations, mypy |
| Documentation | Google-style docstrings |
| Tests | Unit + integration in `tests/` |
| Quality tools | Black, isort, ruff, mypy, pre-commit |
| Query optimization | `services/query_analyzer.py`, `services/query_optimizer.py` |

---

## Future Roadmap

**Near-term**: Mobile app, voice translation, real-time collaboration, API keys, webhooks

**Long-term**: Multi-language expansion, model fine-tuning, third-party integrations

---

**Version**: 2.1.2 | **Status**: Production ready ✅ (12/12 internal API tests | `scripts/stress_test.py` ready)

---

# 日本語

# Elder Company — エンタープライズ製品機能

> **文書目的**: 製品機能と API リファレンス。

**バージョン**: 2.1.2 | **最終更新**: 2026-01-20

---

## 製品ポジショニング

介護施設向けエンタープライズ AI 翻訳製品。マルチテナント、利用統計、パーソナライズ設定をサポート。

---

## コア機能

| # | 機能 | 概要 |
|---|------|------|
| 1 | 組織管理 | マルチテナント、独立データ、権限管理 |
| 2 | 介護用語ライブラリ | 50+ 用語、6 カテゴリ、検索・翻訳 |
| 3 | 利用統計 | 組織/ユーザー別、言語ペア、日次トレンド |
| 4 | パーソナライズ翻訳 | 組織→ユーザー→リクエストの 3 層設定 |
| 5 | ログ・監視 | 構造化ログ（`do-not-upload/logs/`） |
| 6 | 利用制限 | Basic / Professional / Enterprise プラン |

---

## サブスクリプションプラン

| プラン | 最大ユーザー | 月間翻訳 |
|--------|------------|---------|
| Basic | 10 | 1,000 |
| Professional | 50 | 10,000 |
| Enterprise | 無制限 | 無制限 |

---

## セキュリティ

- 組織データ分離、ロールベースアクセス（caregiver/admin/manager）

---

## デプロイ推奨

- PostgreSQL（本番）、接続プール、バックアップ
- ログローテーション、ELK 連携
- Redis キャッシュ、水平スケール
- ローカル開発データ: `do-not-upload/`

---

## アップグレード（1.0 → 2.0）

```bash
cp do-not-upload/elder_company.db do-not-upload/elder_company.db.backup
cd backend && python3 scripts/migrate_v1_to_v2.py
```

- 全 1.0 API 後方互換、`org_id` は任意パラメータ

---

## コード品質（v2.1.2）

- カスタム例外、`BaseService`、型注解、`tests/`、Black/isort/ruff/mypy
- クエリ最適化: `services/query_analyzer.py`, `services/query_optimizer.py`

---

## 今後のロードマップ

**短期**: モバイル、音声翻訳、リアルタイム協働、API キー、Webhook

**長期**: 多言語拡張、モデル微調整、第三者連携

**状態**: 本番準備完了 ✅（内部 API テスト 12/12 | `scripts/stress_test.py` 準備済み）
