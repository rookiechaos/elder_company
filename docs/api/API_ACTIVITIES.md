# Activity Management API Documentation

## Overview

The Activity Management API is a core Elder Company feature, enabling caregivers and elders to co-develop, participate in, and record meaningful activities.

---

## API Endpoints

### 1. Get Activity Templates

**GET** `/api/activities/templates`

**Query parameters**:
- `category` (optional): cognitive, craft, music, exercise, social, reminiscence
- `difficulty` (optional): easy, medium, hard
- `tags` (optional): comma-separated tags
- `limit` (optional): default 50

**Response example**:
```json
{
  "templates": [
    {
      "activity_id": "act_001",
      "title_ja": "折り紙",
      "title_en": "Origami",
      "description_en": "Traditional Japanese origami — create various shapes",
      "category": "craft",
      "tags": ["craft", "relaxing", "creative"],
      "difficulty_level": "easy",
      "duration_minutes": 30,
      "required_materials": ["Origami paper", "Scissors (optional)"],
      "participant_count": "1-2",
      "suitable_for": ["Dementia", "Limited mobility"],
      "steps": ["Choose a pattern", "Prepare materials", "Follow folding steps", "Display finished work"],
      "tips": "Start with simple patterns, gradually increase difficulty"
    }
  ],
  "count": 1
}
```

---

### 2. Get Activity Template Details

**GET** `/api/activities/templates/{activity_id}`

---

### 3. Recommend Activities

**POST** `/api/activities/recommend`

**Request body**:
```json
{
  "caregiver_id": "user123",
  "elder_profile": {
    "interests": ["crafts", "music"],
    "abilities": ["Can sit", "Can use hands"],
    "health_conditions": ["Dementia", "Limited mobility"],
    "mobility_level": "limited",
    "cognitive_level": "mild_impairment"
  },
  "org_id": "org_abc123",
  "limit": 5
}
```

**Response example**:
```json
{
  "recommendation_id": "rec_abc123",
  "recommended_activities": [
    {
      "activity_id": "act_001",
      "title_en": "Origami",
      "category": "craft",
      "difficulty_level": "easy"
    }
  ],
  "recommendation_reason": "Based on interests (crafts, music) and health conditions (dementia, limited mobility), we recommend the following activities."
}
```

---

### 4. Create Activity Record

**POST** `/api/activities/records`

**Request body**:
```json
{
  "caregiver_id": "user123",
  "activity_data": {
    "activity_template_id": "act_001",
    "activity_title": "Origami — Paper Crane",
    "activity_category": "craft",
    "customized_steps": ["Choose colored paper", "Follow tutorial", "Decorate crane"],
    "materials_used": ["Colored origami paper", "Decorative stickers"],
    "duration_minutes": 35,
    "notes": "Elder enjoyed it greatly, made two cranes",
    "elder_engagement": "high",
    "elder_mood_before": "calm",
    "elder_mood_after": "happy",
    "caregiver_feedback": "Very successful, high engagement",
    "elder_feedback": "Fun, want to do more",
    "photos": ["photo1.jpg", "photo2.jpg"],
    "achievements": ["Completed two cranes", "Learned basic folding"]
  },
  "org_id": "org_abc123",
  "elder_id": "elder_001"
}
```

---

### 5. Get Activity Records

**GET** `/api/activities/records`

**Query parameters**: `caregiver_id`, `elder_id`, `org_id`, `limit` (default 50)

---

### 6. Get Activity Record Details

**GET** `/api/activities/records/{record_id}`

---

### 7. Get Activity Categories

**GET** `/api/activities/categories`

**Response**:
```json
{
  "categories": ["cognitive", "craft", "music", "exercise", "social"],
  "descriptions": {
    "cognitive": "Cognitive training",
    "craft": "Crafts and art",
    "music": "Music",
    "exercise": "Exercise",
    "social": "Social activities",
    "reminiscence": "Reminiscence therapy"
  }
}
```

---

## Usage Examples

### Recommend Activities

```python
import requests

elder_profile = {
    "interests": ["crafts", "music"],
    "abilities": ["Can sit"],
    "health_conditions": ["Dementia"],
    "mobility_level": "limited",
    "cognitive_level": "mild_impairment"
}

response = requests.post(
    "http://localhost:8000/api/activities/recommend",
    params={"caregiver_id": "user123", "org_id": "org_abc123"},
    json={"elder_profile": elder_profile}
)
```

### Record an Activity

```python
response = requests.post(
    "http://localhost:8000/api/activities/records",
    params={"caregiver_id": "user123", "elder_id": "elder_001"},
    json={"activity_data": activity_record}
)
```

---

## Activity Categories

- **cognitive**: Memory games, cognitive exercises
- **craft**: Origami, painting, crafts
- **music**: Music appreciation, singing, instruments
- **exercise**: Light exercise, stretching
- **social**: Photo viewing, conversation, games
- **reminiscence**: Reminiscence therapy, story sharing

---

## Data Models

- **ActivityTemplate**: title, description, category, tags, difficulty, steps, tips
- **ActivityRecord**: activity info, participants, process, evaluation, achievements
- **ActivityRecommendation**: recommended list, reason, elder profile snapshot

---

## Best Practices

1. **Personalized recommendations** — provide detailed elder info, adjust based on feedback
2. **Activity records** — record promptly with detailed feedback and photos
3. **Continuous improvement** — adjust recommendations based on engagement and mood changes

---

**Version**: 2.0.0  
**Last updated**: 2026-01-20

---

# 日本語 / Japanese

# 活動管理 API ドキュメント

## 概要

活動管理 API は Elder Company のコア機能で、介護者と高齢者が意味のある活動を共に開発・参加・記録することを支援します。

---

## API エンドポイント

### 1. 活動テンプレート一覧

**GET** `/api/activities/templates`

**クエリパラメータ**:
- `category`: cognitive, craft, music, exercise, social, reminiscence
- `difficulty`: easy, medium, hard
- `tags`: カンマ区切りタグ
- `limit`: デフォルト 50

---

### 2. 活動テンプレート詳細

**GET** `/api/activities/templates/{activity_id}`

---

### 3. 活動推薦

**POST** `/api/activities/recommend`

高齢者情報に基づいて適切な活動を推薦します。

---

### 4. 活動記録作成

**POST** `/api/activities/records`

介護者と高齢者が一緒に完了した活動を記録します。

---

### 5. 活動記録一覧

**GET** `/api/activities/records`

---

### 6. 活動記録詳細

**GET** `/api/activities/records/{record_id}`

---

### 7. 活動カテゴリ

**GET** `/api/activities/categories`

---

## 活動カテゴリ

- **cognitive**（認知訓練）: 記憶ゲーム、認知練習
- **craft**（手工芸）: 折り紙、絵画、工作
- **music**（音楽）: 音楽鑑賞、歌、楽器
- **exercise**（運動）: 軽い運動、ストレッチ
- **social**（社交）: 写真鑑賞、会話、ゲーム
- **reminiscence**（回想）: 回想療法、ストーリー共有

---

## ベストプラクティス

1. **パーソナライズ推薦** — 詳細な高齢者情報を提供、フィードバックに基づき調整
2. **活動記録** — タイムリーに記録、詳細なフィードバックと写真を保存
3. **継続的改善** — 参加度と感情変化に基づき推薦を調整

---

**バージョン**: 2.0.0  
**最終更新**: 2026-01-20
