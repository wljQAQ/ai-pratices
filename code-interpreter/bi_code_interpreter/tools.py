"""
BI Code Interpreter - Core Tools

实现代码生成和结果分析的核心工具
"""

import re
import json
from typing import Optional, Dict, Any
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import CODE_GENERATOR_SYSTEM_PROMPT, RESULT_ANALYZER_SYSTEM_PROMPT


# ============================================================================
# 工具1: generate_python_code - 生成Python代码
# ============================================================================


@tool
def generate_python_code(
    task_description: str,
    data_context: str = None,
    previous_error: str = None,
) -> str:
    """
    生成Python数据分析代码。

    这个工具会调用LLM生成高质量的、可执行的Python代码。

    Args:
        task_description: 要完成的任务描述，例如："分析data.csv的销售趋势"
        data_context: 数据上下文信息（JSON字符串），包含文件路径、已知schema等。
                     例如：'{"file_path": "./data.csv", "schema": {"columns": ["date", "sales"]}}'
        previous_error: 可选，上一次代码执行的错误信息。如果提供，将生成修复后的代码。

    Returns:
        生成的Python代码字符串（不含markdown代码块标记）

    Examples:
        >>> # 首次生成代码
        >>> code = generate_python_code(
        ...     task_description="统计data.csv的基本信息",
        ...     data_context='{"file_path": "./data.csv"}'
        ... )

        >>> # 基于错误修复代码
        >>> code = generate_python_code(
        ...     task_description="统计data.csv的基本信息",
        ...     data_context='{"file_path": "./data.csv"}',
        ...     previous_error="FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'"
        ... )
    """
    # 初始化LLM（这里需要从环境变量或配置中获取）
    from dotenv import load_dotenv
    import os

    load_dotenv(override=True)

    llm = ChatOpenAI(
        base_url=os.getenv("BASE_URL"),
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("API_KEY"),
        temperature=0.1,  # 代码生成使用较低温度，保证稳定性
    )

    # 构建用户消息
    user_message_parts = []

    # 1. 任务描述
    user_message_parts.append(f"**任务描述:**\n{task_description}\n")

    # 2. 数据上下文
    if data_context:
        try:
            context_dict = (
                json.loads(data_context)
                if isinstance(data_context, str)
                else data_context
            )
            context_str = json.dumps(context_dict, ensure_ascii=False, indent=2)
            user_message_parts.append(f"**数据上下文:**\n```json\n{context_str}\n```\n")
        except:
            user_message_parts.append(f"**数据上下文:**\n{data_context}\n")

    # 3. 错误信息（如果有）
    if previous_error:
        user_message_parts.append(
            f"""
**⚠️ 之前的代码执行失败了！错误信息如下:**
```
{previous_error}
```

**请仔细分析错误原因，生成修复后的代码。**
常见修复方法:
- FileNotFoundError: 检查文件路径，使用绝对路径或确认相对路径正确
- KeyError: 先打印df.columns查看实际列名，不要假设列名
- ValueError: 检查数据类型，必要时进行类型转换
- ImportError: 确保导入了所有必要的库
"""
        )

    user_message_parts.append(
        """
**输出要求:**
1. 只输出Python代码，不要有任何解释文字
2. 代码必须放在 ```python 代码块内
3. 代码要完整、可直接执行
4. 使用print()输出关键信息
"""
    )

    user_message = "\n".join(user_message_parts)

    # 调用LLM
    messages = [
        SystemMessage(content=CODE_GENERATOR_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    raw_output = response.content

    # 提取Python代码（去除markdown标记）
    code = extract_python_code(raw_output)

    if not code:
        # 如果没有提取到代码块，可能LLM直接返回了代码
        code = raw_output.strip()

    return code


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


# ============================================================================
# 工具2: analyze_results - 分析执行结果
# ============================================================================


@tool
def analyze_results(
    original_task: str,
    execution_output: str,
    data_context: str = None,
) -> str:
    """
    分析代码执行结果，生成用户友好的数据分析报告。

    这个工具专注于分析代码的执行输出，将技术性结果转化为业务洞察。
    不需要传入代码本身，只需要执行结果即可。

    Args:
        original_task: 用户的原始任务描述，例如："分析销售数据的趋势"
        execution_output: 代码执行的输出结果（stdout），应包含详细的描述性信息
        data_context: 可选，数据上下文信息（JSON字符串）

    Returns:
        Markdown格式的数据分析报告

    Examples:
        >>> report = analyze_results(
        ...     original_task="分析data.csv的销售情况",
        ...     execution_output="数据形状: (200, 5)\\n平均销售额: 19706元\\n...",
        ...     data_context='{"file_path": "./data.csv"}'
        ... )
        >>> print(report)
        # 销售数据分析报告
        ...

    Note:
        为了让分析更准确，生成的代码应该在输出中包含：
        - 清晰的任务描述（"正在分析销售趋势..."）
        - 数据处理步骤说明
        - 图表类型和保存路径（如果生成了图表）
        这样分析工具无需查看代码就能理解做了什么。
    """
    # 初始化LLM
    from dotenv import load_dotenv
    import os

    load_dotenv(override=True)

    llm = ChatOpenAI(
        base_url=os.getenv("BASE_URL"),
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("API_KEY"),
        temperature=0.7,  # 分析报告可以稍微有创造性
    )

    # 构建用户消息（不再包含代码）
    user_message = f"""
请基于以下信息，撰写一份专业的数据分析报告。

## 上下文信息

### 1. 用户原始任务
{original_task}

### 2. 数据上下文
{data_context or "无额外上下文"}

### 3. 代码执行输出
```
{execution_output}
```

## 分析要求

请按照以下结构撰写报告（使用Markdown格式）：

1. **数据概览**: 解读统计数据，说明数据规模、质量、基本特征
2. **核心发现**: 3-5个最重要的洞察，每个洞察要有数据支撑和业务解读
3. **图表解读**: 如果输出中提到生成了图表，解释图表的作用和意义
4. **结论**: 直接回答用户的原始问题
5. **建议**: 基于数据提供可行的业务建议

## 写作原则

- 用业务语言，避免技术术语
- 每个结论都要有数据支撑
- 关注"So What"（数据的业务含义）
- 简洁有力，一段话表达一个核心观点
- 提供具体、可操作的建议

请开始撰写分析报告：
"""

    # 调用LLM
    messages = [
        SystemMessage(content=RESULT_ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)
    analysis_report = response.content

    return analysis_report


# ============================================================================
# 辅助函数
# ============================================================================


def format_error_message(error: Exception) -> str:
    """
    格式化错误信息，使其更易读

    Args:
        error: Python异常对象

    Returns:
        格式化的错误信息字符串
    """
    import traceback

    error_type = type(error).__name__
    error_msg = str(error)
    error_trace = traceback.format_exc()

    formatted = f"""
错误类型: {error_type}
错误信息: {error_msg}

详细堆栈:
{error_trace}
"""
    return formatted.strip()
