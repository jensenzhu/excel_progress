from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import copy


class OperationType(Enum):
    """操作类型枚举"""
    LOAD = "load"
    SAVE = "save"
    CALCULATE = "calculate"
    FILTER = "filter"
    SORT = "sort"
    GROUP = "group"
    EXTRACT = "extract"
    INSERT = "insert"
    MERGE = "merge"
    UPDATE = "update"
    FILL = "fill"
    COPY_COLUMN = "copy_column"
    COLUMN_CALCULATION = "column_calculation"
    SET_HEADER = "set_header"
    DETECT_HEADER = "detect_header"


@dataclass
class OperationRecord:
    """操作记录"""
    
    operation_type: OperationType
    table_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result_summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "operation_type": self.operation_type.value,
            "table_name": self.table_name,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "parameters": self.parameters,
            "result_summary": self.result_summary
        }


class TableHistory:
    """表格操作历史管理"""
    
    def __init__(self, limit: int = 50):
        self.history: List[OperationRecord] = []
        self.limit = limit
        self._snapshot_cache: Dict[str, List[Any]] = {}
        self._undo_stack: List[Any] = []
        self._redo_stack: List[Any] = {}
    
    def add_operation(
        self,
        operation_type: OperationType,
        table_name: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        result_summary: str = ""
    ) -> None:
        """
        添加操作记录
        
        Args:
            operation_type: 操作类型
            table_name: 表格名称
            description: 操作描述
            parameters: 操作参数
            result_summary: 结果摘要
        """
        record = OperationRecord(
            operation_type=operation_type,
            table_name=table_name,
            description=description,
            parameters=parameters or {},
            result_summary=result_summary
        )
        self.history.append(record)
        
        if len(self.history) > self.limit:
            self.history.pop(0)
        
        self._redo_stack.clear()
    
    def save_snapshot(self, table_name: str, table_data: Any) -> None:
        """
        保存表格快照
        
        Args:
            table_name: 表格名称
            table_data: 表格数据
        """
        if table_name not in self._snapshot_cache:
            self._snapshot_cache[table_name] = []
        
        snapshot = copy.deepcopy(table_data)
        self._snapshot_cache[table_name].append({
            "timestamp": datetime.now(),
            "data": snapshot
        })
        
        if len(self._snapshot_cache[table_name]) > 10:
            self._snapshot_cache[table_name].pop(0)
    
    def get_snapshot(self, table_name: str, index: int = -1) -> Optional[Any]:
        """
        获取表格快照
        
        Args:
            table_name: 表格名称
            index: 快照索引，-1表示最新的快照
        
        Returns:
            表格快照，如果不存在则返回 None
        """
        if table_name not in self._snapshot_cache:
            return None
        
        snapshots = self._snapshot_cache[table_name]
        if not snapshots:
            return None
        
        try:
            return snapshots[index]["data"]
        except IndexError:
            return None
    
    def can_undo(self, table_name: str) -> bool:
        """
        检查是否可以撤销
        
        Args:
            table_name: 表格名称
        
        Returns:
            是否可以撤销
        """
        if table_name not in self._snapshot_cache:
            return False
        return len(self._snapshot_cache[table_name]) > 1
    
    def can_redo(self, table_name: str) -> bool:
        """
        检查是否可以重做
        
        Args:
            table_name: 表格名称
        
        Returns:
            是否可以重做
        """
        return table_name in self._redo_stack and len(self._redo_stack[table_name]) > 0
    
    def undo(self, table_name: str) -> Optional[Any]:
        """
        撤销上一次操作
        
        Args:
            table_name: 表格名称
        
        Returns:
            恢复后的表格数据，如果无法撤销则返回 None
        """
        if not self.can_undo(table_name):
            return None
        
        snapshots = self._snapshot_cache[table_name]
        
        current = snapshots.pop()
        if table_name not in self._redo_stack:
            self._redo_stack[table_name] = []
        self._redo_stack[table_name].append(current)
        
        return snapshots[-1]["data"]
    
    def redo(self, table_name: str) -> Optional[Any]:
        """
        重做上一次撤销的操作
        
        Args:
            table_name: 表格名称
        
        Returns:
            恢复后的表格数据，如果无法重做则返回 None
        """
        if not self.can_redo(table_name):
            return None
        
        redo_stack = self._redo_stack[table_name]
        snapshot = redo_stack.pop()
        
        if table_name not in self._snapshot_cache:
            self._snapshot_cache[table_name] = []
        self._snapshot_cache[table_name].append(snapshot)
        
        return snapshot["data"]
    
    def get_history(self, table_name: Optional[str] = None) -> List[OperationRecord]:
        """
        获取操作历史
        
        Args:
            table_name: 表格名称，如果为None则返回所有历史
        
        Returns:
            操作记录列表
        """
        if table_name is None:
            return self.history.copy()
        
        return [record for record in self.history if record.table_name == table_name]
    
    def clear_history(self, table_name: Optional[str] = None) -> None:
        """
        清除操作历史
        
        Args:
            table_name: 表格名称，如果为None则清除所有历史
        """
        if table_name is None:
            self.history.clear()
            self._snapshot_cache.clear()
            self._undo_stack.clear()
            self._redo_stack.clear()
        else:
            self.history = [record for record in self.history if record.table_name != table_name]
            if table_name in self._snapshot_cache:
                del self._snapshot_cache[table_name]
            if table_name in self._redo_stack:
                del self._redo_stack[table_name]
    
    def get_operation_count(self, table_name: Optional[str] = None) -> int:
        """
        获取操作数量
        
        Args:
            table_name: 表格名称
        
        Returns:
            操作数量
        """
        if table_name is None:
            return len(self.history)
        
        return sum(1 for record in self.history if record.table_name == table_name)
