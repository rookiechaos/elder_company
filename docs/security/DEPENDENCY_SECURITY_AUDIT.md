# Dependency Security Audit Guide

**Created**: 2026-01-20

## Overview

This document explains how to audit project dependencies for known security vulnerabilities in third-party libraries.

## Audit Tools

### 1. pip-audit

`pip-audit` checks Python dependencies for known security vulnerabilities.

**Install**:
```bash
pip install pip-audit
```

**Usage**:
```bash
cd backend
pip-audit -r requirements.txt
```

### 2. safety

`safety` is another popular Python dependency security checker.

**Install**:
```bash
pip install safety
```

**Usage**:
```bash
cd backend
safety check -r requirements.txt
```

### 3. GitHub Dependabot

Enable Dependabot on your GitHub repository to automatically detect dependency vulnerabilities and open PRs.

## Current Dependency Status

### Main Dependency Versions

- **FastAPI**: 0.104.1
- **SQLAlchemy**: 2.0.23
- **Pydantic**: 2.5.0
- **PyJWT**: >=2.8.0
- **bcrypt**: >=4.0.1
- **requests**: >=2.31.0

### Recommended Audit Process

1. **Regular audits** (monthly)
   ```bash
   pip-audit -r requirements.txt
   ```

2. **Update dependencies**
   - Check for new versions
   - Read changelogs for security fixes
   - Validate in a test environment before updating

3. **Pin versions**
   - Production should use fixed version numbers
   - Avoid `>=` or `*` wildcards

## Known Security Notes

### 1. requests
- Use >=2.31.0 (fixes multiple security issues)
- Check for updates regularly

### 2. PyJWT
- Use >=2.8.0 (fixes JWT validation vulnerabilities)
- Configure algorithm allowlists carefully

### 3. SQLAlchemy
- Use the latest version (2.0.23)
- Prevent SQL injection via ORM, not raw SQL

## Automated Auditing

### CI/CD Integration

Add dependency security checks to your CI/CD pipeline:

```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install pip-audit
        run: pip install pip-audit
      - name: Run security audit
        run: |
          cd backend
          pip-audit -r requirements.txt
```

## Update Strategy

1. **Security updates**: Apply immediately
2. **Minor updates**: Evaluate monthly
3. **Major updates**: Evaluate quarterly with thorough testing

## Record

- **Last audit date**: 2026-01-20
- **Audit tool**: pip-audit
- **Issues found**: No known high-severity vulnerabilities

---

**Maintained by**: Elder Company Development Team

---

# 日本語 / Japanese

# 依存関係セキュリティ監査ガイド

**作成日**: 2026-01-20

## 概要

本ドキュメントは、プロジェクトの依存関係に既知のセキュリティ脆弱性がないか監査する方法を説明します。

## 監査ツール

### 1. pip-audit

`pip-audit` は Python 依存関係の既知のセキュリティ脆弱性をチェックする専用ツールです。

**インストール**:
```bash
pip install pip-audit
```

**使用方法**:
```bash
cd backend
pip-audit -r requirements.txt
```

### 2. safety

`safety` はもう一つの人気のある Python 依存関係セキュリティチェックツールです。

**インストール**:
```bash
pip install safety
```

**使用方法**:
```bash
cd backend
safety check -r requirements.txt
```

### 3. GitHub Dependabot

GitHub リポジトリで Dependabot を有効にすると、依存関係の脆弱性を自動検出し PR を作成できます。

## 現在の依存関係状態

### 主要依存関係バージョン

- **FastAPI**: 0.104.1
- **SQLAlchemy**: 2.0.23
- **Pydantic**: 2.5.0
- **PyJWT**: >=2.8.0
- **bcrypt**: >=4.0.1
- **requests**: >=2.31.0

### 推奨監査フロー

1. **定期監査**（月1回）
   ```bash
   pip-audit -r requirements.txt
   ```

2. **依存関係の更新**
   - 新バージョンの確認
   - 変更ログでセキュリティ修正を確認
   - テスト環境で検証後に更新

3. **バージョン固定**
   - 本番環境では固定バージョン番号を使用
   - `>=` や `*` ワイルドカードは避ける

## 既知のセキュリティ注意事項

### 1. requests ライブラリ
- >=2.31.0 を使用（複数のセキュリティ脆弱性を修正）
- 定期的に更新を確認

### 2. PyJWT
- >=2.8.0 を使用（JWT 検証の脆弱性を修正）
- アルゴリズムホワイトリスト設定に注意

### 3. SQLAlchemy
- 最新バージョン（2.0.23）を使用
- SQL インジェクション対策（生 SQL ではなく ORM を使用）

## 自動監査

### CI/CD 統合

CI/CD パイプラインに依存関係セキュリティチェックを追加:

```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install pip-audit
        run: pip install pip-audit
      - name: Run security audit
        run: |
          cd backend
          pip-audit -r requirements.txt
```

## 更新戦略

1. **セキュリティ更新**: 即時適用
2. **マイナー更新**: 月1回評価
3. **メジャー更新**: 四半期ごとに評価、十分なテストが必要

## 記録

- **最終監査日**: 2026-01-20
- **監査ツール**: pip-audit
- **発見された問題**: 既知の高危険度脆弱性なし

---

**管理**: Elder Company 開発チーム
