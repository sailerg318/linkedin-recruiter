"""
测试 OAuth 版本的 Google Sheets 导出
"""

from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth


def test_oauth_export():
    """测试 OAuth 导出"""
    print("\n" + "="*70)
    print("测试 OAuth 版本 Google Sheets 导出")
    print("="*70)
    
    print("\n提示:")
    print("- 首次使用会打开浏览器进行授权")
    print("- 请登录您的 Google 账号并允许访问")
    print("- 认证成功后会自动保存凭证")
    
    # 创建导出器
    exporter = GoogleSheetsExporterOAuth("oauth_credentials.json")
    
    # 测试数据
    test_candidates = [
        {
            "name": "测试候选人",
            "final_score": 85,
            "职位匹配": {"匹配": "✅"},
            "年限匹配": {"匹配": "✅"},
            "背景匹配": {
                "匹配": "✅",
                "咨询经验": "McKinsey 3年",
                "甲方经验": "Google 2年"
            },
            "地点匹配": {"匹配": "✅"},
            "current_title": "Senior Product Manager",
            "current_company": "Google",
            "experience_years": 8,
            "url": "https://linkedin.com/in/test",
            "推荐理由": [
                "职位完全匹配",
                "MBB + FAANG 背景",
                "工作年限符合要求"
            ]
        }
    ]
    
    print("\n开始导出...")
    url = exporter.export_candidates(
        candidates=test_candidates,
        requirement_text="测试岗位要求",
        job_title="测试职位",
        share_emails=[]  # 不分享给其他人
    )
    
    if url:
        print("\n" + "="*70)
        print("✓ 测试成功！")
        print("="*70)
        print(f"\n表格链接: {url}")
        print("\n说明:")
        print("- 表格已创建在您的 Google Drive 中")
        print("- 使用的是您自己的存储空间")
        print("- 下次使用不需要重新认证")
    else:
        print("\n✗ 测试失败")
        print("请检查:")
        print("1. oauth_credentials.json 文件是否存在")
        print("2. 是否已启用 Google Sheets API 和 Drive API")
        print("3. 网络连接是否正常")


if __name__ == "__main__":
    test_oauth_export()
