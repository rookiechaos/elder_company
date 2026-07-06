# Game Design Document

**Version**: 1.0.0 | **Created**: 2026-01-20 | **Updated**: 2026-01-20

---

## Design Philosophy

### Core Values

1. **Collaboration over competition** — Caregivers and older adults are partners with shared goals
2. **Cognitive training through fun** — Training embedded in enjoyable play
3. **Respect and dignity** — Older adults are active participants, not passive recipients
4. **Emotional connection first** — Games strengthen relationships and create shared memories

---

## User Research

### Older Adult Users (65–85)
- **Needs**: Stay cognitively active, build caregiver relationships, feel achievement
- **Challenges**: Declining vision, reduced dexterity, shorter attention, unfamiliarity with technology

### Caregiver Users (25–55)
- **Needs**: Build trust, find effective interaction methods, assess cognitive state
- **Challenges**: Limited time, need quick onboarding, must see measurable results

---

## Game Mechanics

### Dual-Player Collaboration
- Shared goals, turn-based or simultaneous play, communication required, no failure — only completion

### Adaptive Difficulty
- Auto-adjust from performance; manual override by caregiver; tracks ability trends

### Achievements & Rewards
- Non-competitive, progress-focused, visual badges, shareable with family

### Progress Tracking
- Session data, trend charts, simple reports for caregivers

---

## UI/UX Design

### Principles
- **Clear**: Min 44×44px touch targets, ≤3 navigation levels, feedback on every action
- **High contrast**: WCAG AA (4.5:1), min 16px text (18–20px recommended)
- **Warm**: Rounded corners, soft colors, encouraging language

### Color Palette
| Role | Color |
|------|-------|
| Primary | #4A90E2 (calm blue) |
| Success | #7ED321 (green) |
| Accent | #F5A623 (warm orange) |
| Background | #F8F9FA |

### Typography
- Titles: 24–32px bold | Body: 18–20px | Labels: 16px | System fonts preferred

---

## Technical Design

### Frontend Layers
```
React App → Game Engine (state, logic, animation) → UI Components → Services (API, storage) → Platform
```

### Performance Targets
- Touch response <100ms | 60fps animations | First paint <2s | Service Worker offline cache

---

## Accessibility

- **Visual**: 3-level font scaling, high-contrast mode, color-blind-safe icons
- **Audio**: Action sounds, optional BGM, voice prompts, speech input (Story Chain)
- **Motor**: Large touch areas, simplified gestures, no time pressure, pause anytime

---

## Personalization

- Initial cognitive assessment and preference survey
- Auto/manual/hybrid difficulty modes
- Theme, font, layout, and animation intensity customization

---

## Game Designs (Summary)

| Game | Rules | Collaboration | Difficulty Levers |
|------|-------|---------------|-------------------|
| Memory Match | Flip pairs until all matched | Turn-taking, shared memory | 4–12 pairs, hints, time limit |
| Story Chain | Alternate sentences | Co-creation, AI hints | Sentence length, vocabulary, themes |
| Number Puzzle | Order numbers / arithmetic | Hints, shared strategy | Range 1–100, hints count |
| Music Rhythm | Tap on beat | Sing/clap together | BPM, precision window |
| Picture Sort | Drag to categories | Discuss classifications | 6–20 images, 2–5 categories |

---

## Data Models

```typescript
interface GameSession {
  id: string;
  gameType: 'memory' | 'story' | 'number' | 'music' | 'picture';
  player1: string; player2: string;
  difficulty: 'easy' | 'medium' | 'hard';
  completion: number;
}
```

---

## Deployment Phases

1. **MVP (3 mo)**: 2 core games, basic collaboration, simple tracking
2. **Expand (6 mo)**: All 5 games, full personalization, analytics
3. **Optimize (9 mo)**: Performance, UX polish, new features

---

# ゲーム設計ドキュメント

**バージョン**: 1.0.0 | **作成日**: 2026-01-20 | **更新**: 2026-01-20

---

## 設計理念

### 核心価値

1. **協働而非競争** — 介護者と高齢者はパートナー
2. **認知訓練と娯楽の融合** — 楽しさの中で自然に訓練
3. **尊重と尊厳** — 高齢者は能動的参加者
4. **感情的つながり優先** — 関係構築と思い出創造

---

## ユーザー調査

### 高齢者ユーザー（65–85歳）
- **ニーズ**: 認知活性、介護者との良好な関係、達成感
- **課題**: 視力低下、手指の不自由、注意力の短さ、新技術への不慣れ

### 介護者ユーザー（25–55歳）
- **ニーズ**: 信頼関係構築、効果的な交流方法、認知状態評価
- **課題**: 時間制限、迅速な習得、効果の可視化

---

## ゲームメカニクス

### デュアルプレイヤー協働
- 共同目標、交互または同時操作、コミュニケーション必須、失敗なし（完成度のみ）

### 適応的難易度
- パフォーマンスに基づく自動調整、介護者による手動設定、能力変化の追跡

### 達成と報酬
- 非競争的、進歩重視、視覚バッジ、家族への共有

---

## UI/UX設計

### 原則
- **明確**: 最小44×44pxタッチ、3階層以内のナビ、全操作にフィードバック
- **高コントラスト**: WCAG AA、最小16px（推奨18–20px）
- **温かみ**: 角丸、柔らかい色、励ましの言葉

### カラーパレット
| 役割 | 色 |
|------|-----|
| メイン | #4A90E2（穏やかな青） |
| 成功 | #7ED321（緑） |
| アクセント | #F5A87C（温かいオレンジ） |
| 背景 | #F8F9FA |

---

## 技術設計

### パフォーマンス目標
- タッチ応答 <100ms | 60fps | 初回表示 <2秒 | Service Workerオフライン

---

## アクセシビリティ

- **視覚**: 3段階フォント、ハイコントラスト、色覚対応アイコン
- **聴覚**: 操作音、BGM、音声プロンプト、音声入力
- **操作**: 大タッチエリア、簡易ジェスチャ、時間制限なし、いつでも一時停止

---

## ゲーム設計（概要）

| ゲーム | ルール | 協働 | 難易度調整 |
|--------|--------|------|-----------|
| 記憶ペアリング | カードをめくってペア完成 | 交互操作、共同記憶 | 4–12ペア、ヒント |
| ストーリー接続 | 交互に文を追加 | 共同創作、AI提案 | 文長、語彙、テーマ |
| 数字パズル | 並べ替え・計算 | ヒント、戦略議論 | 1–100、ヒント数 |
| 音楽リズム | リズムに合わせてタップ | 一緒に歌・拍子 | BPM、精度 |
| 画像分類 | カテゴリーにドラッグ | 分類の議論 | 6–20枚、2–5カテゴリー |

---

## デプロイフェーズ

1. **MVP（3ヶ月）**: 2コアゲーム、基本協働、簡易追跡
2. **拡張（6ヶ月）**: 全5ゲーム、パーソナライズ、分析
3. **最適化（9ヶ月）**: パフォーマンス、UX改善

**ドキュメント管理**: Elder Company 開発チーム
