# Excel智能数据操作助手 - ReAct Agent版本

基于 **LangGraph ReAct Agent** 框架重构的智能Excel数据处理系统，使用GLM-4.5-Flash + Pydantic实现更强的自然语言理解能力。

## 🚀 新架构特性

### 1. **ReAct Agent框架**
- **推理**: Agent自动分析用户意图，制定执行计划
- **行动**: 自动选择合适的工具并执行操作
- **观察**: 根据执行结果调整策略，支持多步骤任务

### 2. **Pydantic类型安全**
- 所有工具输入使用Pydantic模型定义
- 自动类型验证和错误提示
- 生成准确的工具参数说明

### 3. **工具系统**
- 10个专用Excel数据处理工具
- 自动参数验证
- 清晰的错误处理

### 4. **智能查询解析**
- 自动识别"XX部有多少人"等复杂查询
- 自动分解为多个步骤
- 支持多轮对话和上下文理解

## 📦 项目结构

```
excelprogress/
├── app_agent.py              # 新版Streamlit应用（使用Agent）
├── app.py                    # 旧版应用（向后兼容）
├── core/
│   ├── excel_agent.py         # LangGraph ReAct Agent实现
│   ├── schemas.py             # Pydantic模型定义
│   ├── data_manager.py       # 数据管理器
│   ├── cell_operations.py    # 单元格操作
│   ├── operation_engine.py    # 旧版操作引擎
│   └── nlp_parser.py         # 旧版NLP解析器
├── ui/
│   ├── table_viewer.py
│   ├── chat_interface.py
│   └── operation_preview.py
├── utils/
│   ├── excel_handler.py
│   └── validators.py
├── config/
│   ├── settings.py
│   └── prompts.py
├── examples/
│   └── create_samples.py
└── requirements.txt
```

## 🔧 核心组件

### 1. **ExcelAgent** (core/excel_agent.py)
基于LangGraph的ReAct Agent实现：

```python
class ExcelAgent:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.llm = ChatOpenAI(...)  # GLM-4.5-Flash
        self.tools = self._create_tools()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def invoke(self, query: str) -> dict:
        """处理用户查询"""
        return self.app.invoke({"messages": [...]})
```

### 2. **工具列表**
所有工具使用Pydantic模型定义输入：

1. **list_tables**: 列出所有已加载的表格
2. **get_table_info**: 获取表格详细信息
3. **calculate**: 计算统计值（sum, mean, count, max, min, median, std, var）
4. **filter_data**: 根据条件筛选数据
5. **sort_data**: 对数据排序
6. **group_data**: 分组聚合
7. **insert_data**: 插入数据到指定位置
8. **merge_tables**: 合并多个表格
9. **update_data**: 更新表格数据
10. **save_table**: 保存表格到文件

### 3. **Pydantic模型** (core/schemas.py)
所有工具输入使用Pydantic定义，确保类型安全：

```python
class CalculateInput(BaseModel):
    operation: Literal['sum', 'mean', 'count', 'max', 'min', 'median', 'std', 'var']
    column: str
    table_name: Optional[str] = None
```

## 🎯 使用方式

### 启动新版应用（推荐）

```bash
streamlit run app_agent.py
```

### 启动旧版应用

```bash
streamlit run app.py
```

## 💬 查询示例

### 统计查询
```
技术部有多少人
统计技术部人数
计算销售额的平均值
查看销售部的员工
```

### 数据操作
```
筛选利润大于500的行
按地区分组，计算总和
按工资降序排序
```

### 跨表操作
```
从sales_data提取产品名称列
将inventory_data的库存数量插入到sales_data的库存列
合并sales_data和employee_data，基于员工ID
```

### 复杂查询
```
先筛选技术部的员工，然后计算他们的平均工资
查看销售额大于10000的订单，按地区分组统计
```

## 🔍 工作流程

### Agent处理流程

```
用户输入 "技术部有多少人"
    ↓
Agent推理
    ↓
选择工具: filter_data (condition: "部门 == '技术部'")
    ↓
执行工具 → 返回筛选结果
    ↓
Agent观察结果
    ↓
选择工具: calculate (operation: "count")
    ↓
执行工具 → 返回计数结果
    ↓
生成回答 "技术部有X人"
```

### 状态流转

```
[用户查询]
    ↓
[Agent节点] - LLM推理
    ↓
[需要工具?] → 是
    ↓
[Tools节点] - 执行工具
    ↓
[Agent节点] - 观察结果
    ↓
[需要工具?] → 否
    ↓
[END]
```

## 📊 对比：旧版 vs 新版

| 特性 | 旧版 (app.py) | 新版 (app_agent.py) |
|------|-----------------|---------------------|
| 解析方式 | 手动提示词 | ReAct Agent自动推理 |
| 操作链 | 手动传递result_key | Agent自动管理 |
| 错误处理 | 基础 | 智能重试和恢复 |
| 类型安全 | 无 | Pydantic验证 |
| 扩展性 | 中等 | 高（易添加工具） |
| 上下文理解 | 有限 | 强（支持多轮对话） |

## 🛠️ 开发指南

### 添加新工具

1. 在 `core/schemas.py` 中定义Pydantic模型：

```python
class MyToolInput(BaseModel):
    param1: str = Field(description="参数1")
    param2: int = Field(description="参数2")
```

2. 在 `core/excel_agent.py` 的 `_create_tools()` 方法中添加工具：

```python
@tool(args_schema=MyToolInput)
def my_tool(param1: str, param2: int) -> str:
    """工具描述"""
    # 实现逻辑
    return json.dumps({"success": True, "result": ...})
```

3. 更新系统提示词（`_get_system_prompt` 方法）

### 自定义LLM

修改 `config/settings.py`：

```python
MODEL = "glm-4-plus"  # 或其他模型
API_KEY = "your-api-key"
BASE_URL = "your-base-url"
```

## 📝 技术栈

- **Agent框架**: LangGraph 0.2+
- **LLM**: GLM-4.5-Flash (OpenAI兼容)
- **数据处理**: Pandas, OpenPyXL
- **类型验证**: Pydantic 2.0+
- **Web框架**: Streamlit
- **工具管理**: LangChain Core

## 🔮 未来计划

- [ ] 支持更多图表类型
- [ ] 添加数据可视化工具
- [ ] 支持CSV导入/导出
- [ ] 添加操作撤销功能
- [ ] 支持批量文件处理
- [ ] 添加数据质量检查工具

## 📄 相关文档

- [design.md](design.md) - 项目设计文档
- [README.md](README.md) - 原版README
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [Pydantic文档](https://docs.pydantic.dev/)

## ⚠️ 注意事项

1. **依赖安装**: 需要安装LangGraph相关依赖包
2. **API配置**: 确保GLM-4.5-Flash API密钥正确
3. **性能**: 复杂查询可能需要多次LLM调用
4. **兼容性**: 旧版app.py仍可使用，但功能有限

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License