from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class TableMetadata:
    """表格元数据"""
    
    name: str
    file_path: str
    columns: List[str]
    total_rows: int
    header_row: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    file_size: int = 0
    sheet_name: str = "Sheet1"
    data_types: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "columns": self.columns,
            "total_rows": self.total_rows,
            "header_row": self.header_row,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "file_size": self.file_size,
            "sheet_name": self.sheet_name,
            "data_types": self.data_types
        }
    
    def update_modified_time(self):
        """更新最后修改时间"""
        self.last_modified = datetime.now()
    
    def add_column_type(self, column: str, dtype: str):
        """添加列的数据类型"""
        self.data_types[column] = dtype
    
    def get_column_count(self) -> int:
        """获取列数"""
        return len(self.columns)
