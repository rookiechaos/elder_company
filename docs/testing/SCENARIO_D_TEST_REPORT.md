# Scenario D Feature Test Report

**Date:** 2026-01-20  
**Environment:** chatbot conda  
**Method:** FastAPI TestClient (no open ports)

> Scenario D: night mode and emergency relief features.

---

## Overview

Verified:

1. Night mode service
2. Emergency service
3. API endpoints
4. Frontend components
5. Database models

---

## Results — 8/8 passed

| Test | Status |
|------|--------|
| Database models (`EmergencyRecordDB`, `NightModeConfigDB`) | Pass |
| Night mode service | Pass |
| Emergency service | Pass |
| Reminder service (fallback) | Pass |
| Night mode API endpoints | Pass |
| Emergency API endpoints | Pass |
| Frontend component files | Pass |
| `App.jsx` integration | Pass |

---

## Key details

### Night mode service
- Create/get/update config; activation check
- Test config: `enabled=True`, `brightness="low"`, `22:00`–`07:00`

### Emergency service
- Record emergency (no AI guidance to avoid API calls)
- History query
- Sample record: `emergency_dc68fe3ccfb5`, type `emotional`, severity `medium`

### API endpoints
- `GET /api/night-mode/config`, `GET /api/night-mode/active`
- `POST /api/emergency/record`, `GET /api/emergency/history`
- 401 without auth — expected

### Frontend
- `frontend/src/components/NightMode.jsx` (+ CSS)
- `frontend/src/components/EmergencyRecord.jsx` (+ CSS)
- Imported in `App.jsx` with routes and icons (Moon, AlertTriangle)

---

## Environment

- Framework: FastAPI TestClient
- Database: SQLite (in-memory)
- `TEST_MODE=true`

---

## Conclusion

All Scenario D backend services and frontend components verified.

**Status:** All passed — 2026-01-20

---

# シナリオ D 機能テストレポート

**日付:** 2026-01-20  
**環境:** chatbot conda  
**方式:** FastAPI TestClient（ポート不要）

> シナリオ D: ナイトモードと緊急緩和機能。

---

## 概要

ナイトモード、緊急、API、フロントコンポーネント、DB モデルを検証。

---

## 結果 — 8/8 合格

| テスト | 状態 |
|--------|------|
| DB モデル | 合格 |
| ナイトモードサービス | 合格 |
| 緊急サービス | 合格 |
| リマインダー（フォールバック） | 合格 |
| ナイトモード API | 合格 |
| 緊急 API | 合格 |
| フロントコンポーネント | 合格 |
| `App.jsx` 統合 | 合格 |

---

## 検証 API

`/api/night-mode/config` · `/api/night-mode/active` · `/api/emergency/record` · `/api/emergency/history`

未認証 401 は正常。

---

## 結論

シナリオ D のバックエンド・フロントエンド — すべて正常。

**状態:** 全合格 — 2026-01-20
