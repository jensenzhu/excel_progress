import pytest
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_manager import DataManager
from core.exceptions import TableNotFoundError


class TestDataManager:
    """DataManager 单元测试"""
    
    @pytest.fixture
    def data_manager(self):
        """创建 DataManager 实例"""
        return DataManager()
    
    @pytest.fixture
    def sample_df(self):
        """创建测试 DataFrame"""
        return pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Paris']
        })
    
    @pytest.fixture
    def temp_excel(self, sample_df, tmp_path):
        """创建临时 Excel 文件"""
        file_path = tmp_path / "test.xlsx"
        sample_df.to_excel(file_path, index=False)
        return file_path
    
    def test_load_table(self, data_manager, temp_excel):
        """测试加载表格"""
        result = data_manager.load_table(str(temp_excel), table_name="test_table")
        assert result is True
        assert "test_table" in data_manager.tables
        assert data_manager.active_table == "test_table"
    
    def test_get_table(self, data_manager, temp_excel):
        """测试获取表格"""
        data_manager.load_table(str(temp_excel), table_name="test_table")
        df = data_manager.get_table("test_table")
        assert df is not None
        assert len(df) == 3
        assert list(df.columns) == ['name', 'age', 'city']
    
    def test_get_table_not_found(self, data_manager):
        """测试获取不存在的表格"""
        df = data_manager.get_table("non_existent_table")
        assert df is None
    
    def test_get_all_tables(self, data_manager, temp_excel):
        """测试获取所有表格"""
        data_manager.load_table(str(temp_excel), table_name="table1")
        data_manager.load_table(str(temp_excel), table_name="table2")
        tables = data_manager.get_all_tables()
        assert set(tables) == {"table1", "table2"}
    
    def test_set_active_table(self, data_manager, temp_excel):
        """测试设置激活表格"""
        data_manager.load_table(str(temp_excel), table_name="table1")
        data_manager.load_table(str(temp_excel), table_name="table2")
        
        result = data_manager.set_active_table("table1")
        assert result is True
        assert data_manager.active_table == "table1"
    
    def test_set_active_table_not_found(self, data_manager):
        """测试设置不存在的激活表格"""
        result = data_manager.set_active_table("non_existent")
        assert result is False
    
    def test_remove_table(self, data_manager, temp_excel):
        """测试移除表格"""
        data_manager.load_table(str(temp_excel), table_name="test_table")
        result = data_manager.remove_table("test_table")
        assert result is True
        assert "test_table" not in data_manager.tables
    
    def test_get_table_info(self, data_manager, temp_excel):
        """测试获取表格信息"""
        data_manager.load_table(str(temp_excel), table_name="test_table")
        info = data_manager.get_table_info("test_table")
        assert info is not None
        assert info["total_rows"] == 3
        assert "columns" in info
        assert "missing_values" in info
    
    def test_can_undo_redo(self, data_manager, temp_excel):
        """测试撤销/重做功能"""
        data_manager.load_table(str(temp_excel), table_name="test_table")
        assert data_manager.can_undo("test_table") is True
        assert data_manager.can_redo("test_table") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
