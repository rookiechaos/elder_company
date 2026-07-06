# Attack Prevention Mechanisms Summary

**Created**: 2026-01-20

## Quick Reference

### Implemented Protections

1. **Rate limiting** — Prevents DDoS and brute-force attacks
   - Default: 100 requests/minute
   - Auth: 5 requests/minute
   - Translation: 10 requests/minute

2. **Authentication security** — Prevents account attacks
   - bcrypt password hashing
   - JWT strong-key validation
   - Account status management

3. **Input validation** — Prevents injection attacks
   - Pydantic model validation
   - Input sanitization functions
   - File upload validation

4. **Content security** — Prevents malicious content
   - NSFW detection
   - Content filtering

5. **Network security** — Prevents network attacks
   - Security response headers (CSP, HSTS, etc.)
   - CORS configuration
   - HTTPS enforcement

6. **Path security** — Prevents path traversal
   - Path normalization
   - Directory validation

7. **Error security** — Prevents information leakage
   - Production error hiding
   - Sensitive information filtering

8. **Database security** — Prevents data attacks
   - ORM usage
   - Transaction management

9. **Logging and monitoring** — Attack detection
   - Request logs
   - Error logs
   - Performance monitoring

10. **File security** — Prevents file attacks
    - Type whitelist
    - Size limits
    - Path validation

## Full Documentation

See the complete guide: [ATTACK_PREVENTION_MECHANISMS.md](./ATTACK_PREVENTION_MECHANISMS.md)

---

# 日本語 / Japanese

# 攻撃防止メカニズム サマリー

**作成日**: 2026-01-20

## クイックリファレンス

### 実装済みの防御

1. **レート制限** — DDoS・ブルートフォース対策
   - デフォルト: 100回/分
   - 認証: 5回/分
   - 翻訳: 10回/分

2. **認証セキュリティ** — アカウント攻撃対策
   - bcrypt パスワードハッシュ
   - JWT 強キー検証
   - アカウント状態管理

3. **入力検証** — インジェクション攻撃対策
   - Pydantic モデル検証
   - 入力サニタイズ関数
   - ファイルアップロード検証

4. **コンテンツセキュリティ** — 悪意あるコンテンツ対策
   - NSFW 検出
   - コンテンツフィルタリング

5. **ネットワークセキュリティ** — ネットワーク攻撃対策
   - セキュリティレスポンスヘッダー（CSP、HSTS 等）
   - CORS 設定
   - HTTPS 強制

6. **パスセキュリティ** — パストラバーサル対策
   - パス正規化
   - ディレクトリ検証

7. **エラーセキュリティ** — 情報漏洩対策
   - 本番環境でのエラー非表示
   - 機密情報フィルタリング

8. **データベースセキュリティ** — データ攻撃対策
   - ORM 使用
   - トランザクション管理

9. **ログ・監視** — 攻撃検出
   - リクエストログ
   - エラーログ
   - パフォーマンス監視

10. **ファイルセキュリティ** — ファイル攻撃対策
    - タイプホワイトリスト
    - サイズ制限
    - パス検証

## 詳細ドキュメント

完全版: [ATTACK_PREVENTION_MECHANISMS.md](./ATTACK_PREVENTION_MECHANISMS.md)
