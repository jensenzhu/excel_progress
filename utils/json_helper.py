import json
from typing import Any, Dict
from datetime import datetime, date
import pandas as pd
import numpy as np


class PandasEncoder(json.JSONEncoder):
    """Pandas DataFrame和Series的JSON编码器"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (pd.DataFrame, pd.Series)):
            return obj.to_dict()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def json_dumps(data: Any, ensure_ascii: bool = False, indent: int = None) -> str:
    """
    统一的JSON序列化函数
    
    Args:
        data: 要序列化的数据
        ensure_ascii: 是否确保ASCII编码
        indent: 缩进空格数
    
    Returns:
        JSON字符串
    """
    return json.dumps(data, cls=PandasEncoder, ensure_ascii=ensure_ascii, indent=indent)


def json_loads(json_str: str) -> Any:
    """
    统一的JSON反序列化函数
    
    Args:
        json_str: JSON字符串
    
    Returns:
        反序列化的数据
    """
    return json.loads(json_str)


def create_success_response(data: Any = None, message: str = "") -> str:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        JSON字符串
    """
    response = {
        "success": True
    }
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return json_dumps(response)


def create_error_response(error: str, details: Any = None) -> str:
    """
    创建错误响应
    
    Args:
        error: 错误消息
        details: 错误详情
    
    Returns:
        JSON字符串
    """
    response = {
        "success": False,
        "error": error
    }
    
    if details is not None:
        response["details"] = details
    
    return json_dumps(response)
