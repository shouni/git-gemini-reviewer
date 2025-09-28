import argparse
import sys
import os
from typing import Optional

# 2つのクラスをインポート
from .backlog_reviewer import BacklogCodeReviewer
from .generic_reviewer import GitCodeReviewer

# --- 定数定義 ---
DEFAULT_LOCAL_PATH = os.path.join(os.getcwd(), 'var', 'tmp')
DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash'

# --- 処理のコアロジック ---

def run_reviewer(args: argparse.Namespace, is_backlog_mode: bool):
    """レビュープロセス全体を管理・実行する。"""
    try:
        reviewer = _select_reviewer(args, is_backlog_mode)
        review_result = reviewer.execute_review()

        # GitCodeReviewer（標準出力担当）の場合のみ結果を表示
        if isinstance(reviewer, GitCodeReviewer):
            _print_review_result(review_result)

    except ValueError as ve:
        # 引数バリデーションなど、予測可能なエラー
        print(f"エラー: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # 予期せぬ致命的なエラー
        print(f"致命的なエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

def _select_reviewer(args: argparse.Namespace, is_backlog_mode: bool) -> (GitCodeReviewer | BacklogCodeReviewer):
    """引数に基づいて適切なレビュワークラスのインスタンスを返す。"""
    # Backlogモードで、かつ投稿スキップ(--no-post)が指定されていない場合
    if is_backlog_mode and not args.no_post:
        # Backlog投稿には issue-id が必須
        if not args.issue_id:
            raise ValueError("Backlogへコメント投稿するには `--issue-id` が必須です。\n投稿をスキップする場合は `--no-post` を指定してください。")
        print("Backlog連携モードで実行します。")
        return BacklogCodeReviewer(args)

    # それ以外の場合（汎用モード or Backlogモードで--no-post指定時）
    if is_backlog_mode:
        print("--- ⚠️ `--no-post`が指定されました。Backlogへの投稿をスキップします。 ---")
    else:
        print("汎用モードで実行します。")
    return GitCodeReviewer(args)

def _print_review_result(result: Optional[str]):
    """レビュー結果を標準出力にフォーマットして表示する。"""
    if result:
        print("\n--- 📝 Gemini Code Review Result ---")
        print(result)
        print("------------------------------------")
    else:
        print("レビュー対象の差分がなかったか、結果が空のため処理を終了します。")

# --- 引数パーサーの定義 ---

def _build_common_parser() -> argparse.ArgumentParser:
    """両方のエントリーポイントで共通の引数を定義するパーサーを構築する。"""
    parser = argparse.ArgumentParser()
    # 必須引数
    parser.add_argument('-u', '--git-clone-url', required=True, type=str,
                        help='レビュー対象のGitリポジトリURL')
    # 任意引数（デフォルト値あり）
    parser.add_argument('-b', '--base-branch', type=str, default='main',
                        help='差分比較の基準ブランチ (デフォルト: main)')
    parser.add_argument('-f', '--feature-branch', type=str, default='develop',
                        help='レビュー対象のフィーチャーブランチ (デフォルト: develop)')
    parser.add_argument('-p', '--local-path', type=str, default=DEFAULT_LOCAL_PATH,
                        help=f'リポジトリを格納するローカルパス (デフォルト: {DEFAULT_LOCAL_PATH})')
    parser.add_argument('-i', '--issue-id', type=str, default=None,
                        help='関連課題ID (レビュープロンプトやBacklog投稿に使用)')
    parser.add_argument('-g', '--gemini-model-name', type=str, default=DEFAULT_GEMINI_MODEL,
                        help=f'使用するGeminiモデル名 (デフォルト: {DEFAULT_GEMINI_MODEL})')
    return parser

# --- エントリーポイント ---

def main():
    """コマンド: `backlog-reviewer` のエントリーポイント (Backlog連携)"""
    parser = _build_common_parser()
    parser.description = "Gitリポジトリの差分をGeminiでコードレビューし、Backlogにコメントします。"
    # Backlogモード専用の引数を追加
    parser.add_argument('--no-post', action='store_true',
                        help='レビュー結果をBacklogにコメント投稿せず、標準出力します。')

    args = parser.parse_args()
    run_reviewer(args, is_backlog_mode=True)

def main_generic():
    """コマンド: `reviewer` のエントリーポイント (汎用)"""
    parser = _build_common_parser()
    parser.description = "Gitリポジトリの差分をGeminiでコードレビューし、結果を標準出力します。"

    args = parser.parse_args()
    run_reviewer(args, is_backlog_mode=False)