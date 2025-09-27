import sys
import subprocess
import os
from pathlib import Path
from typing import Optional, Any

# 依存関係（これらのファイルがプロジェクト内に存在することを前提とします）
from core.git_client import GitClient
from core.gemini_reviewer import GeminiReviewer
from core.settings import Settings

# --- Custom Exceptions for GitCodeReviewer ---
# Note: これらはcore.exceptionsファイルに移動することが望ましい
class GitReviewerError(Exception):
    """GitCodeReviewer関連のエラー基底クラス。"""
    pass

class ConfigurationError(GitReviewerError):
    """必須の設定が見つからない、または無効な場合に発生。"""
    pass
# ---------------------------------------------

class GitCodeReviewer:
    """
    Gitリポジトリの差分を取得し、Geminiにコードレビューを実行させる汎用的なクラス。
    Backlogへの依存性はありません。
    """
    def __init__(self, args: Any):
        """
        初期化を行い、引数を保持し、必要なクライアントをセットアップします。
        """
        self.args = args
        # ★ local-path は CLI 側でデフォルト値が設定されていることを前提とし、Path オブジェクトに変換
        self.local_path_obj = Path(args.local_path)
        self.gemini_reviewer: Optional[GeminiReviewer] = None
        self.git_client: Optional[GitClient] = None

        # issue_id はオプションとして getattr で取得し、Noneを許容
        self.issue_id: Optional[str] = getattr(args, 'issue_id', None)

        # 初期化フェーズで依存関係をセットアップ
        try:
            self._setup_gemini_reviewer()
            self._setup_git_client()
        except (ConfigurationError, GitReviewerError) as e:
            # __init__ 内で発生したエラーは、呼び出し元（cli.py）に伝播させる
            print(f"初期化中にエラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)


    def _setup_gemini_reviewer(self):
        """GeminiReviewerを環境変数から初期化します。"""
        api_key = Settings.get('GEMINI_API_KEY')
        if not api_key or "YOUR_GEMINI_API_KEY" in api_key:
            raise ConfigurationError("Gemini APIキーが設定されていません。環境変数またはconfig.pyを確認してください。")

        self.gemini_reviewer = GeminiReviewer(
            api_key=api_key,
            model_name=self.args.gemini_model_name
        )

    def _prepare_local_repository(self) -> Path:
        """
        指定されたGitリポジトリURLからローカルにクローンまたは更新します。（汎用フロー）
        """
        git_clone_url = self.args.git_clone_url

        # URLからリポジトリ名（ディレクトリ名）を抽出
        repo_name = Path(git_clone_url).stem

        # 1. ローカルパス（親ディレクトリ）が存在しない場合は作成
        if not self.local_path_obj.exists():
            try:
                # 存在しない場合は作成 (mkdir -p 相当)
                self.local_path_obj.mkdir(parents=True, exist_ok=True)
                print(f"✅ ローカルパスを作成しました: {self.local_path_obj}")
            except OSError as e:
                # パス作成エラーをカスタム例外でラップ
                raise GitReviewerError(f"ローカルパスの作成に失敗しました ({self.local_path_obj}): {e}") from e

        local_repo_path = self.local_path_obj / repo_name

        print(f"ターゲットリポジトリ: '{git_clone_url}'")

        try:
            if not local_repo_path.exists():
                print(f"リポジトリをクローン中: {git_clone_url} -> {local_repo_path}")
                command = ['git', 'clone', git_clone_url, str(local_repo_path)]
                subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
                print("✅ クローンが完了しました。")
            else:
                print(f"ローカルリポジトリが既に存在します: {local_repo_path}")
                print("リモートの最新情報を取得します (git fetch)...")
                command = ['git', '-C', str(local_repo_path), 'fetch', '--all']
                subprocess.run(command, check=True, stdout=sys.stdout, stderr=sys.stderr)
                print("✅ リモート情報の取得が完了しました。")

            return local_repo_path # <--- インデントが修正されたことを確認

        except subprocess.CalledProcessError as e:
            raise GitReviewerError(f"Gitコマンドの実行に失敗しました。詳細: {e}") from e
        except Exception as e:
            raise GitReviewerError(f"予期せぬエラーが発生しました: {e}") from e

    def _setup_git_client(self):
        """リポジトリの準備とGitClientの初期化を結合します。"""
        local_repo_path = self._prepare_local_repository()
        self.git_client = GitClient(repo_path=str(local_repo_path))


    def _process_diff_and_review(self) -> Optional[str]:
        """Gitの差分を取得し、Geminiにレビューさせます。（引数を内部属性に依存）"""
        if not self.git_client or not self.gemini_reviewer:
            raise RuntimeError("GitClientまたはGeminiReviewerが初期化されていません。")

        base_branch = self.args.base_branch
        feature_branch = self.args.feature_branch

        diff = self.git_client.get_diff(base_branch=base_branch, feature_branch=feature_branch)

        if diff is None or not diff.strip():
            print("差分がありませんでした。レビューをスキップします。")
            return None

        print("Geminiによるコードレビューを実行中...")

        # issue_id は None の場合もそのまま渡す（GeminiReviewer側で対応済み）
        result = self.gemini_reviewer.review_code(
            code_diff=diff,
            issue_key=self.issue_id
        )
        print("✅ コードレビューが完了しました。")
        return result

    def execute_review(self) -> Optional[str]:
        """
        コードレビューのメイン処理を実行し、結果の文字列を返します。
        """
        try:
            # すべてのクライアントは __init__ でセットアップ済み
            review_result = self._process_diff_and_review()
            return review_result

        except (GitReviewerError, ConfigurationError):
            # 認証やGit操作エラーはそのまま上位に伝播
            raise
        except Exception as e:
            # 予期せぬエラーを捕捉し、カスタム例外でラップして上位に伝播
            raise GitReviewerError(f"GitCodeReviewer実行中に予期せぬエラーが発生しました: {e}") from e