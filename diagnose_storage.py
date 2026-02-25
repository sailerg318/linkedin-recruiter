"""
详细的 Drive 存储诊断
使用 Drive API 查看真实的存储使用情况
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import traceback


def diagnose_drive_storage():
    """诊断Drive存储使用情况"""
    print("\n" + "="*70)
    print("Google Drive 存储诊断")
    print("="*70)
    
    # 连接
    print("\n步骤1: 连接到 Google Drive...")
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
    
    # 获取存储配额信息
    print("\n步骤2: 查询存储配额...")
    try:
        about = service.about().get(fields="storageQuota,user").execute()
        
        quota = about.get('storageQuota', {})
        user = about.get('user', {})
        
        print(f"\n用户信息:")
        print(f"  邮箱: {user.get('emailAddress', 'Unknown')}")
        
        print(f"\n存储配额:")
        limit = int(quota.get('limit', 0))
        usage = int(quota.get('usage', 0))
        usage_in_drive = int(quota.get('usageInDrive', 0))
        usage_in_drive_trash = int(quota.get('usageInDriveTrash', 0))
        
        print(f"  总配额: {limit / (1024**3):.2f} GB")
        print(f"  已使用: {usage / (1024**3):.2f} GB")
        print(f"  Drive使用: {usage_in_drive / (1024**3):.2f} GB")
        print(f"  回收站: {usage_in_drive_trash / (1024**3):.2f} GB")
        print(f"  剩余: {(limit - usage) / (1024**3):.2f} GB")
        
        if usage >= limit:
            print(f"\n⚠️  存储已满！")
        
    except Exception as e:
        print(f"✗ 查询配额失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
    
    # 列出所有文件（包括非Sheets）
    print("\n步骤3: 列出所有文件...")
    try:
        page_token = None
        all_files = []
        
        while True:
            results = service.files().list(
                pageSize=100,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, size, mimeType, trashed, createdTime)",
                q="trashed=false"  # 只看非回收站的
            ).execute()
            
            files = results.get('files', [])
            all_files.extend(files)
            
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        print(f"✓ 找到 {len(all_files)} 个文件")
        
        if all_files:
            # 按类型分组
            by_type = {}
            total_size = 0
            
            for f in all_files:
                mime = f.get('mimeType', 'unknown')
                size = int(f.get('size', 0))
                
                if mime not in by_type:
                    by_type[mime] = {'count': 0, 'size': 0, 'files': []}
                
                by_type[mime]['count'] += 1
                by_type[mime]['size'] += size
                by_type[mime]['files'].append(f)
                total_size += size
            
            print(f"\n文件类型统计:")
            for mime, info in sorted(by_type.items(), key=lambda x: x[1]['size'], reverse=True):
                size_mb = info['size'] / (1024**2)
                print(f"  {mime}")
                print(f"    数量: {info['count']}")
                print(f"    大小: {size_mb:.2f} MB")
            
            print(f"\n总大小: {total_size / (1024**2):.2f} MB")
            
            # 显示最大的文件
            print(f"\n最大的10个文件:")
            sorted_files = sorted(all_files, key=lambda x: int(x.get('size', 0)), reverse=True)
            for i, f in enumerate(sorted_files[:10], 1):
                size_mb = int(f.get('size', 0)) / (1024**2)
                print(f"  {i}. {f['name']}")
                print(f"     大小: {size_mb:.2f} MB")
                print(f"     类型: {f.get('mimeType', 'unknown')}")
                print(f"     ID: {f['id']}")
        
    except Exception as e:
        print(f"✗ 列出文件失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
    
    # 检查回收站
    print("\n步骤4: 检查回收站...")
    try:
        results = service.files().list(
            pageSize=100,
            fields="files(id, name, size, mimeType)",
            q="trashed=true"
        ).execute()
        
        trashed_files = results.get('files', [])
        print(f"✓ 回收站有 {len(trashed_files)} 个文件")
        
        if trashed_files:
            trashed_size = sum(int(f.get('size', 0)) for f in trashed_files)
            print(f"  总大小: {trashed_size / (1024**2):.2f} MB")
            print(f"\n建议: 清空回收站可以释放空间")
        
    except Exception as e:
        print(f"✗ 检查回收站失败: {e}")
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)


if __name__ == "__main__":
    diagnose_drive_storage()
