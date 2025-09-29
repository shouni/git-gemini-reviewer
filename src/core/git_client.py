import subprocess
import os
import shutil
from pathlib import Path
from typing import List, Optional
import logging

# ロギング設定 (Go版のログ出力に近づける)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
    Go版と同様に、リポジトリの存在チェック、URL不一致時の自動再クローン機能を提供します。
    """

    def __init__(self, repo_url: str, repo_path: str, ssh_key_path: Optional[str] = None):
        """
        GitClientを初期化し、リポジトリをクローンまたは開きます。
        このコンストラクタ内で clone_or_open の処理を実行します。

        Args:
            repo_url (str): クローンするGitリポジトリのURL。
            local_path (str): ローカルリポジトリへのパス。
            ssh_key_path (Optional[str]): SSH秘密鍵へのパス。
        """
        self.repo_url = repo_url
        self.repo_path = Path(repo_path).resolve()
        self.ssh_key_path = ssh_key_path

        # SSHキーパスを環境変数 GIT_SSH_COMMAND に設定
        if self.ssh_key_path:
            # "~"を展開
            expanded_key_path = os.path.expanduser(self.ssh_key_path)
            # sshコマンドのラッパーを設定 (Go版の認証ロジックをエミュレート)
            ssh_cmd = f'ssh -i {expanded_key_path}'
            os.environ['GIT_SSH_COMMAND'] = ssh_cmd
            logging.info(f"Setting GIT_SSH_COMMAND for SSH authentication.")

        # 既存の __init__ のチェックロジックを置き換え、URLチェックと再クローンを実行
        self.clone_or_open()


    def _run_git_command(self, command: List[str], check: bool = True, cwd: Path = None) -> subprocess.CompletedProcess:
        """
        指定されたGitコマンドを実行する内部ヘルパーメソッド。

        Args:
            command (List[str]): 実行するコマンドのリスト。
            check (bool): Trueの場合、コマンドが失敗したらCalledProcessErrorを送出する。
            cwd (Path): コマンドを実行するディレクトリ。指定がなければ self.repo_path。

        Returns:
            subprocess.CompletedProcess: 実行結果。

        Raises:
            GitCommandError: 'git'コマンドが見つからない、またはコマンド実行に失敗した場合。
        """
        if cwd is None:
            cwd = self.repo_path

        try:
            return subprocess.run(
                ['git'] + command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8'
            )
        except FileNotFoundError:
            raise GitCommandError("'git' コマンドが見つかりません。Gitがインストールされ、PATHが通っているか確認してください。")
        except subprocess.CalledProcessError as e:
            raise GitCommandError(f"Gitコマンド '{' '.join(e.cmd)}' の実行に失敗しました。", stderr=e.stderr) from e


    def _get_remote_url(self, remote: str = "origin") -> Optional[str]:
        """既存リポジトリの 'origin' リモートのURLを取得します。"""
        try:
            # git config --get remote.origin.url を実行
            result = self._run_git_command(['config', '--get', f'remote.{remote}.url'])
            return result.stdout.strip()
        except GitCommandError as e:
            # リモートが存在しない、または config が見つからない場合
            if "not found" in e.stderr:
                return None
            # その他のエラーは再送出
            raise


    def _remove_and_clone(self, url: str):
        """既存のディレクトリを削除し、指定されたURLで新しくクローンします。"""
        if self.repo_path.exists():
            logging.info(f"Removing old repository directory {self.repo_path}...")
            try:
                shutil.rmtree(self.repo_path)
            except Exception as e:
                raise GitClientError(f"Failed to remove old repository directory: {e}")

        logging.info(f"Cloning {url} into {self.repo_path}...")

        # クローン先ディレクトリの親ディレクトリが存在しない場合は作成
        self.repo_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # git clone コマンドを self.repo_path の親ディレクトリで実行
            self._run_git_command(['clone', url, self.repo_path.name], cwd=self.repo_path.parent)
        except GitCommandError as e:
            raise GitClientError(f"Failed to clone repository {url}: {e.stderr}")


    def clone_or_open(self):
        """
        リポジトリをクローンするか、既存のものを開きます。
        URLが不一致の場合は自動的に再クローンします。
        """
        is_git_repo = self.repo_path.is_dir() and (self.repo_path / '.git').is_dir()

        if not is_git_repo:
            # 1. リポジトリが存在しない場合は単純にクローン
            self._remove_and_clone(self.repo_url)
            print(f"--- ✅ リポジトリをクローンしました: {self.repo_path} ---")
            return

        # 2. 既存リポジトリを開く
        logging.info(f"Opening repository at {self.repo_path}...")
        existing_url = self._get_remote_url()

        if existing_url is None:
            # リモート'origin'がない、または config が壊れている場合
            logging.warning("Warning: Remote 'origin' not found or failed to read. Re-cloning...")
            self._remove_and_clone(self.repo_url)
            print(f"--- ✅ リモート設定不一致のため再クローンしました: {self.repo_path} ---")
            return

        # 3. URLチェック
        # Go版と同様に、末尾のスラッシュや大文字小文字の違いを許容するため、比較前に正規化
        normalized_existing_url = existing_url.strip().rstrip('/')
        normalized_target_url = self.repo_url.strip().rstrip('/')

        if normalized_existing_url != normalized_target_url:
            # URLが一致しない場合、削除して再クローン
            logging.warning(
                f"Warning: Existing repository remote URL ({existing_url}) does not match the requested URL ({self.repo_url}). Re-cloning..."
            )
            self._remove_and_clone(self.repo_url)
            print(f"--- ✅ URL不一致のため再クローンしました: {self.repo_path} ---")
        else:
            # URLが一致する場合は、そのまま利用
            logging.info("Repository URL matches. Using existing local repository.")
            print(f"--- ✅ 既存リポジトリを利用します: {self.repo_path} ---")

    def fetch_updates(self, remote: str = "origin") -> None:
        """リモートリポジトリの最新情報を取得します。"""
        print(f"'{self.repo_path.name}' のリモート情報を更新中 (git fetch)...")
        # 既に repo_path が設定されているので self.repo_path を cwd に使う
        self._run_git_command(['fetch', remote, '--prune'])


    def _remote_branch_exists(self, branch_name: str, remote: str = "origin") -> bool:
        """指定されたリモートブランチが存在するかどうかをチェックします。"""
        # Note: self.repo_path は __init__ で既にクローン済み/開かれていることが保証されている
        result = self._run_git_command(
            ['show-ref', '--verify', f'refs/remotes/{remote}/{branch_name}'],
            check=False
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