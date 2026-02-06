# Excel智能数据操作助手 - 项目设计文档

## 项目概述

一个基于Streamlit和GLM-4.5-Flash的智能Excel数据处理系统，支持通过自然语言交互进行多表数据操作，包括数据提取、计算、跨表迁移和单元格级操作。

## 核心功能

### 1. 多表管理
- 同时加载和管理多个Excel文件
- 支持多sheet切换
- 表格对比视图
- 数据概览（行数、列数、数据类型、缺失值统计）

### 2. 自然语言交互
- 支持单表操作（筛选、计算、排序）
- 支持跨表操作（数据提取、合并、迁移）
- 支持单元格级操作（读取、写入特定单元格）
- 支持链式操作（"从...提取...然后...最后..."）

### 3. 数据操作
- **单表操作**：筛选、排序、分组、聚合
- **计算功能**：求和、平均值、计数、百分比、自定义计算
- **跨表操作**：合并、连接、数据迁移、基于键值映射
- **单元格操作**：读取、写入、范围操作

### 4. 可视化展示
- 交互式表格预览
- 多表标签页视图
- 并排对比模式
- 操作预览和确认
- 操作历史记录

## 技术架构

### 技术栈
- **前端框架**: Streamlit
- **数据处理**: Pandas, OpenPyXL
- **LLM**: GLM-4.5-Flash (通过OpenAI兼容API)
- **语言**: Python 3.9+

### 项目结构
```
excelprogress/
├── app.py                      # Streamlit主应用
├── core/
│   ├── data_manager.py         # 多表数据管理器
│   ├── nlp_parser.py           # 自然语言解析器
│   ├── operation_engine.py     # 操作执行引擎
│   └── cell_operations.py      # 单元格操作工具
├── ui/
│   ├── table_viewer.py         # 表格展示组件
│   ├── chat_interface.py       # 聊天界面
│   └── operation_preview.py    # 操作预览
├── utils/
│   ├── excel_handler.py        # Excel文件处理
│   └── validators.py           # 数据验证
├── config/
│   ├── settings.py             # 配置参数
│   └── prompts.py              # LLM提示词模板
├── examples/                    # 示例Excel文件
├── requirements.txt            # 依赖包
├── .gitignore
└── README.md
```

## 核心模块设计

### 1. DataManager（数据管理器）
```python
class DataManager:
    def __init__(self):
        self.tables = {}  # {table_name: DataFrame}
        self.active_table = None
    
    def load_table(self, file_path, table_name):
        """加载Excel文件"""
    
    def save_table(self, table_name, output_path):
        """保存Excel文件"""
    
    def get_table(self, table_name):
        """获取指定表格"""
    
    def get_cell_value(self, table_name, cell_ref):
        """获取单元格值"""
    
    def set_cell_value(self, table_name, cell_ref, value):
        """设置单元格值"""
    
    def get_table_info(self, table_name):
        """获取表格信息"""
```

### 2. NLPParser（自然语言解析器）
```python
class NLPParser:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def parse_instruction(self, instruction, context):
        """
        解析自然语言指令
        返回结构化操作列表
        """
    
    def extract_entities(self, instruction):
        """提取实体（表名、列名、单元格、操作类型）"""
    
    def identify_intent(self, instruction):
        """识别用户意图"""
```

### 3. OperationEngine（操作执行引擎）
```python
class OperationEngine:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def execute_operations(self, operations):
        """执行操作链"""
    
    def _extract(self, op):
        """提取数据"""
    
    def _calculate(self, op):
        """计算操作"""
    
    def _insert(self, op):
        """插入数据"""
    
    def _merge(self, op):
        """合并表格"""
```

### 4. CellOperations（单元格操作工具）
```python
class CellOperations:
    @staticmethod
    def parse_cell_reference(cell_ref):
        """解析单元格引用 A5 -> (row, col)"""
    
    @staticmethod
    def parse_range(range_ref):
        """解析范围引用 A5:C10 -> (start_row, start_col, end_row, end_col)"""
    
    @staticmethod
    def cell_to_excel(row, col):
        """将行列转换为Excel引用 (0, 0) -> A1"""
```

## UI设计

### 布局结构
```
┌─────────────────────────────────────────────────────────┐
│  Excel智能数据操作助手                    [上传文件]    │
├─────────────────────────────────────────────────────────┤
│  侧边栏          │  主区域                              │
│  ┌────────────┐  │  ┌────────────────────────────────┐ │
│  │ 已加载表格 │  │  │ 表1 (sales.xlsx)  [x]          │ │
│  │ □ 表1     │  │  │ ┌────────────────────────────┐ │ │
│  │ ☑ 表2     │  │  │ │ 数据表格展示               │ │ │
│  │ □ 表3     │  │  │ └────────────────────────────┘ │ │
│  │            │  │  │                                  │ │
│  │ 操作历史  │  │  │ [表2 (report.xlsx)  [x]]        │ │
│  │ 1. 提取A列│  │  │ ┌────────────────────────────┐ │ │
│  │ 2. 计算总和│  │  │ │ 数据表格展示               │ │ │
│  │ 3. 插入B5 │  │  │ └────────────────────────────┘ │ │
│  └────────────┘  │  └────────────────────────────────┘ │
│                  │                                      │
│                  │  ┌────────────────────────────────┐ │
│                  │  │ 💬 自然语言操作                 │ │
│                  │  │ ┌────────────────────────────┐ │ │
│                  │  │ │ 输入指令...                 │ │ │
│                  │  │ │ [执行] [预览]               │ │ │
│                  │  │ └────────────────────────────┘ │ │
│                  │  │                                │ │
│                  │  │ 📋 操作预览                    │ │
│                  │  │ • 从表1提取A列                 │ │
│                  │  │ • 计算平均值                   │ │
│                  │  │ • 插入到表2的B5单元格          │ │
│                  │  │                                │ │
│                  │  │ [确认执行] [取消]              │ │
│                  │  └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 典型使用场景

### 场景1：数据迁移
```
用户: "打开sales.xlsx和report.xlsx"
系统: [显示两个标签页]

用户: "从sales表提取产品名称列，计算每个产品的总销量，
     然后将结果填入report表的C2到C100区域"
系统: [显示操作预览]
     - 提取：sales['产品名称']
     - 计算：按产品分组求和
     - 插入：report['C2:C100']

用户: "确认执行"
系统: [执行并显示结果]
```

### 场景2：数据更新
```
用户: "用inventory表的库存数量更新sales表的对应产品库存"
系统: [识别共同列：产品ID]
     [显示将要更新的行数]
     [执行更新]
```

### 场景3：数据合并
```
用户: "将表A的姓名列和表B的工资列合并，
     根据员工ID匹配，保存为新表merged.xlsx"
系统: [执行合并操作]
```

### 场景4：单元格级操作
```
用户: "计算表1所有行的总和，结果存入表2的A1单元格"
系统: [执行计算并写入]
```

## 自然语言交互复杂度

### Level 1: 简单交互
```
"计算A列的平均值"
"筛选B列大于100的行"
"选择第3列到第5列"
```

### Level 2: 中等复杂
```
"筛选销售额大于1000的行，然后计算这些行的平均利润"
"将A列和B列相加，结果存为新列C"
"按地区分组，计算每个地区的总销售额"
```

### Level 3: 复杂交互（跨表操作）
```
"从表1提取A列数据，计算平均值后填入表2的B5单元格"
"将表1的姓名列和表2的年龄列合并，存为新表"
"用表1的销售额更新表2中对应产品的库存"
```

## LLM配置

### GLM-4.5-Flash API配置
- **API Key**: 2a7ec09588b14d14b66d730ac2e5266e.2ATkSDwtRBlgi6Rn
- **Base URL**: https://open.bigmodel.cn/api/paas/v4
- **Model**: glm-4.5-flash
- **兼容性**: OpenAI API格式

### 提示词设计
提示词将包含：
- 当前已加载的表格列表
- 当前激活的表格
- 表格结构信息（列名、数据类型）
- 操作指令
- 输出格式要求（JSON结构化操作）

## 依赖包

```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
openai>=1.0.0
python-dotenv>=1.0.0
```

## 实施计划

### 阶段1：基础功能
- [x] 项目结构搭建
- [ ] Streamlit应用框架
- [ ] 单表加载和展示
- [ ] 基础自然语言解析（单表操作）

### 阶段2：多表支持
- [ ] 多表管理器
- [ ] 表格切换UI
- [ ] 跨表操作解析

### 阶段3：高级功能
- [ ] 单元格级操作
- [ ] 数据范围操作
- [ ] 操作预览和确认

### 阶段4：优化增强
- [ ] 操作历史和撤销
- [ ] 批量操作
- [ ] 数据验证和错误处理

## 扩展功能

- **数据洞察**：自动分析数据特征
- **智能推荐**：根据数据类型推荐操作
- **模板保存**：保存常用操作流程
- **批量处理**：支持多文件处理
- **数据验证**：检查数据质量
- **操作脚本导出**：将操作导出为Python脚本

## 注意事项

1. **安全性**: API Key不应提交到版本控制，使用环境变量
2. **性能**: 大文件处理需要考虑分页和懒加载
3. **错误处理**: 提供友好的错误提示和恢复机制
4. **用户体验**: 操作前预览，避免误操作
5. **数据备份**: 重要操作前自动备份数据