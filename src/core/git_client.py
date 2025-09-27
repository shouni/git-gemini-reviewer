import subprocess
from pathlib import Path
from typing import List


# --- Custom Exceptions for better error handling ---
class GitClientError(Exception):
    """GitClient related errors base class."""
    pass

class GitCommandError(GitClientError):
    """Raised when a git command fails."""
    def __init__(self, message: str, stderr: str = ""):
        super().__init__(message)
        self.stderr = stderr

class BranchNotFoundError(GitClientError):
    """Raised when a branch is not found in the remote repository."""
    pass

class GitClient:
    """
    Gitリポジトリを操作するためのクライアントクラス。
    差分取得やブランチの存在確認などの機能を提供します。
    """

    def __init__(self, repo_path: str):
        """
        GitClientを初期化します。

        Args:
            repo_path (str): ローカルリポジトリへのパス。

        Raises:
            FileNotFoundError: 指定されたリポジトリパスが存在しない場合。
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.is_dir():
            raise FileNotFoundError(f"リポジトリパスが見つかりません: {self.repo_path}")

    def _run_git_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        指定されたGitコマンドをリポジトリ内で実行する内部ヘルパーメソッド。

        Args:
            command (List[str]): 実行するコマンドのリスト（例: ['fetch', '--all']）。
            check (bool): Trueの場合、コマンドが失敗したらCalledProcessErrorを送出する。

        Returns:
            subprocess.CompletedProcess: 実行結果。

        Raises:
            GitCommandError: 'git'コマンドが見つからない、またはコマンド実行に失敗した場合。
        """
        try:
            return subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8'
            )
        except FileNotFoundError:
            raise GitCommandError("'git' コマンドが見つかりません。Gitがインストールされ、PATHが通っているか確認してください。")
        except subprocess.CalledProcessError as e:
            # 失敗したコマンドの情報を付加して再送出
            raise GitCommandError(f"Gitコマンド '{' '.join(e.cmd)}' の実行に失敗しました。", stderr=e.stderr) from e

    def fetch_updates(self, remote: str = "origin") -> None:
        """リモートリポジトリの最新情報を取得します。"""
        print(f"'{self.repo_path.name}' のリモート情報を更新中 (git fetch)...")
        self._run_git_command(['fetch', remote, '--prune'])

    def _remote_branch_exists(self, branch_name: str, remote: str = "origin") -> bool:
        """指定されたリモートブランチが存在するかどうかをチェックします。"""
        result = self._run_git_command(
            ['show-ref', '--verify', f'refs/remotes/{remote}/{branch_name}'],
            check=False  # 失敗しても例外を送出しない
        )
        return result.returncode == 0

    def get_diff(self, base_branch: str, feature_branch: str, remote: str = "origin") -> str:
        """
        指定された2つのブランチ間の差分を取得します。

        Args:
            base_branch (str): 比較の基準となるブランチ名（例: 'main'）。
            feature_branch (str): 比較対象のブランチ名（例: 'develop'）。
            remote (str): リモート名（デフォルトは 'origin'）。

        Returns:
            str: git diffの出力結果。

        Raises:
            BranchNotFoundError: 指定されたブランチがリモートに存在しない場合。
            GitCommandError: git diffコマンドの実行に失敗した場合。
        """
        # 1. リモートの最新情報を取得（最初に一度だけ実行）
        self.fetch_updates(remote)

        # 2. 両方のブランチの存在をまとめてチェック
        missing_branches = []
        if not self._remote_branch_exists(base_branch, remote):
            missing_branches.append(f"{remote}/{base_branch}")
        if not self._remote_branch_exists(feature_branch, remote):
            missing_branches.append(f"{remote}/{feature_branch}")

        if missing_branches:
            raise BranchNotFoundError(f"ブランチが存在しません: {', '.join(missing_branches)}")

        # 3. diff を実行
        print(f"差分を取得中: {remote}/{base_branch}...{remote}/{feature_branch}")
        diff_command = [
            'diff',
            f'{remote}/{base_branch}...{remote}/{feature_branch}',
            '--unified=10'
        ]
        result = self._run_git_command(diff_command)
        # 差分取得が完了したことを示すメッセージを追加
        print(f"--- ✅ 差分の取得が完了しました ---")

        return result.stdout