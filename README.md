# Elder Company — Care Collaboration Platform

**Version 2.1.2 — Mobile PWA, code quality, and security improvements**

| | |
|---|---|
| **Tests** | 12/12 internal API tests passing · stress-test tooling ready · code quality & security improvements complete |
| **Business** | Launch Q2 2026 · annual target: 15 facilities |
| **Docs** | See [DOCS_INDEX.md](./DOCS_INDEX.md) for the full documentation index |

An intelligent collaboration platform for caregivers in Japan (介護) — helping caregivers and elders co-create meaningful activities and communicate more deeply.

> **Product notice:** This is a care collaboration and companionship tool, **not a medical device**. For health or medical decisions, consult qualified healthcare professionals. See [Non-Medical Product Compliance](./docs/compliance/PRODUCT_NON_MEDICAL.md).

---

## Overview

Elder Company is more than a translation tool. It is a platform that **helps caregivers and elders collaborate** — building stronger connections through shared activities and clearer communication.

### Core values

- **Co-creation** — Caregivers and elders design and join activities together
- **Deeper communication** — Go beyond language barriers to understand needs and interests
- **Personalized activities** — Tailored to interests, abilities, and health status
- **Shared journey** — Care becomes a two-way experience, not one-way support

---

## Features

### Collaboration & activities

| Area | Capabilities |
|------|----------------|
| **Communication** | AI-assisted dialogue, multilingual support, care-scenario context |
| **Activities** | Template library, personalized recommendations, customization, activity logs |
| **Tools** | Joint planning, sharing outcomes, AI-generated ideas, impact tracking |

### Platform capabilities

- **Translation** — Japanese ↔ Chinese/English/Korean; 50+ care terms in 6 categories
- **Enterprise (v2.0)** — Multi-tenant orgs, usage analytics, RBAC, quotas, structured logging, 3-tier personalization (org / user / request)
- **Engineering (v2.1.2)** — Black, isort, ruff, mypy; unified error handling; type hints; pytest coverage; query optimization

---

## Tech stack

| Layer | Stack |
|-------|--------|
| **Backend** | Python 3.9+, FastAPI, SQLAlchemy, OpenAI / Claude / Gemini |
| **Frontend** | React 18, Vite, i18next (installed), PWA, responsive mobile UI |
| **Tooling** | Black, isort, ruff, mypy, pytest, pre-commit |

---

## Quick start

See [docs/deployment/SETUP.md](./docs/deployment/SETUP.md) for detailed setup.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Local secrets and data (not committed to git)
cd ..
./scripts/setup_local_dirs.sh
cp backend/env.example do-not-upload/env/.env
# Edit do-not-upload/env/.env — add API keys and set AI_PROVIDER

cd backend
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### AI providers

Set `AI_PROVIDER` in `do-not-upload/env/.env`:

- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **Google Gemini** (Gemini Pro)

---

## Project structure

```
elder_company/
├── backend/          # FastAPI API, models, middleware, utils
├── services/         # Business logic services
├── tests/            # Pytest unit and integration tests
├── scripts/          # Migration, stress test, folder limit checks
├── do-not-upload/    # Local secrets, DB, logs (gitignored)
├── frontend/         # React PWA
├── game/             # Optional game module
├── docs/             # Architecture, API, deployment, compliance
├── LICENSE           # Apache License 2.0
└── README.md
```

---

## Publishing to GitHub

1. Run `./scripts/setup_local_dirs.sh` — local data stays in `do-not-upload/` (gitignored).
2. Never commit `do-not-upload/env/.env`, databases, or logs.
3. Verify: `./scripts/check_folder_limits.sh`
4. Push the repository; include `LICENSE` (Apache 2.0).

---

## Testing

Recommended: **internal API tests** (no server or open ports required).

```bash
pytest tests/integration/test_internal_api.py -v

# Or via helper script
./scripts/run_test_in_chatbot.sh
```

Other options:

| Type | Command | Notes |
|------|---------|-------|
| All pytest | `pytest tests/` | Unit + integration (run from repo root) |
| Live API | `python tests/test_api.py` | Requires running server |
| Stress | `python scripts/stress_test.py` | Requires running server |
| Folder limits | `./scripts/check_folder_limits.sh` | Ensures ≤99 files per top-level folder |

See [docs/testing/TESTING.md](./docs/testing/TESTING.md).

---

## Code quality

```bash
black backend/
isort backend/
ruff check backend/
mypy backend/
pytest tests/
```

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

---

## Research direction (long-term)

The platform’s long-term AI direction uses **uncertainty-aware** world models:

- World models infer **posterior distributions** over state or next outcomes — not single-point actions
- Bayesian + Transformer sequence modeling supports safer recommendations when confidence is low
- Suggested rollout: start with next-step prediction distributions, validate in controlled settings, then expand

---

## Roadmap snapshot

**Done:** Translation, care terms, org/enterprise features, PWA, offline cache, code quality tooling, activity library, family participation, voice, multimedia, collaborative design

**Next:** Wire up i18next for Japanese UI, consolidate rate-limit modules, expand E2E coverage

---

---

# 日本語 / Japanese

# Elder Company — 介護協働プラットフォーム

**バージョン 2.1.2 — モバイルPWA・コード品質・セキュリティ改善**

| | |
|---|---|
| **テスト** | 内部APIテスト 12/12 合格 · 負荷テスト準備完了 · 品質・セキュリティ改善完了 |
| **事業** | 2026年Q2開始 · 年間目標15施設 |
| **ドキュメント** | 一覧は [DOCS_INDEX.md](./DOCS_INDEX.md) |

日本の介護現場向けの協働プラットフォーム。介護者と高齢者が一緒に意味のある活動を創り、深いコミュニケーションを支援します。

> **製品性質について：** 本製品は介護協働・見守り支援ツールであり、**医療機器ではありません**。健康・医療に関する判断は専門の医療従事者にご相談ください。[非医療製品コンプライアンス](./docs/compliance/PRODUCT_NON_MEDICAL.md) を参照。

---

## 概要

Elder Company は翻訳ツールにとどまりません。**介護者と高齢者の協働**を支援し、共有活動を通じてつながりを深めます。

### 核心理念

- **共創** — 介護者と高齢者が一緒に活動を設計・参加
- **深いコミュニケーション** — 言語の壁を越え、ニーズと関心を理解
- **パーソナライズ活動** — 興味・能力・健康状態に合わせた提案
- **協働の旅** — 一方的な介護ではなく、双方が参加するプロセス

---

## 機能

### 協働と活動

| 領域 | 内容 |
|------|------|
| **コミュニケーション** | AI対話支援、多言語、介護シーン理解 |
| **活動** | テンプレートライブラリ、個別推薦、カスタマイズ、記録 |
| **ツール** | 共同計画、成果共有、AIアイデア、効果追跡 |

### プラットフォーム機能

- **翻訳** — 日本語 ↔ 中国語/英語/韓国語、介護用語50語以上（6分類）
- **エンタープライズ (v2.0)** — マルチテナント、利用統計、権限、クォータ、ログ、3層パーソナライズ
- **エンジニアリング (v2.1.2)** — Black/isort/ruff/mypy、統一エラー処理、型注釈、pytest、クエリ最適化

---

## 技術スタック

| 層 | 技術 |
|----|------|
| **バックエンド** | Python 3.9+, FastAPI, SQLAlchemy, OpenAI / Claude / Gemini |
| **フロントエンド** | React 18, Vite, i18next（導入済み）, PWA, レスポンシブUI |
| **開発ツール** | Black, isort, ruff, mypy, pytest, pre-commit |

---

## クイックスタート

詳細は [docs/deployment/SETUP.md](./docs/deployment/SETUP.md) を参照。

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# .env を編集 — APIキーと AI_PROVIDER を設定
uvicorn main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### AIプロバイダー

`backend/.env` の `AI_PROVIDER` で選択：

- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Anthropic Claude** (Claude 3.5 Sonnet)
- **Google Gemini** (Gemini Pro)

---

## プロジェクト構成

```
elder_company/
├── backend/          # FastAPI API, models, middleware, utils
├── services/         # Business logic services
├── tests/            # Pytest unit and integration tests
├── scripts/          # Migration, stress test, folder limit checks
├── do-not-upload/    # ローカル専用（gitignore）
├── frontend/         # React PWA
├── game/             # Optional game module
├── docs/             # Architecture, API, deployment, compliance
├── LICENSE           # Apache License 2.0
└── README.md
```

### GitHub 公開

1. `./scripts/setup_local_dirs.sh` — 秘密情報は `do-not-upload/` に配置
2. `.env`、DB、ログをコミットしない
3. `./scripts/check_folder_limits.sh` で確認

---

## テスト

推奨：**内部APIテスト**（サーバー起動・ポート公開不要）

```bash
pytest tests/integration/test_internal_api.py -v

# または
./scripts/run_test_in_chatbot.sh
```

| 種類 | コマンド | 備考 |
|------|----------|------|
| 全pytest | `pytest tests/` | 単体+統合（リポジトリルートから） |
| 実API | `python tests/test_api.py` | サーバー起動が必要 |
| 負荷 | `python scripts/stress_test.py` | サーバー起動が必要 |
| フォルダ上限 | `./scripts/check_folder_limits.sh` | 各トップレベルフォルダ99ファイル以下 |

詳細：[docs/testing/TESTING.md](./docs/testing/TESTING.md)

---

## コード品質

```bash
black backend/
isort backend/
ruff check backend/
mypy backend/
pytest tests/
```

pre-commit：

```bash
pip install pre-commit
pre-commit install
```

---

## 研究・技術ビジョン（長期）

**不確実性を意識した**世界モデルを基盤とします：

- 世界モデルは状態や次の結果の**事後分布**を推定し、単一点の予測ではない
- ベイズ + Transformer により、信頼度が低い場面ではより安全な推薦が可能
- 段階的導入：次ステップ予測の分布から始め、検証後に拡張

---

## ロードマップ（概要）

**完了：** 翻訳、介護用語、機関管理、PWA、オフライン、品質ツール、活動ライブラリ、家族参加、音声、マルチメディア、協働デザイン

**今後：** i18next による日本語UI、レート制限モジュール統合、E2Eテスト拡充

---

## License & contact

Licensed under the [Apache License 2.0](./LICENSE).  
ライセンス: [Apache License 2.0](./LICENSE)

See [CHANGELOG.md](./CHANGELOG.md) for release history.
