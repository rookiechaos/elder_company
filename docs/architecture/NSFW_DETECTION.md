# NSFW Content Detection System

## Overview

The NSFW (Not Safe For Work) content detection system detects and blocks inappropriate content across all user interactions, ensuring platform safety and suitability.

## Features

### 1. Multi-Provider Support
- **OpenAI Moderation API** (primary): Official OpenAI content moderation API
- **Keyword detection** (fallback): Used when AI API is unavailable

### 2. Detection Levels
- **SAFE**: Content is safe to process
- **SUSPICIOUS**: Content is suspicious, requires further review
- **UNSAFE**: Content is inappropriate and must be blocked

### 3. Integrated Endpoints
NSFW detection is integrated into all user interaction endpoints:
- `/api/translate` — Translation
- `/api/chat` — Chat
- `/api/voice/speech-to-text` — Speech-to-text
- `/api/voice/text-to-speech` — Text-to-speech

## Configuration

### Environment Variables

Configure in `do-not-upload/env/.env`:

```env
# NSFW Detection Configuration
NSFW_DETECTION_ENABLED=true  # Enable NSFW detection (default: true)
NSFW_DETECTION_STRICT=true   # Strict mode: block all flagged content (default: true)
                              # If false, only block unsafe content

# AI Provider (for NSFW detection)
AI_PROVIDER=openai  # openai, claude, gemini
OPENAI_API_KEY=your-openai-api-key  # If using OpenAI
```

### Configuration Notes

- **NSFW_DETECTION_ENABLED**: Controls whether NSFW detection is active
  - `true`: Enable detection (recommended)
  - `false`: Disable detection (not recommended for production)

- **NSFW_DETECTION_STRICT**: Controls detection strictness
  - `true`: Strict mode — all flagged content is blocked
  - `false`: Relaxed mode — only clearly unsafe content is blocked

## Usage

### In Code

```python
from services.nsfw_detector import get_nsfw_detector

# Get detector instance
nsfw_detector = get_nsfw_detector()

# Check text
result = await nsfw_detector.check("User input text", language="ja")

# Check if should block
if nsfw_detector.should_block(result):
    raise HTTPException(
        status_code=400,
        detail=nsfw_detector.get_block_message("ja")
    )
```

### Detection Result Format

```python
{
    "safe": True,
    "level": "safe",                 # safe, suspicious, unsafe
    "flagged": False,
    "flagged_categories": [],
    "scores": {...},
    "blocked": False,
    "reason": "No unsafe content detected",
    "provider": "openai"
}
```

## Detection Categories

OpenAI Moderation API detects:
- `hate`: Hate content
- `hate/threatening`: Threatening hate content
- `harassment`: Harassment
- `harassment/threatening`: Threatening harassment
- `self-harm`: Self-harm content
- `self-harm/intent`: Self-harm intent
- `self-harm/instructions`: Self-harm instructions
- `sexual`: Sexual content
- `sexual/minors`: Sexual content involving minors
- `violence`: Violence
- `violence/graphic`: Graphic violence

## Error Handling

### When Inappropriate Content Is Detected

The system will:
1. Log a warning (content preview and detection result)
2. Return 400 with a user-friendly block message
3. Prevent the request from continuing

### Block Messages

The system returns language-appropriate block messages. English example:

> "Sorry, your input contains inappropriate content and cannot be processed. Please use polite and respectful language."

Japanese and other locales use equivalent messages via `get_block_message(language)`.

## Logging

All blocked requests are logged with:
- Content preview (first 50 characters)
- Detection level
- Detection reason
- Flagged categories

## Performance Considerations

- NSFW detection runs at the earliest stage of request processing
- Falls back to keyword detection if OpenAI API is unavailable
- Detection failures do not fail the entire request (unless inappropriate content is detected)

## Best Practices

1. **Always enable in production**: `NSFW_DETECTION_ENABLED` should be `true`
2. **Use strict mode**: For care platforms, recommend `NSFW_DETECTION_STRICT=true`
3. **Monitor logs**: Regularly review NSFW detection logs for content quality
4. **API key security**: Store OpenAI API keys in `do-not-upload/env/.env`; never commit to version control

## Troubleshooting

### OpenAI API Unavailable

If OpenAI API is unavailable or not configured:
- System falls back to keyword detection
- Warning: "Warning: OpenAI not available for NSFW detection"
- Functionality remains available but detection accuracy may be reduced

### False Positives

If false positives occur:
1. Check `scores` in the detection result for category scores
2. Consider adjusting `NSFW_DETECTION_STRICT`
3. Contact an administrator to review specific cases

## Future Improvements

- [ ] Support more AI provider moderation APIs (Claude, Gemini)
- [ ] Custom keyword lists
- [ ] Detection result caching
- [ ] Detection statistics and reporting
- [ ] Custom block messages

---

# 日本語 / Japanese

# NSFW コンテンツ検出システム

## 概要

NSFW（Not Safe For Work）コンテンツ検出システムは、すべてのユーザーインタラクションで不適切なコンテンツを検出・ブロックし、プラットフォームの安全性と適切性を確保します。

## 機能

### 1. マルチプロバイダー対応
- **OpenAI Moderation API**（主要）: OpenAI 公式コンテンツモデレーション API
- **キーワード検出**（フォールバック）: AI API が利用不可の場合に使用

### 2. 検出レベル
- **SAFE**: コンテンツは安全、処理可能
- **SUSPICIOUS**: コンテンツは疑わしい、追加レビューが必要
- **UNSAFE**: コンテンツは不適切、ブロック必須

### 3. 統合エンドポイント
NSFW 検出は以下のすべてのユーザーインタラクションエンドポイントに統合:
- `/api/translate` — 翻訳
- `/api/chat` — チャット
- `/api/voice/speech-to-text` — 音声テキスト変換
- `/api/voice/text-to-speech` — テキスト音声変換

## 設定

### 環境変数

`do-not-upload/env/.env` で設定:

```env
# NSFW Detection Configuration
NSFW_DETECTION_ENABLED=true  # NSFW 検出を有効化（デフォルト: true）
NSFW_DETECTION_STRICT=true   # 厳格モード: フラグ付きコンテンツをすべてブロック（デフォルト: true）
                              # false の場合、不安全なコンテンツのみブロック

# AI Provider (for NSFW detection)
AI_PROVIDER=openai  # openai, claude, gemini
OPENAI_API_KEY=your-openai-api-key  # OpenAI 使用時
```

### 設定説明

- **NSFW_DETECTION_ENABLED**: NSFW 検出の有効/無効
  - `true`: 検出を有効化（推奨）
  - `false`: 検出を無効化（本番環境では非推奨）

- **NSFW_DETECTION_STRICT**: 検出の厳格さ
  - `true`: 厳格モード — フラグ付きコンテンツをすべてブロック
  - `false`: 緩和モード — 明確に不安全なコンテンツのみブロック

## 使用方法

### コードでの使用

```python
from services.nsfw_detector import get_nsfw_detector

# 検出器インスタンスを取得
nsfw_detector = get_nsfw_detector()

# テキストを検出
result = await nsfw_detector.check("ユーザー入力テキスト", language="ja")

# ブロックすべきか確認
if nsfw_detector.should_block(result):
    raise HTTPException(
        status_code=400,
        detail=nsfw_detector.get_block_message("ja")
    )
```

### 検出結果フォーマット

```python
{
    "safe": True,
    "level": "safe",                 # safe, suspicious, unsafe
    "flagged": False,
    "flagged_categories": [],
    "scores": {...},
    "blocked": False,
    "reason": "No unsafe content detected",
    "provider": "openai"
}
```

## 検出カテゴリ

OpenAI Moderation API が検出するカテゴリ:
- `hate`: ヘイトコンテンツ
- `hate/threatening`: 脅迫的ヘイトコンテンツ
- `harassment`: ハラスメント
- `harassment/threatening`: 脅迫的ハラスメント
- `self-harm`: 自傷コンテンツ
- `self-harm/intent`: 自傷の意図
- `self-harm/instructions`: 自傷の説明
- `sexual`: 性的コンテンツ
- `sexual/minors`: 未成年者を含む性的コンテンツ
- `violence`: 暴力
- `violence/graphic`: グラフィック暴力

## エラー処理

### 不適切なコンテンツが検出された場合

システムは:
1. 警告ログを記録（コンテンツプレビューと検出結果）
2. ユーザー向けブロックメッセージ付きで 400 を返す
3. リクエストの継続処理を阻止

### ブロックメッセージ

システムは言語に応じたブロックメッセージを返す:
- **日本語**: "申し訳ございませんが、入力された内容に不適切な内容が含まれているため、処理できません。礼儀正しい言葉を使用してください。"
- **英語**: "Sorry, your input contains inappropriate content and cannot be processed. Please use polite and respectful language."

## ログ記録

ブロックされたすべてのリクエストをログに記録:
- コンテンツプレビュー（最初の50文字）
- 検出レベル
- 検出理由
- フラグ付きカテゴリ

## パフォーマンス考慮事項

- NSFW 検出はリクエスト処理の最早期段階で実行
- OpenAI API が利用不可の場合、キーワード検出に自動フォールバック
- 検出失敗はリクエスト全体を失敗させない（不適切なコンテンツが検出された場合を除く）

## ベストプラクティス

1. **本番環境では必ず有効化**: `NSFW_DETECTION_ENABLED` は常に `true`
2. **厳格モードを使用**: 介護プラットフォームでは `NSFW_DETECTION_STRICT=true` を推奨
3. **ログを監視**: NSFW 検出ログを定期的に確認し、コンテンツ品質を把握
4. **API キーのセキュリティ**: OpenAI API キーは `do-not-upload/env/.env` に保存、バージョン管理にコミットしない

## トラブルシューティング

### OpenAI API が利用不可

OpenAI API が利用不可または未設定の場合:
- キーワード検出に自動フォールバック
- 警告: "Warning: OpenAI not available for NSFW detection"
- 機能は利用可能だが検出精度が低下する可能性

### 誤検出

誤検出が発生した場合:
1. 検出結果の `scores` フィールドでカテゴリスコアを確認
2. `NSFW_DETECTION_STRICT` 設定の調整を検討
3. 管理者に具体的なケースのレビューを依頼

## 今後の改善

- [ ] より多くの AI プロバイダーのモデレーション API 対応（Claude, Gemini）
- [ ] カスタムキーワードリストの追加
- [ ] 検出結果のキャッシュ
- [ ] 検出統計とレポート機能
- [ ] カスタムブロックメッセージのサポート
