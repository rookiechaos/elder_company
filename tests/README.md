# Tests

Run from the **repository root** (see `pytest.ini` for `pythonpath`).

## Setup

```bash
pip install -r backend/requirements.txt
```

For local directories and secrets, run `./scripts/setup_local_dirs.sh` and configure `do-not-upload/env/.env` — see [do-not-upload/README.md](../do-not-upload/README.md).

## Internal integration tests (recommended)

```bash
pytest tests/integration/test_internal_api.py -v
# or
./scripts/run_test_in_chatbot.sh
```

## Run specific tests

```bash
pytest tests/test_customer_service.py
pytest tests/test_customer_service.py::TestCustomerService
pytest tests/test_customer_service.py::TestCustomerService::test_create_customer_success
```

## Coverage

```bash
pytest --cov=services --cov=backend --cov-report=html --cov-report=term
```

Report: `do-not-upload/coverage/index.html`

## Layout

```
tests/
├── conftest.py              # Fixtures and path setup
├── integration/             # DI, internal API, scenario tests
├── test_*.py                # Unit tests
├── test_api.py              # Live API smoke test (server required)
└── test_services.py         # Service smoke test (server required)
```

## Notes

- `TEST_MODE=true` is set in `conftest.py` to disable rate limits during tests.
- Business logic lives in `services/` at the repo root; API code stays in `backend/`.
- Helper scripts live in `scripts/` at the repo root.

See also [docs/testing/TESTING.md](../docs/testing/TESTING.md).

---

# テスト

**リポジトリルート**から実行してください（`pythonpath` は `pytest.ini` を参照）。

## セットアップ

```bash
pip install -r backend/requirements.txt
```

ローカルディレクトリと秘密情報は `./scripts/setup_local_dirs.sh` を実行し、`do-not-upload/env/.env` を設定 — [do-not-upload/README.md](../do-not-upload/README.md) を参照。

## 内部統合テスト（推奨）

```bash
pytest tests/integration/test_internal_api.py -v
# または
./scripts/run_test_in_chatbot.sh
```

## 特定テストの実行

```bash
pytest tests/test_customer_service.py
pytest tests/test_customer_service.py::TestCustomerService
pytest tests/test_customer_service.py::TestCustomerService::test_create_customer_success
```

## カバレッジ

```bash
pytest --cov=services --cov=backend --cov-report=html --cov-report=term
```

レポート: `do-not-upload/coverage/index.html`

## 構成

```
tests/
├── conftest.py              # フィクスチャとパス設定
├── integration/             # DI、内部 API、シナリオテスト
├── test_*.py                # ユニットテスト
├── test_api.py              # ライブ API スモークテスト（サーバー必要）
└── test_services.py         # サービススモークテスト（サーバー必要）
```

## 注意事項

- テスト中のレート制限無効化のため、`conftest.py` で `TEST_MODE=true` を設定。
- ビジネスロジックはリポジトリルートの `services/`、API コードは `backend/` に配置。
- 補助スクリプトはリポジトリルートの `scripts/` に配置。

詳細は [docs/testing/TESTING.md](../docs/testing/TESTING.md) を参照。
