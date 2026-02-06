# 已弃用模块

本目录包含已弃用的旧版代码，保留用于历史参考。

## 已弃用模块

- `nlp_parser.py` - 旧版自然语言解析器
- `operation_engine.py` - 旧版操作引擎

## 原因

这些模块已被新的基于 LangGraph ReAct Agent 的架构取代。新架构（`core/excel_agent.py`）提供：
- 更好的自然语言理解能力
- 更灵活的工具调用机制
- 更容易维护和扩展的代码结构

## 推荐使用

- **应用入口**: `app_agent.py` (使用新架构)
- **核心模块**: `core/excel_agent.py` + `core/data_manager.py`
- **已弃用**: `app.py` (使用旧架构)

## 迁移指南

如果你正在使用 `app.py`，建议迁移到 `app_agent.py`：

1. 新版本提供相同的用户界面
2. 新版本使用更强大的 LLM Agent
3. 新版本支持更复杂的操作序列
4. 新版本有更好的错误处理和恢复能力
