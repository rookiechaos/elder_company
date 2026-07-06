# Elder Company — Customer Information Database Design

## Overview

This document describes the database design for storing customer information and personalization optimization.

---

## Database Architecture

```
customers (main customer table)
├── caregiver_profiles (caregiver details)
├── elder_profiles (elder details)
├── care_relationships (care relationships)
├── personalization_data (personalization data)
├── behavior_logs (behavior logs)
├── preference_learning (preference learning)
└── interaction_history (interaction history)
```

---

## Table Designs

### 1. customers — Main Customer Table

**Purpose**: Store basic information for all customers (caregivers, elders, family members)

**Key fields**:
- `customer_id`: unique identifier
- `customer_type`: caregiver, elder, family_member
- `name`, `name_ja`, `name_en`: multilingual names
- `email`, `phone`: contact information
- `native_language`, `spoken_languages`: language info
- `org_id`, `user_id`: associations

**Indexes**: `customer_id` (unique), `customer_type`, `email`, `phone`, `org_id`, `user_id`

---

### 2. caregiver_profiles — Caregiver Details

**Key fields**:
- `role`: e.g., certified care worker, care assistant
- `certification`, `experience_years`, `work_shift`
- `specialties`, `preferred_care_style`, `communication_style`
- `translation_preferences`, `activity_preferences`

**Relationship**: 1:1 with `customers`

---

### 3. elder_profiles — Elder Details

**Key fields**:
- `health_status`, `health_conditions`
- `mobility_level`, `cognitive_level`
- `adl_scores`, `iadl_scores`
- `interests`, `hobbies`, `favorite_topics`
- `occupation_history`, `life_story`
- `activity_capabilities`, `personality_traits`, `mood_patterns`

**Relationship**: 1:1 with `customers`

---

### 4. care_relationships — Care Relationships

**Key fields**:
- `caregiver_id`, `elder_id`
- `relationship_type`: professional, family, volunteer
- `care_frequency`, `care_duration_hours`
- `interaction_quality`, `communication_effectiveness`

**Relationship**: N:M (caregiver ↔ elder)

---

### 5. personalization_data — Personalization Data

**Key fields**:
- `data_type`: translation_pref, activity_pref, communication_pref
- `preference_data`: JSON
- `source`: explicit, inferred, learned
- `confidence_score`: 0–1
- `usage_count`, `last_used_at`

---

### 6. behavior_logs — Behavior Logs

**Key fields**:
- `behavior_type`: translation, activity, communication, search
- `action`, `behavior_data`: JSON
- `context`: JSON
- `outcome`: success, failure, partial
- `feedback`: JSON
- `device_id`, `session_id`

---

### 7. preference_learning — Preference Learning

**Key fields**:
- `learned_preferences`: JSON
- `source_behaviors`: behavior ID list
- `learning_method`: pattern_analysis, ml_model, rule_based
- `confidence_score`, `sample_size`
- `is_validated`, `validation_method`

---

### 8. interaction_history — Interaction History

**Key fields**:
- `interaction_type`: translation, activity, conversation, care_task
- `content`, `content_metadata`: JSON
- `quality_score`, `engagement_level`, `satisfaction_score`
- `elder_mood_before`, `elder_mood_after`
- `caregiver_feedback`, `elder_feedback`
- `duration_minutes`, `interaction_date`

---

## Data Relationships

```
customers (1) ── (1) caregiver_profiles
customers (1) ── (1) elder_profiles
customers (N) ── (M) care_relationships
customers (1) ── (N) personalization_data
customers (1) ── (N) behavior_logs
customers (1) ── (N) preference_learning
care_relationships (1) ── (N) interaction_history
```

---

## Personalization Data Flow

```
User behavior → behavior_logs → Analysis → preference_learning → personalization_data
                                                                    ↓
                                              Personalized recommendations → User feedback loop
```

---

## Data Examples

### Caregiver Customer

```json
{
  "customer_id": "customer_001",
  "customer_type": "caregiver",
  "name": "Taro Tanaka",
  "name_ja": "田中太郎",
  "role": "Certified care worker",
  "experience_years": 5,
  "specialties": ["Dementia care", "Rehabilitation"],
  "translation_preferences": {
    "style": "professional",
    "use_honorifics": true
  }
}
```

### Elder Customer

```json
{
  "customer_id": "customer_002",
  "customer_type": "elder",
  "name": "Hanako Suzuki",
  "name_ja": "鈴木花子",
  "health_conditions": ["Dementia", "Hypertension"],
  "mobility_level": "limited",
  "cognitive_level": "mild_impairment",
  "interests": ["Crafts", "Music", "Reminiscence"],
  "personality_traits": ["Gentle", "Enjoys conversation"]
}
```

### Personalization Data

```json
{
  "data_id": "pref_001",
  "customer_id": "customer_001",
  "data_type": "translation_pref",
  "preference_data": {
    "preferred_terms": {
      "特別養護老人ホーム": "Special nursing home for the elderly"
    },
    "style_preference": "professional"
  },
  "source": "explicit",
  "confidence_score": 1.0
}
```

---

## Query Optimization

```sql
-- Get complete customer info
SELECT * FROM customers c
LEFT JOIN caregiver_profiles cp ON c.customer_id = cp.customer_id
WHERE c.customer_id = ?

-- Get all elders for a caregiver
SELECT e.* FROM customers e
JOIN care_relationships cr ON e.customer_id = cr.elder_id
WHERE cr.caregiver_id = ? AND cr.relationship_status = 'active'

-- Get personalization data
SELECT * FROM personalization_data
WHERE customer_id = ? AND data_type = ?
ORDER BY confidence_score DESC
```

---

## Privacy and Security

1. **Encryption**: email, phone encrypted; address data masked
2. **Access control**: role-based, organization and user isolation
3. **Data retention**: behavior log retention policies, periodic cleanup
4. **Compliance**: personal information protection law, data export/deletion support

---

## Scalability

- Horizontal: partition by organization, archive by time
- Performance: index optimization, query caching, read/write separation
- Archival: historical data archiving, hot/cold data separation

---

**Version**: 2.0.0  
**Last updated**: 2025-01-19

---

# 日本語 / Japanese

# Elder Company — 顧客情報データベース設計

## 概要

顧客情報とパーソナライズ最適化のためのデータベース設計を説明します。

---

## データベースアーキテクチャ

```
customers（顧客マスタ）
├── caregiver_profiles（介護者詳細）
├── elder_profiles（高齢者詳細）
├── care_relationships（介護関係）
├── personalization_data（パーソナライズデータ）
├── behavior_logs（行動ログ）
├── preference_learning（嗜好学習）
└── interaction_history（インタラクション履歴）
```

---

## テーブル設計

### 1. customers — 顧客マスタ

- `customer_id`, `customer_type`（caregiver, elder, family_member）
- `name`, `name_ja`, `name_en`
- `email`, `phone`, `org_id`, `user_id`

### 2. caregiver_profiles — 介護者詳細

- `role`, `certification`, `experience_years`
- `specialties`, `translation_preferences`, `activity_preferences`

### 3. elder_profiles — 高齢者詳細

- `health_status`, `health_conditions`
- `mobility_level`, `cognitive_level`
- `interests`, `hobbies`, `mood_patterns`

### 4. care_relationships — 介護関係

- `caregiver_id`, `elder_id`
- `relationship_type`, `interaction_quality`

### 5–8. その他テーブル

- `personalization_data` — 嗜好データ（JSON）
- `behavior_logs` — 行動記録
- `preference_learning` — 学習された嗜好
- `interaction_history` — インタラクション履歴

---

## データ例

```json
{
  "customer_id": "customer_001",
  "customer_type": "caregiver",
  "name_ja": "田中太郎",
  "role": "介護士",
  "experience_years": 5
}
```

---

## プライバシーとセキュリティ

1. **暗号化**: メール・電話番号の暗号化
2. **アクセス制御**: RBAC、組織・ユーザー分離
3. **データ保持**: 行動ログ保持期限、定期クリーンアップ
4. **コンプライアンス**: 個人情報保護法、データエクスポート/削除

---

## スケーラビリティ

- 組織別パーティション、時間別アーカイブ
- インデックス最適化、クエリキャッシュ、読み書き分離

---

**バージョン**: 2.0.0  
**最終更新**: 2025-01-19
