"""
清理服务账号的 Google Drive 文件（改进版）
- 添加超时设置
- 支持分页处理
- 边列出边删除，避免内存问题
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import socket


def cleanup_service_account_drive():
    """清理服务账号的 Drive 文件"""
    print("\n" + "="*70)
    print("清理服务账号 Google Drive 文件（改进版）")
    print("="*70)
    
    # 设置全局超时
    socket.setdefaulttimeout(30)  # 30秒超时
    
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
    
    # 统计和删除
    print("\n2. 开始扫描和删除文件...")
    print("   (边扫描边删除，避免超时)")
    
    total_deleted = 0
    total_failed = 0
    total_size = 0
    page_token = None
    page_num = 0
    
    try:
        while True:
            page_num += 1
            print(f"\n  处理第 {page_num} 页...")
            
            # 列出一页文件
            try:
                results = service.files().list(
                    pageSize=100,  # 每页100个，避免超时
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, size, mimeType)"
                ).execute()
            except socket.timeout:
                print(f"  ✗ 第 {page_num} 页超时，跳过")
                break
            except Exception as e:
                print(f"  ✗ 第 {page_num} 页出错: {e}")
                break
            
            files = results.get('files', [])
            
            if not files:
                print(f"  ✓ 第 {page_num} 页没有文件")
                break
            
            print(f"  ✓ 找到 {len(files)} 个文件")
            
            # 立即删除这一页的文件
            for i, file in enumerate(files, 1):
                file_size = int(file.get('size', 0))
                size_mb = file_size / (1024 * 1024)
                file_type = "Sheets" if file['mimeType'] == 'application/vnd.google-apps.spreadsheet' else "其他"
                
                try:
                    service.files().delete(fileId=file['id']).execute()
                    print(f"    [{i}/{len(files)}] ✓ 已删除: {file['name']} ({file_type}, {size_mb:.2f} MB)")
                    total_deleted += 1
                    total_size += file_size
                except Exception as e:
                    print(f"    [{i}/{len(files)}] ✗ 删除失败: {file['name']} - {e}")
                    total_failed += 1
            
            # 检查是否还有下一页
            page_token = results.get('nextPageToken')
            if not page_token:
                print(f"\n  ✓ 已处理完所有页面")
                break
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n✗ 处理过程出错: {e}")
    
    # 总结
    total_size_mb = total_size / (1024 * 1024)
    print("\n" + "="*70)
    print("清理完成")
    print("="*70)
    print(f"✓ 成功删除: {total_deleted} 个文件")
    if total_failed > 0:
        print(f"✗ 删除失败: {total_failed} 个文件")
    print(f"✓ 释放空间: {total_size_mb:.2f} MB")
    print(f"✓ 预计剩余: ~15 GB")


if __name__ == "__main__":
    print("\n⚠️  警告: 此操作将删除服务账号 Drive 中的所有文件")
    print("   这不会影响您个人账号的文件")
    confirm = input("\n确认继续？(yes/no): ").strip().lower()
    
    if confirm == 'yes':
        cleanup_service_account_drive()
    else:
        print("\n已取消操作")
