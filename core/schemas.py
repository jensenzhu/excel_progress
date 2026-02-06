from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal


class LoadTableInput(BaseModel):
    """加载Excel表格工具的输入模型"""
    
    file_path: str = Field(
        description="Excel文件路径"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称，如果不提供则使用文件名"
    )
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        if not v.endswith(('.xlsx', '.xls')):
            raise ValueError("必须是Excel文件(.xlsx或.xls)")
        return v


class CalculateInput(BaseModel):
    """计算工具的输入模型"""
    
    operation: Literal['sum', 'mean', 'count', 'max', 'min', 'median', 'std', 'var'] = Field(
        description="计算类型"
    )
    
    column: str = Field(
        description="要计算的列名"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class FilterInput(BaseModel):
    """筛选工具的输入模型"""
    
    condition: str = Field(
        description="筛选条件，使用pandas查询语法，如 '销售额 > 1000' 或 '部门 == \"技术部\"'"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class SortInput(BaseModel):
    """排序工具的输入模型"""
    
    column: str = Field(
        description="要排序的列名"
    )
    
    order: Literal['asc', 'desc'] = Field(
        default='asc',
        description="排序方向"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class GroupInput(BaseModel):
    """分组工具的输入模型"""
    
    column: str = Field(
        description="分组列名"
    )
    
    agg_func: Literal['sum', 'mean', 'count', 'max', 'min'] = Field(
        default='sum',
        description="聚合函数"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class ExtractInput(BaseModel):
    """提取工具的输入模型"""
    
    columns: List[str] = Field(
        description="要提取的列名列表"
    )
    
    rows: Optional[str] = Field(
        default='all',
        description="要提取的行，'all'表示全部，或使用 'start:end' 格式"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class InsertInput(BaseModel):
    """插入工具的输入模型"""
    
    target_table: str = Field(
        description="目标表格名称"
    )
    
    target_column: Optional[str] = Field(
        default=None,
        description="目标列名"
    )
    
    target_cell: Optional[str] = Field(
        default=None,
        description="目标单元格，如 'A5'"
    )
    
    value: Optional[str] = Field(
        default=None,
        description="要插入的值"
    )
    
    @field_validator('target_column', 'target_cell')
    @classmethod
    def validate_target(cls, v, info):
        if not info.data.get('target_column') and not info.data.get('target_cell'):
            raise ValueError("必须指定target_column或target_cell之一")
        return v


class MergeInput(BaseModel):
    """合并工具的输入模型"""
    
    tables: List[str] = Field(
        min_items=2,
        description="要合并的表格名称列表"
    )
    
    key: str = Field(
        description="合并键列名"
    )
    
    how: Literal['inner', 'outer', 'left', 'right'] = Field(
        default='inner',
        description="合并方式"
    )


class UpdateInput(BaseModel):
    """更新工具的输入模型"""
    
    target_table: str = Field(
        description="目标表格名称"
    )
    
    source_table: str = Field(
        description="源表格名称"
    )
    
    key: str = Field(
        description="匹配键列名"
    )
    
    update_column: str = Field(
        description="要更新的列名"
    )


class SaveInput(BaseModel):
    """保存工具的输入模型"""
    
    table_name: str = Field(
        description="要保存的表格名称"
    )
    
    output_path: str = Field(
        description="输出文件路径"
    )


class GetTableInfoInput(BaseModel):
    """获取表格信息工具的输入模型"""
    
    table_name: str = Field(
        description="表格名称"
    )


class ListTablesInput(BaseModel):
    """列出表格工具的输入模型"""
    pass


class QueryInput(BaseModel):
    """查询工具的输入模型"""
    
    query: str = Field(
        description="自然语言查询，如 '技术部有多少人' 或 '计算销售额的平均值'"
    )


class DetectHeaderInput(BaseModel):
    """检测表头工具的输入模型"""
    
    table_name: str = Field(
        description="表格名称"
    )
    
    preview_rows: int = Field(
        default=10,
        description="预览的行数，用于分析表头"
    )


class SetHeaderInput(BaseModel):
    """设置表头工具的输入模型"""
    
    table_name: str = Field(
        description="表格名称"
    )
    
    header_row: int = Field(
        description="表头所在的行索引（0表示第一行）"
    )


class FillInput(BaseModel):
    """填充空值工具的输入模型"""
    
    target_column: str = Field(
        description="要填充空值的列名"
    )
    
    source_column: Optional[str] = Field(
        default=None,
        description="源列名，用于填充目标列的空值"
    )
    
    value: Optional[str] = Field(
        default=None,
        description="填充的固定值"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class CopyColumnInput(BaseModel):
    """复制列数据工具的输入模型"""
    
    target_column: str = Field(
        description="目标列名，将被覆盖"
    )
    
    source_column: str = Field(
        description="源列名，数据将复制到目标列"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )


class ColumnCalculationInput(BaseModel):
    """列运算工具的输入模型"""
    
    operation: Literal['add', 'subtract', 'multiply', 'divide'] = Field(
        description="运算类型：add(加)、subtract(减)、multiply(乘)、divide(除)"
    )
    
    column1: str = Field(
        description="第一列名"
    )
    
    column2: str = Field(
        description="第二列名"
    )
    
    target_column: str = Field(
        description="结果列名，如果不存在则创建新列"
    )
    
    table_name: Optional[str] = Field(
        default=None,
        description="表格名称"
    )