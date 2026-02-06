import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChatInterface:
    """
    聊天界面组件
    负责自然语言交互界面
    """
    
    @staticmethod
    def initialize_chat_history() -> None:
        """
        初始化聊天历史
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    @staticmethod
    def add_user_message(message: str) -> None:
        """
        添加用户消息
        
        Args:
            message: 消息内容
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        st.session_state.chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    @staticmethod
    def add_assistant_message(message: str) -> None:
        """
        添加助手消息
        
        Args:
            message: 消息内容
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    @staticmethod
    def add_system_message(message: str) -> None:
        """
        添加系统消息
        
        Args:
            message: 消息内容
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        st.session_state.chat_history.append({
            'role': 'system',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    
    @staticmethod
    def display_chat_history() -> None:
        """
        显示聊天历史
        """
        if 'chat_history' not in st.session_state:
            return
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
                st.caption(f"{msg['timestamp']}")
    
    @staticmethod
    def get_user_input(placeholder: str = "输入操作指令...", 
                       key: str = "user_input") -> str:
        """
        获取用户输入
        
        Args:
            placeholder: 输入框占位符
            key: 输入框键名
            
        Returns:
            用户输入内容
        """
        user_input = st.text_input(
            placeholder,
            key=key,
            label_visibility="collapsed"
        )
        return user_input
    
    @staticmethod
    def get_user_input_multiline(placeholder: str = "输入操作指令...", 
                                   key: str = "user_input_multiline") -> str:
        """
        获取多行用户输入
        
        Args:
            placeholder: 输入框占位符
            key: 输入框键名
            
        Returns:
            用户输入内容
        """
        user_input = st.text_area(
            placeholder,
            key=key,
            height=100,
            label_visibility="collapsed"
        )
        return user_input
    
    @staticmethod
    def display_suggestions(suggestions: List[str]) -> Optional[str]:
        """
        显示建议操作
        
        Args:
            suggestions: 建议列表
            
        Returns:
            用户选择的建议
        """
        if not suggestions:
            return None
        
        st.subheader("💡 建议操作")
        
        selected = st.selectbox(
            "点击选择或直接输入",
            [""] + suggestions,
            label_visibility="collapsed"
        )
        
        return selected if selected else None
    
    @staticmethod
    def display_quick_actions(actions: List[Dict[str, str]]) -> Optional[str]:
        """
        显示快捷操作按钮
        
        Args:
            actions: 操作列表 [{"label": "显示", "command": "显示表格"}]
            
        Returns:
            用户选择的操作命令
        """
        if not actions:
            return None
        
        st.subheader("⚡ 快捷操作")
        
        cols = st.columns(min(len(actions), 4))
        
        for i, action in enumerate(actions):
            with cols[i]:
                if st.button(action['label'], key=f"quick_action_{i}"):
                    return action['command']
        
        return None
    
    @staticmethod
    def display_operation_result(result: Dict[str, Any]) -> None:
        """
        显示操作结果
        
        Args:
            result: 操作结果字典
        """
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
            
            if 'result_key' in result:
                st.info(f"结果已保存，键名: {result['result_key']}")
        else:
            st.error("❌ 操作失败")
            
            if 'error' in result:
                st.error(result['error'])
    
    @staticmethod
    def display_error(message: str) -> None:
        """
        显示错误消息
        
        Args:
            message: 错误消息
        """
        st.error(f"❌ {message}")
    
    @staticmethod
    def display_warning(message: str) -> None:
        """
        显示警告消息
        
        Args:
            message: 警告消息
        """
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def display_info(message: str) -> None:
        """
        显示信息消息
        
        Args:
            message: 信息消息
        """
        st.info(f"ℹ️ {message}")
    
    @staticmethod
    def display_success(message: str) -> None:
        """
        显示成功消息
        
        Args:
            message: 成功消息
        """
        st.success(f"✅ {message}")
    
    @staticmethod
    def clear_chat_history() -> None:
        """
        清空聊天历史
        """
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
    
    @staticmethod
    def get_chat_history() -> List[Dict[str, str]]:
        """
        获取聊天历史
        
        Returns:
            聊天历史列表
        """
        return st.session_state.get('chat_history', [])
    
    @staticmethod
    def export_chat_history() -> str:
        """
        导出聊天历史为文本
        
        Returns:
            聊天历史文本
        """
        history = st.session_state.get('chat_history', [])
        
        lines = []
        for msg in history:
            role_name = {
                'user': '用户',
                'assistant': '助手',
                'system': '系统'
            }.get(msg['role'], msg['role'])
            
            lines.append(f"[{msg['timestamp']}] {role_name}:")
            lines.append(msg['content'])
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def display_help() -> None:
        """
        显示帮助信息
        """
        with st.expander("📖 使用帮助"):
            st.markdown("""
            ### 基本操作
            - **加载数据**: 上传Excel文件
            - **查看数据**: 选择表格查看内容
            - **自然语言操作**: 输入自然语言指令进行操作
            
            ### 示例指令
            - **单表操作**:
              - "计算A列的平均值"
              - "筛选B列大于100的行"
              - "按C列分组求和"
            
            - **跨表操作**:
              - "从表1提取A列，插入到表2的B列"
              - "用表1的销售额更新表2的对应产品"
              - "合并表1和表2，基于产品ID"
            
            - **单元格操作**:
              - "计算所有行的总和，存入A1单元格"
              - "将表1的平均值填入表2的B5单元格"
            
            ### 操作类型
            - **提取**: 从表格中提取数据
            - **计算**: 执行各种计算操作（求和、平均值等）
            - **筛选**: 根据条件筛选数据
            - **排序**: 对数据进行排序
            - **分组**: 按列分组并聚合
            - **插入**: 将数据插入到指定位置
            - **合并**: 合并多个表格
            - **更新**: 更新表格数据
            - **保存**: 保存表格到文件
            """)
    
    @staticmethod
    def display_examples() -> None:
        """
        显示示例指令
        """
        with st.expander("💬 示例指令"):
            examples = [
                "计算销售额列的总和",
                "筛选利润大于500的行",
                "按地区分组，计算每个地区的平均销售额",
                "从表1提取产品名称列",
                "将表1的销售额列插入到表2的C列",
                "用表1的库存数量更新表2的对应产品",
                "合并表1和表2，基于产品ID列",
                "计算所有行的平均值，存入A1单元格"
            ]
            
            for i, example in enumerate(examples, 1):
                st.markdown(f"{i}. {example}")