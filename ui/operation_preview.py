import streamlit as st
from typing import List, Dict, Any, Optional
from core.nlp_parser import NLPParser


class OperationPreview:
    """
    操作预览组件
    负责显示操作预览和确认
    """
    
    @staticmethod
    def display_operations_preview(operations: List[Dict], 
                                   parser: Optional[NLPParser] = None) -> bool:
        """
        显示操作预览
        
        Args:
            operations: 操作列表
            parser: NLP解析器（用于生成摘要）
            
        Returns:
            用户是否确认执行
        """
        if not operations:
            st.info("无操作需要预览")
            return False
        
        st.subheader("📋 操作预览")
        
        if parser:
            summaries = parser.generate_operation_summary(operations)
            for i, summary in enumerate(summaries, 1):
                st.markdown(f"{i}. {summary}")
        else:
            for i, op in enumerate(operations, 1):
                op_type = op.get('type', 'unknown')
                st.markdown(f"{i}. 执行 {op_type} 操作")
        
        st.warning("⚠️ 请确认以上操作是否正确")
        
        col1, col2 = st.columns(2)
        
        with col1:
            confirm = st.button("✅ 确认执行", type="primary", key="confirm_execute")
        
        with col2:
            cancel = st.button("❌ 取消", key="cancel_execute")
        
        if confirm:
            return True
        elif cancel:
            return False
        
        return False
    
    @staticmethod
    def display_operation_details(operations: List[Dict]) -> None:
        """
        显示操作详细信息
        
        Args:
            operations: 操作列表
        """
        if not operations:
            st.info("无操作详情")
            return
        
        st.subheader("🔍 操作详情")
        
        for i, op in enumerate(operations, 1):
            with st.expander(f"操作 {i}: {op.get('type', 'unknown')}", expanded=False):
                for key, value in op.items():
                    if key != 'type':
                        st.markdown(f"**{key}**: {value}")
    
    @staticmethod
    def display_execution_plan(operations: List[Dict]) -> None:
        """
        显示执行计划
        
        Args:
            operations: 操作列表
        """
        if not operations:
            st.info("无执行计划")
            return
        
        st.subheader("📊 执行计划")
        
        steps = []
        for i, op in enumerate(operations, 1):
            op_type = op.get('type', 'unknown')
            source = op.get('source_table', '未知')
            target = op.get('target_table', '未知')
            
            step_desc = f"步骤 {i}: {op_type}"
            if source != '未知':
                step_desc += f" (源: {source})"
            if target != '未知':
                step_desc += f" (目标: {target})"
            
            steps.append(step_desc)
        
        for step in steps:
            st.markdown(f"- {step}")
    
    @staticmethod
    def display_risk_assessment(operations: List[Dict], 
                                 tables_info: Dict[str, Dict]) -> None:
        """
        显示风险评估
        
        Args:
            operations: 操作列表
            tables_info: 表格信息字典
        """
        if not operations:
            return
        
        st.subheader("⚠️ 风险评估")
        
        risks = []
        
        for op in operations:
            op_type = op.get('type', '')
            
            if op_type in ['update', 'insert']:
                target_table = op.get('target_table')
                if target_table and target_table in tables_info:
                    rows = tables_info[target_table].get('rows', 0)
                    risks.append(f"⚠️ 将修改表格 {target_table}（{rows} 行数据）")
            
            if op_type == 'save':
                output_path = op.get('output_path')
                if output_path:
                    risks.append(f"⚠️ 将保存文件到 {output_path}")
            
            if op_type == 'merge':
                tables = op.get('tables', [])
                if len(tables) > 1:
                    risks.append(f"⚠️ 将合并 {len(tables)} 个表格")
        
        if risks:
            for risk in risks:
                st.warning(risk)
        else:
            st.info("✅ 未发现明显风险")
    
    @staticmethod
    def display_expected_results(operations: List[Dict]) -> None:
        """
        显示预期结果
        
        Args:
            operations: 操作列表
        """
        if not operations:
            return
        
        st.subheader("🎯 预期结果")
        
        results = []
        
        for op in operations:
            op_type = op.get('type', '')
            
            if op_type == 'calculate':
                operation = op.get('operation', '')
                column = op.get('column', '')
                results.append(f"将计算 {column} 列的 {operation}")
            
            if op_type == 'filter':
                condition = op.get('condition', '')
                results.append(f"将筛选满足条件的数据: {condition}")
            
            if op_type == 'sort':
                column = op.get('column', '')
                order = op.get('order', '升序')
                results.append(f"将按 {column} 列{order}排序")
            
            if op_type == 'group':
                column = op.get('column', '')
                agg_func = op.get('agg_func', '求和')
                results.append(f"将按 {column} 列分组并{agg_func}")
            
            if op_type == 'insert':
                target_table = op.get('target_table', '')
                target_cell = op.get('target_cell', '')
                target_column = op.get('target_column', '')
                if target_cell:
                    results.append(f"将数据插入到 {target_table} 的 {target_cell} 单元格")
                elif target_column:
                    results.append(f"将数据插入到 {target_table} 的 {target_column} 列")
            
            if op_type == 'merge':
                tables = op.get('tables', [])
                key = op.get('key', '')
                results.append(f"将合并表格: {', '.join(tables)}，基于 {key} 列")
            
            if op_type == 'save':
                output_path = op.get('output_path', '')
                results.append(f"将保存文件到: {output_path}")
        
        if results:
            for result in results:
                st.markdown(f"- {result}")
        else:
            st.info("无预期结果")
    
    @staticmethod
    def display_execution_results(results: List[Dict[str, Any]]) -> None:
        """
        显示执行结果
        
        Args:
            results: 执行结果列表
        """
        if not results:
            st.info("无执行结果")
            return
        
        st.subheader("📊 执行结果")
        
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("总操作数", total_count)
        
        with col2:
            st.metric("成功数", success_count)
        
        with col3:
            st.metric("失败数", total_count - success_count)
        
        for i, result in enumerate(results, 1):
            with st.expander(f"操作 {i}: {result.get('operation_type', 'unknown')}", 
                            expanded=not result.get('success', True)):
                if result.get('success', False):
                    st.success("✅ 操作成功")
                    
                    if 'message' in result:
                        st.info(result['message'])
                    
                    if 'value' in result:
                        st.metric("结果", result['value'])
                    
                    if 'rows' in result:
                        st.info(f"处理了 {result['rows']} 行数据")
                    
                    if 'columns' in result:
                        st.info(f"处理了 {result['columns']} 列数据")
                else:
                    st.error("❌ 操作失败")
                    
                    if 'error' in result:
                        st.error(result['error'])
    
    @staticmethod
    def display_execution_summary(results: List[Dict[str, Any]]) -> None:
        """
        显示执行摘要
        
        Args:
            results: 执行结果列表
        """
        if not results:
            return
        
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        if success_count == total_count:
            st.success(f"✅ 所有操作成功完成 ({success_count}/{total_count})")
        elif success_count > 0:
            st.warning(f"⚠️ 部分操作成功 ({success_count}/{total_count})")
        else:
            st.error(f"❌ 所有操作失败 (0/{total_count})")
    
    @staticmethod
    def display_undo_option() -> bool:
        """
        显示撤销选项
        
        Returns:
            用户是否选择撤销
        """
        st.subheader("🔄 撤销操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            undo = st.button("↩️ 撤销上一步", key="undo_last")
        
        with col2:
            clear_all = st.button("🗑️ 清空所有", key="clear_all")
        
        if undo:
            return True
        elif clear_all:
            return 'clear'
        
        return False
    
    @staticmethod
    def display_progress(current: int, total: int, message: str = "") -> None:
        """
        显示进度条
        
        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        if total > 0:
            progress = current / total
            st.progress(progress)
            
            if message:
                st.info(f"{message} ({current}/{total})")
            else:
                st.info(f"进度: {current}/{total}")
    
    @staticmethod
    def display_operation_log(logs: List[str]) -> None:
        """
        显示操作日志
        
        Args:
            logs: 日志列表
        """
        if not logs:
            return
        
        st.subheader("📝 操作日志")
        
        for log in logs:
            st.text(log)
    
    @staticmethod
    def confirm_dangerous_operation(operation_type: str, 
                                     description: str = "") -> bool:
        """
        确认危险操作
        
        Args:
            operation_type: 操作类型
            description: 操作描述
            
        Returns:
            用户是否确认
        """
        st.error(f"⚠️ 警告：即将执行危险操作 - {operation_type}")
        
        if description:
            st.warning(description)
        
        st.warning("此操作可能不可逆，请谨慎操作！")
        
        confirm_text = st.text_input(
            "输入 'CONFIRM' 确认执行",
            key="dangerous_operation_confirm"
        )
        
        if st.button("确认执行", type="primary", key="confirm_dangerous"):
            if confirm_text == "CONFIRM":
                return True
            else:
                st.error("请输入 'CONFIRM' 确认")
        
        return False