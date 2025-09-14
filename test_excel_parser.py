"""
测试Excel解析功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.utils.excel_parser import ExcelParser

async def test_parser():
    parser = ExcelParser()
    
    # 测试文件列表
    test_files = [
        'data/19.99V 6.00A data_detail_1_2025-05-09T12-15-19.xlsx',
        'data/20.2V  19.8Ω 1.3Adata_detail_1_2025-05-02T06-23-00.xlsx',
        'data/39.9V 9.02A data_detail_1_2025-05-09T13-02-36.xlsx'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n{'='*60}")
            print(f"解析文件: {file_path}")
            print('='*60)
            
            result = await parser.parse_file(file_path)
            
            if result['success']:
                print("✅ 解析成功!")
                print(f"记录数: {len(result['records'])}")
                
                for record in result['records']:
                    print(f"\n📊 测试记录:")
                    print(f"  - 文件名: {record['file_name']}")
                    print(f"  - 测试日期: {record['test_date']}")
                    print(f"  - 电压: {record.get('voltage')} V")
                    print(f"  - 电流: {record.get('current')} A")
                    print(f"  - 电阻: {record.get('resistance')} Ω")
                    print(f"  - 功率: {record.get('power')} W")
                    print(f"  - 设备型号: {record.get('device_model')}")
                    print(f"  - 样本数: {record.get('sample_count')}")
                    
                print(f"\n详细数据条数: {sum(len(details) for details in result['details'].values())}")
            else:
                print(f"❌ 解析失败: {result.get('error')}")
        else:
            print(f"⚠️  文件不存在: {file_path}")

if __name__ == "__main__":
    print("🚀 开始测试Excel解析器...")
    asyncio.run(test_parser())
    print("\n✨ 测试完成!")