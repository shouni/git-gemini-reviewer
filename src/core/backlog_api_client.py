import requests
from typing import Dict, Any

class BacklogApiClient:
    """Backlog APIへのリクエストを管理するクライアントクラス。"""

    def __init__(self, api_key: str, backlog_domain: str):
        """
        クライアントを初期化します。

        Args:
            api_key (str): Backlog APIキー。
            backlog_domain (str): Backlogのドメイン (例: your-space.backlog.jp)。
        """
        if not all([api_key, backlog_domain]):
            raise ValueError("APIキーとドメインは必須です。")

        self.api_key = api_key
        self.backlog_domain = backlog_domain
        self.base_url = f"https://{self.backlog_domain}/api/v2"

        # requests.Sessionを使用し、APIキーを一度だけ設定する
        self.session = requests.Session()
        self.session.params = {'apiKey': self.api_key}
        self.session.headers.update({'Content-Type': 'application/json'})

    def _send_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Any:
        """汎用的なBacklog APIリクエストメソッド。"""
        url = f"{self.base_url}/{endpoint}"

        try:
            # セッションオブジェクトを使ってリクエストを送信
            response = self.session.request(
                method,
                url,
                params=params,
                json=data, # `data`の代わりに`json`を使用
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # カスタム例外の利用
            raise ConnectionError(f"APIリクエストに失敗しました: {e}") from e
        except requests.exceptions.JSONDecodeError:
            raise ValueError("APIレスポンスのJSON解析に失敗しました。")

    def get_repository(self, project_id: str, repo_id_or_name: str) -> dict:
        """
        プロジェクトの特定のリポジトリ情報を取得します。

        Args:
            project_id (str): プロジェクトIDまたはキー。
            repo_id_or_name (str): リポジトリIDまたはリポジトリ名。

        Returns:
            dict: リポジトリ情報。
        """
        endpoint = f"projects/{project_id}/git/repositories/{repo_id_or_name}"
        return self._send_request('GET', endpoint)

    def add_issue_comment(self, issue_key: str, content: str) -> dict:
        """
        課題にコメントを投稿します。

        Args:
            issue_key (str): 課題キー (例: PROJECT-123)。
            content (str): 投稿するコメント内容。

        Returns:
            dict: 投稿されたコメントの情報。
        """
        endpoint = f"issues/{issue_key}/comments"
        data = {'content': content}
        return self._send_request('POST', endpoint, data=data)