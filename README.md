# Excel智能数据操作助手

一个基于Streamlit和GLM-4.5-Flash的智能Excel数据处理系统，支持通过自然语言交互进行多表数据操作。

## 功能特性

### 核心功能
- 📊 **多表管理**: 同时加载和管理多个Excel文件
- 💬 **自然语言交互**: 使用自然语言指令进行数据操作
- 🔗 **跨表操作**: 支持多表之间的数据提取、合并、迁移
- 📝 **单元格级操作**: 支持读取和写入特定单元格
- 👁️ **操作预览**: 执行前预览操作内容和预期结果
- 📜 **操作历史**: 记录所有操作，支持查看和追溯

### 支持的操作
- **提取**: 从表格中提取数据
- **计算**: 求和、平均值、计数、最大值、最小值等
- **筛选**: 根据条件筛选数据
- **排序**: 对数据进行排序
- **分组**: 按列分组并聚合
- **插入**: 将数据插入到指定位置
- **合并**: 合并多个表格
- **更新**: 更新表格数据
- **保存**: 保存表格到文件

## 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas, OpenPyXL
- **LLM**: GLM-4.5-Flash (通过OpenAI兼容API)
- **语言**: Python 3.9+

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd excelprogress
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

API配置已在 `config/settings.py` 中设置，无需额外配置：

```python
API_KEY = "2a7ec09588b14d14b66d730ac2e5266e.2ATkSDwtRBlgi6Rn"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
MODEL = "glm-4.5-flash"
```

## 使用

### 启动应用

```bash
streamlit run app.py
```

应用将在浏览器中打开，默认地址为 `http://localhost:8501`

### 创建示例数据

```bash
python examples/create_samples.py
```

这将在 `examples/` 目录下创建示例Excel文件：
- `sales_data.xlsx` - 销售数据
- `inventory_data.xlsx` - 库存数据
- `report_template.xlsx` - 报表模板
- `employee_data.xlsx` - 员工数据

### 使用流程

1. **上传文件**: 在侧边栏上传Excel文件
2. **选择表格**: 选择要操作的表格
3. **输入指令**: 在右侧输入自然语言指令
4. **预览操作**: 点击"预览"查看操作详情
5. **执行操作**: 点击"执行"执行操作
6. **查看结果**: 查看操作结果和更新后的数据

### 示例指令

#### 单表操作
```
计算销售额列的总和
筛选利润大于500的行
按地区分组，计算每个地区的平均销售额
按销售额降序排序
```

#### 跨表操作
```
从sales_data提取产品名称列
将sales_data的销售额列插入到report_template的C列
用inventory_data的库存数量更新sales_data的对应产品
合并sales_data和inventory_data，基于产品ID列
```

#### 单元格操作
```
计算所有行的平均值，存入A1单元格
将sales_data的总销售额填入report_template的B5单元格
```

## 项目结构

```
excelprogress/
├── app.py                      # Streamlit主应用
├── core/
│   ├── __init__.py
│   ├── data_manager.py         # 多表数据管理器
│   ├── nlp_parser.py           # 自然语言解析器
│   ├── operation_engine.py     # 操作执行引擎
│   └── cell_operations.py      # 单元格操作工具
├── ui/
│   ├── __init__.py
│   ├── table_viewer.py         # 表格展示组件
│   ├── chat_interface.py       # 聊天界面
│   └── operation_preview.py    # 操作预览
├── utils/
│   ├── __init__.py
│   ├── excel_handler.py        # Excel文件处理
│   └── validators.py           # 数据验证
├── config/
│   ├── __init__.py
│   ├── settings.py             # 配置参数
│   └── prompts.py              # LLM提示词模板
├── examples/
│   └── create_samples.py       # 创建示例数据
├── design.md                   # 项目设计文档
├── requirements.txt            # 依赖包
├── .gitignore
└── README.md
```

## 开发

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black .
isort .
```

### 代码检查

```bash
flake8 .
mypy .
```

## 注意事项

1. **文件大小限制**: 默认最大支持200MB的Excel文件
2. **API限制**: GLM-4.5-Flash API有调用频率限制
3. **数据备份**: 重要操作前建议备份数据
4. **网络连接**: 需要网络连接以调用LLM API

## 常见问题

### Q: 如何处理大文件？
A: 对于大文件，建议先进行筛选或分页处理，避免一次性加载全部数据。

### Q: 支持哪些Excel格式？
A: 支持 `.xlsx` 和 `.xls` 格式。

### Q: 如何撤销操作？
A: 当前版本支持查看操作历史，但暂不支持撤销。建议在执行重要操作前先预览。

### Q: 可以离线使用吗？
A: 不可以，需要网络连接以调用GLM-4.5-Flash API进行自然语言解析。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

## 致谢

- [Streamlit](https://streamlit.io/) - Web应用框架
- [Pandas](https://pandas.pydata.org/) - 数据处理库
- [GLM-4.5-Flash](https://open.bigmodel.cn/) - 大语言模型