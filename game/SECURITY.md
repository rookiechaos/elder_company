# Game Module Security Design

**Version**: 1.0.0 | **Created**: 2026-01-20

---

## Threat Analysis

### Frontend Threats
XSS, CSRF, clickjacking, client data tampering, session/token theft

### Backend API Threats
Unauthorized access, SQL/NoSQL injection, rate-limit bypass, parameter tampering, session fixation

### Game-Specific Threats
Score cheating, time manipulation, state tampering, bot automation, forged game data

---

## Frontend Security

### Input Validation (`frontend/src/utils/security.js`)
- `sanitizeInput()` — strip HTML, javascript: protocols, event handlers; length limits
- `validateGameId()` — whitelist: memory, story, number, music, picture
- `validateDifficulty()` — easy | medium | hard
- `validateGameState()` — structure and score range (0–100)

### XSS Protection
- Content Security Policy in `index.html`
- React auto-escaping; sanitize before any `dangerouslySetInnerHTML`

### CSRF Protection
- `getCSRFToken()` + `X-CSRF-Token` header on all API requests

### Session Security
- JWT in httpOnly cookies (backend-set); refresh before expiry

---

## Backend API Security

### Authentication
- All game endpoints require JWT via `get_current_user`
- Users may only access their own sessions (`verify_game_session_access`)

### Input Validation (Pydantic)
```python
class GameStartRequest(BaseModel):
    game_type: Literal['memory_match', 'story_chain', ...]
    player1_id: str = Field(..., max_length=100)
    difficulty: Literal['easy', 'medium', 'hard']
```

### Rate Limits
| Action | Limit |
|--------|-------|
| Start | 10/min |
| Update | 60/min |
| Complete | 20/min |
| History | 30/min |
| Stats | 20/min |

### State Validation
- Max state size 100KB (DoS prevention)
- Game-type-specific validators (card count ≤24 for Memory Match, etc.)

---

## Anti-Cheat

### Client + Server Validation
- Action whitelist, index bounds, timestamp checks (±5 min window)
- Progress cannot decrease; max increment per action enforced

### Anomaly Detection (`detect_cheating_patterns`)
- Score >100, completion faster than minimum expected time
- Action interval <100ms (bot detection)
- State inconsistency flags

---

## Security Checklists

### Frontend
- ✅ Input sanitization, CSP, CSRF tokens, HTTPS, pre-send state validation

### Backend
- ✅ JWT auth, rate limits, Pydantic validation, server-side logic checks, no secrets in logs

### Game-Specific
- ✅ Timestamp validation, consistency checks, score bounds, frequency limits

---

## Implementation Roadmap

| Phase | Items |
|-------|-------|
| 1 (immediate) | Input tools, CSP, CSRF, API auth |
| 2 (1 week) | State validation, integrity checks |
| 3 (2 weeks) | Anomaly detection, suspicious session flagging |

---

# Gameモジュール セキュリティ設計

**バージョン**: 1.0.0 | **作成日**: 2026-01-20

---

## 脅威分析

### フロントエンド
XSS、CSRF、クリックジャッキング、クライアントデータ改ざん、セッション/トークン窃取

### バックエンドAPI
未認証アクセス、SQL/NoSQLインジェクション、レート制限回避、パラメータ改ざん

### ゲーム固有
スコア不正、時間改ざん、状態改ざん、ボット自動化、データ偽造

---

## フロントエンドセキュリティ

### 入力検証（`frontend/src/utils/security.js`）
- `sanitizeInput()` — HTML除去、長さ制限
- `validateGameId()` — ホワイトリスト検証
- `validateGameState()` — 構造とスコア範囲（0–100）

### XSS/CSRF対策
- CSP設定、React自動エスケープ
- CSRFトークンを全APIリクエストに付与

### セッション
- JWTをhttpOnly cookieに保存、期限前に更新

---

## バックエンドAPIセキュリティ

### 認証・認可
- 全ゲームAPIでJWT必須
- 自分のセッションのみアクセス可能

### レート制限
| アクション | 制限 |
|-----------|------|
| 開始 | 10/分 |
| 更新 | 60/分 |
| 完了 | 20/分 |
| 履歴 | 30/分 |
| 統計 | 20/分 |

### 状態検証
- 最大100KB（DoS防止）
- ゲーム種別ごとの検証（Memory Match: カード≤24枚等）

---

## 不正防止

### クライアント+サーバー検証
- アクションホワイトリスト、インデックス範囲、タイムスタンプ（±5分）
- 進捗の逆行不可、最大増分制限

### 異常検出
- スコア>100、最短時間未満の完了、100ms未満の操作間隔、状態不整合

---

## 実装ロードマップ

| フェーズ | 項目 |
|---------|------|
| 1（即時） | 入力ツール、CSP、CSRF、API認証 |
| 2（1週間） | 状態検証、整合性チェック |
| 3（2週間） | 異常検出、疑わしいセッションのフラグ |

**ドキュメント管理**: Elder Company セキュリティチーム
