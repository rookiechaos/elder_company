# Redis Distributed Rate Limiting Setup Guide

> **Note**: How to configure and use Redis for distributed rate limiting.

**Last updated**: 2026-01-20

---

## Table of Contents

- [Overview](#overview)
- [Install Redis](#install-redis)
- [Configure Redis](#configure-redis)
- [Verify Configuration](#verify-configuration)
- [Test Distributed Rate Limiting](#test-distributed-rate-limiting)
- [Troubleshooting](#troubleshooting)

---

## Overview

Elder Company supports Redis-based distributed rate limiting for multi-server deployments. Without Redis, the system uses in-memory rate limiting (single-server mode).

### Benefits

- **Distributed**: Multiple server instances share rate limit counters
- **Consistent**: All servers use the same rate limit rules
- **Scalable**: Supports horizontal scaling

---

## Install Redis

### macOS

```bash
brew install redis
brew services start redis
# Or manually: redis-server
```

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### CentOS/RHEL

```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Docker

```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### Verify Installation

```bash
redis-cli ping
# Should return: PONG
```

---

## Configure Redis

### 1. Set Environment Variables

Add to `do-not-upload/env/.env`:

```env
REDIS_URL=redis://localhost:6379/0
# With password: REDIS_URL=redis://:password@localhost:6379/0
# Cluster: REDIS_URL=redis://host1:6379,host2:6379/0
```

### 2. Install Python Redis Library

```bash
cd backend
pip install redis
```

Or add to `requirements.txt`: `redis>=5.0.0`

### 3. Restart Backend

```bash
cd backend
uvicorn main:app --reload
```

---

## Verify Configuration

### Method 1: Setup Script

```bash
chmod +x scripts/setup_redis.sh
./scripts/setup_redis.sh
```

### Method 2: Manual Verification

```bash
redis-cli ping
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv('../do-not-upload/env/.env'); print('REDIS_URL:', os.getenv('REDIS_URL'))"
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Redis:', r.ping())"
```

### Method 3: Check Logs

On startup you should see:
```
Using Redis for distributed rate limiting
```

Without Redis:
```
Using in-memory rate limiting
```

---

## Test Distributed Rate Limiting

### Using Test Script

```bash
python scripts/test_redis_rate_limit.py
```

### Manual Test

```bash
# Check rate limit headers
curl -i -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "source_lang": "ja", "target_lang": "en"}'

# Trigger rate limit
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/translate \
    -H "Content-Type: application/json" \
    -d '{"text": "test", "source_lang": "ja", "target_lang": "en"}' &
done
wait

# Check Redis keys
redis-cli KEYS LIMITER:*
```

---

## Troubleshooting

### Redis Connection Failed

1. Check Redis is running: `redis-cli ping`
2. Check port: `netstat -an | grep 6379`
3. Verify `REDIS_URL` in `do-not-upload/env/.env`

### Rate Limiting Not Working

1. Confirm Redis mode in logs
2. Check `REDIS_URL` environment variable
3. Verify rate limit decorators on API routes

### Inconsistent Multi-Server Limits

- Ensure all servers use the same `REDIS_URL`
- Verify Redis connectivity

### Redis Performance

- Use connection pooling
- Consider Redis Sentinel or Cluster for production

---

## Production Recommendations

1. **High availability**: Redis Sentinel or Cluster
2. **Monitoring**: Connection count, memory usage, rate limit triggers
3. **Security**: Password, TLS (Redis 6.0+), IP restrictions
4. **Performance**: Memory limits, eviction policy, Pipeline batching

---

## Related Documentation

- [Deployment Guide](../deployment/DEPLOYMENT.md)
- [Environment template](../../backend/env.example)
- [Rate limit middleware](../../backend/middleware/rate_limit_enhanced.py)

---

**Last updated**: 2026-01-20

---

# 日本語 / Japanese

# Redis 分散レート制限 設定ガイド

> **説明**: Redis を使用した分散レート制限の設定と使用方法。

**最終更新**: 2026-01-20

---

## 目次

- [概要](#概要-1)
- [Redis のインストール](#redis-のインストール)
- [Redis の設定](#redis-の設定)
- [設定の検証](#設定の検証)
- [分散レート制限のテスト](#分散レート制限のテスト)
- [トラブルシューティング](#トラブルシューティング-1)

---

## 概要

Elder Company は Redis による分散レート制限をサポートし、マルチサーバーデプロイに対応します。Redis 未設定時はメモリ内レート制限（単一サーバーモード）を使用します。

### メリット

- **分散**: 複数サーバーインスタンスがレート制限カウンターを共有
- **一貫性**: すべてのサーバーが同じレート制限ルールを使用
- **スケーラブル**: 水平スケーリングに対応

---

## Redis のインストール

### macOS

```bash
brew install redis
brew services start redis
# 手動起動: redis-server
```

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### CentOS/RHEL

```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Docker

```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### インストール確認

```bash
redis-cli ping
# 返答: PONG
```

---

## Redis の設定

### 1. 環境変数の設定

`do-not-upload/env/.env` に追加:

```env
REDIS_URL=redis://localhost:6379/0
# パスワード付き: REDIS_URL=redis://:password@localhost:6379/0
# クラスター: REDIS_URL=redis://host1:6379,host2:6379/0
```

### 2. Python Redis ライブラリのインストール

```bash
cd backend
pip install redis
```

または `requirements.txt` に追加: `redis>=5.0.0`

### 3. バックエンドの再起動

```bash
cd backend
uvicorn main:app --reload
```

---

## 設定の検証

### 方法 1: セットアップスクリプト

```bash
chmod +x scripts/setup_redis.sh
./scripts/setup_redis.sh
```

### 方法 2: 手動検証

```bash
redis-cli ping
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv('../do-not-upload/env/.env'); print('REDIS_URL:', os.getenv('REDIS_URL'))"
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Redis:', r.ping())"
```

### 方法 3: ログ確認

起動時に以下が表示されるはず:
```
Using Redis for distributed rate limiting
```

Redis 未設定時:
```
Using in-memory rate limiting
```

---

## 分散レート制限のテスト

### テストスクリプトを使用

```bash
python scripts/test_redis_rate_limit.py
```

### 手動テスト

```bash
# レート制限ヘッダーを確認
curl -i -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "テスト", "source_lang": "ja", "target_lang": "en"}'

# レート制限をトリガー
for i in {1..20}; do
  curl -X POST http://localhost:8000/api/translate \
    -H "Content-Type: application/json" \
    -d '{"text": "テスト", "source_lang": "ja", "target_lang": "en"}' &
done
wait

# Redis キーを確認
redis-cli KEYS LIMITER:*
```

---

## トラブルシューティング

### Redis 接続失敗

1. Redis 稼働確認: `redis-cli ping`
2. ポート確認: `netstat -an | grep 6379`
3. `do-not-upload/env/.env` の `REDIS_URL` を確認

### レート制限が動作しない

1. ログで Redis モードを確認
2. `REDIS_URL` 環境変数を確認
3. API ルートのレート制限デコレータを確認

### マルチサーバーで制限が不一致

- すべてのサーバーが同じ `REDIS_URL` を使用していることを確認
- Redis 接続を検証

### Redis パフォーマンス

- コネクションプールを使用
- 本番環境では Redis Sentinel または Cluster を検討

---

## 本番環境の推奨事項

1. **高可用性**: Redis Sentinel または Cluster
2. **監視**: 接続数、メモリ使用量、レート制限トリガー頻度
3. **セキュリティ**: パスワード、TLS（Redis 6.0+）、IP 制限
4. **パフォーマンス**: メモリ制限、退避ポリシー、Pipeline バッチ操作

---

## 関連ドキュメント

- [デプロイガイド](../deployment/DEPLOYMENT.md)
- [環境変数テンプレート](../../backend/env.example)
- [レート制限ミドルウェア](../../backend/middleware/rate_limit_enhanced.py)

---

**最終更新**: 2026-01-20
