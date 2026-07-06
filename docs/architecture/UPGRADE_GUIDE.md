# Upgrade Guide — Version 1.0 to 2.0

> This document provides detailed steps for upgrading from version 1.0 to 2.0.

**Last updated**: 2026-01-20

---

## Table of Contents

- [Upgrade Overview](#upgrade-overview)
- [Pre-Upgrade Preparation](#pre-upgrade-preparation)
- [Upgrade Steps](#upgrade-steps)
- [Post-Upgrade Configuration](#post-upgrade-configuration)
- [API Compatibility](#api-compatibility)
- [Troubleshooting](#troubleshooting)

---

## Upgrade Overview

### Version 2.0 Major Changes

1. **Organization Management**
   - New organization (care facility) management
   - Multi-organization, multi-user support
   - Organization-level configuration and limits

2. **Database Structure Changes**
   - New `organizations` table
   - `user_profiles` table adds `org_id` field
   - `translation_history` table adds `org_id` field

3. **API Enhancements**
   - New organization management API
   - Translation API supports organization limits
   - Backward compatible with v1.0 API

### Data Migration

The upgrade process automatically:
- Creates a default organization
- Migrates existing users to the default organization
- Preserves all historical data
- Creates missing user profiles

---

## Pre-Upgrade Preparation

### 1. Backup Database

**Important**: Always backup before upgrading!

```bash
# SQLite backup
cp elder_company.db elder_company.db.backup

# PostgreSQL backup
pg_dump -U username -d elder_company > elder_company_backup.sql
```

### 2. Check Current Version

```bash
cd backend
python3 -c "
from config.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text(\"SELECT name FROM sqlite_master WHERE type='table' AND name='organizations'\"))
    if result.fetchone():
        print('Current version: 2.0')
    else:
        print('Current version: 1.0')
finally:
    db.close()
"
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Upgrade Steps

### Step 1: Database Migration

```bash
cd backend
python3 scripts/migrate_v1_to_v2.py
```

The migration script will:
1. Check current database version
2. Initialize new table structure
3. Create default organization
4. Migrate user data
5. Migrate translation history

### Step 2: Configuration Update

Update `do-not-upload/env/.env`:

```env
# Organization config (optional, has defaults)
DEFAULT_ORG_ID=default_org

# Subscription plan config
ORG_SUBSCRIPTION_PLAN=basic  # basic, professional, enterprise
ORG_MAX_USERS=100
ORG_MONTHLY_TRANSLATION_LIMIT=10000
```

### Step 3: Verify Upgrade

```bash
python3 -c "
from config.database import SessionLocal
from models.database import OrganizationDB, UserProfileDB
db = SessionLocal()
orgs = db.query(OrganizationDB).all()
print(f'Organizations: {len(orgs)}')
users = db.query(UserProfileDB).filter(UserProfileDB.org_id.isnot(None)).all()
print(f'Users with org: {len(users)}')
db.close()
"
```

---

## Post-Upgrade Configuration

### 1. Configure Organization

```bash
curl -X PUT http://localhost:8000/api/organizations/default_org \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Organization Name",
    "name_ja": "組織名",
    "org_type": "Special nursing home for the elderly",
    "subscription_plan": "professional"
  }'
```

### 2. Subscription Plans

- **basic**: max 10 users, 1,000 translations/month
- **professional**: max 50 users, 10,000 translations/month
- **enterprise**: unlimited users and translations

---

## API Compatibility

### Translation API

**v1.0 format** (still supported):
```json
{
  "text": "こんにちは",
  "source_language": "ja",
  "target_language": "en"
}
```

**v2.0 format** (enhanced):
```json
{
  "text": "こんにちは",
  "source_language": "ja",
  "target_language": "en",
  "user_id": "user123",
  "org_id": "org456"
}
```

### New APIs in v2.0

- `POST /api/organizations`
- `GET /api/organizations/{org_id}`
- `PUT /api/organizations/{org_id}`
- `GET /api/organizations/{org_id}/users`
- `GET /api/organizations/{org_id}/statistics`

See `API_CLOUD.md` for full API documentation.

---

## Troubleshooting

### Migration script fails: Table already exists
Database may already be v2.0. Re-run `python3 scripts/migrate_v1_to_v2.py` to verify.

### Users cannot login after migration
1. Restore database backup
2. Check `user_auth` table data
3. Re-run migration script

### Translation history missing org_id
Manually migrate records with null `org_id` to `default_org`.

### API returns 403: Translation limit exceeded
Check organization translation limits and subscription plan.

---

## Rollback

```bash
# Restore backup
cp elder_company.db.backup elder_company.db

# Restore code
git checkout v1.0.0

# Restart
cd backend
python3 -m uvicorn main:app --reload
```

---

## Upgrade Checklist

- [ ] Database backed up
- [ ] Current version confirmed
- [ ] Dependencies installed
- [ ] Migration script run
- [ ] Organization configured
- [ ] API tests passed

---

**Last updated**: 2026-01-20  
**Version**: 2.1.2

---

# 日本語 / Japanese

# アップグレードガイド — バージョン 1.0 から 2.0

> バージョン 1.0 から 2.0 へのアップグレード手順を提供します。

**最終更新**: 2026-01-20

---

## アップグレード概要

### バージョン 2.0 の主な変更

1. **組織管理機能** — 介護施設管理、マルチ組織・マルチユーザー
2. **DB 構造変更** — `organizations` テーブル追加、`org_id` フィールド追加
3. **API 強化** — 組織管理 API、v1.0 後方互換

---

## アップグレード前準備

### 1. データベースバックアップ

```bash
cp elder_company.db elder_company.db.backup
```

### 2. 依存関係インストール

```bash
cd backend
pip install -r requirements.txt
```

---

## アップグレード手順

### ステップ 1: データベース移行

```bash
cd backend
python3 scripts/migrate_v1_to_v2.py
```

### ステップ 2: 設定更新

`do-not-upload/env/.env` を更新：

```env
DEFAULT_ORG_ID=default_org
ORG_SUBSCRIPTION_PLAN=basic
ORG_MAX_USERS=100
ORG_MONTHLY_TRANSLATION_LIMIT=10000
```

### ステップ 3: アップグレード確認

組織数とユーザー数を確認。

---

## API 互換性

v1.0 形式は引き続きサポート。v2.0 では `user_id` と `org_id` が追加可能。

詳細は `API_CLOUD.md` を参照。

---

## トラブルシューティング

- **移行失敗**: バックアップから復元、再実行
- **403 エラー**: 組織の翻訳制限・サブスクリプションプランを確認

---

## アップグレードチェックリスト

- [ ] DB バックアップ済み
- [ ] 移行スクリプト実行済み
- [ ] 組織情報設定済み
- [ ] API テスト合格

---

**最終更新**: 2026-01-20  
**バージョン**: 2.1.2
