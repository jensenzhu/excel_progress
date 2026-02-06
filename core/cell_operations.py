import re
from typing import Optional, Tuple, List


class CellOperations:
    
    @staticmethod
    def parse_cell_reference(cell_ref: str) -> Optional[Tuple[int, int]]:
        """
        解析Excel单元格引用，转换为行列索引
        
        Args:
            cell_ref: Excel单元格引用，如 "A5", "B10", "Z100"
            
        Returns:
            (row, col) 元组，行列从0开始索引
            如果解析失败返回None
        """
        if not cell_ref:
            return None
            
        match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
        if not match:
            return None
            
        col_str, row_str = match.groups()
        
        col = 0
        for i, c in enumerate(reversed(col_str)):
            col += (ord(c) - ord('A') + 1) * (26 ** i)
        col -= 1
        
        row = int(row_str) - 1
        
        return (row, col)
    
    @staticmethod
    def parse_range(range_ref: str) -> Optional[Tuple[int, int, int, int]]:
        """
        解析Excel范围引用，转换为起始和结束行列索引
        
        Args:
            range_ref: Excel范围引用，如 "A5:C10", "A1:B2"
            
        Returns:
            (start_row, start_col, end_row, end_col) 元组
            如果解析失败返回None
        """
        if not range_ref or ':' not in range_ref:
            return None
            
        parts = range_ref.split(':')
        if len(parts) != 2:
            return None
            
        start = CellOperations.parse_cell_reference(parts[0])
        end = CellOperations.parse_cell_reference(parts[1])
        
        if not start or not end:
            return None
            
        return (start[0], start[1], end[0], end[1])
    
    @staticmethod
    def cell_to_excel(row: int, col: int) -> str:
        """
        将行列索引转换为Excel单元格引用
        
        Args:
            row: 行索引（从0开始）
            col: 列索引（从0开始）
            
        Returns:
            Excel单元格引用，如 "A5", "B10"
        """
        col_str = ""
        temp_col = col + 1
        
        while temp_col > 0:
            temp_col -= 1
            col_str = chr(ord('A') + (temp_col % 26)) + col_str
            temp_col = temp_col // 26
        
        return f"{col_str}{row + 1}"
    
    @staticmethod
    def range_to_excel(start_row: int, start_col: int, end_row: int, end_col: int) -> str:
        """
        将行列范围转换为Excel范围引用
        
        Args:
            start_row: 起始行索引（从0开始）
            start_col: 起始列索引（从0开始）
            end_row: 结束行索引（从0开始）
            end_col: 结束列索引（从0开始）
            
        Returns:
            Excel范围引用，如 "A5:C10"
        """
        start_cell = CellOperations.cell_to_excel(start_row, start_col)
        end_cell = CellOperations.cell_to_excel(end_row, end_col)
        return f"{start_cell}:{end_cell}"
    
    @staticmethod
    def parse_column_reference(col_ref: str) -> Optional[int]:
        """
        解析Excel列引用，转换为列索引
        
        Args:
            col_ref: Excel列引用，如 "A", "B", "Z", "AA"
            
        Returns:
            列索引（从0开始），如果解析失败返回None
        """
        if not col_ref:
            return None
            
        match = re.match(r'^([A-Z]+)$', col_ref.upper())
        if not match:
            return None
            
        col_str = match.group(1)
        col = 0
        for i, c in enumerate(reversed(col_str)):
            col += (ord(c) - ord('A') + 1) * (26 ** i)
        col -= 1
        
        return col
    
    @staticmethod
    def column_to_excel(col: int) -> str:
        """
        将列索引转换为Excel列引用
        
        Args:
            col: 列索引（从0开始）
            
        Returns:
            Excel列引用，如 "A", "B", "AA"
        """
        col_str = ""
        temp_col = col + 1
        
        while temp_col > 0:
            temp_col -= 1
            col_str = chr(ord('A') + (temp_col % 26)) + col_str
            temp_col = temp_col // 26
        
        return col_str
    
    @staticmethod
    def validate_cell_position(row: int, col: int, max_rows: int, max_cols: int) -> bool:
        """
        验证单元格位置是否有效
        
        Args:
            row: 行索引
            col: 列索引
            max_rows: 最大行数
            max_cols: 最大列数
            
        Returns:
            如果位置有效返回True，否则返回False
        """
        return 0 <= row < max_rows and 0 <= col < max_cols
    
    @staticmethod
    def validate_range(start_row: int, start_col: int, end_row: int, end_col: int, 
                      max_rows: int, max_cols: int) -> bool:
        """
        验证范围是否有效
        
        Args:
            start_row: 起始行索引
            start_col: 起始列索引
            end_row: 结束行索引
            end_col: 结束列索引
            max_rows: 最大行数
            max_cols: 最大列数
            
        Returns:
            如果范围有效返回True，否则返回False
        """
        if not (0 <= start_row < max_rows and 0 <= start_col < max_cols):
            return False
        if not (0 <= end_row < max_rows and 0 <= end_col < max_cols):
            return False
        if start_row > end_row or start_col > end_col:
            return False
        return True