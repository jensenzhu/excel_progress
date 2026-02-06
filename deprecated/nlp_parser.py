import json
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from config.settings import settings
from config.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, CELL_REFERENCE_PROMPT


class NLPParser:
    """
    自然语言解析器
    使用GLM-4.5-Flash解析用户的自然语言指令
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    def parse_instruction(self, instruction: str, context: Dict) -> Optional[List[Dict]]:
        """
        解析自然语言指令
        
        Args:
            instruction: 用户指令
            context: 上下文信息，包含已加载的表格、当前激活表格等
            
        Returns:
            操作列表，如果解析失败返回None
        """
        try:
            tables = context.get('tables', [])
            active_table = context.get('active_table', '')
            table_info = self._format_table_info(context.get('table_info', {}))
            
            prompt = USER_PROMPT_TEMPLATE.format(
                tables=tables,
                active_table=active_table,
                table_info=table_info,
                instruction=instruction
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            content = self._extract_json(content)
            
            result = json.loads(content)
            
            if 'operations' in result:
                return result['operations']
            elif isinstance(result, list):
                return result
            else:
                return [result]
                
        except Exception as e:
            print(f"解析指令失败: {e}")
            return None
    
    def parse_cell_reference(self, reference: str, context: Dict) -> Optional[Dict]:
        """
        解析单元格引用
        
        Args:
            reference: 单元格引用
            context: 上下文信息
            
        Returns:
            解析结果字典
        """
        try:
            prompt = CELL_REFERENCE_PROMPT.format(reference=reference)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个Excel单元格引用解析器"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            content = self._extract_json(content)
            
            return json.loads(content)
            
        except Exception as e:
            print(f"解析单元格引用失败: {e}")
            return None
    
    def extract_entities(self, instruction: str) -> Dict[str, Any]:
        """
        从指令中提取实体
        
        Args:
            instruction: 用户指令
            
        Returns:
            实体字典
        """
        entities = {
            'tables': [],
            'columns': [],
            'cells': [],
            'ranges': [],
            'numbers': [],
            'operations': []
        }
        
        table_pattern = r'(表\d+|表[一二三四五六七八九十]+|[\w]+\.xlsx|[\w]+\.xls)'
        entities['tables'] = re.findall(table_pattern, instruction)
        
        cell_pattern = r'[A-Z]+\d+'
        entities['cells'] = re.findall(cell_pattern, instruction)
        
        range_pattern = r'[A-Z]+\d+:[A-Z]+\d+'
        entities['ranges'] = re.findall(range_pattern, instruction)
        
        number_pattern = r'\d+\.?\d*'
        entities['numbers'] = re.findall(number_pattern, instruction)
        
        operation_keywords = ['提取', '计算', '筛选', '排序', '分组', '合并', '插入', '更新', '保存',
                             '求和', '平均值', '计数', '最大值', '最小值', 'sum', 'mean', 'count', 'max', 'min']
        for keyword in operation_keywords:
            if keyword in instruction:
                entities['operations'].append(keyword)
        
        return entities
    
    def identify_intent(self, instruction: str) -> str:
        """
        识别用户意图
        
        Args:
            instruction: 用户指令
            
        Returns:
            意图类型
        """
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ['提取', 'extract', '选择', 'select']):
            return 'extract'
        elif any(word in instruction_lower for word in ['计算', 'calculate', '求和', 'sum', '平均', 'mean']):
            return 'calculate'
        elif any(word in instruction_lower for word in ['筛选', 'filter', '过滤', 'where']):
            return 'filter'
        elif any(word in instruction_lower for word in ['排序', 'sort', 'order']):
            return 'sort'
        elif any(word in instruction_lower for word in ['分组', 'group', 'groupby']):
            return 'group'
        elif any(word in instruction_lower for word in ['插入', 'insert', '填入', '写入']):
            return 'insert'
        elif any(word in instruction_lower for word in ['合并', 'merge', 'join']):
            return 'merge'
        elif any(word in instruction_lower for word in ['更新', 'update', '修改']):
            return 'update'
        elif any(word in instruction_lower for word in ['保存', 'save', '导出', 'export']):
            return 'save'
        else:
            return 'unknown'
    
    def _format_table_info(self, table_info: Dict) -> str:
        """
        格式化表格信息
        
        Args:
            table_info: 表格信息字典
            
        Returns:
            格式化后的字符串
        """
        if not table_info:
            return "无表格信息"
        
        formatted = []
        for table_name, info in table_info.items():
            formatted.append(f"\n{table_name}:")
            formatted.append(f"  行数: {info.get('rows', 0)}")
            formatted.append(f"  列数: {info.get('columns', 0)}")
            formatted.append(f"  列名: {', '.join(info.get('column_names', []))}")
        
        return '\n'.join(formatted)
    
    def _extract_json(self, content: str) -> str:
        """
        从响应中提取JSON内容
        
        Args:
            content: 响应内容
            
        Returns:
            JSON字符串
        """
        content = content.strip()
        
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        content = content.strip()
        
        json_start = content.find('{')
        json_end = content.rfind('}')
        
        if json_start != -1 and json_end != -1:
            content = content[json_start:json_end + 1]
        
        array_start = content.find('[')
        array_end = content.rfind(']')
        
        if array_start != -1 and array_end != -1:
            content = content[array_start:array_end + 1]
        
        return content
    
    def generate_operation_summary(self, operations: List[Dict]) -> List[str]:
        """
        生成操作摘要
        
        Args:
            operations: 操作列表
            
        Returns:
            摘要列表
        """
        summaries = []
        
        for op in operations:
            op_type = op.get('type', 'unknown')
            
            if op_type == 'extract':
                source = op.get('source_table', '未知表')
                cols = ', '.join(op.get('columns', []))
                summaries.append(f"从{source}提取{cols}列")
            
            elif op_type == 'calculate':
                calc_type = op.get('operation', '计算')
                col = op.get('column', '未知列')
                summaries.append(f"计算{col}的{calc_type}")
            
            elif op_type == 'filter':
                condition = op.get('condition', '条件')
                summaries.append(f"筛选{condition}的数据")
            
            elif op_type == 'sort':
                col = op.get('column', '未知列')
                order = op.get('order', '升序')
                summaries.append(f"按{col}{order}排序")
            
            elif op_type == 'group':
                col = op.get('column', '未知列')
                summaries.append(f"按{col}分组")
            
            elif op_type == 'insert':
                target = op.get('target_table', '未知表')
                cell = op.get('target_cell', '未知位置')
                summaries.append(f"插入数据到{target}的{cell}")
            
            elif op_type == 'merge':
                tables = op.get('tables', [])
                key = op.get('key', '未知键')
                summaries.append(f"合并{', '.join(tables)}，基于{key}")
            
            elif op_type == 'update':
                target = op.get('target_table', '未知表')
                summaries.append(f"更新{target}的数据")
            
            elif op_type == 'save':
                path = op.get('output_path', '未知路径')
                summaries.append(f"保存到{path}")
            
            else:
                summaries.append(f"执行{op_type}操作")
        
        return summaries