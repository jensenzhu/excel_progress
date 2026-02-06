## 修复 fill_na 空值检测问题

### 问题
- `get_table_info` 显示"规格商家编码"有 44 个缺失值
- `fill_na` 检测到 0 个空值，无法填充

### 解决方案
简化 `fill_na` 工具的空值检测逻辑，直接使用 `df.isnull()` 方法，与 `get_table_info` 保持一致：

```python
null_mask = df_copy[target_column].isnull()
```

### 修改文件
- `core/excel_agent.py` 的 `fill_na` 工具函数

### 测试
修改后重新测试查询："判断每一行的规格商家编码，如果为空，就将这行的主商家编码中的内容复制过来"