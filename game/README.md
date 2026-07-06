# Elder Company - Collaborative Game Platform

**Version**: 1.0.0  
**Created**: 2026-01-20  
**Last Updated**: 2026-01-20

---

## Project Overview

The Elder Company collaborative game platform is a mobile game collection designed for older adults and caregivers, promoting emotional connection and cognitive training through shared play.

### Core Principles

- **Collaborative play** — Caregivers and older adults play together, cooperating rather than competing
- **Cognitive training** — Games maintain and improve cognitive abilities
- **Emotional connection** — Build understanding and trust through play
- **Personalization** — Adjust difficulty based on ability and interests

---

## Game List

### 1. Memory Match
Classic card-matching game for memory and attention. Players take turns flipping cards to find pairs. Custom themes (animals, food, scenery). Best for mild cognitive impairment and attention training.

### 2. Story Chain
Players take turns adding sentences to co-create a story. AI provides creative suggestions and vocabulary hints. Stories can be saved and shared.

### 3. Number Puzzle
Number ordering and basic arithmetic. Difficulty scales from 1–10 sorting to addition/subtraction.

### 4. Music Rhythm
Tap along with familiar music to train reaction time and coordination. Caregivers and older adults can sing or clap together.

### 5. Picture Sort
Drag images into categories (animals, plants, food) to train classification and logical thinking.

---

## Technical Architecture

### Frontend
- **Framework**: React / React Native (PWA)
- **State**: Redux / Zustand
- **Animation**: Framer Motion
- **Audio**: Web Audio API
- **Storage**: LocalStorage / IndexedDB

### Backend Integration
- Elder Company Backend API
- Game data stored per user account
- Progress tracking and difficulty personalization

### Mobile Optimization
- PWA install support, large touch targets, accessibility (voice, large fonts), partial offline play

---

## Project Structure

```
game/
├── README.md
├── DESIGN.md
├── GAME_SPECS.md
├── frontend/src/games/   # MemoryMatch, StoryChain, etc.
├── assets/
└── docs/API.md
```

---

## Design Principles

1. **Simple** — Large buttons, clear icons, intuitive flow
2. **Accessible** — Large fonts, high contrast, voice feedback
3. **Personalized** — Adaptive difficulty, themes, achievements
4. **Collaborative** — Non-competitive, communication-focused
5. **Engaging** — Animations, sound, rewards

---

## Quick Start

```bash
cd game/frontend
npm install
npm run dev
```

---

## Platform Integration

| Endpoint | Purpose |
|----------|---------|
| `POST /api/games/start` | Start session |
| `POST /api/games/save` | Save progress |
| `GET /api/games/history` | Game history |
| `GET /api/games/stats` | Statistics |

Data syncs across devices; caregivers can view older adult performance.

---

## Roadmap

- **3 months**: 5 core games, basic tracking, mobile optimization
- **6 months**: 3–5 more games, AI recommendations, family sharing
- **1 year**: VR/AR, multilingual support, community features

---

**License**: Part of Elder Company platform.

---

# Elder Company - 協働ゲームプラットフォーム

**バージョン**: 1.0.0  
**作成日**: 2026-01-20  
**最終更新**: 2026-01-20

---

## プロジェクト概要

Elder Company 協働ゲームプラットフォームは、高齢者と介護者向けのモバイルゲーム集です。共同プレイを通じて感情的なつながりと認知訓練を促進します。

### 核心理念

- 🤝 **協働ゲーム** — 競争ではなく協力
- 🎯 **認知訓練** — 認知能力の維持・向上
- 💬 **感情的つながり** — 理解と信頼の構築
- 🎨 **パーソナライゼーション** — 能力と興味に応じた難易度調整

---

## ゲーム一覧

### 1. 記憶ペアリング（Memory Match）
カードをめくってペアを探す古典的ゲーム。記憶力と注意力の訓練に最適。

### 2. ストーリー接続（Story Chain）
交互に文を追加して物語を共同創作。AIが創意提案と語彙ヒントを提供。

### 3. 数字パズル（Number Puzzle）
数字の並べ替えと基礎計算。1〜10の並べ替えから加減算まで難易度調整可能。

### 4. 音楽リズム（Music Rhythm）
馴染みのある音楽に合わせてタップ。反応力と協調性を訓練。

### 5. 画像分類（Picture Sort）
画像をカテゴリー別にドラッグ分類。分類思考と認知能力を訓練。

---

## 技術アーキテクチャ

### フロントエンド
- **フレームワーク**: React / React Native (PWA)
- **状態管理**: Redux / Zustand
- **アニメーション**: Framer Motion
- **ストレージ**: LocalStorage / IndexedDB

### バックエンド連携
- Elder Company Backend API
- ユーザーアカウントにゲームデータ保存
- 進捗追跡と難易度パーソナライズ

### モバイル最適化
- PWA対応、大きなタッチターゲット、音声・大フォント対応、部分オフライン

---

## クイックスタート

```bash
cd game/frontend
npm install
npm run dev
```

---

## プラットフォーム連携

| エンドポイント | 用途 |
|---------------|------|
| `POST /api/games/start` | セッション開始 |
| `POST /api/games/save` | 進捗保存 |
| `GET /api/games/history` | 履歴取得 |
| `GET /api/games/stats` | 統計取得 |

---

## 今後の計画

- **3ヶ月**: 5つのコアゲーム、基本データ追跡
- **6ヶ月**: 追加ゲーム、AI推薦、家族共有
- **1年**: VR/AR、多言語、コミュニティ機能

---

**ライセンス**: Elder Company プラットフォームの一部
