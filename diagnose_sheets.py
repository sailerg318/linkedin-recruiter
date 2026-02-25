"""
诊断 Google Sheets 创建问题
显示详细的错误信息
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import traceback


def diagnose_sheets_creation():
    """诊断表格创建问题"""
    print("\n" + "="*70)
    print("Google Sheets 创建诊断")
    print("="*70)
    
    # 步骤1: 连接测试
    print("\n步骤1: 测试连接...")
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'google_credentials.json', scope
        )
        client = gspread.authorize(creds)
        print("✓ 连接成功")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        return
    
    # 步骤2: 列出现有文件
    print("\n步骤2: 列出现有文件...")
    try:
        files = client.list_spreadsheet_files()
        print(f"✓ 找到 {len(files)} 个表格")
        if files:
            print("\n现有表格:")
            for i, f in enumerate(files[:5], 1):  # 只显示前5个
                print(f"  {i}. {f.get('name', 'Unknown')}")
            if len(files) > 5:
                print(f"  ... 还有 {len(files) - 5} 个")
    except Exception as e:
        print(f"⚠ 列出文件失败: {e}")
    
    # 步骤3: 尝试创建最小表格
    print("\n步骤3: 尝试创建最小表格...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sheet_name = f"诊断测试_{timestamp}"
    
    try:
        print(f"  创建表格: {sheet_name}")
        spreadsheet = client.create(sheet_name)
        print(f"✓ 创建成功!")
        print(f"  表格ID: {spreadsheet.id}")
        print(f"  表格URL: {spreadsheet.url}")
        
        # 步骤4: 尝试转移所有权
        print("\n步骤4: 尝试转移所有权...")
        try:
            spreadsheet.share(
                'sailerg318@gmail.com',
                perm_type='user',
                role='owner',
                transfer_ownership=True
            )
            print("✓ 所有权转移成功!")
            print(f"  新所有者: sailerg318@gmail.com")
            print(f"  表格URL: {spreadsheet.url}")
            
        except Exception as e:
            print(f"✗ 转移所有权失败: {e}")
            print(f"\n详细错误:\n{traceback.format_exc()}")
            
            # 尝试只分享（不转移所有权）
            print("\n尝试只分享（不转移所有权）...")
            try:
                spreadsheet.share(
                    'sailerg318@gmail.com',
                    perm_type='user',
                    role='writer'
                )
                print("✓ 分享成功（编辑权限）")
                print(f"  表格URL: {spreadsheet.url}")
            except Exception as e2:
                print(f"✗ 分享也失败: {e2}")
        
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        
        # 分析错误类型
        error_str = str(e).lower()
        print("\n可能的原因:")
        
        if 'quota' in error_str or 'limit' in error_str:
            print("  • API配额限制")
            print("    解决: 等待配额重置（通常是每天）")
        
        elif 'permission' in error_str or 'forbidden' in error_str:
            print("  • 权限问题")
            print("    解决: 检查服务账号权限配置")
        
        elif 'storage' in error_str or 'space' in error_str:
            print("  • 存储空间问题")
            print("    解决: 清理Drive空间")
        
        elif 'timeout' in error_str or 'timed out' in error_str:
            print("  • 网络超时")
            print("    解决: 检查网络连接，稍后重试")
        
        else:
            print("  • 未知错误")
            print("    建议: 查看上面的详细错误信息")


if __name__ == "__main__":
    diagnose_sheets_creation()
