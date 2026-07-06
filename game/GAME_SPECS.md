# Game Specifications

**Version**: 1.0.0 | **Created**: 2026-01-20

---

## 1. Memory Match

**Goal**: Train memory and attention by matching card pairs.

### Rules
- Cards face-down in a grid; players flip two per turn
- Match → remove; mismatch → flip back
- Goal: find all pairs

### Difficulty
| Level | Pairs | Theme | Hints |
|-------|-------|-------|-------|
| Easy | 4 (8 cards) | Simple shapes | On (3s preview) |
| Medium | 8 (16 cards) | Animals, fruit | Off |
| Hard | 12 (24 cards) | Complex scenes | Off; optional 10-min limit |

### UI
- Min card 80×80px, 300ms flip animation, progress bar, turn counter

### Metrics
- Duration, turns, match rate, errors → memory, attention, strategy scores

---

## 2. Story Chain

**Goal**: Co-create stories; train language and creativity.

### Difficulty
| Level | Sentence Length | Vocabulary | AI Hints |
|-------|-----------------|------------|----------|
| Easy | 5–10 chars | Simple | Strong (full sentences) |
| Medium | 10–20 chars | Moderate | Keywords |
| Hard | 20+ chars | Rich | Weak (words only) |

### Features
- Text/voice input, AI suggestion cards, theme selection, story library

---

## 3. Number Puzzle

**Goal**: Number ordering and basic arithmetic.

### Modes
- **Sort**: Drag numbers into sequence (1–10 to 1–100)
- **Calculate**: Simple addition/subtraction

### Difficulty
| Level | Range | Type | Questions |
|-------|-------|------|-----------|
| Easy | 1–10 | Sort | 5 |
| Medium | 1–20 | Sort + add | 10 |
| Hard | 1–100 | Sort + ± | 15 |

---

## 4. Music Rhythm

**Goal**: Reaction time and coordination via rhythm tapping.

### Difficulty
| Level | BPM | Precision | Hint Lead |
|-------|-----|-----------|-----------|
| Easy | 60–80 | ±500ms | 1s |
| Medium | 80–100 | ±300ms | 0.5s |
| Hard | 100–120 | ±200ms | 0.3s |

### UI
- Central rhythm indicator, min 200×200px tap area, accuracy %, combo counter

---

## 5. Picture Sort

**Goal**: Category classification training.

### Difficulty
| Level | Images | Categories | Hints |
|-------|--------|--------------|-------|
| Easy | 6 | 2 (e.g. animal/plant) | Names + examples |
| Medium | 12 | 3 | Names only |
| Hard | 20 | 4–5 | None |

---

## General Specifications

### Performance
- Touch <100ms | 60fps | Load <2s | Sync <1s | Memory <200MB

### Compatibility
- Chrome 90+, Safari 14+, Firefox 88+, iOS 12+, Android 8+, 720p+ screens

### Accessibility (WCAG 2.1 AA)
- Contrast 4.5:1 | Min 16px font | Min 44×44px targets | Screen reader support

### Security
- Local-first storage, encrypted transport, GDPR-compliant, cloud backup

### API
```
POST /api/games/start | POST /api/games/save
GET /api/games/history | GET /api/games/stats
```

---

# ゲーム仕様書

**バージョン**: 1.0.0 | **作成日**: 2026-01-20

---

## 1. 記憶ペアリング（Memory Match）

**目標**: 記憶力と注意力を訓練。

### ルール
- カードを裏向きに配置、2枚ずつめくる
- 一致 → 除去、不一致 → 裏返し
- 全ペア完成が目標

### 難易度
| レベル | ペア数 | テーマ | ヒント |
|--------|--------|--------|--------|
| 簡単 | 4（8枚） | 単純図形 | あり（3秒表示） |
| 普通 | 8（16枚） | 動物・果物 | なし |
| 難しい | 12（24枚） | 複雑な風景 | なし、10分制限可 |

---

## 2. ストーリー接続（Story Chain）

**目標**: 物語を共同創作、言語能力と創造力を訓練。

### 難易度
| レベル | 文の長さ | 語彙 | AIヒント |
|--------|---------|------|----------|
| 簡単 | 5–10文字 | 簡単 | 強（完全な文） |
| 普通 | 10–20文字 | 中程度 | キーワード |
| 難しい | 20文字以上 | 豊富 | 弱（語のみ） |

---

## 3. 数字パズル（Number Puzzle）

**目標**: 数字認知と論理思考。

### 難易度
| レベル | 範囲 | タイプ | 問題数 |
|--------|------|--------|--------|
| 簡単 | 1–10 | 並べ替え | 5 |
| 普通 | 1–20 | 並べ替え+足し算 | 10 |
| 難しい | 1–100 | 並べ替え+± | 15 |

---

## 4. 音楽リズム（Music Rhythm）

**目標**: 反応力と手眼協調。

### 難易度
| レベル | BPM | 精度 | ヒント先行 |
|--------|-----|------|-----------|
| 簡単 | 60–80 | ±500ms | 1秒 |
| 普通 | 80–100 | ±300ms | 0.5秒 |
| 難しい | 100–120 | ±200ms | 0.3秒 |

---

## 5. 画像分類（Picture Sort）

**目標**: 分類思考と認知能力。

### 難易度
| レベル | 画像数 | カテゴリー | ヒント |
|--------|--------|-----------|--------|
| 簡単 | 6 | 2 | 名称+例 |
| 普通 | 12 | 3 | 名称のみ |
| 難しい | 20 | 4–5 | なし |

---

## 共通仕様

### パフォーマンス
- タッチ <100ms | 60fps | 読込 <2秒 | メモリ <200MB

### 互換性
- Chrome 90+、Safari 14+、iOS 12+、Android 8+、720p以上

### アクセシビリティ（WCAG 2.1 AA）
- コントラスト 4.5:1 | 最小16px | 最小44×44pxタッチ

### セキュリティ
- ローカル優先、暗号化通信、GDPR準拠

**ドキュメント管理**: Elder Company ゲーム開発チーム
