# 类型注解指南

本项目使用 Python 类型注解来提高代码质量和可维护性。

## 已添加类型注解的模块

### 核心模块

#### core/data_manager.py
所有公共方法都已添加完整的类型注解：
- `load_table(file_path: str, table_name: Optional[str] = None, sheet_name: Optional[str] = None) -> bool`
- `save_table(table_name: str, output_path: str) -> bool`
- `get_table(table_name: str) -> Optional[pd.DataFrame]`
- `undo(table_name: Optional[str] = None) -> bool`
- `redo(table_name: Optional[str] = None) -> bool`

#### core/table_metadata.py
使用 `@dataclass` 装饰器，自动生成类型注解：
```python
@dataclass
class TableMetadata:
    name: str
    file_path: str
    columns: List[str]
    total_rows: int
    ...
```

#### core/table_history.py
完整的类型注解：
```python
def add_operation(
    self,
    operation_type: OperationType,
    table_name: str,
    description: str = "",
    parameters: Optional[Dict[str, Any]] = None,
    result_summary: str = ""
) -> None
```

#### core/exceptions.py
所有异常类都有类型注解：
```python
def __init__(self, message: str, details: str = "")
def to_dict(self) -> dict
```

#### utils/json_helper.py
完整的类型注解：
```python
def json_dumps(data: Any, ensure_ascii: bool = False, indent: int = None) -> str
def json_loads(json_str: str) -> Any
def create_success_response(data: Any = None, message: str = "") -> str
def create_error_response(error: str, details: Any = None) -> str
```

## 待添加类型注解的模块

### core/excel_agent.py
需要为以下方法添加类型注解：
- `_create_tools()`
- `_build_workflow()`
- `_call_model()`
- `_process_tool_calls()`

### core/cell_operations.py
需要为所有方法添加类型注解。

### UI 模块
- `app_agent.py`
- `app.py`

## 类型注解最佳实践

### 1. 使用 Optional 表示可能为 None 的值
```python
def get_table(table_name: str) -> Optional[pd.DataFrame]:
    return self.tables.get(table_name)
```

### 2. 使用 Union 表示多种可能的类型
```python
from typing import Union

def process_data(data: Union[str, int, float]) -> str:
    return str(data)
```

### 3. 使用 List, Dict, Tuple 表示集合类型
```python
def get_tables() -> List[str]:
    return list(self.tables.keys())

def get_metadata() -> Dict[str, Any]:
    return metadata.to_dict()
```

### 4. 使用 Callable 表示函数类型
```python
from typing import Callable

def apply_function(df: pd.DataFrame, func: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
    return func(df)
```

### 5. 使用 Literal 表示固定的字符串值
```python
from typing import Literal

def set_mode(mode: Literal["edit", "view"]) -> None:
    self.mode = mode
```

## 使用 mypy 进行类型检查

安装 mypy：
```bash
pip install mypy
```

运行类型检查：
```bash
mypy core/
mypy utils/
```

在 `requirements.txt` 中添加：
```
mypy>=1.0.0
```

## 类型注解的优势

1. **IDE 支持**：更好的自动补全和类型提示
2. **早期发现错误**：在运行前发现类型错误
3. **代码文档**：类型注解本身就是文档
4. **重构安全**：重构时更容易发现不兼容的改动
5. **团队协作**：统一的接口定义

## 推荐阅读

- [PEP 484 -- Type Hints](https://peps.python.org/pep-0484/)
- [Python Type Checking Guide](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
