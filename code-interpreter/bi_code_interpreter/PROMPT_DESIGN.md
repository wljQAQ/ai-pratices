# Prompt设计说明

## 问题回顾

**用户提问**: CODE_INTERPRETER_AGENT_PROMPT 是系统提示词还是用户消息？如果是系统提示词，不应该包含具体的 query 和 data_context 吗？

**回答**: 完全正确！这是一个重要的设计问题。

## 修正方案

### 问题分析

原设计将系统提示词和用户消息混在一起：
```python
# ❌ 错误设计
CODE_INTERPRETER_AGENT_PROMPT = """
你是一个Agent...

## 数据上下文
{data_context}  # 动态变量！

## 用户查询  
{query}  # 动态变量！
"""
```

**问题**:
1. 系统提示词应该是**静态的、通用的**
2. 动态内容（query、data_context）应该在**用户消息**中传递
3. 混在一起会导致每次调用都要重新格式化整个提示词

### 正确设计

现在分离为两部分：

#### 1. 系统提示词（静态）
```python
CODE_INTERPRETER_AGENT_SYSTEM_PROMPT = """
你是一个专业的BI数据分析代码解释器Agent...

## 你的能力
...工具列表...

## 工作流程
...标准流程和错误处理...

## 重要规则
...规则说明...
"""
```

**特点**:
- ✅ 完全静态，无动态变量
- ✅ 定义Agent的角色和能力
- ✅ 可以复用，不需要每次格式化

#### 2. 用户消息（动态）
```python
def create_agent_user_message(query: str, data_context: dict = None) -> str:
    """创建Agent的用户消息"""
    context_str = json.dumps(data_context, ensure_ascii=False, indent=2)
    
    message = f"""请完成以下数据分析任务：

## 用户查询
{query}

## 数据上下文
```json
{context_str}
```

请按照标准流程开始执行任务。
"""
    return message
```

**特点**:
- ✅ 只包含动态内容
- ✅ 每次调用时生成
- ✅ 清晰的输入结构

## 使用方式对比

### 修正前（错误）
```python
from langchain_core.prompts import PromptTemplate

# 需要格式化整个大提示词
prompt = PromptTemplate.from_template(CODE_INTERPRETER_AGENT_PROMPT)
message = prompt.format(query="...", data_context="...")
```

### 修正后（正确）
```python
from langchain_core.messages import SystemMessage, HumanMessage

# 系统提示词固定
system_msg = SystemMessage(content=CODE_INTERPRETER_AGENT_SYSTEM_PROMPT)

# 用户消息动态生成
user_msg = HumanMessage(content=create_agent_user_message(
    query="分析销售数据",
    data_context={"file_path": "./data.csv"}
))

# 传递给Agent
messages = [system_msg, user_msg]
```

## 实际应用

### 在Agent创建时使用

```python
from langchain.agents import create_react_agent, AgentExecutor
from bi_code_interpreter.prompts import (
    CODE_INTERPRETER_AGENT_SYSTEM_PROMPT,
    create_agent_user_message
)

def create_code_interpreter_agent(llm, tools):
    """创建Code Interpreter Agent"""
    
    # 方式1: 使用LangChain的ChatPromptTemplate
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", CODE_INTERPRETER_AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )

# 使用Agent
agent_executor = create_code_interpreter_agent(llm, tools)

# 调用时传入动态内容
user_input = create_agent_user_message(
    query="分析data.csv的销售趋势",
    data_context={"file_path": "./data.csv"}
)

result = agent_executor.invoke({"input": user_input})
```

### 或者更简单的方式

```python
# 方式2: 直接构造消息列表
from langchain_core.messages import SystemMessage, HumanMessage

def invoke_code_interpreter_agent(query: str, data_context: dict = None):
    """调用Code Interpreter Agent"""
    
    messages = [
        SystemMessage(content=CODE_INTERPRETER_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=create_agent_user_message(query, data_context))
    ]
    
    # 如果使用create_react_agent
    result = agent_executor.invoke({"input": messages[-1].content})
    
    return result
```

## 设计原则总结

### 系统提示词（System Prompt）
- **作用**: 定义AI的角色、能力、规则
- **特点**: 静态、通用、可复用
- **内容**: 
  - 角色定义："你是一个..."
  - 能力描述："你可以使用工具..."
  - 工作流程："先...再...最后..."
  - 规则约束："必须...不要..."

### 用户消息（User Message）
- **作用**: 提供具体任务和上下文
- **特点**: 动态、具体、每次不同
- **内容**:
  - 具体任务："分析销售数据"
  - 上下文信息：文件路径、已知schema等
  - 特殊要求：输出格式、时间限制等

## 其他提示词的检查

### CODE_GENERATOR_SYSTEM_PROMPT ✅
```python
CODE_GENERATOR_SYSTEM_PROMPT = """你是一个专业的Python代码生成器..."""
```
- ✅ 纯系统提示词，无动态变量
- ✅ 定义代码生成的规则和最佳实践

### RESULT_ANALYZER_SYSTEM_PROMPT ✅
```python
RESULT_ANALYZER_SYSTEM_PROMPT = """你是一位资深的数据分析师..."""
```
- ✅ 纯系统提示词，无动态变量
- ✅ 定义分析报告的框架和写作原则

### 工具调用时的消息构建 ✅
在 `tools.py` 中，工具函数正确地构建了完整的消息：

```python
# generate_python_code 工具
messages = [
    SystemMessage(content=CODE_GENERATOR_SYSTEM_PROMPT),  # 系统提示词
    HumanMessage(content=user_message),  # 动态构建的用户消息
]
```

```python
# analyze_results 工具
messages = [
    SystemMessage(content=RESULT_ANALYZER_SYSTEM_PROMPT),  # 系统提示词
    HumanMessage(content=user_message),  # 动态构建的用户消息
]
```

这些设计都是正确的！✅

## 最佳实践

### 1. 提示词命名约定
```python
# 系统提示词
ROLE_NAME_SYSTEM_PROMPT = "..."

# 用户消息生成函数
def create_role_name_user_message(...) -> str:
    ...
```

### 2. 分离原则
- **系统提示词**: 描述"**你是谁**"、"**你能做什么**"、"**你应该如何做**"
- **用户消息**: 描述"**我要你做什么**"、"**这里是数据**"、"**这里是要求**"

### 3. 可测试性
分离后更容易测试：
```python
def test_system_prompt():
    # 系统提示词应该是固定的
    assert "{" not in CODE_INTERPRETER_AGENT_SYSTEM_PROMPT
    assert "}" not in CODE_INTERPRETER_AGENT_SYSTEM_PROMPT

def test_user_message_generation():
    msg = create_agent_user_message("test query", {"key": "value"})
    assert "test query" in msg
    assert "key" in msg
```

## 总结

感谢你指出这个设计问题！修正后的设计更加清晰和符合最佳实践：

1. ✅ **系统提示词纯净**: 无动态变量
2. ✅ **职责分离**: 系统提示词定义能力，用户消息传递任务
3. ✅ **易于维护**: 修改系统提示词不影响消息构建逻辑
4. ✅ **符合LangChain规范**: 使用标准的SystemMessage和HumanMessage
5. ✅ **向后兼容**: 保留了旧的变量名但标注为废弃

这是一个很好的代码审查点！🎯
