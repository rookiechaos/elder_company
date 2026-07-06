# Personalized Translation API Documentation

## Overview

Elder Company AI Translator supports personalized translation optimization based on user profile data. By configuring personal preferences, translations are customized according to work habits, language preferences, and care scenarios.

---

## User Profile API

### 1. Get User Profile

**GET** `/api/user/{user_id}/profile`

**Response example**:
```json
{
  "user_id": "user123",
  "name": "Taro Tanaka",
  "role": "Certified care worker",
  "experience_years": 5,
  "preferred_source_language": "ja",
  "preferred_target_language": "en",
  "translation_style": "professional",
  "detail_level": "moderate",
  "use_honorifics": true,
  "care_scenarios": ["Meal assistance", "Bathing assistance"],
  "custom_terms": {
    "特別養護老人ホーム": "Special nursing home for the elderly",
    "デイサービス": "Day service center"
  },
  "work_shift": "day",
  "common_tasks": ["Feeding assistance", "Bathing assistance"]
}
```

---

### 2. Update User Profile

**POST** `/api/user/{user_id}/profile`

**Request body**:
```json
{
  "name": "Taro Tanaka",
  "role": "Certified care worker",
  "experience_years": 5,
  "preferred_source_language": "ja",
  "preferred_target_language": "en",
  "translation_style": "professional",
  "detail_level": "moderate",
  "use_honorifics": true,
  "care_scenarios": ["Meal assistance", "Bathing assistance", "Repositioning"],
  "custom_terms": {
    "特別養護老人ホーム": "Special nursing home for the elderly",
    "デイサービス": "Day service center"
  },
  "work_shift": "day",
  "common_tasks": ["Feeding assistance", "Bathing assistance", "Repositioning"]
}
```

---

### 3. Get Translation History

**GET** `/api/user/{user_id}/history?limit=50`

**Query parameters**: `limit` (default 50, max 100)

---

## Personalized Translation API

### Translation Endpoint

**POST** `/api/translate`

Include `user_id` to enable personalization.

**Request body**:
```json
{
  "text": "食事介助をお願いします",
  "source_language": "ja",
  "target_language": "en",
  "context": "Care scenario",
  "user_id": "user123"
}
```

**Response**:
```json
{
  "original_text": "食事介助をお願いします",
  "translated_text": "Please assist with meal feeding",
  "source_language": "ja",
  "target_language": "en",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### Chat Translation Endpoint

**POST** `/api/chat`

**Request body**:
```json
{
  "message": "おはようございます",
  "source_language": "ja",
  "target_language": "en",
  "conversation_id": "conv123",
  "user_id": "user123"
}
```

---

## Personalization Settings

### Translation Style (`translation_style`)
- `professional`: Professional, formal style (default)
- `casual`: Friendly, relaxed style
- `formal`: Formal, respectful style

### Detail Level (`detail_level`)
- `brief`: Concise, core information only
- `moderate`: Balanced translation (default)
- `detailed`: Detailed with additional context

### Honorifics (`use_honorifics`)
- `true`: Use appropriate honorifics (default)
- `false`: Standard language without excessive honorifics

### Care Scenarios (`care_scenarios`)
Common care scenarios for terminology optimization:
- `食事介助` — Meal assistance
- `入浴介助` — Bathing assistance
- `体位変換` — Repositioning
- `移動介助` — Mobility assistance
- `更衣介助` — Dressing assistance

### Custom Terms (`custom_terms`)
User-defined terminology dictionary: `{source: translation}`

---

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"
USER_ID = "user123"

profile_data = {
    "name": "Taro Tanaka",
    "role": "Certified care worker",
    "translation_style": "professional",
    "use_honorifics": True,
    "care_scenarios": ["Meal assistance", "Bathing assistance"],
    "custom_terms": {
        "特別養護老人ホーム": "Special nursing home for the elderly"
    }
}

requests.post(f"{BASE_URL}/api/user/{USER_ID}/profile", json=profile_data)

translation = requests.post(
    f"{BASE_URL}/api/translate",
    json={
        "text": "食事介助をお願いします",
        "source_language": "ja",
        "target_language": "en",
        "user_id": USER_ID
    }
)
print(translation.json())
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';
const USER_ID = 'user123';

await fetch(`${BASE_URL}/api/user/${USER_ID}/profile`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Taro Tanaka',
    translation_style: 'professional',
    use_honorifics: true,
    care_scenarios: ['Meal assistance', 'Bathing assistance']
  })
});

const response = await fetch(`${BASE_URL}/api/translate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: '食事介助をお願いします',
    source_language: 'ja',
    target_language: 'en',
    user_id: USER_ID
  })
});
```

---

## Personalization Effects

When personalization is enabled:

1. **Translation style** — adjusts to user preference (professional/casual/formal)
2. **Custom terms** — prioritizes user-defined terminology
3. **Care scenarios** — optimizes for user's common care contexts
4. **Detail level** — adjusts translation verbosity
5. **Honorifics** — controls honorific usage
6. **Translation history** — uses history as context in chat translation

---

## Notes

- `user_id` is optional; default settings used when omitted
- Default profile auto-created on first translation
- Translation history auto-saved when `user_id` provided
- Custom terms: max 10 shown in prompt
- Care scenarios: max 5 shown in prompt

---

**Version**: 2.0.0  
**Last updated**: 2026-01-20

---

# 日本語 / Japanese

# パーソナライズ翻訳 API ドキュメント

## 概要

Elder Company AI 翻訳官は、ユーザーの個人データに基づくパーソナライズ翻訳最適化をサポートします。個人設定により、業務習慣、言語嗜好、介護シナリオに合わせた翻訳結果を提供します。

---

## ユーザープロフィール API

### 1. プロフィール取得

**GET** `/api/user/{user_id}/profile`

### 2. プロフィール更新

**POST** `/api/user/{user_id}/profile`

### 3. 翻訳履歴取得

**GET** `/api/user/{user_id}/history?limit=50`

---

## パーソナライズ翻訳 API

### 翻訳エンドポイント

**POST** `/api/translate`

`user_id` を含めることでパーソナライズが有効になります。

```json
{
  "text": "食事介助をお願いします",
  "source_language": "ja",
  "target_language": "en",
  "user_id": "user123"
}
```

### チャット翻訳エンドポイント

**POST** `/api/chat`

---

## パーソナライズ設定

### 翻訳スタイル (`translation_style`)
- `professional`: 専門的・正式（デフォルト）
- `casual`: カジュアル・フレンドリー
- `formal`: フォーマル・敬意

### 詳細度 (`detail_level`)
- `brief`: 簡潔
- `moderate`: バランス（デフォルト）
- `detailed`: 詳細

### 敬語 (`use_honorifics`)
- `true`: 適切な敬語を使用（デフォルト）
- `false`: 標準的な言語

### 介護シナリオ (`care_scenarios`)
- `食事介助`、`入浴介助`、`体位変換`、`移動介助`、`更衣介助`

### カスタム用語 (`custom_terms`)
ユーザー定義の用語辞書: `{原文: 訳文}`

---

## パーソナライズ効果

1. **翻訳スタイル** — ユーザー嗜好に合わせた調整
2. **カスタム用語** — ユーザー定義用語を優先
3. **介護シナリオ** — 常用シナリオに最適化
4. **詳細度** — 翻訳の詳しさを調整
5. **敬語** — 敬語使用の制御
6. **翻訳履歴** — チャット翻訳で履歴をコンテキストとして利用

---

## 注意事項

- `user_id` は任意。省略時はデフォルト設定
- 初回翻訳時にデフォルトプロフィールを自動作成
- `user_id` 指定時に翻訳履歴を自動保存
- カスタム用語: プロンプトに最大10件
- 介護シナリオ: プロンプトに最大5件

---

**バージョン**: 2.0.0  
**最終更新**: 2026-01-20
