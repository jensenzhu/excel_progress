import pandas as pd
import numpy as np
from pathlib import Path


def create_sample_sales_data():
    """
    创建示例销售数据
    """
    np.random.seed(42)
    
    data = {
        '产品ID': [f'P{str(i).zfill(4)}' for i in range(1, 101)],
        '产品名称': [f'产品{i}' for i in range(1, 101)],
        '类别': np.random.choice(['电子产品', '服装', '食品', '家居'], 100),
        '价格': np.random.uniform(10, 1000, 100).round(2),
        '销量': np.random.randint(1, 500, 100),
        '销售额': np.random.uniform(100, 50000, 100).round(2),
        '利润': np.random.uniform(10, 5000, 100).round(2),
        '地区': np.random.choice(['华东', '华南', '华北', '西南', '西北'], 100),
        '销售日期': pd.date_range('2024-01-01', periods=100, freq='D')
    }
    
    df = pd.DataFrame(data)
    return df


def create_sample_inventory_data():
    """
    创建示例库存数据
    """
    np.random.seed(43)
    
    data = {
        '产品ID': [f'P{str(i).zfill(4)}' for i in range(1, 101)],
        '产品名称': [f'产品{i}' for i in range(1, 101)],
        '库存数量': np.random.randint(0, 1000, 100),
        '仓库位置': np.random.choice(['仓库A', '仓库B', '仓库C'], 100),
        '入库日期': pd.date_range('2024-01-01', periods=100, freq='D'),
        '供应商': np.random.choice(['供应商A', '供应商B', '供应商C'], 100),
        '单价': np.random.uniform(10, 500, 100).round(2)
    }
    
    df = pd.DataFrame(data)
    return df


def create_sample_report_data():
    """
    创建示例报表数据
    """
    data = {
        '月份': ['1月', '2月', '3月', '4月', '5月', '6月', 
                 '7月', '8月', '9月', '10月', '11月', '12月'],
        '目标销售额': [10000, 12000, 15000, 18000, 20000, 22000,
                       25000, 28000, 30000, 32000, 35000, 40000],
        '实际销售额': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        '完成率': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        '增长率': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    df = pd.DataFrame(data)
    return df


def create_sample_employee_data():
    """
    创建示例员工数据
    """
    np.random.seed(44)
    
    departments = ['销售部', '技术部', '市场部', '人事部', '财务部']
    positions = ['经理', '主管', '专员']
    
    data = {
        '员工ID': [f'E{str(i).zfill(4)}' for i in range(1, 51)],
        '姓名': [f'员工{i}' for i in range(1, 51)],
        '部门': np.random.choice(departments, 50),
        '职位': np.random.choice(positions, 50),
        '年龄': np.random.randint(22, 55, 50),
        '工资': np.random.uniform(3000, 20000, 50).round(2),
        '入职日期': pd.date_range('2020-01-01', periods=50, freq='W'),
        '绩效评分': np.random.uniform(1, 5, 50).round(1)
    }
    
    df = pd.DataFrame(data)
    return df


def main():
    """
    创建所有示例文件
    """
    examples_dir = Path(__file__).parent.parent / 'examples'
    examples_dir.mkdir(exist_ok=True)
    
    print("创建示例Excel文件...")
    
    sales_df = create_sample_sales_data()
    sales_path = examples_dir / 'sales_data.xlsx'
    sales_df.to_excel(sales_path, index=False, engine='openpyxl')
    print(f"✅ 已创建: {sales_path}")
    
    inventory_df = create_sample_inventory_data()
    inventory_path = examples_dir / 'inventory_data.xlsx'
    inventory_df.to_excel(inventory_path, index=False, engine='openpyxl')
    print(f"✅ 已创建: {inventory_path}")
    
    report_df = create_sample_report_data()
    report_path = examples_dir / 'report_template.xlsx'
    report_df.to_excel(report_path, index=False, engine='openpyxl')
    print(f"✅ 已创建: {report_path}")
    
    employee_df = create_sample_employee_data()
    employee_path = examples_dir / 'employee_data.xlsx'
    employee_df.to_excel(employee_path, index=False, engine='openpyxl')
    print(f"✅ 已创建: {employee_path}")
    
    print("\n所有示例文件创建完成！")
    print(f"示例文件保存在: {examples_dir}")


if __name__ == "__main__":
    main()