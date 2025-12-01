import re


def extract_python_code(text: str) -> str:
    """
    从LLM响应中提取Python代码块

    Args:
        text: LLM的原始响应

    Returns:
        提取的Python代码，如果没有代码块则返回空字符串
    """
    # 匹配 ```python ... ``` 或 ``` ... ```
    pattern = r"```python\s*\n(.*?)```|```\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # 返回第一个匹配的代码块（可能在group(1)或group(2)）
        code = matches[0][0] if matches[0][0] else matches[0][1]
        return code.strip()

    return ""
