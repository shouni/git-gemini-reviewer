
### 🚀 開発環境のセットアップ

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

プロジェクトのコード（エントリーポイント部分）を拝見しました。

この情報を基に、プロジェクトの利用方法を明確にした `README.md` の「使用方法」セクションを更新します。ユーザーが**Backlog連携あり**と**連携なし**の2つのコマンドを理解し、必要な引数を迷わず入力できるように整理しました。

-----

## 🚀 使い方 (Usage)

本ツールは、Backlog連携の有無に応じて**2つのコマンド**を提供します。どちらのコマンドも、Gitリポジトリの差分を Gemini でレビューし、結果を出力します。

| コマンド名 | 目的 | Backlog連携 |
| :--- | :--- | :--- |
| **`git-gemini-reviewer`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** (`--issue-id` 必須) |
| **`git-gemini-reviewer-generic`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** |

### 1\. 必須引数（共通）

以下の3つの引数は、どちらのコマンドを使用する場合でも**必ず必要**です。

| 引数名 | 必須 | 説明 |
| :--- | :--- | :--- |
| `--git-clone-url` | **必須** | レビュー対象の **GitリポジトリURL**。 (例: `git@github.com:user/repo.git` または `https://...`) |
| `--base-branch` | **必須** | 差分比較の**基準となるブランチ**。通常は `main` や `develop`。 |
| `--feature-branch` | **必須** | **レビュー対象**のフィーチャーブランチ。 |

### 2\. オプション引数（共通）

| 引数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `--local-path` | `./var/tmp` | リポジトリを一時的にクローンするローカルパス。 |
| `--gemini-model-name` | `gemini-2.5-flash` | 使用する Gemini モデル名。 |

-----

了解しました！`pyproject.toml` の **`[project.scripts]`** を新しい設定に合わせて更新します。

新しい設定では、Backlog連携**なし**がメインのコマンドとなり、Backlog連携**あり**が別名に分離されました。これにより、ユーザーにとって利用目的がより明確になります。

-----

## 🚀 使い方 (Usage)

本ツールは、Geminiによるコードレビューを実行するための **2つのコマンド** を提供します。

| コマンド名 | 目的 | Backlog連携 | エントリーポイント |
| :--- | :--- | :--- | :--- |
| **`git-gemini-reviewer`** | レビュー結果を**標準出力**（ターミナル）に表示します。 | **なし** | `main_generic` |
| **`git-gemini-reviewer-backlog`** | レビュー結果を**Backlogの課題にコメントとして投稿**します。 | **あり** (`--issue-id` 必須) | `main` |

### 1\. 必須引数（共通）

以下の3つの引数は、どちらのコマンドを使用する場合でも**必ず必要**です。

| 引数名 | 必須 | 説明 |
| :--- | :--- | :--- |
| `--git-clone-url` | **必須** | レビュー対象の **GitリポジトリURL**。 |
| `--base-branch` | **必須** | 差分比較の**基準となるブランチ**。通常は `main` や `develop`。 |
| `--feature-branch` | **必須** | **レビュー対象**のフィーチャーブランチ。 |

### 2\. オプション引数（共通）

| 引数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `--local-path` | `./var/tmp` | リポジトリを一時的にクローンするローカルパス。 |
| `--gemini-model-name` | `gemini-2.5-flash` | 使用する Gemini モデル名。 |

-----

## 💻 コマンド実行例と詳細オプション

### A. Backlog連携なし (標準出力)

**コマンド名**: `git-gemini-reviewer`

レビュー結果をターミナルで確認する、基本的な実行方法です。

```bash
# --git-clone-url, --base-branch, --feature-branch は必須
git-gemini-reviewer \
  --git-clone-url "git@github.com:shouni/git-gemini-reviewer.git" \
  --base-branch "main" \
  --feature-branch "develop"
```

-----

### B. Backlog連携あり (課題にコメント投稿)

**コマンド名**: `git-gemini-reviewer-backlog`

レビュー結果を Backlog の課題にコメント投稿するには、**`--issue-id`** の指定が**必須**です。

#### 🔹 基本投稿 (必須引数)

```bash
# --issue-id が必須
git-gemini-reviewer-backlog \
  --git-clone-url "..." \
  --base-branch "main" \
  --feature-branch "develop" \
  --issue-id "BLG-123" 
```

#### 🔹 投稿をスキップして標準出力する

Backlog連携モードで起動しつつ、投稿だけをスキップして結果をターミナルで確認したい場合は `--no-post` フラグを使用します。

```bash
git-gemini-reviewer-backlog \
  --git-clone-url "..." \
  --base-branch "main" \
  --feature-branch "develop" \
  --issue-id "BLG-123" \
  --no-post
```
