# Elder Company — Cloud Architecture Design

## Overview

Elder Company uses a **cloud + local hybrid architecture** ensuring data security, multi-device sync, and offline availability.

---

## Architecture

```
┌─────────────────┐
│  Mobile App      │
│  (iOS/Android)   │
└────────┬─────────┘
         │ HTTPS/JWT
┌────────▼─────────────────┐
│  Cloud API Server         │
│  (FastAPI + PostgreSQL)   │
│  - Authentication         │
│  - Data storage           │
│  - Data sync              │
│  - Business logic         │
└────────┬──────────────────┘
         │
┌────────▼────────┐
│  Cloud Database  │
│  (PostgreSQL)    │
└─────────────────┘
```

---

## Core Components

### 1. User Authentication

**Data models**: `UserAuthDB`, `DeviceDB`

**API endpoints**:
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/device/register`
- `GET /api/auth/devices`
- `GET /api/auth/me`

### 2. Data Sync

**Sync data types**: Profile, Activities, Translations

**Data models**: `SyncLogDB`, `DataVersionDB`

**API endpoints**:
- `POST /api/sync/full`
- `POST /api/sync/profile`
- `POST /api/sync/activities`
- `POST /api/sync/translations`
- `GET /api/sync/status`

### 3. Conflict Resolution

**Strategies**:
1. **Server Wins** (default) — for critical data
2. **Client Wins** — for user preferences
3. **Merged** — for mergeable data

---

## Data Flows

### Registration Flow
Register → Create `UserAuthDB` → Generate JWT → Return token

### Login Flow
Login → Verify credentials → Generate/refresh token → Register/update device → Return token

### Sync Flow
Client sync request → Verify token & device → Detect conflicts → Resolve → Update cloud → Return result → Log sync

---

## Security Design

- **JWT**: 30-day expiry, signed, includes user ID and device ID
- **Passwords**: bcrypt with random salt
- **Transport**: HTTPS/TLS
- **Data isolation**: user, organization, and device level
- **Privacy**: minimal data collection, periodic cleanup

---

## Cloud Deployment

**Production**: PostgreSQL  
**Development**: SQLite

### Environment Configuration

```env
# do-not-upload/env/.env
DATABASE_URL=postgresql://user:password@host:5432/elder_company
JWT_SECRET_KEY=your-very-secure-secret-key-here
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
PORT=8000
CORS_ORIGINS=https://app.eldercompany.com
```

---

## Client Integration

```javascript
// Device registration
const response = await fetch('/api/auth/device/register', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    device_token: deviceToken,
    device_type: 'mobile',
    platform: 'ios',
    app_version: '1.0.0'
  })
});

// Full sync
const response = await fetch('/api/sync/full', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Device-ID': deviceId,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(localData)
});
```

---

## Data Model Relationships

```
UserAuthDB (1) ── (1) UserProfileDB
    │ (1:N)
DeviceDB (N) ── (1:N) SyncLogDB

UserProfileDB (1) ── (N) ActivityRecordDB
UserProfileDB (1) ── (N) TranslationHistoryDB
```

---

## Performance Optimization

- Database indexes on user ID, device ID, timestamps
- Connection pooling
- Incremental sync (only changed data)
- Batch insert/update operations
- Redis caching for activity templates and user config

---

## Monitoring, Backup, and Scaling

- Sync success rate, latency, conflict frequency monitoring
- Daily automated backups (30-day retention)
- Horizontal scaling via load balancing
- Vertical scaling via resource upgrades

---

**Version**: 2.0.0  
**Last updated**: 2026-01-20

---

# 日本語 / Japanese

# Elder Company — クラウドアーキテクチャ設計

## 概要

Elder Company は **クラウド + ローカル** のハイブリッドアーキテクチャを採用し、データセキュリティ、マルチデバイス同期、オフライン可用性を確保しています。

---

## アーキテクチャ

```
┌─────────────────┐
│  モバイル App     │
│  (iOS/Android)   │
└────────┬─────────┘
         │ HTTPS/JWT
┌────────▼─────────────────┐
│  クラウド API サーバー     │
│  (FastAPI + PostgreSQL)   │
└────────┬──────────────────┘
         │
┌────────▼────────┐
│  クラウド DB      │
│  (PostgreSQL)    │
└─────────────────┘
```

---

## コアコンポーネント

### 1. ユーザー認証
- JWT トークン認証、bcrypt パスワード暗号化
- エンドポイント: `/api/auth/register`, `/api/auth/login`, `/api/auth/device/register`

### 2. データ同期
- 同期データ: プロフィール、活動記録、翻訳履歴
- エンドポイント: `/api/sync/full`, `/api/sync/profile`, `/api/sync/status`

### 3. 競合解決
- Server Wins（デフォルト）、Client Wins、Merged

---

## セキュリティ設計

- JWT: 30日有効期限、署名検証
- パスワード: bcrypt + ランダムソルト
- 転送: HTTPS/TLS
- データ分離: ユーザー・組織・デバイスレベル

---

## クラウドデプロイ

**本番**: PostgreSQL  
**開発**: SQLite

### 環境変数（`do-not-upload/env/.env`）

```env
DATABASE_URL=postgresql://user:password@host:5432/elder_company
JWT_SECRET_KEY=your-very-secure-secret-key-here
CORS_ORIGINS=https://app.eldercompany.com
```

---

## パフォーマンス最適化

- インデックス、コネクションプール
- 増分同期、バッチ操作
- Redis キャッシュ

---

## 監視・バックアップ・スケーリング

- 同期成功率、レイテンシ、競合頻度の監視
- 日次自動バックアップ（30日保持）
- ロードバランシングによる水平スケーリング

---

**バージョン**: 2.0.0  
**最終更新**: 2026-01-20
