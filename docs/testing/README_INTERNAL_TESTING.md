# Internal API Testing Guide (No Open Ports)

> FastAPI `TestClient` in-process tests — no HTTP server or exposed ports.

**Last updated:** 2026-07-04

---

## Overview

`tests/integration/test_internal_api.py` uses FastAPI `TestClient`. All tests run in-process with **no HTTP server or open ports**.

## Quick start

```bash
# From repository root
pytest tests/integration/test_internal_api.py -v

# Or via helper script (chatbot conda env)
./scripts/run_test_in_chatbot.sh
```

No server startup required.

## What is tested

1. **Health check** — server and dependency status
2. **User registration** — create test user
3. **User login** — obtain auth token
4. **Translation** — AI translation API (when API key configured)
5. **Data export** — GDPR-compliant export
6. **Help center** — articles and FAQ
7. **Feedback** — user feedback system
8. **Support tickets** — customer support
9. **Analytics** — user behavior analytics
10. **Monitoring** — system monitoring
11. **Deletion summary** — account deletion preview
12. **Service layer** — direct service calls

## How it works

### TestClient

FastAPI `TestClient`:

- Simulates HTTP requests in-process
- Does not start an actual HTTP server
- Calls route handlers directly
- Returns standard HTTP response objects

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.get("/health")  # in-process, no network
```

### Database isolation

Tests use an isolated database session:

```python
db = SessionLocal()

def override_get_db():
    yield db

app.dependency_overrides[get_db] = override_get_db
```

## Internal vs live API tests

| Feature | Internal tests | Live API tests |
|---------|----------------|----------------|
| Server required | No | Yes |
| Exposed ports | No | Yes (8000) |
| Network overhead | None | Yes |
| Speed | Fast | Slower |
| CI/CD friendly | Yes | Needs setup |
| Tests network layer | No | Yes |
| Tests load balancing | No | Yes |

## Requirements

```bash
pip install -r backend/requirements.txt
```

Main dependencies: `fastapi`, `httpx`, `sqlalchemy`, `pydantic`

### Environment variables (optional)

For AI translation tests, configure keys in `do-not-upload/env/.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
```

Most tests run without API keys.

## Sample output

```
============================================================
Internal API tests (no open ports)
============================================================

✅ Health check passed: healthy
✅ User registration: testuser_internal
✅ Login: user_12345
⚠️  AI service unavailable (API key not configured)

============================================================
Summary: 12 passed, 0 failed
============================================================
```

**Latest (2025-01-19):** all 12 tests passing after rate-limit, model field, and logging fixes.

## Troubleshooting

**Database errors:** remove `backend/elder_company.db` and re-run — DB is recreated automatically.

**Import errors:** run from repo root with `PYTHONPATH=backend pytest tests/integration/test_internal_api.py -v`.

**Missing dependencies:** `pip install -r backend/requirements.txt`

## CI/CD

```yaml
- name: Run internal tests
  run: pytest tests/integration/test_internal_api.py -v
```

## Extending tests

Add methods in `tests/integration/test_internal_api.py` and register them in `run_all_tests()`.

Direct service example:

```python
from services.translation_service import TranslationService

service = TranslationService(db)
result = service.translate("Hello", "en", "ja")
```

## Performance

Internal tests are typically **5–10× faster** than live HTTP tests (~2–5 s vs ~10–30 s for comparable coverage).

## Best practices

1. **Development** — use internal tests for fast feedback
2. **CI/CD** — use internal tests for quality gates
3. **Pre-deploy** — run live API tests for end-to-end validation
4. **Debugging** — use internal tests to isolate logic issues

## Notes

- Creates a real SQLite DB (`backend/elder_company.db`)
- DB re-initialized each run
- Does not test concurrent requests or actual HTTP/TLS

For network-layer, load-balancer, or deployment validation, use `tests/integration/test_real_api.py`.

---

# 内部 API テストガイド（ポート不要）

> FastAPI `TestClient` によるプロセス内テスト。HTTP サーバー・ポート公開不要。

**最終更新:** 2026-07-04

---

## 概要

`tests/integration/test_internal_api.py` は FastAPI `TestClient` を使用。すべてプロセス内で実行。

## クイックスタート

```bash
pytest tests/integration/test_internal_api.py -v
./scripts/run_test_in_chatbot.sh
```

## テスト内容

ヘルスチェック、認証、翻訳、データエクスポート、ヘルプ、フィードバック、サポート、分析、監視、削除プレビュー、サービス層（計 12 項目）。

## 内部テスト vs ライブ API

| 項目 | 内部 | ライブ |
|------|------|--------|
| サーバー | 不要 | 必要 |
| ポート | 不要 | 8000 |
| 速度 | 速い | 遅い |
| CI | 向き | 設定要 |

## 要件

```bash
pip install -r backend/requirements.txt
```

AI 翻訳テスト用: `do-not-upload/env/.env` に API キーを設定（任意）。

## トラブルシューティング

- DB エラー: `backend/elder_company.db` を削除して再実行
- インポート: リポジトリルートから `PYTHONPATH=backend pytest ...`

## CI

```yaml
run: pytest tests/integration/test_internal_api.py -v
```

## 注意

- SQLite DB を作成する
- 並行リクエスト・実 HTTP はテストしない
- ネットワーク層の検証は `tests/integration/test_real_api.py` を使用
