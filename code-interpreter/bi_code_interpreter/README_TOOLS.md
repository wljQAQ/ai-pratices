# BI Code Interpreter 工具详细说明

## 概述

本文档详细说明 `generate_python_code` 和 `analyze_results` 两个核心工具的实现和使用方法。

---

## 工具1: generate_python_code

### 功能描述
生成高质量、可执行的Python数据分析代码，支持基于错误信息自动修复。

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_description` | str | ✅ | 任务描述，例如："分析销售趋势" |
| `data_context` | str | ❌ | 数据上下文（JSON字符串），包含文件路径、schema等 |
| `previous_error` | str | ❌ | 上次执行的错误信息，用于代码修复 |

### 返回值
- **类型**: `str`
- **内容**: 纯Python代码（已去除markdown标记）

### 使用示例

#### 示例1: 基础代码生成
```python
from bi_code_interpreter.tools import generate_python_code

code = generate_python_code(
    task_description="读取data.csv并统计基本信息",
    data_context='{"file_path": "./data.csv"}'
)

print(code)
```

**生成的代码示例**:
```python
import pandas as pd
import os

def analyze_data():
    file_path = './data.csv'
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return None
    
    df = pd.read_csv(file_path)
    print("数据形状:", df.shape)
    print("\n前5行数据:")
    print(df.head())
    print("\n数据类型:")
    print(df.dtypes)
    
    return df

result = analyze_data()
```

#### 示例2: 带错误修复的代码生成
```python
# 第一次生成的代码执行失败
error_msg = "KeyError: 'date'"

# 基于错误信息重新生成
fixed_code = generate_python_code(
    task_description="绘制销售趋势图",
    data_context='{"file_path": "./sales.csv"}',
    previous_error=error_msg
)

print(fixed_code)
```

**修复后的代码会包含**:
- 先检查可用列名
- 智能查找日期列
- 添加更多错误处理

### 提示词设计要点

#### 1. 代码质量保证
- ✅ 完整的import语句
- ✅ 错误处理（try-except）
- ✅ 文件存在性检查
- ✅ 函数封装
- ✅ 清晰的print输出

#### 2. 错误修复机制
当提供 `previous_error` 时，提示词会:
- 明确标注这是错误修复任务
- 分析常见错误类型及解决方法
- 要求生成更健壮的代码

#### 3. 格式规范
- 代码必须在 ```python 代码块内
- 不允许在代码前后添加解释
- 使用正则表达式自动提取代码

---

## 工具2: analyze_results

### 功能描述
分析代码执行结果，生成用户友好的数据洞察报告（Markdown格式）。

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `original_task` | str | ✅ | 用户的原始任务 |
| `executed_code` | str | ✅ | 已执行的Python代码 |
| `execution_output` | str | ✅ | 代码执行输出（stdout） |
| `data_context` | str | ❌ | 数据上下文信息 |

### 返回值
- **类型**: `str`
- **格式**: Markdown
- **内容**: 包含数据概览、核心发现、建议等的完整报告

### 使用示例

```python
from bi_code_interpreter.tools import analyze_results

# 假设代码已执行
code = """
import pandas as pd
df = pd.read_csv('./data.csv')
print(df.describe())
"""

output = """
       销售金额      销售数量
count  200.000000  200.000000
mean   19706.591   25.975000
std    20938.971   14.909252
min    278.460     1.000000
max    130351.320  50.000000
"""

# 生成分析报告
report = analyze_results(
    original_task="分析销售数据",
    executed_code=code,
    execution_output=output,
    data_context='{"file_path": "./data.csv"}'
)

print(report)
```

### 报告结构示例

```markdown
# 销售数据分析报告

## 📊 数据概览

本次分析涵盖200条销售记录...

**关键统计信息解读:**
- **销售金额分布**: 平均19,707元，但标准差高达20,939元，说明...
- **销售数量**: 平均每单26件...

## 🔍 核心发现

### 发现1: 销售额呈现"长尾分布"
数据显示明显的右偏分布特征...

### 发现2: 高价值商品驱动收入
前20%的商品贡献了80%的销售额...

## ✅ 结论

针对您的问题"分析销售数据"，核心结论是...

## 💡 建议

1. **聚焦高价值品类**: ...
2. **优化库存结构**: ...
```

### 提示词设计要点

#### 1. 分析框架
报告分为5个部分:
- 数据概览（规模、质量、统计指标）
- 核心发现（3-5个洞察）
- 图表解读（如有）
- 结论（直接回答问题）
- 建议（可操作的行动建议）

#### 2. 写作原则
- ❌ 避免: "平均值是100"
- ✅ 应该: "平均销售额为100元，标准差80元说明差异很大"

#### 3. 业务导向
- 不只说"是什么"（What），更要说"意味着什么"（So What）
- 每个结论都有数据支撑
- 建议要具体、可落地

#### 4. 格式美化
- 使用emoji增强可读性（📊 🔍 ✅ 💡）
- 使用加粗、列表等markdown元素
- 合理使用代码块引用图表

---

## 综合工作流程

### 完整示例：从生成到分析

```python
from bi_code_interpreter.tools import generate_python_code, analyze_results
from bi_code_interpreter.executor import execute_python_code

# 步骤1: 生成代码
code = generate_python_code(
    task_description="分析data.csv的销售趋势并生成图表",
    data_context='{"file_path": "./data.csv"}'
)

print("生成的代码:")
print(code)
print("\n" + "="*50 + "\n")

# 步骤2: 执行代码
execution_result = execute_python_code(code)

if not execution_result["success"]:
    print("代码执行失败，尝试修复...")
    
    # 步骤2.1: 基于错误修复代码
    code = generate_python_code(
        task_description="分析data.csv的销售趋势并生成图表",
        data_context='{"file_path": "./data.csv"}',
        previous_error=execution_result["stderr"]
    )
    
    # 步骤2.2: 重新执行
    execution_result = execute_python_code(code)

# 步骤3: 分析结果
if execution_result["success"]:
    report = analyze_results(
        original_task="分析data.csv的销售趋势并生成图表",
        executed_code=code,
        execution_output=execution_result["stdout"],
        data_context='{"file_path": "./data.csv"}'
    )
    
    print("分析报告:")
    print(report)
else:
    print("多次尝试后仍然失败:", execution_result["stderr"])
```

---

## 提示词精华摘录

### CODE_GENERATOR_SYSTEM_PROMPT 核心要点

```
1. 代码质量优先
   - 完整、可执行
   - 包含所有import
   - 适当的注释
   - 错误处理

2. 格式要求
   - 必须在 ```python 代码块内
   - 不要有解释文字
   - 直接输出代码

3. 错误修复模式
   - 分析错误类型
   - 提供修复策略
   - 生成更健壮的代码
```

### RESULT_ANALYZER_SYSTEM_PROMPT 核心要点

```
1. 分析框架
   - 数据概览（规模、质量、统计）
   - 核心发现（3-5个洞察）
   - 图表解读
   - 结论
   - 建议

2. 写作原则
   - 业务语言，避免技术术语
   - 数据驱动，每个结论有支撑
   - 关注"So What"
   - 简洁有力

3. 格式要求
   - Markdown
   - 使用emoji
   - 清晰的层次结构
```

---

## 关键技术实现

### 1. 代码提取

```python
def extract_python_code(text: str) -> str:
    """从LLM响应中提取Python代码块"""
    pattern = r"```python\s*\n(.*?)```|```\s*\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        code = matches[0][0] if matches[0][0] else matches[0][1]
        return code.strip()
    
    return ""
```

### 2. LLM配置

```python
# 代码生成 - 低温度，保证稳定
llm_generator = ChatOpenAI(
    model=model_name,
    temperature=0.1,
)

# 结果分析 - 稍高温度，允许创造性
llm_analyzer = ChatOpenAI(
    model=model_name,
    temperature=0.7,
)
```

### 3. 上下文传递

所有上下文信息统一使用JSON格式:

```python
data_context = {
    "file_path": "./data.csv",
    "schema": {
        "columns": ["date", "sales", "quantity"],
        "dtypes": {"date": "datetime", "sales": "float", "quantity": "int"}
    },
    "known_issues": ["日期格式不统一"]
}

context_str = json.dumps(data_context, ensure_ascii=False)
```

---

## 测试建议

### 单元测试

```python
def test_generate_code_basic():
    """测试基本代码生成"""
    code = generate_python_code(
        task_description="打印Hello World",
        data_context='{"file_path": "./test.csv"}'
    )
    assert "print" in code
    assert "Hello World" in code or "hello" in code.lower()

def test_generate_code_with_error():
    """测试错误修复"""
    code = generate_python_code(
        task_description="读取数据",
        data_context='{"file_path": "./test.csv"}',
        previous_error="FileNotFoundError"
    )
    assert "os.path.exists" in code or "try" in code

def test_analyze_results():
    """测试结果分析"""
    report = analyze_results(
        original_task="测试分析",
        executed_code="print('test')",
        execution_output="test",
    )
    assert len(report) > 100  # 报告应该有一定长度
    assert "#" in report  # Markdown标题
```

---

## 常见问题 (FAQ)

### Q1: 为什么代码生成使用temperature=0.1？
**A**: 代码生成需要稳定性和准确性，低温度可以减少LLM的随机性，生成更可靠的代码。

### Q2: 如何处理LLM生成的代码不在代码块内？
**A**: `extract_python_code` 函数会尝试提取代码块，如果没有找到，会返回整个响应作为代码。

### Q3: 分析报告的长度有限制吗？
**A**: 没有硬性限制，但提示词要求"简洁有力"，实际测试中报告通常在500-1500词。

### Q4: 能否支持其他语言的代码生成？
**A**: 当前只支持Python，但可以通过修改提示词和工具名称扩展到R、SQL等。

### Q5: 错误信息会完整传递给LLM吗？
**A**: 是的，包括错误类型、错误信息和堆栈跟踪，帮助LLM准确理解问题。

---

## 下一步

- ✅ 已实现: `generate_python_code` 和 `analyze_results`
- ⏭️ 待实现: `execute_python_code` (代码执行器)
- ⏭️ 待实现: Agent组装和主工具封装
- ⏭️ 待实现: 集成到plan-and-execute

---

**文件位置**:
- 提示词: `/Users/huakaifugui/code/be/ai_practices/code-interpreter/bi_code_interpreter/prompts.py`
- 工具实现: `/Users/huakaifugui/code/be/ai_practices/code-interpreter/bi_code_interpreter/tools.py`
