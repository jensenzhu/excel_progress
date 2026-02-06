# Excel智能助手项目重构优化计划

## 阶段1：代码清理和基础优化（高优先级）

### 1.1 清理调试代码
- 移除 `excel_agent.py` 中的所有 `print(f"[DEBUG]...")` 调试语句
- 使用标准 `logging` 模块替代
- 配置日志级别（DEBUG/INFO/WARNING/ERROR）

### 1.2 安全性修复
- 将 API Key 从硬编码移至环境变量
- 创建 `.env.example` 模板文件
- 更新 `config/settings.py` 读取环境变量
- 添加 `.env` 到 `.gitignore`

### 1.3 Pydantic 升级
- 将 `schemas.py` 中的 `@validator` 升级为 `@field_validator`
- 更新导入语句和语法

## 阶段2：架构重构（中优先级）

### 2.1 统一架构
- 评估 `nlp_parser.py` 和 `operation_engine.py` 的使用情况
- 如果不再使用，废弃旧代码或移动到 `deprecated/` 目录
- 更新文档，明确 `app_agent.py` 为推荐版本
- 考虑删除或重构 `app.py`

### 2.2 重构 DataManager
- 拆分职责：
  - `DataManager`：核心表格管理
  - `TableMetadata`：元数据管理
  - `TableHistory`：操作历史管理
- 减少单个类的复杂度
- 改进方法命名和文档

### 2.3 创建统一的工具类
- 提取重复的 JSON 序列化逻辑
- 创建 `utils/json_helper.py` 统一处理
- 确保所有工具返回格式一致

## 阶段3：功能增强（中优先级）

### 3.1 实现撤销功能
- 利用现有的 `operation_history`
- 实现 `undo()` 和 `redo()` 方法
- 在 UI 中添加撤销/重做按钮

### 3.2 改进错误处理
- 创建统一的异常类 `ExcelAgentError`
- 实现全局错误处理器
- 提供友好的错误消息给用户
- 添加错误恢复机制

### 3.3 添加类型注解
- 为所有公共方法添加类型注解
- 使用 `mypy` 进行类型检查
- 在 `requirements.txt` 中添加 `mypy`

## 阶段4：代码质量提升（低优先级）

### 4.1 添加单元测试
- 创建 `tests/` 目录
- 为核心模块编写测试：
  - `test_data_manager.py`
  - `test_excel_agent.py`
  - `test_cell_operations.py`
- 使用 `pytest` 框架

### 4.2 代码规范
- 添加 `pyproject.toml` 配置
- 配置 `black`（代码格式化）
- 配置 `ruff`（代码检查）
- 配置 `isort`（导入排序）
- 添加 pre-commit hooks

### 4.3 文档完善
- 为所有公共方法添加 docstring
- 使用 Google 或 NumPy 风格
- 添加类型说明和参数说明

## 阶段5：性能优化（可选）

### 5.1 大文件优化
- 实现分块加载机制
- 添加进度条
- 优化内存使用

### 5.2 缓存机制
- 为频繁查询添加缓存
- 使用 `functools.lru_cache`

## 预期成果

- ✅ 代码质量提升（移除调试代码、统一风格）
- ✅ 安全性增强（API Key 管理）
- ✅ 架构清晰（单一职责、模块化）
- ✅ 功能完善（撤销/重做、错误处理）
- ✅ 可维护性提升（测试、文档、类型注解）

## 时间估计

- 阶段1：1-2小时
- 阶段2：3-4小时
- 阶段3：2-3小时
- 阶段4：3-4小时
- 阶段5：2-3小时

**总计**：11-16小时