# 🤖 Git Gemini Reviewer

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

## 🛠️ 開発環境のセットアップ

### **1. Pythonのインストール (Windows / macOS)**

本ツールはPython 3.9以上が必要です。以下の手順でインストールしてください。

#### **Windows**

1.  **公式サイトからインストーラーをダウンロード**: [Python公式サイト](https://www.python.org/downloads/windows/)にアクセスし、「Python 3.x.x」のインストーラーをダウンロードします。
2.  **インストーラーを実行**: ダウンロードした`.exe`ファイルを実行します。
3.  **注意点**: **「Add python.exe to PATH」のチェックボックスを必ずオンにしてから**、インストールを続行してください。これにより、コマンドプロンプトやPowerShellから`python`コマンドが使えるようになります。

#### **macOS**

macOSにはPythonがプリインストールされていますが、バージョンが古い場合があります。

1.  **公式サイトからインストーラーをダウンロード**: [Python公式サイト](https://www.python.org/downloads/macos/)にアクセスし、最新版をダウンロードします。
2.  **インストーラーを実行**: ダウンロードした`.pkg`ファイルを実行し、指示に従ってインストールします。

### **2. 仮想環境の作成とアクティベート**

Pythonのインストール後、プロジェクトの作業ディレクトリで以下のコマンドを実行します。
これにより、プロジェクト固有の独立した環境が構築されます。

| OS     | コマンド                               |
| :---   | :---                                   |
| **Windows**| `python -m venv .venv`<br>`.\.venv\Scripts\activate`|
| **macOS** | `python3 -m venv .venv`<br>`source .venv/bin/activate`|

### **3. リポジトリのクローン**

仮想環境をアクティベートした後、本プロジェクトをローカルにクローンします。

```bash
git clone https://github.com/shouni/git-gemini-reviewer.git
cd git-gemini-reviewer
```

### **4. pip の更新 (推奨)**

```bash
pip install --upgrade pip
```

### **5. 編集可能モードでのインストール**

```bash
pip install --upgrade --force-reinstall -e .
```

このコマンドは、あなたがプロジェクトのソースコードを編集するたびに、変更がすぐに反映されるようにします。

-----

## 🔑 環境変数の設定

本ツールは、APIキーなどの機密情報を環境変数または `config.py` ファイルから読み込みます。**推奨される設定方法**は、プロジェクトのルートディレクトリに **`config.py`** を作成することです。

### 📄 `config.py` ファイルの例

プロジェクトのルートディレクトリに以下の内容で `config.py` を作成してください。

```python
# Gemini API キー
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# --- Backlog 連携に必要な設定 (backlog-reviewer コマンド利用時のみ必須) ---
# Backlogのドメイン (例: 会社のアカウントが "example" なら "example.backlog.jp")
BACKLOG_DOMAIN = "YOUR_BACKLOG_DOMAIN"

# BacklogのAPIキー (個人設定から発行したもの)
BACKLOG_API_KEY = "YOUR_BACKLOG_API_KEY"

# BacklogのプロジェクトID (例: プロジェクトキーが "PROJECT" なら "PROJECT")
PROJECT_ID = "YOUR_PROJECT_ID"
```

**注意**: `config.py` には機密情報が含まれるため、Git管理から除外するために `.gitignore` ファイルに追記することを強く推奨します。

```
# .gitignore
config.py
```

-----

## 💻 使い方 (Usage)

### コマンド一覧

本ツールは、Backlog連携の有無に応じて**2つのコマンド**を提供します。

| コマンド名 | 目的 | Backlog連携 |
| :--- | :--- | :--- |
| **`reviewer`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** |
| **`backlog-reviewer`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** |

### 引数一覧

| 引数 (ショートカット) | 必須 | デフォルト値             | 説明 |
| :--- | :--- |:-------------------| :--- |
| `--git-clone-url` (`-u`) | **必須** | -                  | レビュー対象の **GitリポジトリURL**。 |
| `--base-branch` (`-b`) | 任意 | `main`             | 差分比較の**基準となるブランチ**。 |
| `--feature-branch` (`-f`) | 任意 | `develop`          | **レビュー対象**のフィーチャーブランチ。 |
| `--local-path` (`-p`) | 任意 | `./var/tmp`        | リポジトリを一時的にクローンするローカルパス。 |
| `--gemini-model-name` (`-g`) | 任意 | `gemini-2.0-flash` | 使用する Gemini モデル名。 |
| `--issue-id` (`-i`) | ※ | -                  | Backlogの課題ID。`backlog-reviewer` で投稿時に必須。 |
| `--no-post` | 任意 | -                  | `backlog-reviewer` でコメント投稿をスキップするフラグ。 |

-----

### 実行例

#### A. Backlog連携なし (標準出力)

```bash
reviewer \
  -u "git@github.com:shouni/git-gemini-reviewer.git"

# ブランチを明示的に指定する例
reviewer \
  -u "git@github.com:shouni/git-gemini-reviewer.git" \
  -b "main" \
  -f "feature/new-function"
```

#### B. Backlog連携あり (課題にコメント投稿)

```bash
# コマンド名: backlog-reviewer
backlog-reviewer \
  -u "git@github.com:shouni/git-gemini-reviewer.git" \
  -b "main" \
  -f "develop" \
  -i "BLG-123"
```

---

### 📜 ライセンス (License)

このプロジェクトは [MIT License](https://opensource.org/licenses/MIT) の下で公開されています。
