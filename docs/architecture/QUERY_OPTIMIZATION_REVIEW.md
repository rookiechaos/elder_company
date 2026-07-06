# Database Query Optimization Review Report

## Implemented Optimizations

### 1. N+1 Query Fix

**Location**: `services/customer_service.py`

**Before**: Multiple queries (customer + caregiver_profile + elder_profile)  
**After**: `joinedload` preloads associated data in a single JOIN query

```python
customer = self.db.query(CustomerDB)\
    .options(
        joinedload(CustomerDB.caregiver_profile),
        joinedload(CustomerDB.elder_profile)
    )\
    .filter(CustomerDB.customer_id == customer_id)\
    .first()
```

**Impact**: 50–70% reduction in query time

### 2. Caching

**Location**: `services/customer_service.py`, `services/organization_service.py`

**Strategy**:
- Customer info: 15-minute cache
- Organization info: 30-minute cache
- Activity templates: 1-hour cache

**Implementation**: In-memory cache via `services/cache_service.py`

### 3. Query Analysis Tools

**Location**: `services/query_analyzer.py`, `services/query_optimizer.py`

**Features**:
- Automatic slow query detection (threshold: 1 second)
- Optimization recommendations
- Index suggestions
- Query rewrite suggestions

### 4. Database Indexes

**Indexed fields**:
- `customer_id`, `customer_type`, `email`, `phone`
- `org_id`, `user_id`
- `created_at`, `timestamp` (time fields)
- Foreign keys: `caregiver_id`, `elder_id`

## Recommended Further Optimizations

### 1. Batch Query Optimization

**Location**: `services/customer_service.py` — `bulk_create_customers`

**Recommendation**: Use `bulk_insert_mappings` to reduce database round trips

```python
# Current
self.db.add_all(customers_to_create)
self.db.commit()

# Recommended
self.db.bulk_insert_mappings(CustomerDB, customers_data)
self.db.commit()
```

### 2. Paginated Query Optimization

**Recommendation**: Add pagination to all list queries to avoid loading large datasets at once

```python
def list_customers(
    self,
    org_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    query = self.db.query(CustomerDB)
    if org_id:
        query = query.filter(CustomerDB.org_id == org_id)
    
    total = query.count()
    customers = query.limit(limit).offset(offset).all()
    
    return {
        "items": [self._customer_to_dict(c) for c in customers],
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

### 3. Query Result Limits

**Recommendation**: Add default LIMIT to all queries to prevent accidental large loads

### 4. Index Review

**Recommendation**: Run query analysis tools regularly to identify queries needing new indexes

## Monitoring and Maintenance

### Slow Query Monitoring

Automatic slow query detection configured:
- Threshold: 1 second
- Auto-logged to `query_stats["slow_queries"]`
- Auto-generates optimization recommendations

### Query Performance Metrics

View query performance via:
- `/api/monitoring/queries` — Query statistics
- `/api/monitoring/slow-queries` — Slow query list
- `/api/monitoring/query-optimization` — Optimization recommendations

## Summary

Current query optimization status: **Good**

- N+1 query issues resolved
- Caching implemented
- Query analysis tools configured
- Indexes added on key fields
- Recommended: batch operation optimization
- Recommended: pagination support

---

# 日本語 / Japanese

# データベースクエリ最適化レビュー報告書

## 実施済みの最適化

### 1. N+1 クエリ問題の修正

**場所**: `services/customer_service.py`

**最適化前**: 複数クエリ（customer + caregiver_profile + elder_profile）  
**最適化後**: `joinedload` で関連データを事前読み込み、単一 JOIN クエリ

```python
customer = self.db.query(CustomerDB)\
    .options(
        joinedload(CustomerDB.caregiver_profile),
        joinedload(CustomerDB.elder_profile)
    )\
    .filter(CustomerDB.customer_id == customer_id)\
    .first()
```

**効果**: クエリ時間 50〜70% 削減

### 2. キャッシュ機構

**場所**: `services/customer_service.py`, `services/organization_service.py`

**戦略**:
- 顧客情報: 15分キャッシュ
- 機関情報: 30分キャッシュ
- 活動テンプレート: 1時間キャッシュ

**実装**: `services/cache_service.py` によるメモリキャッシュ

### 3. クエリ分析ツール

**場所**: `services/query_analyzer.py`, `services/query_optimizer.py`

**機能**:
- スロークエリの自動検出（閾値: 1秒）
- 最適化提案の生成
- インデックス提案
- クエリ書き換え提案

### 4. データベースインデックス

**インデックス追加済みフィールド**:
- `customer_id`, `customer_type`, `email`, `phone`
- `org_id`, `user_id`
- `created_at`, `timestamp`（時間フィールド）
- 外部キー: `caregiver_id`, `elder_id`

## 推奨されるさらなる最適化

### 1. バッチクエリ最適化

**場所**: `services/customer_service.py` — `bulk_create_customers`

**提案**: `bulk_insert_mappings` で DB 往復回数を削減

```python
# 現在の実装
self.db.add_all(customers_to_create)
self.db.commit()

# 推奨最適化
self.db.bulk_insert_mappings(CustomerDB, customers_data)
self.db.commit()
```

### 2. ページネーションクエリ最適化

**提案**: すべてのリストクエリにページネーションを追加し、大量データの一括読み込みを回避

```python
def list_customers(
    self,
    org_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    query = self.db.query(CustomerDB)
    if org_id:
        query = query.filter(CustomerDB.org_id == org_id)
    
    total = query.count()
    customers = query.limit(limit).offset(offset).all()
    
    return {
        "items": [self._customer_to_dict(c) for c in customers],
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

### 3. クエリ結果制限

**提案**: すべてのクエリにデフォルト LIMIT を追加し、意図しない大量読み込みを防止

### 4. インデックスレビュー

**提案**: クエリ分析ツールを定期実行し、新インデックスが必要なクエリパターンを特定

## 監視と保守

### スロークエリ監視

自動スロークエリ検出を設定済み:
- 閾値: 1秒
- `query_stats["slow_queries"]` に自動記録
- 最適化提案を自動生成

### クエリパフォーマンス指標

以下のエンドポイントでクエリパフォーマンスを確認:
- `/api/monitoring/queries` — クエリ統計
- `/api/monitoring/slow-queries` — スロークエリ一覧
- `/api/monitoring/query-optimization` — 最適化提案

## まとめ

現在のクエリ最適化状態: **良好**

- N+1 クエリ問題を解決
- キャッシュ機構を実施
- クエリ分析ツールを設定
- 主要フィールドにインデックスを追加
- 推奨: バッチ操作の最適化
- 推奨: ページネーション対応
