import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from config.settings import settings


class TableViewer:
    """
    表格展示组件
    负责展示和管理多个表格
    """
    
    @staticmethod
    def display_table(df: pd.DataFrame, table_name: str = "", 
                     show_index: bool = False, height: int = 400,
                     editable: bool = False, key: str = None) -> Optional[pd.DataFrame]:
        """
        显示表格（支持可编辑模式）
        
        Args:
            df: DataFrame对象
            table_name: 表格名称
            show_index: 是否显示索引
            height: 表格高度
            editable: 是否可编辑
            key: 组件唯一标识
            
        Returns:
            如果是可编辑模式，返回编辑后的DataFrame；否则返回None
        """
        if df is None or len(df) == 0:
            st.info("表格为空")
            return None
        
        if editable:
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                height=height,
                key=key or f"editor_{table_name}",
                num_rows="dynamic",
                hide_index=not show_index
            )
            return edited_df
        else:
            st.dataframe(
                df,
                use_container_width=True,
                height=height,
                show_index=show_index
            )
            return None
    
    @staticmethod
    def display_table_info(table_info: Dict[str, Any]) -> None:
        """
        显示表格信息
        
        Args:
            table_info: 表格信息字典
        """
        if not table_info:
            st.info("无表格信息")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rows = table_info.get('total_rows', table_info.get('rows', 0))
            st.metric("行数", rows)
        
        with col2:
            columns = table_info.get('columns', table_info.get('column_names', []))
            column_count = len(columns) if isinstance(columns, list) else columns
            st.metric("列数", column_count)
        
        with col3:
            memory_mb = table_info.get('memory_usage', 0) / (1024 * 1024)
            st.metric("内存使用", f"{memory_mb:.2f} MB")
        
        with col4:
            missing_values = table_info.get('missing_values', {})
            total_missing = sum(missing_values.values()) if isinstance(missing_values, dict) else 0
            st.metric("缺失值", total_missing)
    
    @staticmethod
    def display_columns_info(table_info: Dict[str, Any]) -> None:
        """
        显示列信息
        
        Args:
            table_info: 表格信息字典
        """
        if not table_info:
            return
        
        column_names = table_info.get('columns', table_info.get('column_names', []))
        column_types = table_info.get('data_types', table_info.get('column_types', {}))
        missing_values = table_info.get('missing_values', {})
        
        if not column_names:
            st.info("无列信息")
            return
        
        cols_data = []
        for col in column_names:
            cols_data.append({
                '列名': col,
                '数据类型': column_types.get(col, 'unknown'),
                '缺失值': missing_values.get(col, 0)
            })
        
        cols_df = pd.DataFrame(cols_data)
        st.dataframe(cols_df, use_container_width=True, hide_index=True)
    
    @staticmethod
    def display_table_tabs(tables: Dict[str, pd.DataFrame], 
                          active_table: Optional[str] = None) -> str:
        """
        显示多表标签页
        
        Args:
            tables: 表格字典 {table_name: DataFrame}
            active_table: 当前激活的表格
            
        Returns:
            当前选中的表格名称
        """
        if not tables:
            st.info("暂无表格，请上传Excel文件")
            return ""
        
        table_names = list(tables.keys())
        
        if active_table and active_table in table_names:
            default_index = table_names.index(active_table)
        else:
            default_index = 0
        
        selected_table = st.tabs(table_names)[default_index]
        
        return table_names[default_index]
    
    @staticmethod
    def display_side_by_side(tables: Dict[str, pd.DataFrame], 
                             table_names: List[str]) -> None:
        """
        并排显示多个表格
        
        Args:
            tables: 表格字典
            table_names: 要显示的表格名称列表
        """
        if not table_names:
            st.info("请选择要对比的表格")
            return
        
        cols = st.columns(len(table_names))
        
        for i, table_name in enumerate(table_names):
            with cols[i]:
                st.subheader(table_name)
                if table_name in tables:
                    TableViewer.display_table(tables[table_name])
                else:
                    st.error(f"表格 {table_name} 不存在")
    
    @staticmethod
    def display_selected_rows(df: pd.DataFrame, selected_rows: List[int]) -> None:
        """
        显示选中的行
        
        Args:
            df: DataFrame对象
            selected_rows: 选中的行索引列表
        """
        if not selected_rows:
            st.info("未选择任何行")
            return
        
        selected_df = df.iloc[selected_rows]
        st.dataframe(selected_df, use_container_width=True)
    
    @staticmethod
    def display_selected_columns(df: pd.DataFrame, selected_columns: List[str]) -> None:
        """
        显示选中的列
        
        Args:
            df: DataFrame对象
            selected_columns: 选中的列名列表
        """
        if not selected_columns:
            st.info("未选择任何列")
            return
        
        selected_df = df[selected_columns]
        st.dataframe(selected_df, use_container_width=True)
    
    @staticmethod
    def display_cell_highlight(df: pd.DataFrame, cell_ref: str) -> None:
        """
        高亮显示单元格
        
        Args:
            df: DataFrame对象
            cell_ref: 单元格引用
        """
        from core.cell_operations import CellOperations
        
        parsed = CellOperations.parse_cell_reference(cell_ref)
        if parsed is None:
            st.error(f"无效的单元格引用: {cell_ref}")
            return
        
        row, col = parsed
        
        if not (0 <= row < len(df) and 0 <= col < len(df.columns)):
            st.error(f"单元格 {cell_ref} 超出范围")
            return
        
        st.info(f"单元格 {cell_ref} 的值: {df.iloc[row, col]}")
    
    @staticmethod
    def display_range_highlight(df: pd.DataFrame, range_ref: str) -> None:
        """
        高亮显示范围
        
        Args:
            df: DataFrame对象
            range_ref: 范围引用
        """
        from core.cell_operations import CellOperations
        
        parsed = CellOperations.parse_range(range_ref)
        if parsed is None:
            st.error(f"无效的范围引用: {range_ref}")
            return
        
        start_row, start_col, end_row, end_col = parsed
        
        if not (0 <= start_row < len(df) and 0 <= start_col < len(df.columns) and
                0 <= end_row < len(df) and 0 <= end_col < len(df.columns)):
            st.error(f"范围 {range_ref} 超出范围")
            return
        
        range_df = df.iloc[start_row:end_row+1, start_col:end_col+1]
        st.dataframe(range_df, use_container_width=True)
    
    @staticmethod
    def select_table(tables: Dict[str, pd.DataFrame], 
                    label: str = "选择表格") -> Optional[str]:
        """
        选择表格
        
        Args:
            tables: 表格字典
            label: 选择器标签
            
        Returns:
            选中的表格名称
        """
        if not tables:
            return None
        
        table_names = list(tables.keys())
        selected = st.selectbox(label, table_names)
        return selected
    
    @staticmethod
    def select_columns(df: pd.DataFrame, label: str = "选择列") -> List[str]:
        """
        选择列
        
        Args:
            df: DataFrame对象
            label: 选择器标签
            
        Returns:
            选中的列名列表
        """
        if df is None or len(df.columns) == 0:
            return []
        
        columns = df.columns.tolist()
        selected = st.multiselect(label, columns)
        return selected
    
    @staticmethod
    def select_rows(df: pd.DataFrame, label: str = "选择行") -> List[int]:
        """
        选择行
        
        Args:
            df: DataFrame对象
            label: 选择器标签
            
        Returns:
            选中的行索引列表
        """
        if df is None or len(df) == 0:
            return []
        
        row_indices = list(range(len(df)))
        selected = st.multiselect(label, row_indices)
        return selected
    
    @staticmethod
    def display_preview(df: pd.DataFrame, max_rows: int = None, 
                        max_cols: int = None) -> None:
        """
        显示表格预览
        
        Args:
            df: DataFrame对象
            max_rows: 最大显示行数
            max_cols: 最大显示列数
        """
        if df is None or len(df) == 0:
            st.info("表格为空")
            return
        
        if max_rows is None:
            max_rows = settings.TABLE_PREVIEW_ROWS
        if max_cols is None:
            max_cols = settings.TABLE_PREVIEW_COLS
        
        preview_df = df.head(max_rows)
        
        if len(df.columns) > max_cols:
            preview_df = preview_df.iloc[:, :max_cols]
            st.info(f"仅显示前 {max_cols} 列（共 {len(df.columns)} 列）")
        
        st.dataframe(preview_df, use_container_width=True)
        
        if len(df) > max_rows:
            st.info(f"仅显示前 {max_rows} 行（共 {len(df)} 行）")