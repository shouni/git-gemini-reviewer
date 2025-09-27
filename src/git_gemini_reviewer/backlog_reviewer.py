# backlog_reviewer/backlog_reviewer.py

import sys
from typing import Any, Optional

from .generic_reviewer import GitCodeReviewer
from core.backlog_api_client import BacklogApiClient
from core.settings import Settings
from core.string_utils import sanitize_string

class BacklogCodeReviewer(GitCodeReviewer):
    """
    GitCodeReviewerの機能に加え、Backlogへのコメント投稿を行うクラス。
    """
    def __init__(self, args: Any):
        super().__init__(args)
        self.project_id = Settings.get('PROJECT_ID')
        self.backlog_client: Optional[BacklogApiClient] = None

    def _setup_backlog_client(self) -> BacklogApiClient:
        """Backlog APIクライアントを初期化します。（Backlog固有）"""
        api_key = Settings.get('BACKLOG_API_KEY')
        domain = Settings.get('BACKLOG_DOMAIN')

        if not api_key or not domain or "YOUR_API_KEY" in api_key or "your-space.backlog.jp" in domain:
            print("エラー: Backlogの認証情報が設定されていません。環境変数またはconfig.pyを確認してください。", file=sys.stderr)
            sys.exit(1)

        return BacklogApiClient(api_key=api_key, backlog_domain=domain)

    def execute_review(self):
        """
        GitCodeReviewerのレビューを実行し、結果をBacklogに投稿します。
        """
        issue_id = self.args.issue_id
        if not issue_id:
            print("エラー: Backlog連携には --issue-id が必須です。", file=sys.stderr)
            sys.exit(1)

        print(f"--- Backlog連携レビューを開始します (プロジェクトID: {self.project_id}, 課題ID: {issue_id}) ---")

        try:
            # 1. Backlogクライアントの初期化
            self.backlog_client = self._setup_backlog_client()

            # 2. 汎用レビューの実行
            # 親クラスの execute_review を呼び出し、Git操作とGeminiレビューを実行
            review_result = super().execute_review()

            # 3. 結果のBacklogへの投稿 (Backlog固有)
            if review_result:
                print("Backlogにレビュー結果をコメント投稿中...")
                sanitized_result = sanitize_string(review_result)
                self.backlog_client.add_issue_comment(issue_id, sanitized_result)
                print("--- ✅ Backlogにコメントを投稿しました ---")
            else:
                print("--- 処理を終了します（コメント投稿なし） ---")

        except Exception as e:
            print(f"エラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)