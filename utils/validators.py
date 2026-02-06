import pandas as pd
from typing import Any, List, Optional, Dict, Tuple


class DataValidator:
    """
    数据验证工具
    负责验证数据的有效性
    """
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证DataFrame的有效性
        
        Args:
            df: DataFrame对象
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if df is None:
            result['is_valid'] = False
            result['errors'].append('DataFrame为None')
            return result
        
        if len(df) == 0:
            result['is_valid'] = False
            result['errors'].append('DataFrame为空')
        
        if len(df.columns) == 0:
            result['is_valid'] = False
            result['errors'].append('DataFrame没有列')
        
        missing_ratio = df.isnull().sum() / len(df)
        high_missing_cols = missing_ratio[missing_ratio > 0.5].index.tolist()
        if high_missing_cols:
            result['warnings'].append(f'以下列缺失值超过50%: {", ".join(high_missing_cols)}')
        
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            result['warnings'].append(f'发现{duplicate_rows}行重复数据')
        
        return result
    
    @staticmethod
    def validate_column(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        验证列的有效性
        
        Args:
            df: DataFrame对象
            column: 列名
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if column not in df.columns:
            result['is_valid'] = False
            result['errors'].append(f'列 {column} 不存在')
            return result
        
        missing_count = df[column].isnull().sum()
        missing_ratio = missing_count / len(df)
        
        if missing_ratio > 0.5:
            result['warnings'].append(f'列 {column} 缺失值比例为{missing_ratio:.2%}')
        
        if missing_count == len(df):
            result['is_valid'] = False
            result['errors'].append(f'列 {column} 全部为空')
        
        return result
    
    @staticmethod
    def validate_cell_value(value: Any, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """
        验证单元格值的有效性
        
        Args:
            value: 单元格值
            expected_type: 期望的类型 ('numeric', 'string', 'boolean', 'datetime')
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if pd.isna(value):
            result['warnings'].append('值为NaN')
            return result
        
        if expected_type == 'numeric':
            if not isinstance(value, (int, float)) and not pd.api.types.is_numeric_dtype(type(value)):
                result['is_valid'] = False
                result['errors'].append(f'值 {value} 不是数值类型')
        
        elif expected_type == 'string':
            if not isinstance(value, str):
                result['is_valid'] = False
                result['errors'].append(f'值 {value} 不是字符串类型')
        
        elif expected_type == 'boolean':
            if not isinstance(value, bool) and value not in [0, 1, 'True', 'False', 'true', 'false']:
                result['is_valid'] = False
                result['errors'].append(f'值 {value} 不是布尔类型')
        
        elif expected_type == 'datetime':
            if not pd.api.types.is_datetime64_any_dtype(type(value)):
                result['is_valid'] = False
                result['errors'].append(f'值 {value} 不是日期时间类型')
        
        return result
    
    @staticmethod
    def validate_operation(operation: Dict, available_tables: List[str]) -> Dict[str, Any]:
        """
        验证操作的有效性
        
        Args:
            operation: 操作字典
            available_tables: 可用的表格列表
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        op_type = operation.get('type')
        
        if not op_type:
            result['is_valid'] = False
            result['errors'].append('操作缺少type字段')
            return result
        
        valid_types = ['extract', 'calculate', 'filter', 'sort', 'group', 'insert', 'merge', 'update', 'save']
        if op_type not in valid_types:
            result['is_valid'] = False
            result['errors'].append(f'无效的操作类型: {op_type}')
        
        if op_type in ['extract', 'calculate', 'filter', 'sort', 'group', 'update']:
            source_table = operation.get('source_table')
            if source_table and source_table not in available_tables:
                result['is_valid'] = False
                result['errors'].append(f'源表格 {source_table} 不存在')
        
        if op_type in ['insert', 'update']:
            target_table = operation.get('target_table')
            if target_table and target_table not in available_tables:
                result['is_valid'] = False
                result['errors'].append(f'目标表格 {target_table} 不存在')
        
        if op_type == 'merge':
            tables = operation.get('tables', [])
            for table in tables:
                if table not in available_tables:
                    result['is_valid'] = False
                    result['errors'].append(f'表格 {table} 不存在')
        
        if op_type == 'save':
            output_path = operation.get('output_path')
            if not output_path:
                result['is_valid'] = False
                result['errors'].append('保存操作缺少输出路径')
        
        return result
    
    @staticmethod
    def validate_cell_reference(cell_ref: str, max_rows: int, max_cols: int) -> Dict[str, Any]:
        """
        验证单元格引用的有效性
        
        Args:
            cell_ref: 单元格引用
            max_rows: 最大行数
            max_cols: 最大列数
            
        Returns:
            验证结果字典
        """
        from core.cell_operations import CellOperations
        
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not cell_ref:
            result['is_valid'] = False
            result['errors'].append('单元格引用为空')
            return result
        
        parsed = CellOperations.parse_cell_reference(cell_ref)
        if parsed is None:
            result['is_valid'] = False
            result['errors'].append(f'无效的单元格引用: {cell_ref}')
            return result
        
        row, col = parsed
        
        if row < 0 or row >= max_rows:
            result['is_valid'] = False
            result['errors'].append(f'行索引 {row} 超出范围 (0-{max_rows-1})')
        
        if col < 0 or col >= max_cols:
            result['is_valid'] = False
            result['errors'].append(f'列索引 {col} 超出范围 (0-{max_cols-1})')
        
        return result
    
    @staticmethod
    def validate_range_reference(range_ref: str, max_rows: int, max_cols: int) -> Dict[str, Any]:
        """
        验证范围引用的有效性
        
        Args:
            range_ref: 范围引用
            max_rows: 最大行数
            max_cols: 最大列数
            
        Returns:
            验证结果字典
        """
        from core.cell_operations import CellOperations
        
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not range_ref:
            result['is_valid'] = False
            result['errors'].append('范围引用为空')
            return result
        
        parsed = CellOperations.parse_range(range_ref)
        if parsed is None:
            result['is_valid'] = False
            result['errors'].append(f'无效的范围引用: {range_ref}')
            return result
        
        start_row, start_col, end_row, end_col = parsed
        
        if start_row < 0 or start_row >= max_rows:
            result['is_valid'] = False
            result['errors'].append(f'起始行索引 {start_row} 超出范围 (0-{max_rows-1})')
        
        if start_col < 0 or start_col >= max_cols:
            result['is_valid'] = False
            result['errors'].append(f'起始列索引 {start_col} 超出范围 (0-{max_cols-1})')
        
        if end_row < 0 or end_row >= max_rows:
            result['is_valid'] = False
            result['errors'].append(f'结束行索引 {end_row} 超出范围 (0-{max_rows-1})')
        
        if end_col < 0 or end_col >= max_cols:
            result['is_valid'] = False
            result['errors'].append(f'结束列索引 {end_col} 超出范围 (0-{max_cols-1})')
        
        if start_row > end_row:
            result['is_valid'] = False
            result['errors'].append(f'起始行 {start_row} 大于结束行 {end_row}')
        
        if start_col > end_col:
            result['is_valid'] = False
            result['errors'].append(f'起始列 {start_col} 大于结束列 {end_col}')
        
        return result
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 200 * 1024 * 1024) -> Dict[str, Any]:
        """
        验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            max_size: 最大文件大小（字节），默认200MB
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if file_size > max_size:
            result['is_valid'] = False
            result['errors'].append(f'文件大小 {file_size / (1024*1024):.2f}MB 超过最大限制 {max_size / (1024*1024):.2f}MB')
        
        return result
    
    @staticmethod
    def validate_data_types(df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据类型
        
        Args:
            df: DataFrame对象
            
        Returns:
            验证结果字典
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'type_info': {}
        }
        
        for col in df.columns:
            dtype = df[col].dtype
            result['type_info'][col] = str(dtype)
            
            if pd.api.types.is_object_dtype(dtype):
                unique_count = df[col].nunique()
                if unique_count < len(df) * 0.5:
                    result['warnings'].append(f'列 {col} 可能是分类数据（{unique_count}个唯一值）')
        
        return result