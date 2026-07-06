# Web Vitals Alerts & Query Optimization — Completion Report

> **Document purpose**: Web Vitals alerting and query optimization system implementation.

**Completed**: 2024 | **Status**: ✅ Complete

---

## 1. ✅ Web Vitals Alert System

- **File**: `services/web_vitals_alert.py`
- **Features**: Threshold config, trigger mechanism, email notifications, alert history (max 1000)

### Alert Levels
| Level | Behavior |
|-------|----------|
| Good | No alert |
| Needs Improvement | Optional alert |
| Poor | Automatic alert |

### API Endpoints
- `GET /api/metrics/web-vitals/thresholds`
- `POST /api/metrics/web-vitals/thresholds`
- `GET /api/metrics/web-vitals/alerts/history`

### Configuration (`.env`)
```bash
WEB_VITALS_ALERT_NEEDS_IMPROVEMENT=false
WEB_VITALS_LCP_GOOD=2500
WEB_VITALS_LCP_NEEDS_IMPROVEMENT=4000
ADMIN_EMAIL=admin@example.com
```

### Default Thresholds
| Metric | Good | Needs Improvement |
|--------|------|-------------------|
| LCP (ms) | 2500 | 4000 |
| FID (ms) | 100 | 300 |
| CLS | 0.1 | 0.25 |
| FCP (ms) | 1800 | 3000 |
| TTFB (ms) | 800 | 1800 |
| TTI (ms) | 3800 | 7300 |

### Auto-Integration
Integrated into `POST /api/metrics/web-vitals` — checks metrics on ingest.

---

## 2. ✅ Query Optimization System

- **File**: `services/query_optimizer.py`
- **Features**: Slow-query analysis, optimization suggestions (score 0–100), index recommendations, query rewrite, auto-optimize

### Optimization Categories
- **SELECT**: Avoid `SELECT *`, add `LIMIT`, `ORDER BY` index hints
- **JOIN**: Too many joins, missing join conditions
- **WHERE**: Function usage, leading wildcards, OR conditions

### API Endpoints
- `GET /api/metrics/queries/optimization-report`
- `GET /api/metrics/queries/analyze/{query_hash}`
- `POST /api/metrics/queries/rewrite`
- `POST /api/metrics/queries/auto-optimize`

### Auto-Integration
Integrated with `QueryAnalyzer` — slow queries analyzed automatically.

---

## New Files

| File | Purpose |
|------|---------|
| `services/web_vitals_alert.py` | Web Vitals alerts |
| `services/query_optimizer.py` | Query optimization |

### Updated
- `backend/api/web_vitals_routes.py` — alert endpoints
- `backend/main.py` — optimization report endpoint
- `services/query_analyzer.py` — optimizer integration

---

## Workflows

**Web Vitals**: Frontend reports → `POST /api/metrics/web-vitals` → threshold check → email alert → history

**Query optimization**: Slow query detected → `QueryOptimizer` analyzes → suggestions stored → API report available

---

## Next Steps

| Area | Enhancements |
|------|-------------|
| Web Vitals | Slack/webhook, alert aggregation, dashboard |
| Query | Auto rewrite, index usage analysis, query plan analysis |

---

**Status**: ✅ Complete | **Deploy**: Configure thresholds and admin email before production

---

# 日本語

# Web Vitals アラート & クエリ最適化 — 完了報告

> **文書目的**: Web Vitals アラートとクエリ最適化システムの実装詳細。

**完了**: 2024年 | **状態**: ✅ 完了

---

## 1. Web Vitals アラート ✅

- **ファイル**: `services/web_vitals_alert.py`
- **機能**: 閾値設定、3段階アラート（Good / Needs Improvement / Poor）、メール通知、履歴（最大1000件）

### API
- `GET/POST /api/metrics/web-vitals/thresholds`
- `GET /api/metrics/web-vitals/alerts/history`

### デフォルト閾値
| 指標 | Good | 要改善 |
|------|------|--------|
| LCP (ms) | 2500 | 4000 |
| FID (ms) | 100 | 300 |
| CLS | 0.1 | 0.25 |

### 自動統合
`POST /api/metrics/web-vitals` 受信時に自動チェック・アラート。

---

## 2. クエリ最適化 ✅

- **ファイル**: `services/query_optimizer.py`
- **機能**: スロークエリ分析、最適化提案（0–100点）、インデックス提案、クエリ書き換え、自動最適化

### API
- `GET /api/metrics/queries/optimization-report`
- `GET /api/metrics/queries/analyze/{query_hash}`
- `POST /api/metrics/queries/rewrite`
- `POST /api/metrics/queries/auto-optimize`

### 自動統合
`QueryAnalyzer` がスロークエリ検出時に自動分析。

---

## 新規ファイル

| ファイル | 用途 |
|---------|------|
| `services/web_vitals_alert.py` | Web Vitals アラート |
| `services/query_optimizer.py` | クエリ最適化 |

---

## 今後の拡張

- Slack/Webhook 通知、アラート集約
- インデックス使用分析、クエリプラン分析

**本番前**: 閾値と `ADMIN_EMAIL` を設定してください。
