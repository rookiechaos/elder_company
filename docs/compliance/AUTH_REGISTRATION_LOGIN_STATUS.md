# User Registration and Login Requirements

**Last updated**: 2026-01-26

## Registration Required Before Use

The product **requires completed registration / login** (internal data model: `user_auth`) before any use. When not logged in, only the login / registration screen is shown; the main application is inaccessible. After successful login or registration, the backend validates the session via `/api/auth/me` before granting access. Logging out returns the user to the login gate.

---

## Backend (OK)

- **Register**: `POST /api/auth/register`
  - Request: `user_id` (required), `email` / `phone` / `username` (optional), `password` (optional), `auth_method` (default `password`)
  - Password strength validation (minimum 8 characters, upper + lower + digit + special character), bcrypt storage
  - Response: `user`, `token` (JWT)
- **Login**: `POST /api/auth/login`
  - Request: `identifier` (email / phone / username), `password`
  - Response: `user`, `token` (JWT)
- **Authentication**: Protected endpoints validate `Authorization: Bearer <token>`; `middleware.auth.get_current_user` parses the JWT
- **Rate limiting**: `RATE_LIMITS["auth"]` applies to register / login

---

## Frontend (Complete)

- **Gate**: When not logged in, only the login / registration UI (`LoginRegister` gate mode) is rendered — not the main app. On startup, if `auth_token` exists, `/auth/me` is called; failed validation or missing token shows the gate.
- **API requests**: The request interceptor in `frontend/src/utils/api.js` reads `localStorage.auth_token` and sets `Authorization: Bearer <token>`.
- **Login / register entry**: Gate mode shows only the login / register form (no close button). When logged in, the header "Logout" action clears the token and returns to the gate.

---

## Compliance Checklist

- [x] Backend register and login endpoints available
- [x] Password encrypted at rest with strength validation
- [x] JWT issuance and validation
- [x] Frontend requests uniformly carry token (API interceptor)
- [x] Frontend provides login / register entry (`LoginRegister` component + header login entry)

---

# ユーザー登録とログイン要件

**最終更新**: 2026-01-26

## 利用前に登録が必須

本製品は**登録 / ログイン完了**（内部データモデル: `user_auth`）後にのみ利用可能です。未ログイン時はログイン / 登録画面のみ表示され、メインアプリケーションにはアクセスできません。ログインまたは登録成功後、バックエンドが `/api/auth/me` でセッションを検証してからアクセスを許可します。ログアウトすると再びログインゲートに戻ります。

---

## バックエンド（OK）

- **登録**: `POST /api/auth/register`
  - リクエスト: `user_id`（必須）、`email` / `phone` / `username`（任意）、`password`（任意）、`auth_method`（デフォルト `password`）
  - パスワード強度検証（8 文字以上、大文字 + 小文字 + 数字 + 特殊文字）、bcrypt 保存
  - レスポンス: `user`、`token`（JWT）
- **ログイン**: `POST /api/auth/login`
  - リクエスト: `identifier`（メール / 電話 / ユーザー名）、`password`
  - レスポンス: `user`、`token`（JWT）
- **認証**: 保護エンドポイントは `Authorization: Bearer <token>` を検証。`middleware.auth.get_current_user` が JWT を解析
- **レート制限**: `RATE_LIMITS["auth"]` が登録 / ログインに適用

---

## フロントエンド（完了）

- **ゲート**: 未ログイン時はログイン / 登録 UI（`LoginRegister` ゲートモード）のみ表示 — メインアプリは表示しない。起動時に `auth_token` があれば `/auth/me` を呼び出し。検証失敗または token なしの場合はゲートを表示。
- **API リクエスト**: `frontend/src/utils/api.js` のリクエストインターセプターが `localStorage.auth_token` を読み取り、`Authorization: Bearer <token>` を設定。
- **ログイン / 登録入口**: ゲートモードではログイン / 登録フォームのみ表示（閉じるボタンなし）。ログイン後、ヘッダーの「ログアウト」で token を削除しゲートに戻る。

---

## コンプライアンスチェックリスト

- [x] バックエンド登録・ログインエンドポイント利用可能
- [x] パスワード暗号化保存と強度検証
- [x] JWT 発行と検証
- [x] フロントエンドリクエストが token を統一して送信（API インターセプター）
- [x] フロントエンドにログイン / 登録入口（`LoginRegister` コンポーネント + ヘッダーログイン入口）
