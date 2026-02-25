"""
清理服务账号的 Google Drive 文件
删除所有 Google Sheets 文件以释放空间
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build


def cleanup_service_account_drive():
    """清理服务账号的 Drive 文件"""
    print("\n" + "="*70)
    print("清理服务账号 Google Drive 文件")
    print("="*70)
    
    # 初始化
    print("\n1. 连接到 Google Drive...")
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'google_credentials.json',
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✓ 连接成功")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 列出所有文件
    print("\n2. 列出所有文件...")
    try:
        results = service.files().list(
            pageSize=1000,
            fields="files(id, name, size, createdTime, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("✓ 没有找到文件，Drive 已经是空的")
            return
        
        # 计算总大小
        total_size = sum(int(f.get('size', 0)) for f in files)
        total_size_mb = total_size / (1024 * 1024)
        
        print(f"✓ 找到 {len(files)} 个文件")
        print(f"  总大小: {total_size_mb:.2f} MB")
        print(f"  剩余空间: {15*1024 - total_size_mb:.2f} MB")
        
        # 显示文件列表
        print("\n文件列表:")
        for i, file in enumerate(files, 1):
            size_mb = int(file.get('size', 0)) / (1024 * 1024)
            file_type = "Google Sheets" if file['mimeType'] == 'application/vnd.google-apps.spreadsheet' else "其他"
            print(f"  {i}. {file['name']}")
            print(f"     类型: {file_type}")
            print(f"     大小: {size_mb:.2f} MB")
            print(f"     创建时间: {file['createdTime']}")
        
    except Exception as e:
        print(f"✗ 列出文件失败: {e}")
        return
    
    # 确认删除
    print("\n" + "="*70)
    print("⚠️  警告: 即将删除所有文件")
    print("="*70)
    confirm = input("\n确认删除所有文件？(yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n已取消删除")
        return
    
    # 删除文件
    print("\n3. 删除文件...")
    deleted_count = 0
    failed_count = 0
    
    for i, file in enumerate(files, 1):
        try:
            service.files().delete(fileId=file['id']).execute()
            print(f"  [{i}/{len(files)}] ✓ 已删除: {file['name']}")
            deleted_count += 1
        except Exception as e:
            print(f"  [{i}/{len(files)}] ✗ 删除失败: {file['name']} - {e}")
            failed_count += 1
    
    # 总结
    print("\n" + "="*70)
    print("清理完成")
    print("="*70)
    print(f"✓ 成功删除: {deleted_count} 个文件")
    if failed_count > 0:
        print(f"✗ 删除失败: {failed_count} 个文件")
    print(f"✓ 释放空间: {total_size_mb:.2f} MB")
    print(f"✓ 当前剩余: ~15 GB")


if __name__ == "__main__":
    cleanup_service_account_drive()
