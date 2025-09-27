import argparse
import sys
import os # local-pathのデフォルト値処理のために追加
# 2つのクラスをインポート
from .backlog_reviewer import BacklogCodeReviewer
from .generic_reviewer import GitCodeReviewer

# --- 共通の引数定義 ---

def _build_parser(description: str, is_backlog_reviewer_context: bool) -> argparse.ArgumentParser:
    """
    コマンドライン引数パーサーを構築し、必須・任意の順で引数を定義する。
    """
    parser = argparse.ArgumentParser(description=description)

    # 1. 必須の引数 (コアレビュー機能に必須)
    parser.add_argument('--git-clone-url', required=True, type=str,
                        help='レビュー対象のGitリポジトリURL')
    parser.add_argument('--base-branch', required=True, type=str,
                        help='差分比較の基準ブランチ')
    parser.add_argument('--feature-branch', required=True, type=str,
                        help='レビュー対象のフィーチャーブランチ')

    # ★ リファクタリング済み: local-path を任意にし、デフォルト値を設定 ★
    default_local_path = os.path.join(os.getcwd(), 'var', 'tmp')
    parser.add_argument('--local-path',
                        default=default_local_path,
                        type=str,
                        help=f'リポジトリを格納するローカルパス (デフォルト: {default_local_path})')

    # 2. 任意の引数 (オプション)
    issue_help = '関連する課題ID (レビュープロンプトのコンテキストに使用)'
    if is_backlog_reviewer_context:
        issue_help += ' (Backlog投稿時には必須)'

    parser.add_argument('--issue-id', type=str, default=None,
                        help=issue_help)

    parser.add_argument('--gemini-model-name', default='gemini-2.5-flash', type=str,
                        help='使用するGeminiモデル名 (デフォルト: gemini-2.5-flash)')

    # ★ リファクタリング済み: Backlog投稿スキップフラグ ★
    if is_backlog_reviewer_context:
        parser.add_argument('--no-post', action='store_true',
                            help='レビュー結果をBacklogにコメント投稿するのをスキップします。')

    return parser

# --- エントリーポイント ---

def main():
    """
    コマンド: backlog-reviewer のエントリーポイント。（Backlog連携ベース）
    """
    parser = _build_parser(
        description="Gitリポジトリの差分をGeminiでコードレビューし、Backlogにコメントします。",
        is_backlog_reviewer_context=True # 修正済み
    )
    args = parser.parse_args()

    # --- 投稿処理を行うかどうかのロジック ---

    # 1. --no-post フラグが指定されている場合 (任意引数モード)
    if args.no_post:
        print("--- ⚠️ `--no-post`が指定されました。Backlogへのコメント投稿はスキップし、結果は標準出力されます。 ---")
        reviewer = GitCodeReviewer(args)

    # 2. --no-post フラグがなく、Backlog投稿が必要な場合 (本来の必須モード)
    elif not args.issue_id:
        # issue-id が指定されていない場合、エラーとして処理を中断
        print("エラー: Backlogへコメント投稿するには `--issue-id` が必須です。投稿をスキップする場合は `--no-post` を指定してください。", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # 3. issue-id が指定されており、投稿が可能な場合
    else:
        # Backlog連携クラスを呼び出す
        reviewer = BacklogCodeReviewer(args)

    # レビュー実行
    try:
        review_result = reviewer.execute_review()
    except Exception as e:
        # BacklogCodeReviewer/GitCodeReviewerで処理しきれなかった致命的なエラー
        print(f"致命的なエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 投稿しない場合は結果を標準出力 (GitCodeReviewerの実行結果を流用)
    if args.no_post:
        if review_result:
            print("\n--- 📝 Gemini Code Review Result ---")
            print(review_result)
            print("------------------------------------")
        else:
            print("レビュー対象の差分がなかったため、処理を終了します。")

    sys.exit(0)


# --------------------------------------------------------------------------------

def main_generic():
    """
    コマンド: git-gemini-review のエントリーポイント。（Backlog連携なし）
    """
    parser = _build_parser(
        description="Gitリポジトリの差分をGeminiでコードレビューし、結果を標準出力します。",
        is_backlog_reviewer_context=False # 修正済み
    )
    args = parser.parse_args()

    try:
        # 汎用レビュークラスを呼び出す (issue-idは任意)
        reviewer = GitCodeReviewer(args)
        review_result = reviewer.execute_review()

        if review_result:
            print("\n--- 📝 Gemini Code Review Result ---")
            print(review_result)
            print("------------------------------------")
            sys.exit(0)
        else:
            print("レビュー対象の差分がなかったため、処理を終了します。")
            sys.exit(0)

    except Exception as e:
        print(f"致命的なエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)