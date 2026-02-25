#!/usr/bin/env python3
"""
诊断 OAuth 配置问题
"""

import os
import traceback


def diagnose():
    """诊断 OAuth 配置"""
    print("\n" + "="*70)
    print("OAuth 配置诊断")
    print("="*70)
    
    # 检查文件
    print("\n1. 检查文件...")
    oauth_file = "oauth_credentials.json"
    token_file = "token.pickle"
    
    if os.path.exists(oauth_file):
        print(f"  ✓ {oauth_file} 存在")
    else:
        print(f"  ✗ {oauth_file} 不存在")
        print(f"    请从 Google Cloud Console 下载 OAuth 凭证")
        print(f"    详见: OAUTH_SETUP.md")
        return
    
    if os.path.exists(token_file):
        print(f"  ✓ {token_file} 存在（已认证）")
    else:
        print(f"  ⚠ {token_file} 不存在（需要首次认证）")
    
    # 测试导入
    print("\n2. 测试导入模块...")
    try:
        from google_sheets_exporter import GoogleSheetsExporter
        print("  ✓ GoogleSheetsExporter 导入成功")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        return
    
    # 测试初始化
    print("\n3. 测试初始化...")
    try:
        exporter = GoogleSheetsExporter(oauth_file)
        print("  ✓ 初始化成功")
    except Exception as e:
        print(f"  ✗ 初始化失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        return
    
    # 测试连接
    print("\n4. 测试连接...")
    try:
        success = exporter.connect()
        if success:
            print("  ✓ 连接成功")
            print("\n" + "="*70)
            print("✓ 所有检查通过！OAuth 配置正常")
            print("="*70)
        else:
            print("  ✗ 连接失败")
    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        print(f"\n详细错误:\n{traceback.format_exc()}")
        
        # 分析错误
        error_str = str(e).lower()
        print("\n可能的原因:")
        if "file not found" in error_str or "no such file" in error_str:
            print("  • oauth_credentials.json 文件不存在或路径错误")
        elif "invalid" in error_str:
            print("  • OAuth 凭证文件格式错误或已失效")
        elif "redirect" in error_str or "port" in error_str:
            print("  • OAuth 重定向 URI 配置问题")
            print("    在 Google Cloud Console 中添加: http://localhost")
        else:
            print("  • 未知错误，请查看上面的详细错误信息")


if __name__ == "__main__":
    diagnose()
