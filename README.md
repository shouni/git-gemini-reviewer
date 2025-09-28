# 🤖 Git Gemini Reviewer

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 概要 (About) - 開発チームの生産性を高めるAIパートナー

**`Git Gemini Reviewer`** は、**Google Gemini の強力なAI**を活用し、**コードレビューを自動でお手伝い**するコマンドラインツールです。

このツールを導入することで、開発チームは単なる作業の効率化を超え、より**創造的で価値の高い業務**に集中できるようになります。AIは煩雑な初期チェックを担う、**チームの優秀な新しいパートナー**のような存在です。

このツールは、GitHub や GitLab など、SSH アクセスが可能な任意の Git リポジトリで動作し、コードレビューのプロセスを自動化・高速化します。

### 🌸 導入がもたらすポジティブな変化

| メリット | チームへの影響 | 期待される効果 |
| :--- | :--- | :--- |
| **レビューの質とスピードアップ** | **「細かい見落とし」の心配が減ります。** AIがまず基本的なバグやコード規約をチェックしてくれるため、人間のレビュアーは設計やロジックといった**人間ならではの高度な判断**に集中できます。 | レビュー時間が短縮され、**新しい機能の開発に使える時間**が増えます。 |
| **チーム内の知識共有** | **ベテランも若手も、フィードバックの水準が一定になります。** 誰がレビューしても同じように質の高いフィードバックが得られるため、チーム全体の**コーディングスキル向上**を裏側からサポートします。 | チーム内の知識レベルが底上げされ、**属人性のリスク**が解消に向かいます。 |
| **Backlog連携でストレスフリー** | **「レビュー結果の転記」という地味な作業がなくなります。** AIがレビューコメントを自動でBacklogに投稿するため、開発者は**レビュー依頼からフィードバック確認までをスムーズに行えます**。 | **間接業務の負荷が大幅に軽減**され、チームの心理的なストレスが減ります。 |
| **導入のハードルの低さ** | **「大がかりな準備」は不要です。** 既存のGitやBacklog環境に、コマンドラインツールとして**静かに、素早く導入**できます。 | 新しい試みを**スモールスタート**で始められ、効果をすぐに実感できます。 |

-----

## ✨ 技術スタック (Technology Stack)

| カテゴリ | 要素 / ライブラリ | 役割 |
| :--- | :--- | :--- |
| **言語** | **Python** (3.9+) | CLIの基盤となる言語。 |
| **CLI フレームワーク** | `argparse` / `setuptools` | コマンドライン引数の解析とエントリポイントの管理。 |
| **Git 操作** | **Python `subprocess` 経由の Git** | リポジトリのクローン、フェッチ、および差分 (`git diff`) の取得に使用します。SSH認証に対応しています。 |
| **AI モデル** | **Google Gemini API** | 取得したコード差分を分析し、レビューコメントを生成するために使用します。 |
| **連携サービス** | **Backlog** | レビュー結果をコメントとして投稿する課題管理システム。 |

-----

## 🛠️ 開発環境のセットアップ

### 1\. Pythonのインストール (Windows / macOS)

本ツールはPython 3.9以上が必要です。以下の手順でインストールしてください。（*詳細は省略*）

### 2\. 仮想環境の作成とアクティベート

プロジェクトの作業ディレクトリで以下のコマンドを実行し、仮想環境を構築・アクティベートします。

| OS | コマンド |
| :--- | :--- |
| **Windows** | `python -m venv .venv`<br>`.\.venv\Scripts\activate` |
| **macOS** | `python3 -m venv .venv`<br>`source .venv/bin/activate` |

### 3\. リポジトリのクローン

仮想環境をアクティベートした後、本プロジェクトをローカルにクローンします。

```bash
git clone YOUR_REPOSITORY_URL
cd git-gemini-reviewer
```

### 4\. 編集可能モードでのインストール

プロジェクトのルートディレクトリで、以下のコマンドを実行し、依存関係をインストールします。

```bash
pip install --upgrade --force-reinstall -e .
```

-----

## 🔑 環境変数の設定 (APIキーとBacklog情報)

本ツールは、APIキーなどの機密情報を**環境変数**または **`config.py`** ファイルから読み込みます。**推奨される設定方法**は、プロジェクトのルートディレクトリに **`config.py`** を作成することです。

### 📄 必要な変数一覧

| 変数名 | 使用コマンド | 説明 | 必須条件 |
| :--- | :--- | :--- | :--- |
| **`GEMINI_API_KEY`** | 全てのコマンド | Gemini APIへアクセスするためのキー。 | **必須** |
| **`BACKLOG_API_KEY`** | `backlog-reviewer` | Backlogへコメント投稿するためのAPIキー。 | **Backlog連携時のみ必須** |
| **`BACKLOG_DOMAIN`** | `backlog-reviewer` | Backlogスペースの**ドメイン名**（例: `your-space.backlog.jp`）。URL全体ではありません。 | **Backlog連携時のみ必須** |
| **`PROJECT_ID`** | `backlog-reviewer` | Backlogでリポジトリ情報取得などに使用する**プロジェクトID**（数値またはキー）。 | **Backlog連携時のみ必須** |

### 📄 `config.py` ファイルの例 (推奨)

プロジェクトのルートディレクトリに以下の内容で **`config.py`** を作成してください。

```python
# Gemini API キー (必須)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# --- Backlog 連携に必要な設定 (backlog-reviewer コマンド利用時のみ必須) ---
# BacklogのAPIキー
BACKLOG_API_KEY = "YOUR_BACKLOG_API_KEY"

# Backlogのドメイン名 (例: your-space.backlog.jp)
BACKLOG_DOMAIN = "your-space.backlog.jp" 

# Backlogでリポジトリ情報取得などに使用するプロジェクトID (数値またはキー)
PROJECT_ID = "PROJECT_KEY_OR_ID"
```

-----

## 5\. プロンプトファイルの準備 (必須)

このツールは、Geminiにレビューを依頼する際の指示を記述したプロンプトファイルを読み込みます。

| ファイル名 | 役割 | 説明 |
| :--- | :--- | :--- |
| **`prompt_generic.md`** | 汎用レビュー用のプロンプト | Backlogに依存しない標準のレビューコメントを生成。 |
| **`prompt_backlog.md`** | Backlog連携レビュー用のプロンプト | Backlogの課題形式に合わせた、よりフォーマルなレビューコメントを生成。 |

これらのファイルが**プロジェクトの設定ディレクトリ**（`core/prompts`など）に存在する必要があります。各ファイルには、**必ず**コード差分が挿入されるプレースホルダー **`%s`** を含めてください。（*`prompt_generic.md` の内容例は元のドキュメント通りで省略*）

-----

## 🚀 使い方 (Usage) と実行例

### GitClientの賢い動作

本ツールは、ローカルにリポジトリが存在する場合、渡された `--git-clone-url` と既存のリモートURLを比較します。（*詳細は元のドキュメント通りで省略*）

### コマンド一覧

本ツールは、Backlog連携の有無に応じて**2つのコマンド**を提供します。

| コマンド名 | 目的 | Backlog連携 |
| :--- | :--- | :--- |
| **`reviewer`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** |
| **`backlog-reviewer`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** |

### 引数一覧

| 引数 (ショートカット) | 必須 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- |
| `--git-clone-url` (`-u`) | **必須** | - | レビュー対象の **GitリポジトリURL**（SSH形式推奨）。 |
| `--base-branch` (`-b`) | 任意 | `main` | 差分比較の**基準となるブランチ**。 |
| `--feature-branch` (`-f`) | 任意 | `develop` | **レビュー対象**のフィーチャーブランチ。 |
| `--local-path` (`-p`) | 任意 | `./var/tmp` | リポジトリを一時的にクローンするローカルパス。 |
| `--ssh-key-path` (`-s`) | 任意 | `~/.ssh/id_rsa` | SSH認証用の秘密鍵パス（SSH URL接続時に必要）。 |
| `--gemini-model-name` (`-g`) | 任意 | `gemini-2.5-flash` | 使用する Gemini モデル名。 |
| `--issue-id` (`-i`) | ※ | - | Backlogの課題ID。`backlog-reviewer` で投稿時に必須。 |
| `--no-post` | 任意 | - | `backlog-reviewer` コマンドで、**レビュー結果のBacklogへのコメント投稿をスキップ**するフラグ。 |

-----

### 実行例

#### A. 汎用レビューモード (`reviewer`)

```bash
reviewer \
  -u "git@github.com:shouni/git-gemini-reviewer.git" \
  -b "main" \
  -f "feature/new-function" \
  -s "~/.ssh/id_rsa" 
```

#### B. Backlog 投稿モード (`backlog-reviewer`)

**GitリポジトリがSSH認証を必要とする場合、`-s`（`--ssh-key-path`）は必須です。**

```bash
backlog-reviewer \
  -u "git@github.com:shouni/git-gemini-reviewer.git" \
  -b "main" \
  -f "bugfix/issue-456" \
  -i "PROJECT-123" \
  -s "~/.ssh/id_rsa" 
```

-----

### 📜 ライセンス (License)

このプロジェクトは [MIT License](https://opensource.org/licenses/MIT) の下で公開されています。
