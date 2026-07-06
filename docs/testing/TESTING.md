# Testing Guide

> Detailed testing instructions for Elder Company.

**Last updated:** 2026-07-04

---

## Table of contents

- [Test files](#test-files)
- [Running tests](#running-tests)
- [Requirements](#requirements)
- [Output examples](#output-examples)
- [Troubleshooting](#troubleshooting)
- [CI integration](#ci-integration)
- [Coverage](#coverage)
- [Stress testing](#stress-testing)

---

## Test files

| Script | Purpose |
|--------|---------|
| `tests/integration/test_internal_api.py` | Internal API tests (recommended, no open ports) |
| `tests/test_api.py` | Live HTTP API smoke test (server required) |
| `tests/test_services.py` | Translation service smoke test (no HTTP) |
| `tests/integration/test_real_api.py` | Live API integration tests |
| `scripts/stress_test.py` | Load / stress testing |

---

## Running tests

### 1. Internal API tests (recommended)

Fastest and safest — no HTTP server or open ports.

```bash
# From repository root
pytest tests/integration/test_internal_api.py -v

# Or via helper script (chatbot conda env)
./scripts/run_test_in_chatbot.sh
```

**Benefits**

- No server startup required
- No exposed ports
- Faster than live HTTP tests
- CI/CD friendly

**Covers:** health check, auth, translation, data export (JSON/CSV), help center, feedback, support tickets, analytics, monitoring, account deletion summary, direct service calls.

See also [README_INTERNAL_TESTING.md](./README_INTERNAL_TESTING.md).

---

### 2. API smoke test (`tests/test_api.py`)

Tests HTTP endpoints against a running backend.

```bash
cd backend && uvicorn main:app --reload

# Another terminal, from repo root
python tests/test_api.py
```

**Covers:** health, AI provider info, languages, care terms, ja↔en translation, care-context translation, chat translation, long text, empty text validation, same-language handling.

---

### 3. Service-layer test (`tests/test_services.py`)

Tests translation logic without HTTP.

```bash
cp backend/env.example do-not-upload/env/.env   # first time only
python tests/test_services.py
```

**Covers:** env check, AI provider init, service init, basic translation, same-language handling, care context, conversation translation, empty text.

---

## Requirements

1. **Running server** — only for `tests/test_api.py` at `http://localhost:8000`
2. **API keys** — configure at least one provider in `do-not-upload/env/.env` (OpenAI, Claude, or Gemini)
3. **Dependencies** — `pip install -r backend/requirements.txt`

---

## Output examples

### Success

```
============================================================
Elder Company — API smoke test
============================================================

Results: 12/12 passed
All tests passed.
```

### Failure

Check that the backend is running, `do-not-upload/env/.env` has valid keys, and the AI provider is reachable.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Cannot connect | Start backend: `cd backend && uvicorn main:app --reload` |
| API key errors | Verify `do-not-upload/env/.env` and `AI_PROVIDER` match |
| Translation 503 | Check network, provider status, quota |
| Service test fails | Run from repo root; confirm dependencies installed |

---

## CI integration

```yaml
- name: Run API Tests
  run: |
    cd backend
    uvicorn main:app &
    sleep 5
    cd ..
    python tests/test_api.py
```

---

## Coverage

- Major API endpoints
- ja↔en translation and edge cases
- Auth, feedback, support, monitoring, analytics
- GDPR data export

**Stats (v2.1.2):** internal API 12/12 · live API 11/11 · service layer passing

---

## Stress testing

See [STRESS_TEST_GUIDE.md](./STRESS_TEST_GUIDE.md).

```bash
cd backend && uvicorn main:app --reload
python scripts/stress_test.py
python scripts/stress_test.py --concurrent 50 --requests 1000 --endpoint /api/translate
```

---

## Future work

- Expanded pytest unit coverage
- Performance benchmarks
- E2E browser tests
- Long-running stability tests

---

# テストガイド

> Elder Company のテスト手順。

**最終更新:** 2026-07-04

---

## 目次

- [テストファイル](#テストファイル)
- [テスト実行](#テスト実行)
- [要件](#要件)
- [出力例](#出力例)
- [トラブルシューティング](#トラブルシューティング)
- [CI 連携](#ci-連携)
- [カバレッジ](#カバレッジ)
- [負荷テスト](#負荷テスト)

---

## テストファイル

| スクリプト | 用途 |
|-----------|------|
| `tests/integration/test_internal_api.py` | 内部 API テスト（推奨・ポート不要） |
| `tests/test_api.py` | ライブ HTTP スモークテスト |
| `tests/test_services.py` | 翻訳サービス直接テスト |
| `tests/integration/test_real_api.py` | ライブ API 統合テスト |
| `scripts/stress_test.py` | 負荷・ストレステスト |

---

## テスト実行

### 1. 内部 API テスト（推奨）

```bash
pytest tests/integration/test_internal_api.py -v
./scripts/run_test_in_chatbot.sh
```

サーバー起動不要・ポート公開不要・CI 向き。

詳細: [README_INTERNAL_TESTING.md](./README_INTERNAL_TESTING.md)

### 2. API スモークテスト

```bash
cd backend && uvicorn main:app --reload
python tests/test_api.py
```

### 3. サービス層テスト

```bash
cp backend/env.example do-not-upload/env/.env
python tests/test_services.py
```

---

## 要件

1. ライブ API テストのみバックエンド起動が必要
2. `do-not-upload/env/.env` に API キーを設定
3. `pip install -r backend/requirements.txt`

---

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| 接続不可 | バックエンドを起動 |
| API キー | `do-not-upload/env/.env` を確認 |
| 翻訳 503 | ネットワーク・プロバイダ・クォータを確認 |

---

## CI 連携

リポジトリルートから `python tests/test_api.py` を実行。

---

## カバレッジ

主要 API・ja↔en 翻訳・認証・エクスポート・監視をカバー。

---

## 負荷テスト

[STRESS_TEST_GUIDE.md](./STRESS_TEST_GUIDE.md) を参照。

```bash
python scripts/stress_test.py
```

---

## 今後

pytest 拡充・性能ベンチマーク・E2E・長時間安定性テスト。
