from typing import List
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from core.data_manager import DataManager
from core.schemas import (
    LoadTableInput, CalculateInput, FilterInput, SortInput,
    GroupInput, ExtractInput, InsertInput, MergeInput,
    UpdateInput, SaveInput, GetTableInfoInput, ListTablesInput, FillInput,
    DetectHeaderInput, SetHeaderInput, CopyColumnInput, ColumnCalculationInput
)
from config.settings import settings
from config.logger import logger
from utils.json_helper import json_dumps, json_loads, create_success_response, create_error_response
import pandas as pd
import numpy as np


class ExcelAgent:
    """LangGraph ReAct Excel Agent"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.llm = ChatOpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL,
            model=settings.MODEL,
            temperature=settings.TEMPERATURE
        )
        self.tools = self._create_tools()
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()

    def _create_tools(self):
        """创建Excel数据处理工具"""

        @tool(args_schema=ListTablesInput)
        def list_tables() -> str:
            """列出所有已加载的Excel表格"""
            tables = self.data_manager.get_all_tables()
            return json_dumps({
                "success": True,
                "tables": tables,
                "count": len(tables)
            })

        @tool(args_schema=GetTableInfoInput)
        def get_table_info(table_name: str) -> str:
            """获取指定表格的详细信息"""
            logger.debug(f"get_table_info called for: {table_name}")
            info = self.data_manager.get_table_info(table_name)
            logger.debug(f"info from data_manager: {info}")
            if info is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {table_name} 不存在"
                })
            result = {
                "success": True,
                "table_name": table_name,
                **info
            }
            logger.debug(f"get_table_info result: {result}")
            return json_dumps(result)

        @tool(args_schema=CalculateInput)
        def calculate(operation: str, column: str, table_name: str = None) -> str:
            """对表格数据进行计算（求和、平均值、计数等）"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                })
            df = self.data_manager.get_table(table_name)
            if df is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {table_name} 不存在"
                })
            if column not in df.columns:
                return json_dumps({
                    "success": False,
                    "error": f"列 {column} 不存在"
                })
            try:
                if operation == 'sum':
                    result = float(df[column].sum())
                elif operation == 'mean':
                    result = float(df[column].mean())
                elif operation == 'count':
                    result = int(df[column].count())
                elif operation == 'max':
                    result = float(df[column].max())
                elif operation == 'min':
                    result = float(df[column].min())
                elif operation == 'median':
                    result = float(df[column].median())
                elif operation == 'std':
                    result = float(df[column].std())
                elif operation == 'var':
                    result = float(df[column].var())
                else:
                    return json_dumps({
                        "success": False,
                        "error": f"未知计算类型: {operation}"
                    })
                return json_dumps({
                    "success": True,
                    "operation": operation,
                    "column": column,
                    "table_name": table_name,
                    "result": result
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=FilterInput)
        def filter_data(condition: str, table_name: str = None) -> str:
            """根据条件筛选表格数据"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                })
            df = self.data_manager.get_table(table_name)
            if df is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {table_name} 不存在"
                })
            try:
                filtered_df = df.query(condition)
                sample_data = []
                for record in filtered_df.head(5).to_dict('records'):
                    sample_data.append({k: (str(v) if pd.isna(v) else v) for k, v in record.items()})
                return json_dumps({
                    "success": True,
                    "condition": condition,
                    "table_name": table_name,
                    "rows": int(len(filtered_df)),
                    "sample_data": sample_data
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": f"筛选失败: {str(e)}"
                })

        @tool(args_schema=SortInput)
        def sort_data(column: str, order: str = 'asc', table_name: str = None) -> str:
            """对表格数据进行排序"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                })
            df = self.data_manager.get_table(table_name)
            if df is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {table_name} 不存在"
                })
            if column not in df.columns:
                return json_dumps({
                    "success": False,
                    "error": f"列 {column} 不存在"
                })
            try:
                ascending = order.lower() == 'asc'
                sorted_df = df.sort_values(by=column, ascending=ascending)
                self.data_manager.tables[table_name] = sorted_df
                self.data_manager._update_table_metadata(table_name)
                return json_dumps({
                    "success": True,
                    "column": column,
                    "order": order,
                    "table_name": table_name,
                    "rows": int(len(sorted_df))
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=GroupInput)
        def group_data(column: str, agg_func: str = 'sum', table_name: str = None) -> str:
            """按列分组并聚合数据"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                })
            df = self.data_manager.get_table(table_name)
            if df is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {table_name} 不存在"
                })
            if column not in df.columns:
                return json_dumps({
                    "success": False,
                    "error": f"列 {column} 不存在"
                })
            try:
                grouped_df = df.groupby(column).agg(agg_func).reset_index()
                result_key = f'grouped_{table_name}'
                self.data_manager.tables[result_key] = grouped_df
                self.data_manager._update_table_metadata(result_key)
                return json_dumps({
                    "success": True,
                    "column": column,
                    "agg_func": agg_func,
                    "result_table": result_key,
                    "rows": int(len(grouped_df))
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=InsertInput)
        def insert_data(target_table: str, target_column: str = None, target_cell: str = None, value: str = None) -> str:
            """将数据插入到指定位置"""
            df = self.data_manager.get_table(target_table)
            if df is None:
                return json_dumps({
                    "success": False,
                    "error": f"表格 {target_table} 不存在"
                })
            try:
                from core.cell_operations import CellOperations
                if target_cell:
                    row, col = CellOperations.parse_cell_reference(target_cell)
                    if row is not None and col is not None:
                        df.iloc[row, col] = value
                        self.data_manager._update_table_metadata(target_table)
                        return json_dumps({
                            "success": True,
                            "message": f"已插入到 {target_table} 的 {target_cell}"
                        })
                if target_column:
                    df[target_column] = value
                    self.data_manager._update_table_metadata(target_table)
                    return json_dumps({
                        "success": True,
                        "message": f"已插入到 {target_table} 的 {target_column} 列"
                    })
                return json_dumps({
                    "success": False,
                    "error": "必须指定target_column或target_cell"
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=MergeInput)
        def merge_tables(tables: List[str], key: str, how: str = 'inner') -> str:
            """合并多个表格"""
            dfs = []
            for table_name in tables:
                df = self.data_manager.get_table(table_name)
                if df is None:
                    return json_dumps({
                        "success": False,
                        "error": f"表格 {table_name} 不存在"
                    })
                dfs.append(df)
            try:
                merged_df = dfs[0]
                for i in range(1, len(dfs)):
                    merged_df = pd.merge(merged_df, dfs[i], on=key, how=how)
                result_key = f'merged_{tables[0]}_and_{tables[1]}'
                self.data_manager.tables[result_key] = merged_df
                self.data_manager._update_table_metadata(result_key)
                return json_dumps({
                    "success": True,
                    "tables": tables,
                    "key": key,
                    "result_table": result_key,
                    "rows": int(len(merged_df)),
                    "columns": int(len(merged_df.columns))
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=UpdateInput)
        def update_data(target_table: str, source_table: str, key: str, update_column: str) -> str:
            """用源表格的数据更新目标表格"""
            target_df = self.data_manager.get_table(target_table)
            source_df = self.data_manager.get_table(source_table)
            if target_df is None or source_df is None:
                return json_dumps({
                    "success": False,
                    "error": "源表格或目标表格不存在"
                })
            try:
                for idx, row in source_df.iterrows():
                    key_value = row[key]
                    mask = target_df[key] == key_value
                    if mask.any():
                        if update_column in target_df.columns:
                            target_df.loc[mask, update_column] = row[update_column]
                        else:
                            target_df[update_column] = None
                            target_df.loc[mask, update_column] = row[update_column]
                self.data_manager._update_table_metadata(target_table)
                return json_dumps({
                    "success": True,
                    "message": f"已更新 {target_table} 的 {update_column} 列"
                })
            except Exception as e:
                return json_dumps({
                    "success": False,
                    "error": str(e)
                })

        @tool(args_schema=SaveInput)
        def save_table(table_name: str, output_path: str) -> str:
            """保存表格到Excel文件"""
            logger.debug(f"save_table tool called: table_name={table_name}, output_path={output_path}")
            success = self.data_manager.save_table(table_name, output_path)
            logger.debug(f"save_table result: success={success}")
            if success:
                from pathlib import Path
                filename = Path(output_path).name
                return json_dumps({
                    "success": True,
                    "message": f"已保存到 {output_path}",
                    "filename": filename
                })
            else:
                return json_dumps({
                    "success": False,
                    "error": "保存失败"
                })

        @tool(args_schema=FillInput)
        def fill_na(target_column: str, source_column: str = None, value: str = None, table_name: str = None) -> str:
            """填充目标列中的空值，可以使用源列的值或固定值"""
            import traceback
            import sys
            
            try:
                logger.debug(f"fill_na called with: target_column={target_column}, source_column={source_column}, value={value}, table_name={table_name}")
                
                if table_name is None:
                    table_name = self.data_manager.active_table
                if table_name is None:
                    return json_dumps({
                        "success": False,
                        "error": "未指定表格且没有激活的表格"
                    }, ensure_ascii=False)
                df = self.data_manager.get_table(table_name)
                if df is None:
                    return json_dumps({
                        "success": False,
                        "error": f"表格 {table_name} 不存在"
                    }, ensure_ascii=False)
                if target_column not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"目标列 {target_column} 不存在"
                    }, ensure_ascii=False)
                if source_column and source_column not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"源列 {source_column} 不存在"
                    }, ensure_ascii=False)
                
                df_copy = df.copy()
                
                if source_column:
                    logger.debug(f"target_column sample values: {df_copy[target_column].head(10).tolist()}")
                    logger.debug(f"target_column dtype: {df_copy[target_column].dtype}")
                    logger.debug(f"target_column value counts: {df_copy[target_column].value_counts().head()}")
                    
                    null_mask = df_copy[target_column].isnull()
                    null_count_before = int(null_mask.sum())
                    logger.debug(f"null_count_before: {null_count_before}")
                    if null_count_before > 0:
                        logger.debug(f"null row indices: {df_copy[null_mask].index.tolist()[:10]}")
                        logger.debug(f"null values sample: {df_copy.loc[null_mask, [source_column, target_column]].head(5).to_dict('records')}")
                    
                    if null_count_before > 0:
                        df_copy.loc[null_mask, target_column] = df_copy.loc[null_mask, source_column]
                        filled_count = null_count_before - int(df_copy[target_column].isnull().sum())
                    else:
                        filled_count = 0
                    
                    self.data_manager.tables[table_name] = df_copy
                    self.data_manager._update_table_metadata(table_name)
                    result = {
                        "success": True,
                        "target_column": str(target_column),
                        "source_column": str(source_column),
                        "table_name": str(table_name),
                        "null_count_before": int(null_count_before),
                        "filled_count": int(filled_count),
                        "message": f"已用 {source_column} 列的值填充 {target_column} 列的 {filled_count} 个空值"
                    }
                elif value is not None:
                    null_mask = df_copy[target_column].isna() | (df_copy[target_column].astype(str).str.strip() == "")
                    null_count_before = int(null_mask.sum())
                    
                    df_copy.loc[null_mask, target_column] = value
                    filled_count = null_count_before - int((df_copy[target_column].isna() | (df_copy[target_column].astype(str).str.strip() == "")).sum())
                    
                    self.data_manager.tables[table_name] = df_copy
                    self.data_manager._update_table_metadata(table_name)
                    result = {
                        "success": True,
                        "target_column": str(target_column),
                        "value": str(value),
                        "table_name": str(table_name),
                        "null_count_before": int(null_count_before),
                        "filled_count": int(filled_count),
                        "message": f"已用固定值 '{value}' 填充 {target_column} 列的 {filled_count} 个空值"
                    }
                else:
                    result = {
                        "success": False,
                        "error": "必须指定 source_column 或 value 参数"
                    }
                
                logger.debug(f"result before json.dumps: {result}")
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"json_str: {json_str}")
                return json_str
            except Exception as e:
                traceback.print_exc()
                result = {
                    "success": False,
                    "error": str(e)
                }
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"exception json_str: {json_str}")
                return json_str

        @tool(args_schema=CopyColumnInput)
        def copy_column(target_column: str, source_column: str, table_name: str = None) -> str:
            """将源列的数据复制到目标列（覆盖操作）"""
            import traceback
            
            try:
                logger.debug(f"copy_column called with: target_column={target_column}, source_column={source_column}, table_name={table_name}")
                
                if table_name is None:
                    table_name = self.data_manager.active_table
                if table_name is None:
                    return json_dumps({
                        "success": False,
                        "error": "未指定表格且没有激活的表格"
                    }, ensure_ascii=False)
                df = self.data_manager.get_table(table_name)
                if df is None:
                    return json_dumps({
                        "success": False,
                        "error": f"表格 {table_name} 不存在"
                    }, ensure_ascii=False)
                if source_column not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"源列 {source_column} 不存在"
                    }, ensure_ascii=False)
                if target_column not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"目标列 {target_column} 不存在"
                    }, ensure_ascii=False)
                
                df_copy = df.copy()
                df_copy[target_column] = df_copy[source_column]
                self.data_manager.tables[table_name] = df_copy
                self.data_manager._update_table_metadata(table_name)
                
                result = {
                    "success": True,
                    "target_column": str(target_column),
                    "source_column": str(source_column),
                    "table_name": str(table_name),
                    "rows_updated": int(len(df)),
                    "message": f"已将 {source_column} 列的数据复制到 {target_column} 列"
                }
                
                logger.debug(f"copy_column result: {result}")
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"copy_column json_str: {json_str}")
                return json_str
            except Exception as e:
                traceback.print_exc()
                result = {
                    "success": False,
                    "error": str(e)
                }
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"copy_column exception json_str: {json_str}")
                return json_str

        @tool(args_schema=ColumnCalculationInput)
        def column_calculation(operation: str, column1: str, column2: str, target_column: str, table_name: str = None) -> str:
            """对两列数据进行算术运算（加、减、乘、除）"""
            import traceback
            
            try:
                if table_name is None:
                    table_name = self.data_manager.active_table
                if table_name is None:
                    return json_dumps({
                        "success": False,
                        "error": "未指定表格且没有激活的表格"
                    }, ensure_ascii=False)
                df = self.data_manager.get_table(table_name)
                if df is None:
                    return json_dumps({
                        "success": False,
                        "error": f"表格 {table_name} 不存在"
                    }, ensure_ascii=False)
                if column1 not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"列 {column1} 不存在"
                    }, ensure_ascii=False)
                if column2 not in df.columns:
                    return json_dumps({
                        "success": False,
                        "error": f"列 {column2} 不存在"
                    }, ensure_ascii=False)
                
                df_copy = df.copy()
                
                col1_data = pd.to_numeric(df_copy[column1], errors='coerce')
                col2_data = pd.to_numeric(df_copy[column2], errors='coerce')
                
                if operation == 'add':
                    result_data = col1_data + col2_data
                elif operation == 'subtract':
                    result_data = col1_data - col2_data
                elif operation == 'multiply':
                    result_data = col1_data * col2_data
                elif operation == 'divide':
                    result_data = col1_data / col2_data
                else:
                    return json_dumps({
                        "success": False,
                        "error": f"未知运算类型: {operation}"
                    }, ensure_ascii=False)
                
                df_copy[target_column] = result_data
                df_copy[target_column] = df_copy[target_column].astype('object')
                for col in df_copy.columns:
                    if pd.api.types.is_numeric_dtype(df_copy[col]):
                        df_copy[col] = df_copy[col].astype('object')
                
                self.data_manager.tables[table_name] = df_copy
                self.data_manager._update_table_metadata(table_name)
                
                op_names = {'add': '加', 'subtract': '减', 'multiply': '乘', 'divide': '除'}
                result = {
                    "success": True,
                    "operation": str(operation),
                    "column1": str(column1),
                    "column2": str(column2),
                    "target_column": str(target_column),
                    "table_name": str(table_name),
                    "rows_updated": int(len(df)),
                    "message": f"已将 {column1} {op_names[operation]} {column2} 的结果存入 {target_column} 列"
                }
                
                logger.debug(f"column_calculation result: {result}")
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"column_calculation json_str: {json_str}")
                return json_str
            except Exception as e:
                traceback.print_exc()
                result = {
                    "success": False,
                    "error": str(e)
                }
                json_str = json_dumps(result, ensure_ascii=False)
                logger.debug(f"column_calculation exception json_str: {json_str}")
                return json_str

        @tool(args_schema=DetectHeaderInput)
        def detect_header(table_name: str, preview_rows: int = 10) -> str:
            """检测表格的表头位置，并预览前几行数据供用户确认"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                }, ensure_ascii=False)
            
            result = self.data_manager.detect_header(table_name, preview_rows)
            return json_dumps(result, ensure_ascii=False)

        @tool(args_schema=SetHeaderInput)
        def set_header_row(table_name: str, header_row: int) -> str:
            """设置表格的表头行"""
            if table_name is None:
                table_name = self.data_manager.active_table
            if table_name is None:
                return json_dumps({
                    "success": False,
                    "error": "未指定表格且没有激活的表格"
                }, ensure_ascii=False)
            
            result = self.data_manager.set_header_row(table_name, header_row)
            return json_dumps(result, ensure_ascii=False)

        return [
            list_tables,
            get_table_info,
            detect_header,
            set_header_row,
            calculate,
            filter_data,
            sort_data,
            group_data,
            insert_data,
            merge_tables,
            update_data,
            copy_column,
            column_calculation,
            fill_na,
            save_table
        ]

    def _build_workflow(self):
        """构建ReAct Agent工作流"""
        llm_with_tools = self.llm.bind_tools(self.tools)

        def agent_node(state):
            """Agent节点：负责推理和决策"""
            messages = state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )
        workflow.add_edge("tools", "agent")
        return workflow

    def invoke(self, query: str, step_callback=None) -> dict:
        """调用Agent处理查询
        
        Args:
            query: 用户查询
            step_callback: 步骤回调函数，每次工具调用时会调用
        """
        system_prompt = self._get_system_prompt()
        messages = [
            HumanMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        tool_calls_log = []
        
        for event in self.app.stream({"messages": messages}):
            for node_name, node_output in event.items():
                if node_name == "agent":
                    new_messages = node_output.get("messages", [])
                    for msg in new_messages:
                        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                tool_info = {
                                    "name": tool_call['name'],
                                    "args": tool_call['args'],
                                    "status": "executing",
                                    "result": None,
                                    "error": None
                                }
                                tool_calls_log.append(tool_info)
                                
                                if step_callback:
                                    step_callback({
                                        "type": "tool_start",
                                        "tool": tool_info
                                    })
                
                elif node_name == "tools":
                    new_messages = node_output.get("messages", [])
                    for msg in new_messages:
                        if hasattr(msg, 'name'):
                            tool_name = msg.name
                            tool_result = msg.content
                            
                            for tool_info in tool_calls_log:
                                if tool_info["name"] == tool_name and tool_info["status"] == "executing":
                                    try:
                                        result_data = json_loads(tool_result)
                                        tool_info["result"] = result_data
                                        tool_info["status"] = "completed" if result_data.get("success") else "failed"
                                        if not result_data.get("success"):
                                            tool_info["error"] = result_data.get("error", "未知错误")
                                    except:
                                        tool_info["result"] = tool_result
                                        tool_info["status"] = "failed"
                                        tool_info["error"] = "解析结果失败"
                                    break
                            
                            if step_callback:
                                step_callback({
                                    "type": "tool_complete",
                                    "tool_name": tool_name,
                                    "result": tool_result
                                })
        
        final_result = {"messages": messages}
        for event in self.app.stream({"messages": messages}, stream_mode="values"):
            final_result = event
        
        final_message = final_result["messages"][-1]
        return {
            "response": final_message.content,
            "messages": final_result["messages"],
            "tool_calls": tool_calls_log
        }

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        tables = self.data_manager.get_all_tables()
        active_table = self.data_manager.active_table
        prompt = f"""你是一个专业的Excel数据处理助手，可以帮助用户处理Excel文件。

当前已加载的表格：{', '.join(tables) if tables else '无'}
当前激活表格：{active_table if active_table else '无'}

可用工具：
1. list_tables: 列出所有已加载的表格
2. get_table_info: 获取表格详细信息（列名、数据类型、行数等）
3. detect_header: 检测表格的表头位置，并预览前几行数据供用户确认
4. set_header_row: 设置表格的表头行（指定哪一行是表头）
5. calculate: 对数据进行计算（sum求和、mean平均值、count计数、max最大值、min最小值、median中位数、std标准差、var方差）
6. filter_data: 根据条件筛选数据（使用pandas查询语法）
7. sort_data: 对数据进行排序
8. group_data: 按列分组并聚合
9. insert_data: 将数据插入到指定位置
10. merge_tables: 合并多个表格
11. update_data: 用源表格的数据更新目标表格
12. copy_column: 将源列的数据复制到目标列（覆盖操作，无论是否有空值）
13. column_calculation: 对两列数据进行算术运算（加、减、乘、除）
14. fill_na: 填充目标列中的空值，可以使用源列的值或固定值
15. save_table: 保存表格到文件

工作流程：
1. 理解用户的自然语言查询
2. 如果用户问"XX部有多少人"或"统计XX人数"，先使用filter_data筛选部门，再使用calculate计数
3. 如果用户问"计算XX的平均值"或"XX的总和"，直接使用calculate
4. 如果用户问"查看XX部的员工"，只使用filter_data筛选
5. 如果用户说"将XX列复制到YY列"、"用XX列填充YY列"、"把XX列的内容放到YY列"，使用copy_column工具（覆盖操作）
6. 如果用户说"XX列加YY列"、"XX列减YY列"、"XX乘YY"、"XX除YY"、"计算XX减YY的结果"，使用column_calculation工具
7. 如果用户问"如果XX列是空的，就用YY列填充"或"将XX列的空值填充为YY"，使用fill_na工具
8. 如果用户提到表头、列名不正确或第一行不是表头，使用detect_header检测表头，然后使用set_header_row设置表头
9. 如果需要，先使用list_tables和get_table_info了解数据结构
10. 根据用户需求选择合适的工具并执行
11. 清晰地向用户报告操作结果

注意事项：
- 在执行操作前，确保表格已加载
- 检查列名是否正确
- 如果列名显示为 "Unnamed: X"，说明表头设置不正确，应该使用detect_header和set_header_row工具
- 筛选条件使用pandas查询语法（如 '部门 == "技术部"'）
- 字符串值需要用引号包裹
- copy_column工具会覆盖目标列的所有数据，无论是否有空值
- column_calculation工具支持两列之间的算术运算（加、减、乘、除），结果存入指定列
- fill_na工具只填充空值，不会覆盖已有数据
- 设置表头时，使用detect_header预览数据，然后让用户确认哪一行是表头
- 提供清晰的操作结果说明
- 如果操作失败，向用户说明原因"""
        return prompt

    def _extract_tool_calls(self, messages: List) -> List[dict]:
        """提取工具调用记录"""
        tool_calls = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_calls.append({
                            "name": tool_call['name'],
                            "args": tool_call['args']
                        })
        return tool_calls