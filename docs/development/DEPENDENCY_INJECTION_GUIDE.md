# Dependency Injection and API Development Guide

**Last updated**: 2026-01-20  
**Version**: 2.0

---

## Overview

This document describes dependency injection patterns and best practices for Elder Company backend API development. All new API endpoints should follow these patterns for consistency, maintainability, and testability.

---

## Table of Contents

1. [Dependency Injection Basics](#dependency-injection-basics)
2. [Authentication Dependencies](#authentication-dependencies)
3. [Service Dependencies](#service-dependencies)
4. [Error Handling Decorator](#error-handling-decorator)
5. [Complete Examples](#complete-examples)
6. [Migration Guide](#migration-guide)
7. [Best Practices](#best-practices)

---

## Dependency Injection Basics

Dependency Injection (DI) automatically injects dependencies via function parameters rather than creating them inside functions.

**Benefits**:
- ✅ Improved testability (easy to mock)
- ✅ Reduced coupling
- ✅ Unified dependency management

```python
from fastapi import Depends

@router.post("/endpoint")
async def my_endpoint(
    service: MyService = Depends(get_service_dependency)
):
    result = service.do_something()
    return result
```

---

## Authentication Dependencies

### `require_auth` — Required Authentication

```python
from dependencies import require_auth

@router.post("/protected")
async def protected_endpoint(
    current_user: dict = Depends(require_auth)
):
    user_id = current_user["user_id"]
    org_id = current_user.get("org_id")
```

- ✅ Automatic auth check
- ✅ Returns 401 if not authenticated
- ✅ `current_user` is guaranteed to be `dict`, never `None`

### `get_optional_user` — Optional Authentication

```python
from dependencies import get_optional_user

@router.get("/public")
async def public_endpoint(
    current_user: Optional[dict] = Depends(get_optional_user)
):
    if current_user:
        user_id = current_user["user_id"]
```

---

## Service Dependencies

All services should be injected via dependency functions in `dependencies.py`:

```python
from dependencies import get_emergency_service_dependency
from services.emergency_service import EmergencyService

@router.post("/record")
async def record_emergency(
    request: RecordEmergencyRequest,
    current_user: dict = Depends(require_auth),
    emergency_service: EmergencyService = Depends(get_emergency_service_dependency)
):
    record = emergency_service.record_emergency(...)
    return {"record": record}
```

### Available Service Dependencies

- `get_emergency_service_dependency` → `EmergencyService`
- `get_night_mode_service_dependency` → `NightModeService`
- `get_emotion_service_dependency` → `EmotionService`
- `get_task_service_dependency` → `TaskService`
- `get_customer_service_dependency` → `CustomerService`
- `get_sync_service_dependency` → `SyncService`
- And all other services

### ❌ Wrong — Direct Instantiation

```python
# ❌ Don't do this
service = MyService(db)
```

### ✅ Correct — Dependency Injection

```python
# ✅ Do this
service: MyService = Depends(get_service_dependency)
```

---

## Error Handling Decorator

```python
from middleware.api_decorators import handle_api_errors

@router.post("/endpoint")
@handle_api_errors
async def my_endpoint(...):
    service.do_something()
    return {"result": "success"}
```

**Automatic exception mapping**:
- `ValidationError` → 400
- `NotFoundError` → 404
- `ConflictError` → 409
- `AuthenticationError` → 401
- Other → 500

---

## Complete Example

```python
from fastapi import APIRouter, Depends
from dependencies import require_auth, get_task_service_dependency
from services.task_service import TaskService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def create_task(
    request: CreateTaskRequest,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    task = task_service.create_task(
        caregiver_id=current_user["user_id"],
        title=request.title,
        task_type=request.task_type,
        org_id=current_user.get("org_id")
    )
    return {"message": "Task created successfully", "task": task}
```

---

## Migration Guide

### Step 1: Update Imports

**Old**:
```python
from backend.api.auth_routes import get_current_user
from services.task_service import get_task_service
```

**New**:
```python
from dependencies import require_auth, get_task_service_dependency
from services.task_service import TaskService
from middleware.api_decorators import handle_api_errors
```

### Step 2: Update Function Signatures

Remove `if not current_user` checks, try-except blocks, and direct service instantiation.

### Step 3: Apply Decorators

Add `@handle_api_errors` and use `@rate_limit` where appropriate.

---

## Best Practices

1. **Decorator order**: `@router` → `@rate_limit` → `@handle_api_errors`
2. **Type annotations**: always annotate service dependencies
3. **Docstrings**: document all endpoints
4. **Service methods**: throw exceptions, don't return error codes

---

## FAQ

**Q: When to use `require_auth` vs `get_optional_user`?**
- `require_auth`: endpoint requires authentication
- `get_optional_user`: supports anonymous access with optional enhanced permissions

**Q: Services without database sessions?**
- Use dependency functions without `db` parameter (e.g., `StorageService`)

**Q: Multiple services?**
- Inject multiple `Depends()` parameters

---

## Related Documentation

- [Code Design Review](../development/CODE_DESIGN_REVIEW.md)
- [Code Improvements Implemented](../development/CODE_IMPROVEMENTS_IMPLEMENTED.md)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

---

**Last updated**: 2026-01-20  
**Maintained by**: Elder Company Development Team

---

# 日本語 / Japanese

# 依存性注入と API 開発ガイド

**最終更新**: 2026-01-20  
**バージョン**: 2.0

---

## 概要

Elder Company バックエンド API 開発における依存性注入（DI）パターンとベストプラクティスを説明します。新規 API エンドポイントはすべてこのパターンに従ってください。

---

## 依存性注入の基本

FastAPI の `Depends()` により、関数内で依存関係を作成するのではなく、パラメータとして自動注入します。

**利点**:
- ✅ テスト容易性（モック化が簡単）
- ✅ 結合度の低減
- ✅ 依存関係の一元管理

---

## 認証依存関係

### `require_auth` — 必須認証

```python
from dependencies import require_auth

@router.post("/protected")
async def protected_endpoint(
    current_user: dict = Depends(require_auth)
):
    user_id = current_user["user_id"]
```

- 未認証時は自動的に 401 を返却
- `current_user` は常に `dict` 型（`None` にならない）

### `get_optional_user` — 任意認証

匿名アクセスをサポートするエンドポイント用。`current_user` は `None` の可能性あり。

---

## サービス依存関係

全サービスは `dependencies.py` の依存関数経由で注入：

```python
emergency_service: EmergencyService = Depends(get_emergency_service_dependency)
```

### ❌ 誤った方法
```python
service = MyService(db)  # 直接インスタンス化しない
```

### ✅ 正しい方法
```python
service: MyService = Depends(get_service_dependency)
```

---

## エラー処理デコレータ

```python
@handle_api_errors
async def my_endpoint(...):
    service.do_something()
```

- `ValidationError` → 400
- `NotFoundError` → 404
- `ConflictError` → 409
- `AuthenticationError` → 401
- その他 → 500

---

## 完全な例

```python
@router.post("")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def create_task(
    request: CreateTaskRequest,
    current_user: dict = Depends(require_auth),
    task_service: TaskService = Depends(get_task_service_dependency)
):
    task = task_service.create_task(...)
    return {"message": "Task created successfully", "task": task}
```

---

## 移行ガイド

1. インポートを `dependencies` モジュールに更新
2. `if not current_user` チェックと try-except を削除
3. `@handle_api_errors` デコレータを適用

---

## ベストプラクティス

1. デコレータ順序: `@router` → `@rate_limit` → `@handle_api_errors`
2. 型アノテーションを常に使用
3. 全エンドポイントに docstring を追加
4. サービスメソッドは例外をスロー（エラーコードを返さない）

---

## 関連ドキュメント

- [コード設計レビュー](../development/CODE_DESIGN_REVIEW.md)
- [コード改善実施レポート](../development/CODE_IMPROVEMENTS_IMPLEMENTED.md)

---

**最終更新**: 2026-01-20  
**保守**: Elder Company 開発チーム
