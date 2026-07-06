# Game API Documentation

**Version**: 1.0.0  
**Created**: 2026-01-20

---

## Overview

The game module integrates with the Elder Company backend for session management, progress tracking, and analytics.

---

## Endpoints

### Session Management

#### Start Session
```
POST /api/games/start
```
**Request**:
```json
{
  "game_type": "memory_match",
  "player1_id": "caregiver_123",
  "player2_id": "elder_456",
  "difficulty": "medium",
  "settings": { "card_pairs": 8, "time_limit": null, "hints_enabled": false }
}
```
**Response**: `session_id`, `game_state`, `created_at`

#### Update State
```
POST /api/games/update
```

#### Complete Session
```
POST /api/games/complete
```

---

### Progress Tracking

#### History
```
GET /api/games/history?user_id=elder_456&game_type=memory_match&limit=10
```

#### Statistics
```
GET /api/games/stats?user_id=elder_456
```

---

### Ability Assessment

```
POST /api/games/assessment
GET /api/games/assessment?user_id=elder_456
```

---

## Data Models

```typescript
interface GameSession {
  session_id: string;
  game_type: 'memory_match' | 'story_chain' | 'number_puzzle' | 'music_rhythm' | 'picture_sort';
  player1_id: string;
  player2_id: string;
  difficulty: 'easy' | 'medium' | 'hard';
  game_state: object;
  score?: number;
  completion: number; // 0-100
  start_time: Date;
  end_time?: Date;
}
```

---

## Error Handling

| Code | Meaning |
|------|---------|
| 400 | Invalid parameters |
| 401 | Unauthorized |
| 404 | Session not found |
| 500 | Server error |

---

## Authentication

All requests require JWT:
```
Authorization: Bearer <token>
```

---

# ゲームAPIドキュメント

**バージョン**: 1.0.0  
**作成日**: 2026-01-20

---

## 概要

ゲームモジュールは Elder Company バックエンドと連携し、セッション管理、進捗追跡、分析機能を提供します。

---

## エンドポイント

### セッション管理

#### セッション開始
```
POST /api/games/start
```

#### 状態更新
```
POST /api/games/update
```

#### セッション完了
```
POST /api/games/complete
```

---

### 進捗追跡

#### 履歴取得
```
GET /api/games/history?user_id=elder_456&game_type=memory_match&limit=10
```

#### 統計取得
```
GET /api/games/stats?user_id=elder_456
```

---

### 能力評価

```
POST /api/games/assessment
GET /api/games/assessment?user_id=elder_456
```

---

## データモデル

```typescript
interface GameSession {
  session_id: string;
  game_type: 'memory_match' | 'story_chain' | 'number_puzzle' | 'music_rhythm' | 'picture_sort';
  player1_id: string;
  player2_id: string;
  difficulty: 'easy' | 'medium' | 'hard';
  completion: number; // 0-100
}
```

---

## エラー処理

| コード | 意味 |
|--------|------|
| 400 | パラメータエラー |
| 401 | 未認証 |
| 404 | セッション未存在 |
| 500 | サーバーエラー |

---

## 認証

全リクエストにJWT必須:
```
Authorization: Bearer <token>
```

**ドキュメント管理**: Elder Company 開発チーム
