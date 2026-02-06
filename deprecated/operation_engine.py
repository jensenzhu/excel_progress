import pandas as pd
from typing import Dict, List, Optional, Any
from .data_manager import DataManager
from .cell_operations import CellOperations


class OperationEngine:
    """
    操作执行引擎
    负责执行各种数据操作
    """
    
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
        self.cell_ops = CellOperations()
        self.temp_results = {}
    
    def execute_operations(self, operations: List[Dict]) -> List[Dict]:
        """
        执行操作链
        
        Args:
            operations: 操作列表
            
        Returns:
            执行结果列表
        """
        results = []
        last_result_key = None
        
        for i, op in enumerate(operations):
            try:
                op_type = op.get('type', 'unknown')
                
                if op_type in ['calculate', 'filter', 'sort', 'group']:
                    if 'source_table' not in op and 'result_key' not in op and last_result_key:
                        op['result_key'] = last_result_key
                
                if op_type == 'extract':
                    result = self._extract(op)
                elif op_type == 'calculate':
                    result = self._calculate(op)
                elif op_type == 'filter':
                    result = self._filter(op)
                elif op_type == 'sort':
                    result = self._sort(op)
                elif op_type == 'group':
                    result = self._group(op)
                elif op_type == 'insert':
                    result = self._insert(op)
                elif op_type == 'merge':
                    result = self._merge(op)
                elif op_type == 'update':
                    result = self._update(op)
                elif op_type == 'save':
                    result = self._save(op)
                else:
                    result = {'success': False, 'error': f'未知操作类型: {op_type}'}
                
                result['operation_index'] = i
                result['operation_type'] = op_type
                results.append(result)
                
                if result.get('success', True):
                    if 'result_key' in result:
                        last_result_key = result['result_key']
                else:
                    break
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'operation_index': i,
                    'operation_type': op.get('type', 'unknown')
                })
                break
        
        return results
    
    def _extract(self, op: Dict) -> Dict:
        """
        提取数据
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            source_table = op.get('source_table')
            columns = op.get('columns', [])
            rows = op.get('rows', 'all')
            
            df = self.dm.get_table(source_table)
            if df is None:
                return {'success': False, 'error': f'表格 {source_table} 不存在'}
            
            result_df = df.copy()
            
            if columns:
                if isinstance(columns, str):
                    columns = [columns]
                result_df = result_df[columns]
            
            if rows != 'all':
                if isinstance(rows, str) and ':' in rows:
                    start, end = map(int, rows.split(':'))
                    result_df = result_df.iloc[start:end]
                elif isinstance(rows, int):
                    result_df = result_df.iloc[:rows]
            
            result_key = f'temp_{len(self.temp_results)}'
            self.temp_results[result_key] = result_df
            
            return {
                'success': True,
                'result_key': result_key,
                'rows': len(result_df),
                'columns': len(result_df.columns)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate(self, op: Dict) -> Dict:
        """
        计算操作
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            operation = op.get('operation', 'sum')
            column = op.get('column')
            source_table = op.get('source_table')
            target = op.get('target', 'new_column')
            
            if source_table:
                df = self.dm.get_table(source_table)
            elif 'result_key' in op:
                df = self.temp_results[op['result_key']]
            else:
                return {'success': False, 'error': '未指定数据源'}
            
            if df is None:
                return {'success': False, 'error': '数据源不存在'}
            
            if operation == 'sum':
                result = df[column].sum()
            elif operation == 'mean':
                result = df[column].mean()
            elif operation == 'count':
                result = df[column].count()
            elif operation == 'max':
                result = df[column].max()
            elif operation == 'min':
                result = df[column].min()
            elif operation == 'median':
                result = df[column].median()
            elif operation == 'std':
                result = df[column].std()
            elif operation == 'var':
                result = df[column].var()
            else:
                return {'success': False, 'error': f'未知计算类型: {operation}'}
            
            if target == 'new_column':
                result_key = f'temp_{len(self.temp_results)}'
                self.temp_results[result_key] = pd.DataFrame({target: [result]})
                return {
                    'success': True,
                    'result_key': result_key,
                    'value': result,
                    'operation': operation
                }
            else:
                return {
                    'success': True,
                    'value': result,
                    'operation': operation
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _filter(self, op: Dict) -> Dict:
        """
        筛选数据
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            source_table = op.get('source_table')
            condition = op.get('condition', '')
            
            if source_table:
                df = self.dm.get_table(source_table)
            elif 'result_key' in op:
                df = self.temp_results[op['result_key']]
            else:
                return {'success': False, 'error': '未指定数据源'}
            
            if df is None:
                return {'success': False, 'error': '数据源不存在'}
            
            filtered_df = df.query(condition)
            
            result_key = f'temp_{len(self.temp_results)}'
            self.temp_results[result_key] = filtered_df
            
            return {
                'success': True,
                'result_key': result_key,
                'rows': len(filtered_df)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sort(self, op: Dict) -> Dict:
        """
        排序数据
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            source_table = op.get('source_table')
            column = op.get('column')
            order = op.get('order', 'asc')
            
            if source_table:
                df = self.dm.get_table(source_table)
            elif 'result_key' in op:
                df = self.temp_results[op['result_key']]
            else:
                return {'success': False, 'error': '未指定数据源'}
            
            if df is None:
                return {'success': False, 'error': '数据源不存在'}
            
            ascending = order.lower() == 'asc'
            sorted_df = df.sort_values(by=column, ascending=ascending)
            
            result_key = f'temp_{len(self.temp_results)}'
            self.temp_results[result_key] = sorted_df
            
            return {
                'success': True,
                'result_key': result_key,
                'rows': len(sorted_df)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _group(self, op: Dict) -> Dict:
        """
        分组操作
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            source_table = op.get('source_table')
            column = op.get('column')
            agg_func = op.get('agg_func', 'sum')
            
            if source_table:
                df = self.dm.get_table(source_table)
            elif 'result_key' in op:
                df = self.temp_results[op['result_key']]
            else:
                return {'success': False, 'error': '未指定数据源'}
            
            if df is None:
                return {'success': False, 'error': '数据源不存在'}
            
            grouped_df = df.groupby(column).agg(agg_func).reset_index()
            
            result_key = f'temp_{len(self.temp_results)}'
            self.temp_results[result_key] = grouped_df
            
            return {
                'success': True,
                'result_key': result_key,
                'rows': len(grouped_df)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _insert(self, op: Dict) -> Dict:
        """
        插入数据
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            target_table = op.get('target_table')
            data_source = op.get('data')
            target_cell = op.get('target_cell')
            target_column = op.get('target_column')
            
            df = self.dm.get_table(target_table)
            if df is None:
                return {'success': False, 'error': f'表格 {target_table} 不存在'}
            
            if isinstance(data_source, str) and data_source in self.temp_results:
                data = self.temp_results[data_source]
            elif isinstance(data_source, (int, float, str)):
                data = data_source
            else:
                return {'success': False, 'error': '无效的数据源'}
            
            if target_cell:
                row, col = self.cell_ops.parse_cell_reference(target_cell)
                if row is not None and col is not None:
                    if self.cell_ops.validate_cell_position(row, col, len(df), len(df.columns)):
                        if isinstance(data, pd.DataFrame):
                            if len(data) == 1 and len(data.columns) == 1:
                                df.iloc[row, col] = data.iloc[0, 0]
                            else:
                                return {'success': False, 'error': '单元格只能插入单个值'}
                        else:
                            df.iloc[row, col] = data
                        self.dm._update_table_metadata(target_table)
                        return {'success': True, 'message': f'已插入到 {target_cell}'}
            
            elif target_column:
                if isinstance(data, pd.DataFrame):
                    if len(data.columns) == 1:
                        df[target_column] = data.iloc[:, 0].values
                    else:
                        return {'success': False, 'error': '只能插入单列数据'}
                else:
                    df[target_column] = data
                self.dm._update_table_metadata(target_table)
                return {'success': True, 'message': f'已插入到列 {target_column}'}
            
            return {'success': False, 'error': '未指定插入位置'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _merge(self, op: Dict) -> Dict:
        """
        合并表格
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            tables = op.get('tables', [])
            key = op.get('key', '')
            how = op.get('how', 'inner')
            
            if len(tables) < 2:
                return {'success': False, 'error': '至少需要两个表格进行合并'}
            
            dfs = []
            for table_name in tables:
                df = self.dm.get_table(table_name)
                if df is None:
                    return {'success': False, 'error': f'表格 {table_name} 不存在'}
                dfs.append(df)
            
            merged_df = dfs[0]
            for i in range(1, len(dfs)):
                merged_df = pd.merge(merged_df, dfs[i], on=key, how=how)
            
            result_key = f'temp_{len(self.temp_results)}'
            self.temp_results[result_key] = merged_df
            
            return {
                'success': True,
                'result_key': result_key,
                'rows': len(merged_df),
                'columns': len(merged_df.columns)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _update(self, op: Dict) -> Dict:
        """
        更新数据
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            target_table = op.get('target_table')
            source_table = op.get('source_table')
            key = op.get('key', '')
            update_column = op.get('update_column', '')
            
            target_df = self.dm.get_table(target_table)
            source_df = self.dm.get_table(source_table)
            
            if target_df is None:
                return {'success': False, 'error': f'表格 {target_table} 不存在'}
            if source_df is None:
                return {'success': False, 'error': f'表格 {source_table} 不存在'}
            
            if key not in target_df.columns or key not in source_df.columns:
                return {'success': False, 'error': f'键列 {key} 不存在'}
            
            if update_column not in source_df.columns:
                return {'success': False, 'error': f'更新列 {update_column} 不存在'}
            
            for idx, row in source_df.iterrows():
                key_value = row[key]
                update_value = row[update_column]
                
                mask = target_df[key] == key_value
                if mask.any():
                    if update_column in target_df.columns:
                        target_df.loc[mask, update_column] = update_value
                    else:
                        target_df[update_column] = None
                        target_df.loc[mask, update_column] = update_value
            
            self.dm._update_table_metadata(target_table)
            
            return {
                'success': True,
                'message': f'已更新 {target_table} 的 {update_column} 列'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save(self, op: Dict) -> Dict:
        """
        保存表格
        
        Args:
            op: 操作参数
            
        Returns:
            执行结果
        """
        try:
            source_table = op.get('source_table')
            output_path = op.get('output_path', '')
            
            if not output_path:
                return {'success': False, 'error': '未指定输出路径'}
            
            if source_table:
                df = self.dm.get_table(source_table)
            elif 'result_key' in op:
                df = self.temp_results[op['result_key']]
            else:
                return {'success': False, 'error': '未指定数据源'}
            
            if df is None:
                return {'success': False, 'error': '数据源不存在'}
            
            success = self.dm.save_table(source_table, output_path)
            
            if success:
                return {'success': True, 'message': f'已保存到 {output_path}'}
            else:
                return {'success': False, 'error': '保存失败'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_temp_result(self, result_key: str) -> Optional[pd.DataFrame]:
        """
        获取临时结果
        
        Args:
            result_key: 结果键
            
        Returns:
            DataFrame对象
        """
        return self.temp_results.get(result_key)
    
    def clear_temp_results(self):
        """
        清除临时结果
        """
        self.temp_results.clear()