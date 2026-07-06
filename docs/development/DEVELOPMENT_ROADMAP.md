# Development Roadmap — Japan Market Core Features

**Version**: 1.0.0  
**Created**: 2026-01-21  
**Target market**: Japan long-term care market

---

## Overview

This document plans feature modules needed to support Elder Company's core value propositions for the Japan market.

---

## Core Value Development Plan

### Value 1: Reduce Communication Costs

#### Feature 1.1: Intelligent Elder Information Summary

**Goal**: Avoid repeated questions; intelligently organize and present elder information.

**API Design**:
```python
GET /api/customers/{customer_id}/summary
GET /api/customers/{customer_id}/changes?since={timestamp}
GET /api/customers/{customer_id}/info-cards
```

**Database extensions**:
- Add `last_info_update` to `customers` table
- Create `info_change_log` table

**Timeline**: 2–3 weeks

---

### Value 2: Collaboration Support

#### Feature 2.1: Task Management

**API Design**:
```python
POST /api/tasks
GET /api/tasks?elder_id={elder_id}&status={status}
PUT /api/tasks/{task_id}
POST /api/tasks/{task_id}/complete
```

**Timeline**: 4–6 weeks

#### Feature 2.2: Shared Schedules

**API Design**:
```python
POST /api/schedules
GET /api/schedules/calendar?elder_id={elder_id}&start_date={date}&end_date={date}
GET /api/tasks/{task_id}/progress
```

**Timeline**: 3–4 weeks

#### Feature 2.3: Family Member Collaboration

**API Design**:
```python
POST /api/family-members
GET /api/family-members?elder_id={elder_id}
POST /api/notifications
```

**Timeline**: 3–4 weeks

---

### Value 3: Emotional Care

#### Feature 3.1: Emotion Logging System

**API Design**:
```python
POST /api/emotions/log
GET /api/emotions/history?user_id={user_id}&start_date={date}&end_date={date}
GET /api/emotions/analysis?user_id={user_id}&days={30}
```

**Timeline**: 2–3 weeks

#### Feature 3.2: AI Emotional Care

**API Design**:
```python
POST /api/ai/positive-feedback
POST /api/ai/stress-detection
POST /api/ai/care-suggestions
```

**Timeline**: 4–6 weeks

---

## User Scenario Development Plan

### Scenario A: Daily Collaboration

#### Feature A.1: Gentle AI Reminders

**API Design**:
```python
POST /api/reminders
GET /api/tasks/daily-summary?elder_id={elder_id}&date={date}
```

**Reminder template examples**:
- "It's time for medication. Shall we check together?"
- "What a wonderful day! You completed 3 tasks together!"

**Timeline**: 2–3 weeks

---

### Scenario B: Health & Emotion Management

#### Feature B.1: Simplified Emotion Input

- 1–5 quick score buttons
- Voice input support
- Expression recognition (frontend)

**Timeline**: 1–2 weeks (frontend)

---

### Scenario C: Information Organization

#### Feature C.1: Knowledge Base Management

**API Design**:
```python
POST /api/knowledge-base/documents
GET /api/knowledge-base/documents?category={category}&tags={tags}
```

**Timeline**: 2–3 weeks

#### Feature C.2: RAG Intelligent Search

**API Design**:
```python
POST /api/knowledge-base/ask
```

Returns answer with official source links and medical disclaimer.

**Timeline**: 4–6 weeks

---

### Scenario D: Nighttime / Emergency Relief

#### Feature D.1: Night Mode

**API Design**:
```python
GET /api/settings/night-mode?user_id={user_id}
PUT /api/settings/night-mode
```

**Timeline**: 2–3 weeks

#### Feature D.2: Emergency Handling

**API Design**:
```python
POST /api/emergency/record
POST /api/emergency/guide
```

**Timeline**: 3–4 weeks

---

## Development Timeline

### Phase 1: Core Features (Months 1–3)
- Month 1: Task and schedule management
- Month 2: Emotion logging and AI care
- Month 3: Knowledge base and RAG

### Phase 2: Enhanced Features (Months 3–6)
- Month 4: Family collaboration, intelligent summaries
- Month 5: Gentle reminders, task summaries
- Month 6: Night mode, emergency handling

---

## Priority Matrix

| Feature | Importance | Urgency | Priority | Timeline |
|---------|-----------|---------|----------|----------|
| Task management | High | High | P0 | 4–6 weeks |
| Schedule management | High | High | P0 | 3–4 weeks |
| Emotion logging | High | Medium | P1 | 2–3 weeks |
| RAG knowledge base | High | Medium | P1 | 4–6 weeks |
| AI emotional care | Medium | Medium | P2 | 4–6 weeks |
| Family collaboration | Medium | Low | P2 | 3–4 weeks |
| Intelligent summary | Medium | Low | P2 | 2–3 weeks |
| Night mode | Low | Low | P3 | 2–3 weeks |
| Emergency relief | Medium | Medium | P2 | 3–4 weeks |

---

## Tech Stack Recommendations

### Backend
- Task scheduling: Celery + Redis or APScheduler
- Vector DB: ChromaDB (dev) or Pinecone (production)
- Embeddings: OpenAI text-embedding-3-small
- LLM: OpenAI GPT-4 or Claude 3
- TTS: OpenAI TTS or Google Cloud TTS

### Frontend
- State management: React + Zustand
- Calendar: react-big-calendar or fullcalendar
- Voice input: Web Speech API
- Night mode: CSS variables + theme switching

---

## Conclusion

- **Infrastructure**: ✅ Ready
- **Data models**: ✅ Partially ready (needs extension)
- **Core features**: ❌ Need development

**Recommended order**:
1. Task and schedule management (Scenario A)
2. Emotion logging (Scenario B)
3. RAG knowledge base (Scenario C)
4. Night/emergency mode (Scenario D)

**Estimated total**: 12–16 weeks (core), 24–32 weeks (complete)

---

**Maintained by**: Elder Company Development Team  
**Last updated**: 2026-01-21

---

# 日本語 / Japanese

# 開発ロードマップ — 日本市場コア機能

**バージョン**: 1.0.0  
**作成日**: 2026-01-21  
**対象市場**: 日本介護市場

---

## 概要

日本市場のコアバリューを支援するために必要な機能モジュールの開発計画です。

---

## コアバリュー開発計画

### バリュー1：コミュニケーションコストの削減

#### 機能1.1：高齢者情報インテリジェントサマリー

**目標**: 繰り返しの質問を避け、高齢者情報をインテリジェントに整理・提示

**API**:
```python
GET /api/customers/{customer_id}/summary
GET /api/customers/{customer_id}/changes?since={timestamp}
GET /api/customers/{customer_id}/info-cards
```

**開発期間**: 2–3週間

---

### バリュー2：協働サポート

#### 機能2.1：タスク管理

**API**:
```python
POST /api/tasks
GET /api/tasks?elder_id={elder_id}&status={status}
PUT /api/tasks/{task_id}
POST /api/tasks/{task_id}/complete
```

**開発期間**: 4–6週間

#### 機能2.2：共有スケジュール

**開発期間**: 3–4週間

#### 機能2.3：家族メンバー協働

**開発期間**: 3–4週間

---

### バリュー3：情緒ケア

#### 機能3.1：感情ログシステム

**開発期間**: 2–3週間

#### 機能3.2：AI 情緒ケア

**開発期間**: 4–6週間

---

## ユーザーシナリオ開発計画

### シナリオA：日常協働
- AI やさしいリマインダー（2–3週間）

### シナリオB：健康・感情管理
- 感情状態の簡易入力（1–2週間）

### シナリオC：情報整理
- 情報庫管理（2–3週間）
- RAG インテリジェント検索（4–6週間）

### シナリオD：夜間・緊急緩和
- ナイトモード（2–3週間）
- 緊急時対応（3–4週間）

---

## 優先度マトリクス

| 機能 | 重要度 | 緊急度 | 優先度 | 期間 |
|------|--------|--------|--------|------|
| タスク管理 | 高 | 高 | P0 | 4–6週 |
| スケジュール管理 | 高 | 高 | P0 | 3–4週 |
| 感情ログ | 高 | 中 | P1 | 2–3週 |
| RAG 情報庫 | 高 | 中 | P1 | 4–6週 |
| AI 情緒ケア | 中 | 中 | P2 | 4–6週 |
| 家族協働 | 中 | 低 | P2 | 3–4週 |
| ナイトモード | 低 | 低 | P3 | 2–3週 |
| 緊急緩和 | 中 | 中 | P2 | 3–4週 |

---

## 結論

- **基盤**: ✅ 整備済み
- **データモデル**: ✅ 一部整備済み（拡張必要）
- **コア機能**: ❌ 開発必要

**推奨開発順序**:
1. タスク・スケジュール管理（シナリオA）
2. 感情ログ（シナリオB）
3. RAG 情報庫（シナリオC）
4. 夜間・緊急モード（シナリオD）

**総開発期間**: コア機能 12–16週、全機能 24–32週

---

**保守**: Elder Company 開発チーム  
**最終更新**: 2026-01-21
