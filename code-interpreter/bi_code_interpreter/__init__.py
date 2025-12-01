"""
BI Code Interpreter - 具备错误自动修复能力的代码解释器

主要组件:
- tools.py: 核心工具实现
- prompts.py: 提示词模板
- executor.py: 代码执行器
- agent.py: Agent组装
- main_tool.py: 对外接口
"""

from .tools import generate_python_code, analyze_results, execute_python_code
from .main_tool import bi_code_interpreter

__all__ = [
    "generate_python_code",
    "analyze_results", 
    "execute_python_code",
    "bi_code_interpreter",
]
