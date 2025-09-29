import sys
import subprocess
from pathlib import Path
from typing import Optional, Any

from core.backlog_api_client import BacklogApiClient
from core.gemini_reviewer import GeminiReviewer
from core.git_client import GitClient
from core.settings import Settings
from core.string_utils import sanitize_string


class CodeReviewer:
    """
    Gitリポジトリの差分を取得し、Geminiにコードレビューを実行させ、
    その結果をBacklogの課題にコメントとして投稿する処理を管理するクラス。
    """
    def __init__(self, args: Any):
        """
        初期化を行い、設定値を取得します。

        Args:
            args (Any): コマンドライン引数を保持するオブジェクト。
        """
        self.args = args
        self.project_id = Settings.get('PROJECT_ID')
        # Backlogの認証情報は、BacklogApiClientの初期化時にチェックされる
        self.backlog_client: Optional[BacklogApiClient] = None
        self.gemini_reviewer: Optional[GeminiReviewer] = None
        self.git_client: Optional[GitClient] = None

    def _setup_backlog_client(self) -> BacklogApiClient:
        """
        Backlog APIクライアントを環境変数またはconfig.pyから初期化します。
        """
        api_key = Settings.get('BACKLOG_API_KEY')
        domain = Settings.get('BACKLOG_DOMAIN')

        if not api_key or not domain or "YOUR_API_KEY" in api_key or "your-space.backlog.jp" in domain:
            print("エラー: Backlogの認証情報が設定されていません。環境変数またはconfig.pyを確認してください。", file=sys.stderr)
            sys.exit(1)

        return BacklogApiClient(api_key=api_key, backlog_domain=domain)

    def _get_gemini_reviewer(self, model_name: str) -> GeminiReviewer:
        """
        GeminiReviewerを初期化します。
        """
        api_key = Settings.get('GEMINI_API_KEY')
        if not api_key or "YOUR_GEMINI_API_KEY" in api_key:
            print("エラー: Gemini APIキーが設定されていません。環境変数またはconfig.pyを確認してください。", file=sys.stderr)
            sys.exit(1)
        return GeminiReviewer(api_key=api_key, model_name=model_name)

    def _prepare_local_repository(self, git_clone_url: str, local_path_obj: Path) -> Path:
        """
        指定されたGitリポジトリURLからローカルにクローンまたは更新します。

        Args:
            git_clone_url (str): クローンするGitリポジトリのURL。
            local_path_obj (Path): ローカルパスのPathオブジェクト（親ディレクトリ）。

        Returns:
            Path: クローンまたは更新されたリポジトリのパス。
        """
        # リポジトリ名のサニタイズ（ディレクトリ名として安全に使うため）
        repo_name = Path(git_clone_url).stem
        local_repo_path = local_path_obj / repo_name

        print(f"ターゲットリポジトリ: '{git_clone_url}'")

        try:
            if not local_repo_path.exists():
                print(f"リポジトリをクローン中: {git_clone_url} -> {local_repo_path}")
                command = ['git', 'clone', git_clone_url, str(local_repo_path)]
                subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
                print("✅ リポジトリのクローンが完了しました。")
            else:
                print(f"ローカルリポジトリが既に存在します: {local_repo_path}")
                print("リモートの最新情報を取得します (git fetch)...")
                # git -C <path> fetch を実行
                command = ['git', '-C', str(local_repo_path), 'fetch']
                subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
                print("✅ リモートの最新情報の取得が完了しました。")

            return local_repo_path

        except subprocess.CalledProcessError as e:
            print(f"エラー: Gitコマンドの実行に失敗しました。詳細: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)

    def _process_diff_and_review(self, issue_id: str, base_branch: str, feature_branch: str) -> Optional[str]:
        """
        Gitの差分を取得し、Geminiにレビューさせます。
        """
        if not self.git_client or not self.gemini_reviewer:
            raise RuntimeError("GitClientまたはGeminiReviewerが初期化されていません。")

        # 差分を取得
        diff = self.git_client.get_diff(base_branch=base_branch, feature_branch=feature_branch)

        if diff is None or not diff.strip():
            print("差分がありませんでした。レビューをスキップします。")
            return None

        # レビューを実行
        print("Geminiによるコードレビューを実行中...")
        result = self.gemini_reviewer.review_code(diff, issue_key=issue_id)
        print("✅ コードレビューが完了しました。")
        return result

    def execute_review(self):
        """
        コードレビューのメイン処理を実行します。
        """
        print(f"--- レビューを開始します (プロジェクトID: {self.project_id}, 課題ID: {self.args.issue_id}) ---")

        try:
            # 1. クライアントの初期化
            self.backlog_client = self._setup_backlog_client()
            self.gemini_reviewer = self._get_gemini_reviewer(self.args.gemini_model_name)

            # 2. リポジトリのクローン/更新
            # argsには新しい引数 git_clone_url が含まれていることを想定
            local_repo_path = self._prepare_local_repository(
                self.args.git_clone_url,
                Path(self.args.local_path)
            )

            # 3. Gitクライアントの初期化
            git_clone_url = self.args.git_clone_url
            self.git_client = GitClient(
                repo_url=git_clone_url,
                repo_path=str(local_repo_path),
                ssh_key_path=getattr(self.args, 'ssh_key_path', None)
            )

            # 4. 差分の取得とレビューの実行
            review_result = self._process_diff_and_review(
                self.args.issue_id,
                self.args.base_branch,
                self.args.feature_branch
            )

            # 5. 結果のBacklogへの投稿
            if review_result:
                print("Backlogにレビュー結果をコメント投稿中...")
                sanitized_result = sanitize_string(review_result)
                self.backlog_client.add_issue_comment(self.args.issue_id, sanitized_result)
                print("--- ✅ Backlogにコメントを投稿しました ---")
            else:
                print("--- 処理を終了します（コメント投稿なし） ---")

        except RuntimeError as e:
            # 内部の初期化エラーなどをキャッチ
            print(f"重大なエラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            # その他の予期せぬエラー
            print(f"エラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)

# 元の review_pr 関数は、クラスの実行をトリガーするシンプルなラッパーとして残します。
def review_pr(args: Any):
    """
    指定されたブランチ間の差分を取得し、Geminiにレビューさせます。
    （CodeReviewerクラスのラッパー）

    Args:
        args (Any): コマンドライン引数を保持するオブジェクト。
        （git_clone_url、issue_id、base_branch、feature_branch、local_pathなどを含む想定）
    """
    reviewer = CodeReviewer(args)
    reviewer.execute_review()