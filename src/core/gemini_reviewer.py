import textwrap
import google.generativeai as genai
from typing import Optional, List

# --- Custom Exceptions for clear error signaling ---
class GeminiReviewerError(Exception):
    """GeminiReviewer related errors base class."""
    pass

class APIKeyNotFoundError(GeminiReviewerError):
    """Raised when the Gemini API key is not configured."""
    pass

class GeminiReviewer:
    """Gemini APIを使用してコードレビューを行うクラス。"""

    # 1. 共通のベースプロンプト
    _BASE_PROMPT = textwrap.dedent("""\
        あなたは経験豊富なシニアソフトウェアエンジニアです。
        これから、
        """)

    # 2. 課題IDがある場合にのみ挿入するプロンプトの追加部分
    _ISSUE_CONTEXT_PROMPT = "Backlogの課題 `{issue_key}` に関連する"

    # 3. 汎用/Backlog連携なし（指摘なしの記述に ✅ を使用）
    _GENERIC_REVIEW_STRUCTURE = textwrap.dedent("""
        ソースコードの差分（diff形式）をレビューしてもらいます。

        **出力は必ずMarkdown形式で、以下の構成に従ってください。**
        1.  **総評:** レビュー全体の簡単なまとめを記述します。
        2.  **ファイルごとの指摘事項:**
            - 差分に含まれるファイルごとに、`#### ファイル名: path/to/your/file.py` のように第四レベル見出しを作成します。
            - 各ファイルで見つかった指摘事項をリスト形式（`-`）で記述します。
            - 各指摘には、**行番号**、**問題点**、**修正案**を必ず含めてください。
            - 修正案では、具体的なコードを ` ```python ` のようなコードブロックで示してください。
            - 指摘事項がないファイルについては、「✅ 問題は見つかりませんでした。」と記述してください。 
            
        > **重要: 各指摘事項の行番号は、差分（diff）の `+` やコンテキスト行で示される「変更後のファイル」の行番号を基準にしてください。**

        **レビューの観点:**
        - 潜在的なバグやエッジケースの見落とし
        - パフォーマンスの問題（例: 無駄なループ、非効率な処理）
        - セキュリティ上の脆弱性
        - コーディング規約やスタイルガイドからの逸脱
        - 可読性やメンテナンス性の低い箇所
        - より良い実装方法やリファクタリングの提案
        
        指摘事項が全体を通してない場合は、「総評」部分にその旨を記述し、「ファイルごとの指摘事項」セクションは不要です。
        --- diff start ---
        {code_diff}
        --- diff end ---
        """)

    # 4. Backlog連携あり（指摘なしの記述に :ok_woman: を使用） ★★★ 修正済み ★★★
    _BACKLOG_REVIEW_STRUCTURE = textwrap.dedent("""
        ソースコードの差分（diff形式）をレビューしてもらいます。

        **出力は必ずMarkdown形式で、以下の構成に従ってください。**
        1.  **総評:** レビュー全体の簡単なまとめを記述します。
        2.  **ファイルごとの指摘事項:**
            - 差分に含まれるファイルごとに、`#### ファイル名: path/to/your/file.py` のように第四レベル見出しを作成します。
            - 各ファイルで見つかった指摘事項をリスト形式（`-`）で記述します。
            - 各指摘には、**行番号**、**問題点**、**修正案**を必ず含めてください。
            - 修正案では、具体的なコードを ` ```python ` のようなコードブロックで示してください。
            - 指摘事項がないファイルについては、「:ok_woman: 問題は見つかりませんでした。」と記述してください。

        > **重要: 各指摘事項の行番号は、差分（diff）の `+` やコンテキスト行で示される「変更後のファイル」の行番号を基準にしてください。**

        **レビューの観点:**
        - 潜在的なバグやエッジケースの見落とし
        - パフォーマンスの問題（例: 無駄なループ、非効率な処理）
        - セキュリティ上の脆弱性
        - コーディング規約やスタイルガイドからの逸脱
        - 可読性やメンテナンス性の低い箇所
        - より良い実装方法やリファクタリングの提案
        
        指摘事項が全体を通してない場合は、「総評」部分にその旨を記述し、「ファイルごとの指摘事項」セクションは不要です。
        --- diff start ---
        {code_diff}
        --- diff end ---
        """)

    def __init__(self, api_key: str, model_name: str,
                 allowed_extensions: Optional[List[str]] = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions] if allowed_extensions else None

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
        issue_keyの有無に応じて適切なレビュープロンプトを組み立てます。
        """
        # プロンプトの組み立て開始
        prompt_parts = [self._BASE_PROMPT.strip()]

        # 課題IDが提供されているかチェック
        issue_key_provided = bool(issue_key)

        if issue_key_provided:
            # Backlog連携時: 課題コンテキストを追加し、:ok_woman: を含むテンプレートを選択
            issue_context = self._ISSUE_CONTEXT_PROMPT.format(issue_key=issue_key)
            prompt_parts.append(issue_context)
            structure_template = self._BACKLOG_REVIEW_STRUCTURE
        else:
            # 汎用レビュー時: 課題コンテキストなしで、✅ を含むテンプレートを選択
            structure_template = self._GENERIC_REVIEW_STRUCTURE

        # レビュー構造の指示部分と差分を追加
        full_prompt = "".join(prompt_parts) + structure_template.format(code_diff=code_diff)

        # 連続した改行を整理して返す
        return full_prompt.replace('\n\n\n', '\n\n')

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