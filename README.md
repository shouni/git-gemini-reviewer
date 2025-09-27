ご提供いただいた情報に基づき、`README.md` の**概要**、**セットアップ手順**、**使い方**を分かりやすくまとめて再出力します。

-----

# 🤖 git-gemini-reviewer

**`git-gemini-reviewer`** は、Gitリポジトリのブランチ間の差分を **Google Gemini API** を使用して自動でコードレビューするためのコマンドラインツールです。レビュー結果をターミナルに出力するだけでなく、**Backlog** などの課題管理システムへ自動でコメント投稿する機能も提供します。

-----

## 🛠️ 開発環境のセットアップ

本プロジェクトを開発・実行するには、以下の手順で仮想環境を構築し、編集可能モードでインストールしてください。

1.  **仮想環境の作成とアクティベート**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **pip の更新 (推奨)**
    環境作成後、念のため pip を最新版に更新します。

    ```bash
    pip install --upgrade pip
    ```

3.  **編集可能モードでのインストール**
    プロジェクトルートディレクトリにて、編集可能 (`-e`) モードでインストールします。これにより、コードを変更するたびに再インストールする必要がなくなります。

    ```bash
    pip install --upgrade --force-reinstall -e .
    ```

-----

## 🚀 使い方 (Usage)

本ツールは、Backlog連携の有無に応じて**2つのコマンド**を提供します。どちらのコマンドも、Gitリポジトリの差分を Gemini でレビューします。

| コマンド名 | 目的 | Backlog連携 | エントリーポイント |
| :--- | :--- | :--- | :--- |
| **`git-gemini-reviewer`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** | `main_generic` |
| **`git-gemini-reviewer-backlog`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** (`--issue-id` 必須) | `main` |

### 1\. 必須引数（共通）

以下の3つの引数は、どちらのコマンドを使用する場合でも**必ず必要**です。

| 引数名 | 必須 | 説明 |
| :--- | :--- | :--- |
| `--git-clone-url` | **必須** | レビュー対象の **GitリポジトリURL**。 (例: `git@github.com:...` または `https://...`) |
| `--base-branch` | **必須** | 差分比較の**基準となるブランチ**。通常は `main` や `develop`。 |
| `--feature-branch` | **必須** | **レビュー対象**のフィーチャーブランチ。 |

### 2\. オプション引数（共通）

| 引数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `--local-path` | `./var/tmp` | リポジトリを一時的にクローンするローカルパス。 |
| `--gemini-model-name` | `gemini-2.5-flash` | 使用する Gemini モデル名。 |

-----

## 💻 コマンド実行例

### A. Backlog連携なし (標準出力)

Backlogへ投稿せず、レビュー結果をターミナルで確認したい場合に利用します。

```bash
# コマンド名: git-gemini-reviewer
git-gemini-reviewer \
  --git-clone-url "git@github.com:shouni/git-gemini-reviewer.git" \
  --base-branch "main" \
  --feature-branch "develop"
```

-----

### B. Backlog連携あり (課題にコメント投稿)

レビュー結果を Backlog の課題にコメントとして投稿します。このモードでは `--issue-id` の指定が必須となります。

#### 🔹 基本投稿

```bash
# コマンド名: git-gemini-reviewer-backlog
git-gemini-reviewer-backlog \
  --git-clone-url "git@github.com:shouni/git-gemini-reviewer.git" \
  --base-branch "main" \
  --feature-branch "develop" \
  --issue-id "BLG-123"  # Backlog連携時には必須
```

#### 🔹 投稿をスキップして結果を確認

Backlog連携モードのロジックを使いつつ、一時的に投稿をスキップして結果を標準出力したい場合に利用します。

```bash
git-gemini-reviewer-backlog \
  --git-clone-url "..." \
  --base-branch "main" \
  --feature-branch "develop" \
  --issue-id "BLG-123" \
  --no-post  # コメント投稿をスキップし、結果をターミナルに出力
```