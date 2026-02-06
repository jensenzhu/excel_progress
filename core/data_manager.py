import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from .cell_operations import CellOperations
from .table_metadata import TableMetadata
from .table_history import TableHistory, OperationType
from .exceptions import (
    TableNotFoundError, ColumnNotFoundError, CellReferenceError,
    FileLoadError, FileSaveError, HeaderError, UndoRedoError
)
from config.logger import logger


class DataManager:
    """
    多表数据管理器
    负责加载、保存、管理多个Excel表格
    """
    
    def __init__(self):
        self.tables: Dict[str, pd.DataFrame] = {}
        self.table_metadata: Dict[str, TableMetadata] = {}
        self.active_table: Optional[str] = None
        self.history = TableHistory(limit=50)
        self.cell_ops = CellOperations()
        self.last_saved_filename: Optional[str] = None
    
    def load_table(self, file_path: str, table_name: Optional[str] = None, 
                   sheet_name: Optional[str] = None) -> bool:
        """
        加载Excel文件
        
        Args:
            file_path: Excel文件路径
            table_name: 表格名称，如果为None则使用文件名
            sheet_name: 工作表名称，如果为None则加载第一个工作表
            
        Returns:
            加载成功返回True，否则返回False
        """
        try:
            if table_name is None:
                table_name = Path(file_path).stem
            
            if sheet_name is None:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            self.tables[table_name] = df
            self._update_table_metadata(table_name, file_path, sheet_name or "Sheet1")
            
            if self.active_table is None:
                self.active_table = table_name
            
            self.history.save_snapshot(table_name, df)
            
            self.history.add_operation(
                operation_type=OperationType.LOAD,
                table_name=table_name,
                description=f"加载表格: {file_path}",
                parameters={"file_path": file_path, "sheet_name": sheet_name}
            )
            
            return True
        except FileLoadError:
            raise
        except Exception as e:
            logger.error(f"加载表格失败: {e}")
            return False
    
    def save_table(self, table_name: str, output_path: str) -> bool:
        """
        保存表格到Excel文件
        
        Args:
            table_name: 表格名称
            output_path: 输出文件路径
            
        Returns:
            保存成功返回True，否则返回False
        """
        try:
            if table_name not in self.tables:
                return False
            
            self.tables[table_name].to_excel(output_path, index=False)
            filename = Path(output_path).name
            self.last_saved_filename = filename
            
            if table_name in self.table_metadata:
                self.table_metadata[table_name].update_modified_time()
            
            self.save_snapshot(table_name)
            
            self.history.add_operation(
                operation_type=OperationType.SAVE,
                table_name=table_name,
                description=f"保存表格到: {output_path}",
                parameters={"output_path": output_path}
            )
            
            return True
        except Exception as e:
            logger.error(f"保存表格失败: {e}")
            return False
    
    def export_table_to_bytes(self, table_name: str, filename: str) -> Optional[bytes]:
        """
        导出表格为Excel文件的字节内容
        
        Args:
            table_name: 表格名称
            filename: 文件名
            
        Returns:
            Excel文件的字节内容
        """
        try:
            if table_name not in self.tables:
                return None
            
            from io import BytesIO
            buffer = BytesIO()
            self.tables[table_name].to_excel(buffer, index=False)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"导出表格失败: {e}")
            return None
    
    def get_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        获取指定表格
        
        Args:
            table_name: 表格名称
            
        Returns:
            DataFrame对象，如果表格不存在返回None
        """
        return self.tables.get(table_name)
    
    def get_active_table(self) -> Optional[pd.DataFrame]:
        """
        获取当前激活的表格
        
        Returns:
            DataFrame对象，如果没有激活的表格返回None
        """
        if self.active_table and isinstance(self.active_table, str):
            return self.tables.get(self.active_table)
        return None
    
    def set_active_table(self, table_name: str) -> bool:
        """
        设置激活的表格
        
        Args:
            table_name: 表格名称
            
        Returns:
            设置成功返回True，否则返回False
        """
        if table_name and isinstance(table_name, str) and table_name in self.tables:
            self.active_table = table_name
            return True
        return False
    
    def get_cell_value(self, table_name: str, cell_ref: str) -> Optional[Any]:
        """
        获取单元格值
        
        Args:
            table_name: 表格名称
            cell_ref: 单元格引用，如 "A5"
            
        Returns:
            单元格值，如果获取失败返回None
        """
        try:
            if table_name not in self.tables:
                return None
            
            df = self.tables[table_name]
            row, col = self.cell_ops.parse_cell_reference(cell_ref)
            
            if row is None or col is None:
                return None
            
            if not self.cell_ops.validate_cell_position(row, col, len(df), len(df.columns)):
                return None
            
            return df.iloc[row, col]
        except Exception as e:
            logger.error(f"获取单元格值失败: {e}")
            return None
    
    def set_cell_value(self, table_name: str, cell_ref: str, value: Any) -> bool:
        """
        设置单元格值
        
        Args:
            table_name: 表格名称
            cell_ref: 单元格引用，如 "A5"
            value: 要设置的值
            
        Returns:
            设置成功返回True，否则返回False
        """
        try:
            if table_name not in self.tables:
                return False
            
            df = self.tables[table_name]
            row, col = self.cell_ops.parse_cell_reference(cell_ref)
            
            if row is None or col is None:
                return False
            
            if not self.cell_ops.validate_cell_position(row, col, len(df), len(df.columns)):
                return False
            
            df.iloc[row, col] = value
            self.save_snapshot(table_name)
            self._update_table_metadata(table_name)
            return True
        except Exception as e:
            logger.error(f"设置单元格值失败: {e}")
            return False
    
    def get_range_values(self, table_name: str, range_ref: str) -> Optional[pd.DataFrame]:
        """
        获取范围内的值
        
        Args:
            table_name: 表格名称
            range_ref: 范围引用，如 "A5:C10"
            
        Returns:
            DataFrame对象，如果获取失败返回None
        """
        try:
            if table_name not in self.tables:
                return None
            
            df = self.tables[table_name]
            range_info = self.cell_ops.parse_range(range_ref)
            
            if range_info is None:
                return None
            
            start_row, start_col, end_row, end_col = range_info
            
            if not self.cell_ops.validate_range(start_row, start_col, end_row, end_col, 
                                                 len(df), len(df.columns)):
                return None
            
            return df.iloc[start_row:end_row+1, start_col:end_col+1]
        except Exception as e:
            logger.error(f"获取范围值失败: {e}")
            return None
    
    def set_range_values(self, table_name: str, range_ref: str, values: pd.DataFrame) -> bool:
        """
        设置范围内的值
        
        Args:
            table_name: 表格名称
            range_ref: 范围引用，如 "A5:C10"
            values: 要设置的值（DataFrame）
            
        Returns:
            设置成功返回True，否则返回False
        """
        try:
            if table_name not in self.tables:
                return False
            
            df = self.tables[table_name]
            range_info = self.cell_ops.parse_range(range_ref)
            
            if range_info is None:
                return False
            
            start_row, start_col, end_row, end_col = range_info
            
            if not self.cell_ops.validate_range(start_row, start_col, end_row, end_col, 
                                                 len(df), len(df.columns)):
                return False
            
            df.iloc[start_row:end_row+1, start_col:end_col+1] = values.values
            self._update_table_metadata(table_name)
            return True
        except Exception as e:
            logger.error(f"设置范围值失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """
        获取表格信息
        
        Args:
            table_name: 表格名称
            
        Returns:
            包含表格信息的字典
        """
        if table_name not in self.tables:
            return None
        
        metadata = self.table_metadata.get(table_name)
        if metadata:
            info = metadata.to_dict()
            df = self.tables[table_name]
            info["missing_values"] = df.isnull().sum().to_dict()
            info["memory_usage"] = int(df.memory_usage(deep=True).sum())
            return info
        return None
    
    def get_all_tables(self) -> List[str]:
        """
        获取所有表格名称
        
        Returns:
            表格名称列表
        """
        return list(self.tables.keys())
    
    def remove_table(self, table_name: str) -> bool:
        """
        移除表格
        
        Args:
            table_name: 表格名称
            
        Returns:
            移除成功返回True，否则返回False
        """
        if table_name in self.tables:
            del self.tables[table_name]
            if table_name in self.table_metadata:
                del self.table_metadata[table_name]
            
            if self.active_table == table_name:
                self.active_table = list(self.tables.keys())[0] if self.tables else None
            
            return True
        return False
    
    def add_operation_to_history(self, operation: Dict):
        """
        添加操作到历史记录（已弃用，请使用 history.add_operation）
        
        Args:
            operation: 操作信息字典
        """
        logger.warning("add_operation_to_history 已弃用，请使用 history.add_operation")
        self.history.add_operation(
            operation_type=OperationType.GROUP,
            table_name=operation.get("table_name", "unknown"),
            description=operation.get("description", ""),
            parameters=operation.get("parameters", {})
        )
    
    def get_operation_history(self) -> List[Dict]:
        """
        获取操作历史
        
        Returns:
            操作历史列表
        """
        return [record.to_dict() for record in self.history.get_history()]
    
    def _update_table_metadata(self, table_name: str, file_path: Optional[str] = None, sheet_name: Optional[str] = None):
        """
        更新表格元数据
        
        Args:
            table_name: 表格名称
            file_path: 文件路径
            sheet_name: 工作表名称
        """
        if table_name not in self.tables:
            return
        
        df = self.tables[table_name]
        
        existing_metadata = self.table_metadata.get(table_name)
        header_row = existing_metadata.header_row if existing_metadata else 0
        
        metadata = TableMetadata(
            name=table_name,
            file_path=file_path or (existing_metadata.file_path if existing_metadata else ""),
            columns=df.columns.tolist(),
            total_rows=len(df),
            header_row=header_row,
            sheet_name=sheet_name or (existing_metadata.sheet_name if existing_metadata else "Sheet1"),
            data_types={col: str(dtype) for col, dtype in df.dtypes.items()}
        )
        
        if existing_metadata:
            metadata.created_at = existing_metadata.created_at
            metadata.file_size = existing_metadata.file_size
        
        self.table_metadata[table_name] = metadata
    
    def detect_header(self, table_name: str, preview_rows: int = 10) -> Dict:
        """
        检测表头位置并智能推断
        
        Args:
            table_name: 表格名称
            preview_rows: 预览的行数
            
        Returns:
            包含表头分析结果的字典
        """
        if table_name not in self.tables:
            return {
                'success': False,
                'error': f'表格 {table_name} 不存在'
            }
        
        df = self.tables[table_name]
        
        metadata = self.table_metadata.get(table_name)
        current_header_row = metadata.header_row if metadata else 0
        
        analysis = {
            'success': True,
            'table_name': table_name,
            'current_header_row': current_header_row,
            'current_columns': df.columns.tolist(),
            'preview': []
        }
        
        for i in range(min(preview_rows, len(df))):
            row_data = {
                'row_index': i,
                'values': [str(v) if pd.notna(v) else '' for v in df.iloc[i].tolist()]
            }
            analysis['preview'].append(row_data)
        
        return analysis
    
    def set_header_row(self, table_name: str, header_row: int) -> Dict:
        """
        设置表头行
        
        Args:
            table_name: 表格名称
            header_row: 表头所在的行索引
            
        Returns:
            操作结果字典
        """
        if table_name not in self.tables:
            return {
                'success': False,
                'error': f'表格 {table_name} 不存在'
            }
        
        df = self.tables[table_name]
        
        if header_row >= len(df):
            return {
                'success': False,
                'error': f'表头行 {header_row} 超出范围（表格只有 {len(df)} 行）'
            }
        
        try:
            new_header = df.iloc[header_row].tolist()
            
            unique_header = []
            seen = set()
            for i, col in enumerate(new_header):
                if col in seen or pd.isna(col) or col == '':
                    col = f'column_{i}'
                seen.add(col)
                unique_header.append(col)
            
            df.columns = unique_header
            
            if header_row > 0:
                df = df.iloc[header_row + 1:].reset_index(drop=True)
            
            self.tables[table_name] = df
            self._update_table_metadata(table_name)
            
            if table_name in self.table_metadata:
                self.table_metadata[table_name].header_row = header_row
            
            self.history.add_operation(
                operation_type=OperationType.SET_HEADER,
                table_name=table_name,
                description=f"设置表头行为: {header_row}",
                parameters={"header_row": header_row}
            )
            
            return {
                'success': True,
                'table_name': table_name,
                'header_row': header_row,
                'new_columns': unique_header,
                'message': f'已将第 {header_row + 1} 行设置为表头，包含 {len(unique_header)} 列'
            }
        except Exception as e:
            logger.error(f"设置表头失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def can_undo(self, table_name: Optional[str] = None) -> bool:
        """
        检查是否可以撤销
        
        Args:
            table_name: 表格名称，如果为None则使用当前激活的表格
        
        Returns:
            是否可以撤销
        """
        if table_name is None:
            table_name = self.active_table
        if table_name is None:
            return False
        return self.history.can_undo(table_name)
    
    def can_redo(self, table_name: Optional[str] = None) -> bool:
        """
        检查是否可以重做
        
        Args:
            table_name: 表格名称，如果为None则使用当前激活的表格
        
        Returns:
            是否可以重做
        """
        if table_name is None:
            table_name = self.active_table
        if table_name is None:
            return False
        return self.history.can_redo(table_name)
    
    def undo(self, table_name: Optional[str] = None) -> bool:
        """
        撤销上一次操作
        
        Args:
            table_name: 表格名称，如果为None则使用当前激活的表格
        
        Returns:
            撤销成功返回True，否则返回False
        """
        if table_name is None:
            table_name = self.active_table
        if table_name is None:
            return False
        
        if not self.can_undo(table_name):
            return False
        
        try:
            restored_data = self.history.undo(table_name)
            if restored_data is not None:
                self.tables[table_name] = restored_data
                self._update_table_metadata(table_name)
                logger.info(f"已撤销表格 {table_name} 的上一次操作")
                return True
            return False
        except Exception as e:
            logger.error(f"撤销失败: {e}")
            return False
    
    def redo(self, table_name: Optional[str] = None) -> bool:
        """
        重做上一次撤销的操作
        
        Args:
            table_name: 表格名称，如果为None则使用当前激活的表格
        
        Returns:
            重做成功返回True，否则返回False
        """
        if table_name is None:
            table_name = self.active_table
        if table_name is None:
            return False
        
        if not self.can_redo(table_name):
            return False
        
        try:
            restored_data = self.history.redo(table_name)
            if restored_data is not None:
                self.tables[table_name] = restored_data
                self._update_table_metadata(table_name)
                logger.info(f"已重做表格 {table_name} 的上一次操作")
                return True
            return False
        except Exception as e:
            logger.error(f"重做失败: {e}")
            return False
    
    def save_snapshot(self, table_name: str) -> None:
        """
        保存当前表格快照（用于撤销）
        
        Args:
            table_name: 表格名称
        """
        if table_name in self.tables:
            self.history.save_snapshot(table_name, self.tables[table_name])