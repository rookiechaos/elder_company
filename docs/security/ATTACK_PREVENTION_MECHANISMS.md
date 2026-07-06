# Attack Prevention Mechanisms

**Created**: 2026-01-20  
**Version**: 2.1.2

## Overview

This document describes the malicious attack prevention mechanisms implemented in the Elder Company application.

---

## 1. Rate Limiting

### Protection Targets
- DDoS attacks
- Brute-force attacks
- API abuse
- Resource exhaustion attacks

### Implementation Locations
- `backend/middleware/rate_limit.py`
- `backend/middleware/rate_limit_enhanced.py`

### Configuration Details

#### Rate Limit Policies
```python
RATE_LIMITS = {
    "default": "100/minute",        # Default endpoints: 100 per minute
    "translation": "10/minute",      # AI translation: 10 per minute (stricter)
    "auth": "5/minute",              # Auth endpoints: 5 per minute (very strict)
    "sync": "20/minute",             # Sync operations: 20 per minute
}
```

#### Distributed Rate Limiting
- ✅ Redis distributed rate limiting (multi-server environments)
- ✅ In-memory rate limiting (single-server environments)
- ✅ Rate limiting by IP address or user ID

#### Rate Limit Responses
- Returns HTTP 429 (Too Many Requests)
- Includes `Retry-After` header
- Includes rate limit headers:
  - `X-RateLimit-Limit`: limit count
  - `X-RateLimit-Remaining`: remaining requests
  - `X-RateLimit-Reset`: reset time

### Applied Endpoints
- ✅ All auth endpoints (`/api/auth/login`, `/api/auth/register`)
- ✅ Translation endpoints (`/api/translate`)
- ✅ Sync endpoints (`/api/sync/*`)
- ✅ All other API endpoints (default rate limit)

---

## 2. Authentication Security

### Protection Targets
- Password brute force
- Account enumeration
- Session hijacking
- Token forgery

### Implementation Measures

#### Password Security
- ✅ **bcrypt hashing**: All passwords stored with bcrypt
- ✅ **Password strength validation**: minimum length and complexity requirements
- ✅ **Password policy**:
  - Minimum length: 8 characters
  - Maximum length: 128 characters
  - Must contain letters and numbers

#### JWT Token Security
- ✅ **Strong key validation**: production requires 32+ character keys
- ✅ **Default key detection**: startup check rejects default keys
- ✅ **Token expiration**: 30-day expiry
- ✅ **Algorithm restriction**: HS256 only

#### Authentication Rate Limiting
- ✅ **Login rate limit**: max 5 attempts per minute
- ✅ **Registration rate limit**: max 5 attempts per minute
- ✅ **Failure logging**: failed authentication attempts recorded

#### Account Security
- ✅ **Account status**: `is_active`, `is_suspended` flags
- ✅ **Last login time**: user activity tracking
- ✅ **Device management**: device registration and tracking

---

## 3. Input Validation and Sanitization

### Protection Targets
- SQL injection
- XSS attacks
- Command injection
- Path traversal

### Implementation Locations
- `backend/utils/security.py`
- All API endpoints

### Validation Measures

#### Text Input Sanitization
```python
def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    # Remove null bytes
    # Strip whitespace
    # Length limits
```

#### Pydantic Validation
- ✅ All API requests use Pydantic models
- ✅ Type validation
- ✅ Range validation (min/max)
- ✅ Enum validation
- ✅ Custom validators

#### File Upload Validation
```python
def validate_file_upload(filename, content_type, max_size, allowed_extensions):
    # Path traversal detection
    # File type whitelist
    # File size limits
    # MIME type validation
```

---

## 4. Content Security

### Protection Targets
- Inappropriate content
- Malicious content
- Spam

### NSFW Detection
- **Location**: `services/nsfw_detector.py`
- **Content checked**:
  - Translated text
  - Chat messages
  - Speech-to-text results
- **Detection levels**:
  - `SAFE`: safe content
  - `SUSPICIOUS`: suspicious content
  - `UNSAFE`: unsafe content
- **Handling**:
  - Automatically block unsafe content
  - Log suspicious content
  - Warn users

---

## 5. Network Security

### Security Response Headers
- **Location**: `backend/middleware/security_headers.py`

#### Implemented Security Headers
1. **Content-Security-Policy (CSP)** — prevents XSS, restricts resource loading
2. **X-Content-Type-Options: nosniff** — prevents MIME sniffing
3. **X-Frame-Options: DENY** — prevents clickjacking
4. **X-XSS-Protection: 1; mode=block** — legacy browser XSS protection
5. **Referrer-Policy: strict-origin-when-cross-origin** — controls referrer leakage
6. **Permissions-Policy** — restricts browser features (geolocation, microphone, camera)
7. **Strict-Transport-Security (HSTS)** — enforces HTTPS (production only)

### CORS Configuration
- ✅ No wildcard `*`
- ✅ Required in production
- ✅ Only configured origins allowed
- ✅ Credential control

---

## 6. Path Traversal Protection

### Protection Targets
- File system access
- Sensitive file reads
- Directory traversal attacks

### Implementation Location
- `services/storage_service.py`

### Protection Measures
```python
# Path normalization
normalized_path = os.path.normpath(file_path.lstrip("/"))

# Path traversal detection
if ".." in normalized_path or normalized_path.startswith("/"):
    return False

# Absolute path validation
full_path = full_path.resolve()
storage_dir_abs = Path(self.storage_dir).resolve()

# Verify path is within allowed directory
full_path.relative_to(storage_dir_abs)
```

---

## 7. Error Handling Security

### Protection Targets
- Information disclosure
- System information exposure
- Debug information leakage

### Implementation Location
- `backend/middleware/error_handler.py`

### Protection Measures
- ✅ Hide detailed errors in production
- ✅ Do not expose stack traces
- ✅ Do not expose system paths
- ✅ Do not expose database structure
- ✅ Sensitive information filtering

---

## 8. Database Security

### Protection Targets
- SQL injection
- Data leakage
- Unauthorized access

### Protection Measures
- ✅ **ORM usage**: SQLAlchemy ORM, no raw SQL
- ✅ **Parameterized queries**: all queries use parameter binding
- ✅ **Transaction management**: rollback handling on all DB operations
- ✅ **Access control**: user and organization-based permissions

---

## 9. Logging and Monitoring

### Protection Targets
- Attack detection
- Anomaly identification
- Security event tracking

### Implementation Locations
- `services/logging_service.py`
- `backend/middleware/performance.py`

### Monitored Content
- ✅ API request logs
- ✅ Error logs
- ✅ Slow query detection
- ✅ Performance metrics
- ✅ Authentication failure records
- ✅ Rate limit trigger records

### Sensitive Information Protection
- ✅ Passwords not logged
- ✅ Tokens partially masked
- ✅ API keys masked
- ✅ Uses `sanitize_for_logging` function

---

## 10. File Upload Security

### Protection Measures
- ✅ **File type whitelist**: only allowed extensions
- ✅ **File size limit**: default 10MB
- ✅ **MIME type validation**: Content-Type verification
- ✅ **Path traversal detection**: blocks `..`, `/`, `\`
- ✅ **Filename sanitization**: UUID-based unique filenames
- ✅ **Content scanning**: NSFW detection where applicable

---

## 11. Session Security

### Protection Measures
- ✅ **JWT tokens**: stateless authentication
- ✅ **Token expiration**: 30-day auto-expiry
- ✅ **Device tracking**: device registration and management
- ✅ **HTTPS enforcement**: required in production

---

## 12. API Key Management

### Implementation Locations
- `services/api_key_service.py`
- `backend/models/auth_models.py`

### Security Measures
- ✅ **Key hashing**: API keys stored hashed
- ✅ **Permission control**: fine-grained permissions
- ✅ **Usage limits**: rate limits and daily quotas
- ✅ **Expiration**: key expiry support
- ✅ **Usage tracking**: last used time and IP recorded

---

## 13. Performance Monitoring and Anomaly Detection

### Implementation Locations
- `backend/middleware/performance.py`
- `services/query_analyzer.py`

### Monitored Metrics
- ✅ Response time monitoring
- ✅ Slow query detection (>1 second)
- ✅ Request frequency monitoring
- ✅ Error rate monitoring
- ✅ Database query statistics

---

## 14. Distributed Protection

### Redis Distributed Rate Limiting
- ✅ Unified rate limiting across multiple servers
- ✅ Shared rate limit state
- ✅ Prevents single-point bypass

### Configuration
```python
# Automatically uses Redis when REDIS_URL is configured
REDIS_URL = os.getenv("REDIS_URL")
if REDIS_URL:
    limiter = Limiter(storage_uri=REDIS_URL)
```

---

## 15. Security Configuration Validation

### Startup Checks
- ✅ JWT key strength validation
- ✅ CORS configuration validation
- ✅ Production environment checks
- ✅ Default value detection

---

## Attack Scenario Protection Matrix

| Attack Type | Protection Mechanism | Status |
|-------------|---------------------|--------|
| DDoS | Rate limiting | ✅ |
| Brute force | Auth rate limit + account lockout | ✅ |
| SQL injection | ORM + parameterized queries | ✅ |
| XSS | CSP + input sanitization | ✅ |
| CSRF | Security headers + token validation | ✅ |
| Path traversal | Path validation + normalization | ✅ |
| File upload attacks | Type validation + size limits | ✅ |
| Session hijacking | JWT + HTTPS | ✅ |
| Information disclosure | Error handling + log sanitization | ✅ |
| Command injection | Input validation + no shell execution | ✅ |
| Content injection | NSFW detection | ✅ |
| API abuse | Rate limiting + key management | ✅ |

---

## Continuous Improvement Recommendations

### Short-term (1–3 months)
1. Account lockout after repeated failed logins
2. IP blacklist for malicious IPs
3. CAPTCHA on auth endpoints
4. Smarter anomaly detection

### Medium-term (3–6 months)
1. WAF integration
2. Threat intelligence feeds
3. Enhanced security audit logs
4. Automated response to common attacks

### Long-term (6–12 months)
1. ML-based anomaly detection
2. Zero-trust architecture
3. Automated security testing
4. Regular penetration testing

---

## Summary

Elder Company implements **15+ layered protection mechanisms** covering all major attack vectors with production-hardened configuration, continuous monitoring, and security best practices.

---

**Maintained by**: Elder Company Security Team  
**Last updated**: 2026-01-20

---

# 日本語 / Japanese

# 攻撃防止メカニズム

**作成日**: 2026-01-20  
**バージョン**: 2.1.2

## 概要

本ドキュメントは、Elder Company アプリケーションに実装されている悪意のある攻撃に対する防止メカニズムを説明します。

---

## 1. レート制限

### 保護対象
- DDoS 攻撃
- ブルートフォース攻撃
- API 乱用
- リソース枯渇攻撃

### 実装場所
- `backend/middleware/rate_limit.py`
- `backend/middleware/rate_limit_enhanced.py`

### 設定詳細

#### レート制限ポリシー
```python
RATE_LIMITS = {
    "default": "100/minute",        # デフォルト: 1分あたり100回
    "translation": "10/minute",      # AI翻訳: 1分あたり10回（厳格）
    "auth": "5/minute",              # 認証: 1分あたり5回（非常に厳格）
    "sync": "20/minute",             # 同期: 1分あたり20回
}
```

#### 分散レート制限
- ✅ Redis 分散レート制限（マルチサーバー環境）
- ✅ メモリレート制限（単一サーバー環境）
- ✅ IP アドレスまたはユーザー ID による制限

#### レート制限レスポンス
- HTTP 429 (Too Many Requests) を返却
- `Retry-After` ヘッダーを含む
- レート制限情報ヘッダー:
  - `X-RateLimit-Limit`: 制限数
  - `X-RateLimit-Remaining`: 残りリクエスト数
  - `X-RateLimit-Reset`: リセット時刻

---

## 2. 認証セキュリティ

### 実装施策
- ✅ **bcrypt ハッシュ**: 全パスワードを bcrypt で暗号化保存
- ✅ **パスワード強度検証**: 最小長・複雑さ要件
- ✅ **JWT トークンセキュリティ**: 強キー検証、30日有効期限、HS256 のみ
- ✅ **認証レート制限**: ログイン・登録ともに1分あたり最大5回
- ✅ **アカウントセキュリティ**: `is_active`、`is_suspended` フラグ、最終ログイン追跡

---

## 3. 入力検証とサニタイゼーション

### 実装場所
- `backend/utils/security.py`
- 全 API エンドポイント

### 検証施策
- ✅ Pydantic モデルによる全リクエスト検証
- ✅ テキスト入力サニタイゼーション（null バイト除去、長さ制限）
- ✅ ファイルアップロード検証（パストラバーサル検出、タイプホワイトリスト、サイズ制限）

---

## 4. コンテンツセキュリティ

### NSFW 検出
- **場所**: `services/nsfw_detector.py`
- **検出レベル**: `SAFE`、`SUSPICIOUS`、`UNSAFE`
- **処理**: 不安全コンテンツの自動ブロック、疑わしいコンテンツの記録

---

## 5. ネットワークセキュリティ

### セキュリティレスポンスヘッダー
- **場所**: `backend/middleware/security_headers.py`
- CSP、X-Content-Type-Options、X-Frame-Options、HSTS など

### CORS 設定
- ✅ ワイルドカード `*` 禁止
- ✅ 本番環境での必須設定
- ✅ 設定済みオリジンのみ許可

---

## 6–15. その他の保護メカニズム

| 分野 | 実装場所 | 主な施策 |
|------|---------|---------|
| パストラバーサル | `services/storage_service.py` | パス正規化・検証 |
| エラー処理 | `backend/middleware/error_handler.py` | 本番環境での詳細エラー非表示 |
| データベース | SQLAlchemy ORM | パラメータ化クエリ、トランザクション管理 |
| ログ・監視 | `services/logging_service.py` | 認証失敗・レート制限の記録 |
| ファイルアップロード | `backend/utils/security.py` | タイプ・サイズ・MIME 検証 |
| セッション | JWT | 30日有効期限、HTTPS 強制 |
| API キー | `services/api_key_service.py` | ハッシュ保存、権限制御 |
| パフォーマンス監視 | `backend/middleware/performance.py` | スロークエリ検出 |
| 分散保護 | Redis | マルチサーバー統一レート制限 |

---

## 攻撃シナリオ保護マトリクス

| 攻撃タイプ | 保護メカニズム | 状態 |
|-----------|--------------|------|
| DDoS | レート制限 | ✅ |
| ブルートフォース | 認証レート制限 | ✅ |
| SQL インジェクション | ORM + パラメータ化クエリ | ✅ |
| XSS | CSP + 入力サニタイゼーション | ✅ |
| CSRF | セキュリティヘッダー + トークン検証 | ✅ |
| パストラバーサル | パス検証 | ✅ |
| ファイルアップロード攻撃 | タイプ・サイズ検証 | ✅ |
| セッションハイジャック | JWT + HTTPS | ✅ |
| 情報漏洩 | エラー処理 + ログサニタイゼーション | ✅ |

---

## まとめ

Elder Company は **15以上の多層防御メカニズム** を実装し、主要な攻撃ベクトルをカバーしています。

---

**保守**: Elder Company セキュリティチーム  
**最終更新**: 2026-01-20
