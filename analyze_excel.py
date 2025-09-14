import pandas as pd
import os

# 分析Excel文件结构
excel_files = [
    'data/19.99V 6.00A data_detail_1_2025-05-09T12-15-19.xlsx',
    'data/20.2V  19.8Ω 1.3Adata_detail_1_2025-05-02T06-23-00.xlsx',
    'data/39.9V 9.02A data_detail_1_2025-05-09T13-02-36.xlsx'
]

for file in excel_files:
    if os.path.exists(file):
        print(f"\n分析文件: {file}")
        print("=" * 50)
        
        # 读取Excel文件
        excel_data = pd.ExcelFile(file)
        
        # 显示所有sheet名称
        print(f"Sheet名称: {excel_data.sheet_names}")
        
        # 读取第一个sheet的数据
        df = pd.read_excel(file, sheet_name=0)
        print(f"\n数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print(f"\n前5行数据:")
        print(df.head())
        print(f"\n数据类型:")
        print(df.dtypes)
