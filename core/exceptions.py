"""
Excel Agent 统一异常类
"""


class ExcelAgentError(Exception):
    """Excel Agent 基础异常类"""
    
    def __init__(self, message: str, details: str = ""):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class TableNotFoundError(ExcelAgentError):
    """表格未找到异常"""
    pass


class ColumnNotFoundError(ExcelAgentError):
    """列未找到异常"""
    pass


class CellReferenceError(ExcelAgentError):
    """单元格引用错误异常"""
    pass


class OperationError(ExcelAgentError):
    """操作错误异常"""
    pass


class ValidationError(ExcelAgentError):
    """验证错误异常"""
    pass


class FileLoadError(ExcelAgentError):
    """文件加载错误异常"""
    pass


class FileSaveError(ExcelAgentError):
    """文件保存错误异常"""
    pass


class MergeError(ExcelAgentError):
    """合并错误异常"""
    pass


class CalculationError(ExcelAgentError):
    """计算错误异常"""
    pass


class HeaderError(ExcelAgentError):
    """表头错误异常"""
    pass


class UndoRedoError(ExcelAgentError):
    """撤销/重做错误异常"""
    pass
