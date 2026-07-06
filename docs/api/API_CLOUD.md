# Cloud API Documentation

## Overview

Elder Company provides a complete cloud API supporting user authentication, data synchronization, and multi-device management.

---

## Authentication API

### 1. User Registration

**POST** `/api/auth/register`

**Request body**:
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "phone": "+81-90-1234-5678",
  "username": "username",
  "password": "secure_password",
  "auth_method": "password"
}
```

**Response**:
```json
{
  "message": "User registered successfully",
  "user": {
    "user_id": "user123",
    "email": "user@example.com",
    "is_active": true
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. User Login

**POST** `/api/auth/login`

**Request body**:
```json
{
  "identifier": "user@example.com",
  "password": "secure_password"
}
```

---

### 3. Register Device

**POST** `/api/auth/device/register`

**Headers**: `Authorization: Bearer {token}`

**Request body**:
```json
{
  "device_token": "unique_device_identifier",
  "device_name": "iPhone 15",
  "device_type": "mobile",
  "platform": "ios",
  "app_version": "1.0.0"
}
```

---

### 4. Get Device List

**GET** `/api/auth/devices`

**Headers**: `Authorization: Bearer {token}`

---

### 5. Get Current User

**GET** `/api/auth/me`

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "user_id": "user123",
  "profile": {
    "name": "Taro Tanaka",
    "role": "Certified care worker",
    "preferred_source_language": "ja"
  },
  "devices": []
}
```

---

## Data Sync API

### 1. Full Sync

**POST** `/api/sync/full`

**Headers**: `Authorization: Bearer {token}`, `X-Device-ID: device_abc123`

**Request body**:
```json
{
  "profile": {
    "name": "Taro Tanaka",
    "translation_style": "professional"
  },
  "activities": [
    {
      "record_id": "record_001",
      "activity_title": "Origami",
      "elder_engagement": "high"
    }
  ],
  "translations": [
    {
      "original_text": "こんにちは",
      "translated_text": "Hello"
    }
  ]
}
```

---

### 2. Sync Profile

**POST** `/api/sync/profile`

**Request body**:
```json
{
  "name": "Taro Tanaka",
  "translation_style": "professional",
  "custom_terms": {
    "特別養護老人ホーム": "Special nursing home for the elderly"
  },
  "updated_at": "2024-01-15T10:00:00"
}
```

---

### 3. Sync Activities

**POST** `/api/sync/activities`

---

### 4. Sync Translations

**POST** `/api/sync/translations`

**Request body**:
```json
[
  {
    "original_text": "こんにちは",
    "translated_text": "Hello",
    "source_language": "ja",
    "target_language": "en",
    "timestamp": "2024-01-15T10:00:00"
  }
]
```

---

### 5. Get Sync Status

**GET** `/api/sync/status`

**Response**:
```json
{
  "device_id": "device_abc123",
  "last_sync_at": "2024-01-15T10:30:00",
  "sync_status": "active"
}
```

---

## Usage Examples

### Python

```python
import requests

BASE_URL = "https://api.eldercompany.com"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"identifier": "user@example.com", "password": "password"}
)
token = response.json()["token"]

# Full sync
response = requests.post(
    f"{BASE_URL}/api/sync/full",
    headers={
        "Authorization": f"Bearer {token}",
        "X-Device-ID": device_id
    },
    json=local_data
)
```

### JavaScript

```javascript
const BASE_URL = 'https://api.eldercompany.com';

async function login(email, password) {
  const response = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier: email, password })
  });
  const data = await response.json();
  await storeToken(data.token);
  return data;
}
```

---

## Security Notes

1. **Token management** — store securely, auto-refresh on expiry, never commit to version control
2. **Device management** — unique device IDs, periodic cleanup of inactive devices
3. **Data encryption** — HTTPS transport, encrypted sensitive data storage

---

## Error Handling

| Code | Meaning |
|------|---------|
| 401 | Token invalid or expired |
| 403 | Insufficient permissions |
| 400 | Invalid request parameters |
| 409 | Data conflict |
| 500 | Server error |

```json
{
  "detail": "Error message here",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

**Version**: 2.0.0  
**Last updated**: 2025-01-19

---

# 日本語 / Japanese

# クラウド API ドキュメント

## 概要

Elder Company はユーザー認証、データ同期、マルチデバイス管理をサポートする完全なクラウド API を提供します。

---

## 認証 API

### 1. ユーザー登録

**POST** `/api/auth/register`

### 2. ユーザーログイン

**POST** `/api/auth/login`

### 3. デバイス登録

**POST** `/api/auth/device/register`

**ヘッダー**: `Authorization: Bearer {token}`

### 4. デバイス一覧

**GET** `/api/auth/devices`

### 5. 現在のユーザー情報

**GET** `/api/auth/me`

---

## データ同期 API

### 1. 完全同期

**POST** `/api/sync/full`

プロフィール、活動記録、翻訳履歴を一括同期。

### 2. プロフィール同期

**POST** `/api/sync/profile`

### 3. 活動記録同期

**POST** `/api/sync/activities`

### 4. 翻訳履歴同期

**POST** `/api/sync/translations`

### 5. 同期ステータス

**GET** `/api/sync/status`

---

## セキュリティ注意事項

1. **トークン管理** — 安全なストレージ、期限切れ時の自動更新、バージョン管理へのコミット禁止
2. **デバイス管理** — 一意のデバイス ID、非アクティブデバイスの定期クリーンアップ
3. **データ暗号化** — HTTPS 転送、機密データの暗号化保存

---

## エラー処理

| コード | 意味 |
|--------|------|
| 401 | トークン無効または期限切れ |
| 403 | 権限不足 |
| 400 | リクエストパラメータエラー |
| 409 | データ競合 |
| 500 | サーバーエラー |

---

**バージョン**: 2.0.0  
**最終更新**: 2025-01-19
