# Live API Testing Guide

> HTTP integration tests against a running backend server.

**Last updated:** 2026-07-04

---

## Quick start

### 1. Start the server

```bash
cd backend
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`.

### 2. Run tests

**Recommended — pytest integration suite:**

```bash
# From repository root
pytest tests/integration/test_real_api.py -v
```

**Or direct script:**

```bash
python tests/integration/test_real_api.py --url http://localhost:8000
```

### 3. What is tested

1. Health check
2. User registration
3. User login
4. Translation (AI API)
5. Data export (GDPR)
6. Help center
7. Feedback
8. Support tickets
9. Analytics
10. Monitoring
11. Deletion summary

---

## Requirements

```bash
pip install -r backend/requirements.txt
```

Dependencies: `fastapi`, `uvicorn`, `requests`, `sqlalchemy`, `pydantic`

### Environment

```bash
cp backend/env.example do-not-upload/env/.env
```

Minimum configuration:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here

DATABASE_URL=sqlite:///./elder_company.db
JWT_SECRET_KEY=your-secret-key-here
```

---

## Output

**Success:**
```
✅ Health check passed: healthy
✅ Login: user_12345
✅ Translation: こんにちは、お元気ですか？
✅ Data export: 1234 bytes
```

**Summary:**
```
============================================================
Summary: 8 passed, 2 failed, 1 skipped (11 total)
============================================================
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port in use | `lsof -i :8000` |
| 401 Unauthorized | Login first for token |
| 500 Internal Server Error | Check server logs |
| Connection refused | Start backend |
| DB errors | Ensure `backend/elder_company.db` is writable; run `init_database()` |

---

## CI/CD

```yaml
- name: Start server
  run: |
    cd backend
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    sleep 5

- name: Run tests
  run: pytest tests/integration/test_real_api.py -v
```

---

## Notes

- Creates real users and data — use a test database
- Requires valid AI provider API key for translation tests
- Slower than internal TestClient tests (network + AI latency)

See also [README_INTERNAL_TESTING.md](./README_INTERNAL_TESTING.md) for port-free tests.

---

# ライブ API テストガイド

> 起動中のバックエンドに対する HTTP 統合テスト。

**最終更新:** 2026-07-04

---

## クイックスタート

```bash
cd backend && uvicorn main:app --reload
pytest tests/integration/test_real_api.py -v
```

---

## テスト内容

ヘルスチェック、認証、翻訳、データエクスポート、ヘルプ、フィードバック、サポート、分析、監視、削除プレビュー（計 11 項目）。

---

## 要件

```bash
pip install -r backend/requirements.txt
cp backend/env.example do-not-upload/env/.env
```

`AI_PROVIDER` / API キー / `JWT_SECRET_KEY` を設定。

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| 401 | ログインしてトークン取得 |
| 接続拒否 | バックエンド起動 |
| DB エラー | `backend/elder_company.db` の書き込み権限 |

---

## 注意

実データ作成 · AI キー必要 · 内部テストより遅い。

ポート不要テスト: [README_INTERNAL_TESTING.md](./README_INTERNAL_TESTING.md)
