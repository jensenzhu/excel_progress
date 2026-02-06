import streamlit as st
import pandas as pd
from io import BytesIO
from core.data_manager import DataManager
from deprecated.nlp_parser import NLPParser
from deprecated.operation_engine import OperationEngine
from ui.table_viewer import TableViewer
from ui.chat_interface import ChatInterface
from ui.operation_preview import OperationPreview
from utils.excel_handler import ExcelHandler
from utils.validators import DataValidator
from config.settings import settings

st.warning("⚠️ 注意: app.py 已弃用，请使用 app_agent.py 获得更好的体验", icon="⚠️")


def initialize_session_state():
    """
    初始化会话状态
    """
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'nlp_parser' not in st.session_state:
        st.session_state.nlp_parser = NLPParser()
    
    if 'operation_engine' not in st.session_state:
        st.session_state.operation_engine = OperationEngine(st.session_state.data_manager)
    
    if 'table_viewer' not in st.session_state:
        st.session_state.table_viewer = TableViewer()
    
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = ChatInterface()
    
    if 'operation_preview' not in st.session_state:
        st.session_state.operation_preview = OperationPreview()
    
    ChatInterface.initialize_chat_history()


def display_sidebar():
    """
    显示侧边栏
    """
    with st.sidebar:
        st.header("📁 文件管理")
        
        uploaded_files = st.file_uploader(
            "上传Excel文件",
            accept_multiple_files=True,
            type=['xlsx', 'xls'],
            key="file_uploader"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.data_manager.get_all_tables():
                    try:
                        df = ExcelHandler.read_excel_from_bytes(uploaded_file.getvalue())
                        if df is not None:
                            st.session_state.data_manager.tables[uploaded_file.name] = df
                            st.session_state.data_manager._update_table_metadata(uploaded_file.name)
                            st.success(f"✅ 已加载: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"❌ 加载失败 {uploaded_file.name}: {e}")
        
        st.divider()
        
        tables = st.session_state.data_manager.get_all_tables()
        if tables:
            st.header("📊 已加载表格")
            
            current_active = st.session_state.data_manager.active_table
            if current_active not in tables:
                current_active = tables[0]
                st.session_state.data_manager.set_active_table(current_active)
            
            active_table = st.selectbox(
                "选择活动表格",
                tables,
                index=tables.index(current_active) if current_active in tables else 0
            )
            
            if active_table and active_table != current_active:
                st.session_state.data_manager.set_active_table(active_table)
            
            st.divider()
            
            st.header("🗑️ 表格管理")
            
            table_to_remove = st.selectbox(
                "选择要删除的表格",
                [""] + tables
            )
            
            if table_to_remove and st.button("删除表格", key="remove_table"):
                st.session_state.data_manager.remove_table(table_to_remove)
                st.success(f"✅ 已删除: {table_to_remove}")
                st.rerun()
        
        st.divider()
        
        st.header("📝 操作历史")
        history = st.session_state.data_manager.get_operation_history()
        if history:
            for i, op in enumerate(reversed(history[-10:]), 1):
                with st.expander(f"操作 {i}"):
                    st.json(op)
        else:
            st.info("暂无操作历史")


def display_main_area():
    """
    显示主区域
    """
    active_table_name = st.session_state.data_manager.active_table
    
    if active_table_name is None:
        st.info("👈 请先在侧边栏上传Excel文件")
        return
    
    df = st.session_state.data_manager.get_table(active_table_name)
    
    if df is None:
        st.error(f"无法加载表格: {active_table_name}")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 数据预览")
        
        table_info = st.session_state.data_manager.get_table_info(active_table_name)
        
        TableViewer.display_table_info(table_info)
        
        st.divider()
        
        TableViewer.display_preview(df)
        
        with st.expander("📋 列信息"):
            TableViewer.display_columns_info(table_info)
    
    with col2:
        st.header("💬 自然语言操作")
        
        ChatInterface.display_help()
        
        st.divider()
        
        user_input = ChatInterface.get_user_input_multiline(
            "输入操作指令，例如：计算A列的平均值",
            key="operation_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            execute_button = st.button("🚀 执行", type="primary", key="execute_button")
        
        with col2:
            preview_button = st.button("👁️ 预览", key="preview_button")
        
        if user_input:
            ChatInterface.display_examples()
            
            if execute_button:
                execute_operation(user_input)
            elif preview_button:
                preview_operation(user_input)
        
        st.divider()
        
        ChatInterface.display_chat_history()


def execute_operation(user_input: str):
    """
    执行操作
    
    Args:
        user_input: 用户输入
    """
    ChatInterface.add_user_message(user_input)
    
    try:
        context = {
            'tables': st.session_state.data_manager.get_all_tables(),
            'active_table': st.session_state.data_manager.active_table,
            'table_info': st.session_state.data_manager.table_metadata
        }
        
        operations = st.session_state.nlp_parser.parse_instruction(user_input, context)
        
        if operations is None:
            ChatInterface.display_error("无法解析指令，请重试")
            return
        
        if not operations:
            ChatInterface.display_error("未识别到任何操作")
            return
        
        st.session_state.operation_preview.display_operations_preview(
            operations,
            st.session_state.nlp_parser
        )
        
        results = st.session_state.operation_engine.execute_operations(operations)
        
        st.session_state.operation_preview.display_execution_results(results)
        st.session_state.operation_preview.display_execution_summary(results)
        
        for i, result in enumerate(results):
            st.session_state.data_manager.add_operation_to_history({
                'instruction': user_input,
                'operation': operations[i],
                'result': result
            })
        
        success_count = sum(1 for r in results if r.get('success', False))
        if success_count == len(results):
            ChatInterface.add_assistant_message(f"✅ 操作成功完成 ({success_count}/{len(results)})")
        else:
            ChatInterface.add_assistant_message(f"⚠️ 部分操作成功 ({success_count}/{len(results)})")
        
    except Exception as e:
        ChatInterface.display_error(f"执行操作时出错: {str(e)}")
        ChatInterface.add_assistant_message(f"❌ 执行失败: {str(e)}")


def preview_operation(user_input: str):
    """
    预览操作
    
    Args:
        user_input: 用户输入
    """
    ChatInterface.add_user_message(user_input)
    
    try:
        context = {
            'tables': st.session_state.data_manager.get_all_tables(),
            'active_table': st.session_state.data_manager.active_table,
            'table_info': st.session_state.data_manager.table_metadata
        }
        
        operations = st.session_state.nlp_parser.parse_instruction(user_input, context)
        
        if operations is None:
            ChatInterface.display_error("无法解析指令，请重试")
            return
        
        if not operations:
            ChatInterface.display_error("未识别到任何操作")
            return
        
        with st.expander("📋 操作预览", expanded=True):
            st.session_state.operation_preview.display_operations_preview(
                operations,
                st.session_state.nlp_parser
            )
        
        with st.expander("🔍 操作详情"):
            st.session_state.operation_preview.display_operation_details(operations)
        
        with st.expander("📊 执行计划"):
            st.session_state.operation_preview.display_execution_plan(operations)
        
        with st.expander("🎯 预期结果"):
            st.session_state.operation_preview.display_expected_results(operations)
        
        with st.expander("⚠️ 风险评估"):
            st.session_state.operation_preview.display_risk_assessment(
                operations,
                st.session_state.data_manager.table_metadata
            )
        
        if st.button("✅ 确认执行", type="primary", key="confirm_from_preview"):
            execute_operation(user_input)
        
    except Exception as e:
        ChatInterface.display_error(f"预览操作时出错: {str(e)}")


def display_footer():
    """
    显示页脚
    """
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Excel智能数据操作助手 | 使用Streamlit + GLM-4.5-Flash构建
    </div>
    """, unsafe_allow_html=True)


def main():
    """
    主函数
    """
    st.set_page_config(
        page_title=settings.STREAMLIT_TITLE,
        layout=settings.STREAMLIT_LAYOUT,
        page_icon="📊"
    )
    
    st.title("📊 Excel智能数据操作助手")
    st.markdown("使用自然语言处理Excel数据，支持多表操作")
    
    initialize_session_state()
    
    display_sidebar()
    display_main_area()
    display_footer()


if __name__ == "__main__":
    main()