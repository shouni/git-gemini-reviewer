# 🤖 git-gemini-reviewer

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 概要 (About) - 開発チームの生産性を高めるAIパートナー

**`git-gemini-reviewer`** は、**Google Gemini の強力なAI**を活用し、**コードレビューを自動でお手伝い**するコマンドラインツールです。

このツールを導入することで、開発チームは単なる作業の効率化を超え、より**創造的で価値の高い業務**に集中できるようになります。AIは煩雑な初期チェックを担う、**チームの優秀な新しいパートナー**のような存在です。

### 🌸 導入がもたらすポジティブな変化

| メリット | チームへの影響 | 期待される効果 |
| :--- | :--- | :--- |
| **レビューの質とスピードアップ** | **「細かい見落とし」の心配が減ります。** AIがまず基本的なバグやコード規約をチェックしてくれるため、人間のレビュアーは設計やロジックといった**人間ならではの高度な判断**に集中できます。 | レビュー時間が短縮され、**新しい機能の開発に使える時間**が増えます。 |
| **チーム内の知識共有** | **ベテランも若手も、フィードバックの水準が一定になります。** 誰がレビューしても同じように質の高いフィードバックが得られるため、チーム全体の**コーディングスキル向上**を裏側からサポートします。 | チーム内の知識レベルが底上げされ、**属人性のリスク**が解消に向かいます。 |
| **Backlog連携でストレスフリー** | **「レビュー結果の転記」という地味な作業がなくなります。** AIがレビューコメントを自動でBacklogに投稿するため、開発者は**レビュー依頼からフィードバック確認までをスムーズに行えます**。 | **間接業務の負荷が大幅に軽減**され、チームの心理的なストレスが減ります。 |
| **導入のハードルの低さ** | **「大がかりな準備」は不要です。** 既存のGitやBacklog環境に、コマンドラインツールとして**静かに、素早く導入**できます。 | 新しい試みを**スモールスタート**で始められ、効果をすぐに実感できます。 |

-----

## 🛠️ 技術スタック (Tech Stack)

| カテゴリ | 要素 | 詳細な役割 |
| :--- | :--- | :--- |
| **言語** | **Python** (3.9+) | CLIの基盤となる言語。 |
| **AI/API** | **Google Gemini API** | コードレビューのロジックを担うAIモデル。 |
| **パッケージ管理** | `pip`, `setuptools` | パッケージのビルド、依存関係の管理に使用。 |
| **依存ライブラリ** | `google-generativeai`, `python-dotenv`, `requests` | Gemini API連携、環境変数管理、HTTPリクエストに使用。 |
| **連携サービス** | **Backlog** | レビュー結果をコメントとして投稿する課題管理システム。 |

-----

## 🔑 環境変数の設定

本ツールは、APIキーなどの機密情報を環境変数から読み込みます。最も簡単な設定方法は、プロジェクトのルートディレクトリに **`.env`** ファイルを作成することです。

### 📄 `.env` ファイルの例

```bash
# Gemini API キー
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# --- Backlog 連携に必要な設定 (git-gemini-reviewer-backlog コマンド利用時のみ必須) ---
# BacklogのスペースID (例: 会社のアカウント名が "example" ならば "example")
BACKLOG_SPACE_ID="YOUR_BACKLOG_SPACE_ID"

# BacklogのAPIキー (個人設定から発行したもの)
BACKLOG_API_KEY="YOUR_BACKLOG_API_KEY"
```

### 環境変数一覧

| 変数名 | 使用コマンド | 説明 |
| :--- | :--- | :--- |
| **`GEMINI_API_KEY`** | 全てのコマンド | Gemini APIへアクセスするためのキー。**必須**。 |
| **`BACKLOG_SPACE_ID`** | `-backlog` | BacklogスペースのID。URLのサブドメイン部分に該当します。**Backlog連携時に必須**。 |
| **`BACKLOG_API_KEY`** | `-backlog` | Backlogへコメント投稿するためのAPIキー。**Backlog連携時に必須**。 |

-----

## 🛠️ 開発環境のセットアップ

1.  **仮想環境の作成とアクティベート**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **pip の更新 (推奨)**

    ```bash
    pip install --upgrade pip
    ```

3.  **編集可能モードでのインストール**

    ```bash
    pip install --upgrade --force-reinstall -e .
    ```

-----

## 💻 使い方 (Usage)

本ツールは、Backlog連携の有無に応じて**2つのコマンド**を提供します。

| コマンド名 | 目的 | Backlog連携 |
| :--- | :--- | :--- |
| **`git-gemini-reviewer`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** |
| **`git-gemini-reviewer-backlog`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** (`--issue-id` 必須) |

### 1\. 必須引数（コア機能）

| 引数名 | 必須 | 説明 |
| :--- | :--- | :--- |
| `--git-clone-url` | **必須** | レビュー対象の **GitリポジトリURL**。 |
| `--base-branch` | **必須** | 差分比較の**基準となるブランチ**。 |
| `--feature-branch` | **必須** | **レビュー対象**のフィーチャーブランチ。 |

### 2\. オプション引数と詳細

| 引数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `--local-path` | `./var/tmp` | リポジトリを一時的にクローンするローカルパス。 |
| `--gemini-model-name` | `gemini-2.5-flash` | 使用する Gemini モデル名。 |
| `--issue-id` | `None` | **Backlog連携時のみ必須**。レビュー結果を投稿する課題のID（例: `BLG-123`）。 |
| `--no-post` | N/A | **`-backlog` 使用時のみ有効**。API投稿をスキップし、結果をターミナルに出力します。 |

-----

### 実行例

#### A. Backlog連携なし (標準出力)

```bash
# コマンド名: git-gemini-reviewer
git-gemini-reviewer \
  --git-clone-url "git@github.com:shouni/git-gemini-reviewer.git" \
  --base-branch "main" \
  --feature-branch "develop"
```

#### B. Backlog連携あり (課題にコメント投稿)

```bash
# コマンド名: git-gemini-reviewer-backlog
git-gemini-reviewer-backlog \
  --git-clone-url "..." \
  --base-branch "main" \
  --feature-branch "develop" \
  --issue-id "BLG-123"
```
