# Elder Company Application Security

**Version**: 2.1.2  
**Created**: 2026-01-20  
**Last updated**: 2026-01-20

---

## Table of Contents

1. [Security Architecture Overview](#security-architecture-overview)
2. [Frontend Security](#frontend-security)
3. [Backend API Security](#backend-api-security)
4. [Network Security](#network-security)
5. [Data Security](#data-security)
6. [Application Layer Security](#application-layer-security)
7. [Deployment Security](#deployment-security)
8. [Monitoring and Response](#monitoring-and-response)

---

## Security Architecture Overview

### Multi-Layer Defense Architecture

```
┌─────────────────────────────────────────┐
│         Client Layer                     │
│  - Input validation                      │
│  - XSS protection                        │
│  - CSRF protection                       │
└──────────────┬──────────────────────────┘
               │ HTTPS/TLS
┌──────────────▼──────────────────────────┐
│         Network Transport Layer          │
│  - TLS/SSL encryption                    │
│  - Certificate validation                │
│  - Security headers                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         API Gateway Layer                │
│  - Rate limiting                         │
│  - Authentication & authorization        │
│  - Request validation                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Application Service Layer        │
│  - Business logic validation             │
│  - Data sanitization                     │
│  - Anomaly detection                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Storage Layer               │
│  - Data encryption                       │
│  - Access control                        │
│  - Backup and recovery                   │
└─────────────────────────────────────────┘
```

---

## Frontend Security

### 1. Input Validation and Sanitization

#### Implementation Locations
- **Translation input**: `frontend/src/components/TranslationInterface.jsx`
- **User input**: all form components
- **Game input**: `game/frontend/src/utils/security.js`

#### Protection Measures
- ✅ All user input validated
- ✅ Text length limits (DoS prevention)
- ✅ Special character filtering
- ✅ HTML tag escaping
- ✅ JavaScript code filtering

### 2. XSS Protection

#### Content Security Policy (CSP)
- **Location**: `frontend/index.html`, `game/frontend/index.html`

#### React Auto-Escaping
- ✅ React escapes all user input by default
- ✅ Avoid `dangerouslySetInnerHTML`
- ✅ All dynamic content sanitized

### 3. CSRF Protection
- ✅ CSRF token retrieval and validation
- ✅ All POST/PUT/DELETE requests include token
- ✅ SameSite cookie settings

### 4. Session Security
- ✅ JWT stored in httpOnly cookies (set by backend)
- ✅ Frontend does not store sensitive tokens directly
- ✅ Automatic token refresh

### 5. Frontend Route Security
- ✅ Protected routes check token
- ✅ Unauthenticated users redirected to login
- ✅ Role-based permission checks

---

## Backend API Security

### 1. Authentication and Authorization

#### JWT Authentication
- **Location**: `backend/api/auth_routes.py`
- ✅ All API endpoints require JWT (except public endpoints)
- ✅ 30-day token expiry
- ✅ Strong key validation (32+ chars in production)

#### Permission Control
- **Location**: `backend/middleware/permissions.py`
- ✅ Role-based access control (RBAC)
- ✅ Resource-level permission validation
- ✅ Users can only access their own data

### 2. Rate Limiting
- **Location**: `backend/middleware/rate_limit.py`
- ✅ Redis distributed rate limiting
- ✅ Rate limiting by IP and user ID

### 3. Input Validation
- ✅ Pydantic model validation on all routes
- ✅ Input sanitization via `backend/utils/security.py`

### 4. SQL Injection Protection
- ✅ SQLAlchemy ORM with parameterized queries

### 5. File Upload Security
- **Location**: `backend/utils/security.py`, `backend/api/voice_routes.py`
- ✅ File type whitelist, 10MB size limit, path traversal protection

### 6. Content Security
- **Location**: `services/nsfw_detector.py`
- ✅ Automatic inappropriate content detection and blocking

---

## Network Security

### HTTPS/TLS
- ✅ HTTPS required in production
- ✅ TLS 1.2+ required

### CORS Configuration
- **Location**: `backend/main.py`
- ✅ Production warnings for unconfigured CORS

### Security Response Headers
- **Location**: `backend/middleware/security_headers.py`
- ✅ X-Content-Type-Options, X-Frame-Options, CSP, HSTS (production)

---

## Data Security

### Password Security
- **Location**: `services/auth_service.py`
- ✅ bcrypt hashing, password strength validation (8+ chars)

### Sensitive Data Protection
- **Location**: `backend/utils/security.py`
- ✅ `sanitize_for_logging()` masks passwords, tokens, API keys

### Data Access Control
- ✅ Multi-tenant data isolation
- ✅ User data isolation

---

## Application Layer Security

### Error Handling
- **Location**: `backend/middleware/error_handler.py`
- ✅ Hide detailed errors in production

### Logging Security
- **Location**: `services/logging_service.py`
- ✅ Sensitive information automatically filtered

### Performance Monitoring
- **Location**: `backend/middleware/performance.py`
- ✅ Request performance monitoring, slow query detection

---

## Deployment Security

### Environment Variables
- ✅ `do-not-upload/env/.env` in `.gitignore`
- ✅ Use `env.example` as template
- ✅ Strong keys required in production

### Dependencies
- ✅ Managed via `requirements.txt`
- ⏳ Dependency vulnerability scanning (planned)

---

## Monitoring and Response

### Security Event Logging
- **Location**: `services/logging_service.py`
- ✅ Auth failures, rate limit triggers, NSFW blocks, file upload rejections

---

## Security Checklist

### Frontend ✅
- [x] Input validation and sanitization
- [x] XSS protection (CSP)
- [x] CSRF protection
- [x] Session security (httpOnly cookie)
- [x] Route protection

### Backend ✅
- [x] JWT authentication
- [x] RBAC permissions
- [x] Rate limiting
- [x] Pydantic input validation
- [x] SQL injection protection
- [x] File upload validation
- [x] NSFW content detection
- [x] Secure error handling
- [x] Log sanitization

---

## Related Documentation

- [Security Audit](./SECURITY_AUDIT.md)
- [Security Improvements](./SECURITY_IMPROVEMENTS.md)

---

**Maintained by**: Elder Company Security Team  
**Security status**: ✅ Production ready (some features pending deployment)

---

# 日本語 / Japanese

# Elder Company アプリケーションセキュリティ

**バージョン**: 2.1.2  
**作成日**: 2026-01-20  
**最終更新**: 2026-01-20

---

## 目次

1. [セキュリティアーキテクチャ概要](#セキュリティアーキテクチャ概要)
2. [フロントエンドセキュリティ](#フロントエンドセキュリティ)
3. [バックエンド API セキュリティ](#バックエンド-api-セキュリティ)
4. [ネットワークセキュリティ](#ネットワークセキュリティ)
5. [データセキュリティ](#データセキュリティ)
6. [アプリケーション層セキュリティ](#アプリケーション層セキュリティ)
7. [デプロイメントセキュリティ](#デプロイメントセキュリティ)
8. [監視と対応](#監視と対応)

---

## セキュリティアーキテクチャ概要

Elder Company は **多層防御アーキテクチャ** を採用しています：

- **クライアント層**: 入力検証、XSS/CSRF 保護
- **ネットワーク層**: TLS/SSL 暗号化、セキュリティヘッダー
- **API ゲートウェイ層**: レート制限、認証・認可
- **アプリケーション層**: ビジネスロジック検証、データサニタイゼーション
- **データ層**: 暗号化、アクセス制御、バックアップ

---

## フロントエンドセキュリティ

- ✅ 全ユーザー入力の検証とサニタイゼーション
- ✅ CSP による XSS 保護
- ✅ CSRF トークン機構
- ✅ httpOnly Cookie による JWT 保存
- ✅ 認証が必要なルートの保護

---

## バックエンド API セキュリティ

- **JWT 認証**: `backend/api/auth_routes.py`
- **権限制御**: `backend/middleware/permissions.py`（RBAC）
- **レート制限**: `backend/middleware/rate_limit.py`
- **入力検証**: Pydantic モデル + `backend/utils/security.py`
- **SQL インジェクション防止**: SQLAlchemy ORM
- **ファイルアップロード**: タイプ・サイズ・パストラバーサル検証
- **コンテンツセキュリティ**: `services/nsfw_detector.py`

---

## ネットワークセキュリティ

- ✅ 本番環境での HTTPS 強制
- ✅ CORS 設定（`backend/main.py`）
- ✅ セキュリティレスポンスヘッダー（`backend/middleware/security_headers.py`）

---

## データセキュリティ

- ✅ bcrypt パスワードハッシュ（`services/auth_service.py`）
- ✅ ログ内の機密情報マスキング（`backend/utils/security.py`）
- ✅ マルチテナント・ユーザーデータ分離

---

## デプロイメントセキュリティ

- ✅ `do-not-upload/env/.env` は `.gitignore` に含まれる
- ✅ `env.example` をテンプレートとして使用
- ✅ 本番環境では強キーが必須

---

## セキュリティチェックリスト

### フロントエンド ✅
- [x] 入力検証とサニタイゼーション
- [x] XSS 保護（CSP）
- [x] CSRF 保護
- [x] セッションセキュリティ
- [x] ルート保護

### バックエンド ✅
- [x] JWT 認証
- [x] RBAC 権限制御
- [x] レート制限
- [x] 入力検証
- [x] SQL インジェクション防止
- [x] ファイルアップロード検証
- [x] NSFW 検出
- [x] 安全なエラー処理
- [x] ログサニタイゼーション

---

**保守**: Elder Company セキュリティチーム  
**セキュリティ状態**: ✅ 本番準備完了（一部機能はデプロイ時設定）
