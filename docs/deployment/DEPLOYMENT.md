# Elder Company - Production Deployment Guide

> **About this document**: Detailed guide for production deployment.

**Last updated**: 2026-01-20

---

## Table of Contents

- [Environment Requirements](#1-environment-requirements)
- [Database Configuration](#2-database-configuration)
- [Environment Variables](#3-environment-variables)
- [Deployment Steps](#4-deployment-steps)
- [Monitoring and Maintenance](#5-monitoring-and-maintenance)

---

## Production Deployment

### 1. Environment Requirements

- Python 3.9+
- PostgreSQL 12+ (recommended) or SQLite (development)
- At least 2 GB RAM
- Stable network connection (for AI APIs)

### 2. Database Configuration

#### PostgreSQL (recommended)

```bash
# Install PostgreSQL
# macOS
brew install postgresql

# Ubuntu
sudo apt-get install postgresql

# Create database
createdb elder_company

# Update .env
DATABASE_URL=postgresql://user:password@localhost/elder_company
```

#### SQLite (development / small scale)

```bash
# Default; local file lives in do-not-upload/data/
DATABASE_URL=sqlite:///./do-not-upload/data/elder_company.db
```

### 3. Redis Configuration (optional, for distributed rate limiting)

#### Install Redis

**macOS**:

```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:

```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker**:

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

#### Verify Redis

```bash
redis-cli ping
# Expected: PONG
```

**Detailed setup**: See [docs/architecture/REDIS_SETUP.md](../architecture/REDIS_SETUP.md) or run `./scripts/setup_redis.sh`.

---

### 4. Environment Variables

Create `do-not-upload/env/.env` (or `backend/.env` on the server):

```env
# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost/elder_company

# Server
PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### 5. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Initialize Database

```bash
# Tables are created automatically
python -c "from models.database import init_db; init_db()"
```

### 7. Start the Service

#### Development mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production (Gunicorn)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### systemd (Linux)

Create `/etc/systemd/system/elder-company.service`:

```ini
[Unit]
Description=Elder Company API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/elder_company/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable elder-company
sudo systemctl start elder-company
```

### 8. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/elder-company`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/elder-company /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### 10. Log Management

Log locations (local development defaults to `do-not-upload/logs/`):

- `app.log` — All logs
- `error.log` — Error logs

Log rotation (`/etc/logrotate.d/elder-company`):

```
/path/to/elder_company/do-not-upload/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 11. Monitoring and Health Checks

```bash
curl http://localhost:8000/health
```

Monitoring recommendations:

- Prometheus + Grafana
- API response-time alerts
- Error-rate monitoring
- Usage tracking

### 12. Backup Strategy

#### Database backup

```bash
# PostgreSQL
pg_dump elder_company > backup_$(date +%Y%m%d).sql

# SQLite
cp do-not-upload/data/elder_company.db backup_$(date +%Y%m%d).db
```

#### Automated backup script

```bash
#!/bin/bash
# scripts/backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump elder_company > /backups/elder_company_$DATE.sql
find /backups -name "*.sql" -mtime +30 -delete
```

Crontab:

```bash
0 2 * * * /path/to/scripts/backup.sh
```

### 13. Performance Optimization

#### Database connection pool

In `backend/config/database.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

#### Caching (optional)

Use Redis for frequently accessed terms:

```python
pip install redis

import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

### 14. Security Recommendations

1. **API key management**
   - Use environment variables
   - Never commit secrets to version control
   - Rotate keys regularly

2. **Database security**
   - Strong passwords
   - Restrict access by IP
   - Enable SSL connections

3. **API security**
   - API key authentication
   - HTTPS only
   - Rate limiting

4. **Data privacy**
   - Encrypt sensitive data
   - Audit access logs regularly
   - Comply with GDPR and applicable privacy laws

### 15. Scalability

#### Horizontal scaling

Use a load balancer (e.g. Nginx) across multiple instances:

```nginx
upstream elder_company {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

#### Database scaling

- Read/write separation
- Sharding at very large scale
- Connection pooling

### 16. Disaster Recovery

#### Auto-restart (systemd)

```ini
[Service]
Restart=always
RestartSec=10
```

#### Database restore

```bash
# PostgreSQL
psql elder_company < backup.sql

# SQLite
cp backup.db do-not-upload/data/elder_company.db
```

---

## Docker Deployment (optional)

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/elder_company
      - AI_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=elder_company
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start:

```bash
docker-compose up -d
```

---

## Verify Deployment

1. **Health check**

   ```bash
   curl http://localhost:8000/health
   ```

2. **API docs**

   Visit `http://localhost:8000/docs`

3. **Test translation**

   ```bash
   curl -X POST http://localhost:8000/api/translate \
     -H "Content-Type: application/json" \
     -d '{"text":"こんにちは","source_language":"ja","target_language":"en"}'
   ```

---

**Your Elder Company API is ready for production.** 🚀

---

# Elder Company - 本番デプロイガイド

> **本ドキュメントについて**: 本番環境デプロイの詳細ガイドです。

**最終更新**: 2026-01-20

---

## 目次

- [環境要件](#1-環境要件)
- [データベース設定](#2-データベース設定)
- [環境変数](#3-環境変数)
- [デプロイ手順](#4-デプロイ手順)
- [監視とメンテナンス](#5-監視とメンテナンス)

---

## 本番環境デプロイ

### 1. 環境要件

- Python 3.9+
- PostgreSQL 12+（推奨）または SQLite（開発用）
- メモリ 2 GB 以上
- 安定したネットワーク接続（AI API 用）

### 2. データベース設定

#### PostgreSQL（推奨）

```bash
# PostgreSQL をインストール
# macOS
brew install postgresql

# Ubuntu
sudo apt-get install postgresql

# データベースを作成
createdb elder_company

# .env を更新
DATABASE_URL=postgresql://user:password@localhost/elder_company
```

#### SQLite（開発 / 小規模）

```bash
# デフォルト。ローカルファイルは do-not-upload/data/ に配置
DATABASE_URL=sqlite:///./do-not-upload/data/elder_company.db
```

### 3. Redis 設定（任意、分散レート制限用）

#### Redis のインストール

**macOS**:

```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:

```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker**:

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

#### Redis の確認

```bash
redis-cli ping
# 期待値: PONG
```

**詳細設定**: [docs/architecture/REDIS_SETUP.md](../architecture/REDIS_SETUP.md) を参照、または `./scripts/setup_redis.sh` を実行。

---

### 4. 環境変数

`do-not-upload/env/.env`（またはサーバー上の `backend/.env`）を作成:

```env
# AI プロバイダー
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# データベース
DATABASE_URL=postgresql://user:pass@localhost/elder_company

# サーバー
PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# ログ
LOG_LEVEL=INFO
```

### 5. 依存関係のインストール

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. データベース初期化

```bash
# テーブルは自動作成
python -c "from models.database import init_db; init_db()"
```

### 7. サービスの起動

#### 開発モード

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 本番（Gunicorn）

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### systemd（Linux）

`/etc/systemd/system/elder-company.service` を作成:

```ini
[Unit]
Description=Elder Company API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/elder_company/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

有効化と起動:

```bash
sudo systemctl enable elder-company
sudo systemctl start elder-company
```

### 8. Nginx リバースプロキシ

`/etc/nginx/sites-available/elder-company` を作成し、上記英語セクションと同様の設定を適用。

### 9. SSL（Let's Encrypt）

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### 10. ログ管理

ログの場所（ローカル開発のデフォルトは `do-not-upload/logs/`）:

- `app.log` — すべてのログ
- `error.log` — エラーログ

### 11. 監視とヘルスチェック

```bash
curl http://localhost:8000/health
```

監視の推奨事項:

- Prometheus + Grafana
- API 応答時間アラート
- エラー率モニタリング
- 使用量トラッキング

### 12. バックアップ戦略

#### データベースバックアップ

```bash
# PostgreSQL
pg_dump elder_company > backup_$(date +%Y%m%d).sql

# SQLite
cp do-not-upload/data/elder_company.db backup_$(date +%Y%m%d).db
```

#### 自動バックアップスクリプト

`scripts/backup.sh` を crontab に登録（英語セクション参照）。

### 13. パフォーマンス最適化

接続プールは `backend/config/database.py` で設定。Redis キャッシュは任意。

### 14. セキュリティ推奨事項

1. **API キー管理** — 環境変数を使用、バージョン管理に含めない、定期ローテーション
2. **データベースセキュリティ** — 強力なパスワード、IP 制限、SSL 接続
3. **API セキュリティ** — 認証、HTTPS、レート制限
4. **データプライバシー** — 暗号化、監査ログ、GDPR 等の遵守

### 15. スケーラビリティ

Nginx ロードバランサーによる水平スケール、DB 読み書き分離、接続プール。

### 16. 障害復旧

systemd の自動再起動、PostgreSQL / SQLite リストア手順（英語セクション参照）。

---

## Docker デプロイ（任意）

Dockerfile と docker-compose.yml は英語セクションを参照。起動:

```bash
docker-compose up -d
```

---

## デプロイ確認

1. **ヘルスチェック** — `curl http://localhost:8000/health`
2. **API ドキュメント** — `http://localhost:8000/docs`
3. **翻訳テスト** — 英語セクションの curl 例を参照

---

**Elder Company API の本番デプロイが完了しました。** 🚀
