# App–Cloud Interaction Conventions

This document describes how the frontend (App) interacts with cloud APIs, for frontend–backend integration and maintenance.

---

## Error Response Contract

All API error responses are normalized by the backend to the following structure (see [backend/middleware/error_handler.py](../../backend/middleware/error_handler.py)):

```json
{
  "error": {
    "type": "HTTPException",
    "message": "Human-readable error description",
    "code": "HTTP_401",
    "details": {}
  }
}
```

- **message**: User-readable error description; the frontend should display this field first.
- **code**: Optional error code.
- **details**: Optional additional information.

The frontend [utils/api.js](../../frontend/src/utils/api.js) response error interceptor **parses once centrally**: it reads `error.response.data?.error?.message` first, falls back to `detail` / `message`, and `reject(new Error(message))`.  
**Components only need `err.message`** — no need to parse `response.data` or `response.data.detail` again, avoiding inconsistent parsing across components.

---

## Data Sync API

The backend provides data sync endpoints ([backend/api/sync_routes.py](../../backend/api/sync_routes.py)), for example:

- `POST /api/sync/full` — Full data sync
- `POST /api/sync/profile` — Profile sync

These endpoints require the `X-Device-ID` header for multi-device identification.

**Current convention**: Sync APIs are **server-side reserved** — backend implementation only; the frontend App does not call them yet. If multi-device/offline sync is needed, add on the frontend:

- Call sync endpoints after login, on a schedule, or when back online;
- Add `X-Device-ID` uniformly at the request layer (from localStorage or device fingerprint).

---

## Authentication and 401 Handling

- Frontend requests automatically attach `Authorization: Bearer <token>` via axios interceptors.
- When an endpoint returns **401**, the API layer clears the local token and dispatches an `auth:logout` event; AuthContext listens and runs logout, returning the UI to an unauthenticated state. Components do not need separate 401 handling.

---

## References

- Cloud API list and auth: [API_CLOUD.md](./API_CLOUD.md)
- Backend error handling: [backend/middleware/error_handler.py](../../backend/middleware/error_handler.py)
- Frontend request wrapper and error parsing: [frontend/src/utils/api.js](../../frontend/src/utils/api.js)

---

# 日本語 / Japanese

# アプリとクラウドの連携規約

本ドキュメントはフロントエンド（アプリ）とクラウド API の連携規約を説明し、前後端の統合・保守を支援します。

---

## エラーレスポンス契約

すべての API エラーレスポンスはバックエンドで以下の構造に統一されます（[backend/middleware/error_handler.py](../../backend/middleware/error_handler.py) 参照）:

```json
{
  "error": {
    "type": "HTTPException",
    "message": "ユーザー向けエラー説明",
    "code": "HTTP_401",
    "details": {}
  }
}
```

- **message**: ユーザー向けエラー説明。フロントエンドはこのフィールドを優先表示。
- **code**: 任意のエラーコード。
- **details**: 任意の追加情報。

フロントエンド [utils/api.js](../../frontend/src/utils/api.js) のレスポンスエラーインターセプターで**一度だけ統一解析**: `error.response.data?.error?.message` を優先し、`detail` / `message` にフォールバックし、`reject(new Error(message))` します。  
**コンポーネント層は `err.message` のみ使用** — `response.data` や `response.data.detail` を再解析する必要はなく、複数箇所での不整合を防ぎます。

---

## データ同期（Sync）API

バックエンドはデータ同期インターフェースを提供しています（[backend/api/sync_routes.py](../../backend/api/sync_routes.py)）:

- `POST /api/sync/full` — 完全データ同期
- `POST /api/sync/profile` — プロフィール同期

これらのインターフェースは `X-Device-ID` ヘッダーを要求し、マルチデバイス識別に使用します。

**現在の規約**: Sync API は**サーバー側予約** — バックエンド実装のみ利用可能。フロントエンドアプリは現時点で未呼び出し。マルチデバイス/オフライン同期が必要な場合、フロントエンドに追加:

- ログイン後、定期、またはオンライン復帰時に sync インターフェースを呼び出す;
- リクエスト層で `X-Device-ID` を統一追加（localStorage またはデバイスフィンガープリントから生成）。

---

## 認証と 401 処理

- フロントエンドリクエストは axios インターセプターで `Authorization: Bearer <token>` を自動付与。
- インターフェースが **401** を返す場合、api 層はローカル token をクリアし `auth:logout` イベントを発火。AuthContext がリッスンして logout を実行し、UI を未ログイン状態に戻します。コンポーネントは 401 を個別処理する必要はありません。

---

## 参考

- クラウド API 一覧と認証: [API_CLOUD.md](./API_CLOUD.md)
- バックエンドエラー処理: [backend/middleware/error_handler.py](../../backend/middleware/error_handler.py)
- フロントエンドリクエストラッパーとエラー解析: [frontend/src/utils/api.js](../../frontend/src/utils/api.js)
