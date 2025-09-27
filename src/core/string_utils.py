import re
from typing import Optional

# Backlog APIが受け付けない可能性のある制御文字を定義します。
# 改行(\n)、タブ(\t)、復帰(\r)は保持します。
_CONTROL_CHAR_REGEX = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')

def _is_valid_text(text: Optional[str]) -> bool:
    """
    入力が有効な文字列であるかを検証します。

    Args:
        text (Optional[str]): 検証する入力。

    Returns:
        bool: 有効な文字列の場合はTrue、それ以外はFalse。
    """
    return isinstance(text, str) and text is not None

def sanitize_string(text: Optional[str]) -> str:
    """
    文字列からBacklog APIが受け付けない可能性のある制御文字を削除します。

    Args:
        text (Optional[str]): サニタイズ対象の文字列。Noneや非文字列も受け付けます。

    Returns:
        str: 制御文字が削除された文字列。入力が無効な場合は空文字を返します。
    """
    if not _is_valid_text(text):
        return ""

    return _CONTROL_CHAR_REGEX.sub('', text)