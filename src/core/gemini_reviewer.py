import textwrap
import google.generativeai as genai
from pathlib import Path
from typing import Optional, List

# --- Custom Exceptions for clear error signaling ---
class GeminiReviewerError(Exception):
    """GeminiReviewer related errors base class."""
    pass

class APIKeyNotFoundError(GeminiReviewerError):
    """Raised when the Gemini API key is not configured."""
    pass

class GeminiReviewer:

    def __init__(self, api_key: str, model_name: str,
                 prompt_generic_path: Path, prompt_backlog_path: Path,
                 allowed_extensions: Optional[List[str]] = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions] if allowed_extensions else None
        try:
            self.prompt_generic_template = prompt_generic_path.read_text(encoding="utf-8")
            self.prompt_backlog_template = prompt_backlog_path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise GeminiReviewerError(f"プロンプトファイルが見つかりません: {e.filename}") from e

    def _filter_diff_by_extensions(self, code_diff: str) -> str:
        # 以前のリファクタリングで定義されたフィルタリングロジック
        if not self.allowed_extensions:
            return code_diff

        filtered_diff = []
        is_relevant_file = False

        for line in code_diff.splitlines():
            if line.startswith('+++ '):
                file_path = line[4:].strip()
                _, _, extension = file_path.rpartition('.')
                is_relevant_file = f".{extension.lower()}" in self.allowed_extensions

            if line.startswith('diff --git'):
                is_relevant_file = False
                filtered_diff.append(line)
            elif is_relevant_file or line.startswith('--- ') or line.startswith('+++ ') or line.startswith('@@ '):
                filtered_diff.append(line)

        return "\n".join(filtered_diff)

    def _build_review_prompt(self, code_diff: str, issue_key: Optional[str]) -> str:
        """
        issue_keyの有無に応じて適切なプロンプトテンプレートを選択し、変数を埋め込む。
        """
        if issue_key:
            # Backlog用テンプレートに変数を埋め込んで返す
            return self.prompt_backlog_template.format(
                issue_key=issue_key,
                code_diff=code_diff
            )
        else:
            # 汎用テンプレートに変数を埋め込んで返す
            return self.prompt_generic_template.format(code_diff=code_diff)

    def review_code(self, code_diff: str, issue_key: Optional[str] = None) -> str:
        """
        Gemini APIを使用してコード差分をレビューします。

        Args:
            code_diff (str): レビュー対象のコード差分。
            issue_key (Optional[str]): 関連する課題キー。Noneの場合はプロンプトに含めません。

        Returns:
            str: レビュー結果のテキスト。

        Raises:
            GeminiReviewerError: API呼び出しや結果の取得に失敗した場合。
        """
        # 1. フィルタリング処理を実行
        filtered_diff = self._filter_diff_by_extensions(code_diff)

        if not filtered_diff.strip():
            if code_diff.strip():
                print(f"--- ⚠️ 注意: フィルタリングによりレビュー対象の差分がなくなりました。許可された拡張子: {self.allowed_extensions} ---")
            return ""

            # 2. プロンプト生成ロジックを利用してプロンプトを組み立てる
        prompt = self._build_review_prompt(code_diff=filtered_diff, issue_key=issue_key)

        try:
            response = self.model.generate_content(prompt)

            if not response.text:
                if response.prompt_feedback.block_reason:
                    reason = response.prompt_feedback.block_reason.name
                    raise GeminiReviewerError(f"AIによるレビューがブロックされました。理由: {reason}")
                raise GeminiReviewerError("AIからのレビュー結果が空でした。")

            review_text = response.text.strip()
            print("--- ✅ レビューコメントの生成が完了しました ---")

            return review_text

        except Exception as e:
            raise GeminiReviewerError(f"Gemini APIの処理中に予期せぬエラーが発生しました: {e}") from e