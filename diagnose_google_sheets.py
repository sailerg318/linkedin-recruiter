"""
Google Sheets 诊断脚本
检查 OAuth 配置和连接
"""

import os
import sys
import base64
import pickle

def diagnose_google_sheets():
    """诊断 Google Sheets 配置"""
    print("=" * 70)
    print("Google Sheets OAuth 诊断")
    print("=" * 70)
    
    # 1. 检查环境变量
    print("\n1. 检查环境变量")
    print("-" * 70)
    
    token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')
    if token_base64:
        print(f"✅ GOOGLE_TOKEN_BASE64: 已设置 ({len(token_base64)} 字符)")
        
        # 尝试解码
        try:
            token_bytes = base64.b64decode(token_base64)
            print(f"✅ Base64 解码成功 ({len(token_bytes)} 字节)")
            
            # 尝试反序列化
            try:
                creds = pickle.loads(token_bytes)
                print(f"✅ Token 反序列化成功")
                print(f"   - Token 类型: {type(creds).__name__}")
                print(f"   - 是否有效: {creds.valid if hasattr(creds, 'valid') else '未知'}")
                print(f"   - 是否过期: {creds.expired if hasattr(creds, 'expired') else '未知'}")
                if hasattr(creds, 'expiry'):
                    print(f"   - 过期时间: {creds.expiry}")
            except Exception as e:
                print(f"❌ Token 反序列化失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Base64 解码失败: {e}")
            return False
    else:
        print("❌ GOOGLE_TOKEN_BASE64: 未设置")
        print("\n解决方案:")
        print("在 Render Dashboard 添加环境变量:")
        print("Key: GOOGLE_TOKEN_BASE64")
        print("Value: (Base64 编码的 token.pickle)")
        return False
    
    # 2. 测试 Google Sheets 连接
    print("\n2. 测试 Google Sheets 连接")
    print("-" * 70)
    
    try:
        from google_sheets_exporter import GoogleSheetsExporterOAuth
        
        exporter = GoogleSheetsExporterOAuth()
        
        if exporter.connect():
            print("✅ Google Sheets 连接成功")
            
            # 测试创建表格
            print("\n3. 测试创建表格")
            print("-" * 70)
            
            from datetime import datetime
            test_title = f"测试表格_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            url = exporter.create_spreadsheet(
                title=test_title,
                share_emails=None,
                public=True
            )
            
            if url:
                print(f"✅ 表格创建成功")
                print(f"   URL: {url}")
                print(f"\n请访问上面的 URL 验证表格是否可见")
                return True
            else:
                print(f"❌ 表格创建失败")
                return False
        else:
            print("❌ Google Sheets 连接失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("\n可能缺少依赖包:")
        print("pip install gspread google-auth google-auth-oauthlib")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        import traceback
        print(f"\n详细错误:")
        print(traceback.format_exc())
        return False
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LinkedIn 招聘系统 - Google Sheets 诊断")
    print("=" * 70)
    
    success = diagnose_google_sheets()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 所有检查通过！Google Sheets 功能正常")
    else:
        print("❌ 发现问题，请按照上述提示修复")
    print("=" * 70 + "\n")
    
    sys.exit(0 if success else 1)
