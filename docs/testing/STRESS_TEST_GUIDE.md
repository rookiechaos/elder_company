# Stress Testing Guide

> Load and performance testing for API endpoints.

**Last updated:** 2026-07-04

---

## Table of contents

- [Overview](#overview)
- [Quick start](#quick-start)
- [Parameters](#parameters)
- [Scenarios](#scenarios)
- [Interpreting results](#interpreting-results)
- [Best practices](#best-practices)

---

## Overview

Stress tests validate API performance and stability under load. Metrics tracked:

- **Response time:** mean, median, P95, P99
- **Success rate:** percentage of successful requests
- **Throughput:** QPS (requests per second)
- **Error rate:** failed request percentage
- **Status code distribution**

---

## Quick start

```bash
# 1. Start backend
cd backend && uvicorn main:app --reload

# 2. Run stress test (from repo root)
python scripts/stress_test.py
```

### Health check endpoint

```bash
python scripts/stress_test.py --endpoint /health --concurrent 20 --requests 500
```

### Translation endpoint

```bash
python scripts/stress_test.py \
  --endpoint /api/translate \
  --method POST \
  --concurrent 5 \
  --requests 100 \
  --data '{"text":"こんにちは","source_language":"ja","target_language":"en"}'
```

---

## Parameters

| Flag | Description | Default | Example |
|------|-------------|---------|---------|
| `--base-url` | API base URL | `http://localhost:8000` | `--base-url http://localhost:8000` |
| `--endpoint` | Target path | `/health` | `--endpoint /api/translate` |
| `--concurrent` | Concurrent users | `10` | `--concurrent 50` |
| `--requests` | Total requests | `100` | `--requests 1000` |
| `--method` | HTTP method | `GET` | `--method POST` |
| `--timeout` | Timeout (seconds) | `30` | `--timeout 60` |
| `--output` | Report file | `None` | `--output report.json` |
| `--data` | POST JSON body | `None` | `--data '{"key":"value"}'` |

---

## Scenarios

### Light load

```bash
python scripts/stress_test.py --endpoint /health --concurrent 10 --requests 100
```

Expected: success > 99%, avg < 100 ms, QPS > 10

### Medium load

```bash
python scripts/stress_test.py \
  --endpoint /api/translate --method POST \
  --concurrent 20 --requests 500 \
  --data '{"text":"テスト","source_language":"ja","target_language":"en"}'
```

Expected: success > 95%, avg < 500 ms, QPS > 5

### High load

```bash
python scripts/stress_test.py --endpoint /health --concurrent 100 --requests 5000
```

Expected: success > 90%, avg < 1000 ms

### Extreme load

```bash
python scripts/stress_test.py --endpoint /health --concurrent 200 --requests 10000 --timeout 60
```

Run in a test environment only.

---

## Interpreting results

| Rating | Success rate | Avg response |
|--------|--------------|--------------|
| Excellent | ≥ 99% | < 100 ms |
| Good | ≥ 95% | < 500 ms |
| Acceptable | ≥ 90% | < 1000 ms |
| Needs work | < 90% | > 1000 ms |

### Common issues

**High error rate:** reduce concurrency; check DB pool, memory, rate limits.

**Slow responses:** optimize queries; add cache; check external AI API latency.

**Low throughput:** increase concurrency capacity; use async; optimize indexes.

---

## Best practices

1. Use an isolated test environment similar to production
2. Start light, increase load gradually
3. Test multiple endpoints; save reports as baselines
4. Focus on P95/P99, not just averages

---

## Report format

```json
{
  "timestamp": "2025-01-19T10:30:00",
  "config": {
    "base_url": "http://localhost:8000",
    "endpoint": "/health",
    "concurrent": 10,
    "total_requests": 100,
    "method": "GET",
    "timeout": 30
  },
  "results": {
    "total_requests": 100,
    "successful_requests": 100,
    "failed_requests": 0,
    "success_rate": 100.0,
    "avg_response_time": 45.2,
    "median_response_time": 42.0,
    "p95_response_time": 78.0,
    "p99_response_time": 95.0,
    "qps": 22.1,
    "duration": 4.5
  }
}
```

### Batch script

```bash
#!/bin/bash
ENDPOINTS=("/health" "/api/translate" "/api/care-terms")
for endpoint in "${ENDPOINTS[@]}"; do
  python scripts/stress_test.py \
    --endpoint "$endpoint" --concurrent 20 --requests 500 \
    --output "report_${endpoint//\//_}.json"
done
```

**Version:** 2.1.2

---

# 負荷テストガイド

> API エンドポイントの負荷・性能テスト。

**最終更新:** 2026-07-04

---

## 目次

- [概要](#概要-1)
- [クイックスタート](#クイックスタート-1)
- [パラメータ](#パラメータ-1)
- [シナリオ](#シナリオ-1)
- [結果の読み方](#結果の読み方-1)
- [ベストプラクティス](#ベストプラクティス-1)

---

## 概要

高負荷下の性能・安定性を検証。応答時間（平均・P95・P99）、成功率、QPS、エラー率を計測。

---

## クイックスタート

```bash
cd backend && uvicorn main:app --reload
python scripts/stress_test.py
```

```bash
python scripts/stress_test.py --endpoint /health --concurrent 20 --requests 500
```

---

## パラメータ

| フラグ | 説明 | デフォルト |
|--------|------|-----------|
| `--base-url` | ベース URL | `http://localhost:8000` |
| `--endpoint` | パス | `/health` |
| `--concurrent` | 同時ユーザー | `10` |
| `--requests` | 総リクエスト | `100` |
| `--method` | HTTP メソッド | `GET` |
| `--timeout` | タイムアウト（秒） | `30` |
| `--output` | レポートファイル | なし |
| `--data` | POST JSON | なし |

---

## シナリオ

| 負荷 | コマンド例 | 期待値 |
|------|-----------|--------|
| 軽 | `--concurrent 10 --requests 100` | 成功率 > 99% |
| 中 | 翻訳 POST 500 件 | 成功率 > 95% |
| 高 | `--concurrent 100 --requests 5000` | 成功率 > 90% |
| 極限 | `--concurrent 200 --requests 10000` | テスト環境のみ |

---

## 結果の読み方

優: 成功率 ≥ 99%、平均 < 100 ms · 良: ≥ 95%、< 500 ms · 可: ≥ 90%、< 1000 ms

高エラー率 → 並行数削減 · 遅延 → クエリ/キャッシュ最適化 · 低スループット → 非同期・インデックス

---

## ベストプラクティス

独立テスト環境 · 段階的負荷増 · 複数エンドポイント · P95/P99 を重視

**バージョン:** 2.1.2
