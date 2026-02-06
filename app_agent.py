import streamlit as st
import pandas as pd
import json
from io import BytesIO
from core.data_manager import DataManager
from core.excel_agent import ExcelAgent
from ui.table_viewer import TableViewer
from utils.excel_handler import ExcelHandler
from config.settings import settings
from config.logger import logger


def initialize_session_state():
    """
    初始化会话状态
    """
    import json
    from pathlib import Path
    
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'excel_agent' not in st.session_state:
        st.session_state.excel_agent = ExcelAgent(st.session_state.data_manager)
    
    if 'table_viewer' not in st.session_state:
        st.session_state.table_viewer = TableViewer()
    
    if 'chat_history' not in st.session_state:
        chat_history_file = Path(".streamlit/chat_history.json")
        if chat_history_file.exists():
            try:
                with open(chat_history_file, 'r', encoding='utf-8') as f:
                    st.session_state.chat_history = json.load(f)
                    logger.debug(f"Loaded chat_history from file: {len(st.session_state.chat_history)} messages")
            except Exception as e:
                logger.debug(f"Failed to load chat_history: {e}")
                st.session_state.chat_history = []
        else:
            st.session_state.chat_history = []
    
    if 'last_saved_filename' not in st.session_state:
        last_saved_file = Path(".streamlit/last_saved.txt")
        if last_saved_file.exists():
            try:
                with open(last_saved_file, 'r', encoding='utf-8') as f:
                    filename = f.read().strip()
                    if filename:
                        st.session_state.last_saved_filename = filename
                        logger.debug(f"Loaded last_saved_filename from file: {filename}")
                    else:
                        st.session_state.last_saved_filename = None
            except Exception as e:
                logger.debug(f"Failed to load last_saved_filename: {e}")
                st.session_state.last_saved_filename = None
        else:
            st.session_state.last_saved_filename = None

def save_session_state():
    """
    保存会话状态到文件
    """
    import json
    from pathlib import Path
    
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    if 'chat_history' in st.session_state:
        chat_history_file = streamlit_dir / "chat_history.json"
        try:
            with open(chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.chat_history, f, ensure_ascii=False)
                logger.debug(f"Saved chat_history to file: {len(st.session_state.chat_history)} messages")
        except Exception as e:
            logger.debug(f"Failed to save chat_history: {e}")
    
    if 'last_saved_filename' in st.session_state:
        last_saved_file = streamlit_dir / "last_saved.txt"
        try:
            with open(last_saved_file, 'w', encoding='utf-8') as f:
                f.write(st.session_state.last_saved_filename or '')
                logger.debug(f"Saved last_saved_filename to file: {st.session_state.last_saved_filename}")
        except Exception as e:
            logger.debug(f"Failed to save last_saved_filename: {e}")


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
            
            st.header("📋 表头设置")
            
            if st.button("检测表头", key="detect_header_btn"):
                if active_table:
                    with st.spinner("检测中..."):
                        result = st.session_state.data_manager.detect_header(active_table, 10)
                        if result.get("success"):
                            st.session_state.header_preview = result
                        else:
                            st.error(f"检测失败: {result.get('error', '未知错误')}")
            
            if 'header_preview' in st.session_state:
                preview = st.session_state.header_preview
                st.write(f"当前表头行: 第 {preview['current_header_row'] + 1} 行")
                
                if 'current_headers' in preview:
                    st.write("当前列名:")
                    st.write(preview['current_headers'])
                
                st.write("数据预览（前10行）:")
                preview_df = pd.DataFrame([
                    [f"第 {r['row_index'] + 1} 行"] + [str(v) for v in r['values']]
                    for r in preview['preview']
                ])
                st.dataframe(preview_df, use_container_width=True)
                
                header_row_options = [f"第 {i + 1} 行" for i in range(len(preview['preview']))]
                selected_header = st.selectbox(
                    "选择哪一行作为表头",
                    header_row_options,
                    index=preview['current_header_row'] if preview['current_header_row'] < len(header_row_options) else 0
                )
                
                if st.button("设置表头", key="set_header_btn"):
                    header_row_idx = int(selected_header.split("第 ")[1].split(" 行")[0]) - 1
                    result = st.session_state.data_manager.set_header_row(active_table, header_row_idx)
                    if result.get("success"):
                        st.success(f"✅ {result.get('message')}")
                        del st.session_state.header_preview
                        st.rerun()
                    else:
                        st.error(f"设置失败: {result.get('error', '未知错误')}")
                
                if st.button("取消", key="cancel_header_btn"):
                    del st.session_state.header_preview
                    st.rerun()
        
        st.divider()
        
        st.header("📝 Agent状态")
        
        tables = st.session_state.data_manager.get_all_tables()
        st.metric("已加载表格", len(tables))
        
        active_table = st.session_state.data_manager.active_table
        st.metric("当前激活", active_table if active_table else "无")
    
    st.divider()
    
    st.header("↩️ 撤销/重做")
    
    if active_table:
        can_undo = st.session_state.data_manager.can_undo(active_table)
        can_redo = st.session_state.data_manager.can_redo(active_table)
        
        col_undo, col_redo = st.columns(2)
        
        with col_undo:
            if st.button("↩️ 撤销", disabled=not can_undo, key="undo_btn"):
                if st.session_state.data_manager.undo(active_table):
                    st.success("✅ 已撤销")
                    st.rerun()
                else:
                    st.error("❌ 撤销失败")
        
        with col_redo:
            if st.button("↪️ 重做", disabled=not can_redo, key="redo_btn"):
                if st.session_state.data_manager.redo(active_table):
                    st.success("✅ 已重做")
                    st.rerun()
                else:
                    st.error("❌ 重做失败")
    else:
        st.info("请先加载表格")


def display_main_area():
    """
    显示主区域
    """
    active_table_name = st.session_state.data_manager.active_table
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 数据预览")
        
        if active_table_name is None:
            st.info("👈 请先在侧边栏上传Excel文件")
        else:
            if st.button("🔄 刷新数据预览", key="refresh_data"):
                st.rerun()
            
            df = st.session_state.data_manager.get_table(active_table_name)
            
            if df is None:
                st.error(f"无法加载表格: {active_table_name}")
            else:
                table_info = st.session_state.data_manager.get_table_info(active_table_name)
                
                TableViewer.display_table_info(table_info)
                
                st.divider()
                
                col_edit, col_info = st.columns([3, 1])
                with col_edit:
                    edit_mode = st.checkbox("✏️ 启用编辑模式", key="edit_mode", value=False)
                
                with col_info:
                    if edit_mode:
                        st.info("💡 在表格中直接编辑数据，点击保存按钮更新")
                
                st.divider()
                
                if edit_mode:
                    edited_df = TableViewer.display_table(
                        df, 
                        table_name=active_table_name, 
                        editable=True,
                        key=f"editable_table_{active_table_name}",
                        height=500
                    )
                    
                    if edited_df is not None and st.button("💾 保存更改", key="save_edits", type="primary"):
                        st.session_state.data_manager.tables[active_table_name] = edited_df
                        st.session_state.data_manager.save_snapshot(active_table_name)
                        st.session_state.data_manager._update_table_metadata(active_table_name)
                        st.success("✅ 数据已更新！")
                        st.rerun()
                else:
                    TableViewer.display_preview(df)
                
                with st.expander("📋 列信息"):
                    TableViewer.display_columns_info(table_info)
    
    with col2:
        st.header("💬 智能助手")
        
        if st.session_state.data_manager.active_table:
            st.divider()
            st.subheader("📥 下载表格")
            active_table = st.session_state.data_manager.active_table
            last_saved = st.session_state.last_saved_filename
            download_filename = last_saved or active_table
            logger.debug(f"Download button in display_main_area: last_saved={last_saved}, download_filename={download_filename}")
            table_data = st.session_state.data_manager.export_table_to_bytes(active_table, download_filename)
            if table_data:
                st.download_button(
                    label=f"📥 下载 {download_filename}",
                    data=table_data,
                    file_name=download_filename,
                    key=f"download_main_{download_filename}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        display_agent_interface()


def display_agent_interface():
    """
    显示Agent交互界面
    """
    user_input = st.text_area(
        "输入自然语言指令",
        placeholder="例如：技术部有多少人？",
        height=100,
        key="agent_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        execute_button = st.button("🚀 执行", type="primary", key="execute_agent")
    
    with col2:
        clear_button = st.button("🗑️ 清空对话", key="clear_chat")
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if user_input and execute_button:
        process_user_query(user_input)
    
    st.divider()
    
    display_chat_history()


def process_user_query(query: str):
    """
    处理用户查询
    """
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })
    save_session_state()
    
    st.subheader("📊 执行过程")
    
    tool_results = []
    
    def step_callback(step_info):
        """步骤回调函数"""
        if step_info["type"] == "tool_start":
            tool = step_info["tool"]
            step_num = len(tool_results) + 1
            
            status = st.status(
                f"🔄 步骤 {step_num}: {tool['name']}",
                state="running",
                expanded=False
            )
            
            status.write(f"**工具**: `{tool['name']}`")
            status.write("**参数**:")
            status.json(tool['args'])
            
            tool_results.append({
                "step": step_num,
                "name": tool['name'],
                "args": tool['args'],
                "status_obj": status,
                "result": None,
                "success": None
            })
        
        elif step_info["type"] == "tool_complete":
            tool_name = step_info["tool_name"]
            result = step_info["result"]
            
            for tool in tool_results:
                if tool["name"] == tool_name and tool["success"] is None:
                    try:
                        result_data = json.loads(result)
                        tool["result"] = result_data
                        tool["success"] = result_data.get("success", False)
                        
                        if tool["success"]:
                            tool["status_obj"].update(
                                label=f"✅ 步骤 {tool['step']}: {tool['name']}",
                                state="complete",
                                expanded=False
                            )
                            tool["status_obj"].write("**执行成功**")
                        else:
                            tool["status_obj"].update(
                                label=f"❌ 步骤 {tool['step']}: {tool['name']}",
                                state="error",
                                expanded=True
                            )
                            tool["status_obj"].error(f"执行失败: {result_data.get('error', '未知错误')}")
                    except Exception as e:
                        tool["result"] = result
                        tool["success"] = False
                        tool["status_obj"].update(
                            label=f"❌ 步骤 {tool['step']}: {tool['name']}",
                            state="error",
                            expanded=True
                        )
                        tool["status_obj"].error(f"解析结果失败: {str(e)}")
                    break
    
    try:
        result = st.session_state.excel_agent.invoke(query, step_callback)
        
        st.divider()
        
        st.subheader("💬 回答")
        st.markdown(result["response"])
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"]
        })
        
        if "tool_calls" in result:
            logger.debug(f"Processing tool_calls, count={len(result['tool_calls'])}")
            for tool_call in result["tool_calls"]:
                logger.debug(f"tool_call name: {tool_call.get('name')}")
                if tool_call.get("name") == "save_table":
                    tool_result = tool_call.get("result")
                    logger.debug(f"save_table tool_result: {tool_result}")
                    if isinstance(tool_result, dict) and tool_result.get("success"):
                        filename = tool_result.get("filename")
                        logger.debug(f"filename from tool_result: {filename}")
                        if filename:
                            st.session_state.last_saved_filename = filename
                            logger.debug(f"Updated session_state.last_saved_filename: {filename}")
                            save_session_state()
        
    except Exception as e:
        error_msg = f"处理出错: {str(e)}"
        st.error(error_msg)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": error_msg
        })


def display_chat_history():
    """
    显示对话历史
    """
    if not st.session_state.chat_history:
        st.info("暂无对话记录")
        return
    
    st.subheader("📜 对话历史")
    
    for i, msg in enumerate(st.session_state.chat_history[-10:], 1):
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)


def display_footer():
    """
    显示页脚
    """
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Excel智能数据操作助手 | GLM-4.5-Flash
    </div>
    """, unsafe_allow_html=True)


def main():
    """
    主函数
    """
    st.set_page_config(
        page_title=settings.STREAMLIT_TITLE,
        layout=settings.STREAMLIT_LAYOUT,
        page_icon="🤖"
    )
    
    st.title("🤖 Excel智能数据操作助手")
    st.markdown("使用 GLM-4.5-Flash 处理Excel数据")
    
    initialize_session_state()
    
    display_sidebar()
    display_main_area()
    display_footer()


if __name__ == "__main__":
    main()