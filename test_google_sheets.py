"""
测试 Google Sheets 连接
验证凭证是否正确配置
"""

from google_sheets_exporter import GoogleSheetsExporter


def test_google_sheets_connection():
    """测试 Google Sheets 连接"""
    print("\n" + "="*70)
    print("测试 Google Sheets 连接")
    print("="*70)
    
    # 初始化导出器
    print("\n1. 初始化 Google Sheets 导出器...")
    exporter = GoogleSheetsExporter("google_credentials.json")
    
    # 测试连接
    print("\n2. 测试连接...")
    if exporter.connect():
        print("✓ 连接成功！")
    else:
        print("✗ 连接失败，请检查:")
        print("  - google_credentials.json 文件是否存在")
        print("  - 文件路径是否正确")
        print("  - 服务账号权限是否正确")
        return False
    
    # 创建测试表格
    print("\n3. 创建测试表格...")
    test_candidates = [
        {
            "name": "测试候选人",
            "final_score": 85,
            "flash_score": 75,
            "职位匹配": {"匹配": "✅"},
            "年限匹配": {"匹配": "✅"},
            "背景匹配": {"匹配": "✅", "咨询经验": "McKinsey 3年", "甲方经验": "Google 5年"},
            "地点匹配": {"匹配": "✅"},
            "current_title": "Senior Product Manager",
            "current_company": "Alibaba",
            "experience_years": 8,
            "url": "https://linkedin.com/in/test",
            "推荐理由": ["职位完全匹配", "大厂背景", "年限符合"]
        }
    ]
    
    # 获取用户邮箱（用于转移所有权）
    user_email = input("\n请输入你的 Google 邮箱（用于接收表格所有权）: ").strip()
    
    share_emails = [user_email] if user_email else None
    
    url = exporter.export_candidates(
        candidates=test_candidates,
        requirement_text="测试需求：上海的产品经理，5年经验",
        job_title="Product Manager (测试)",
        share_emails=share_emails
    )
    
    if url:
        print("\n✓ 测试成功！")
        print(f"\n测试表格 URL: {url}")
        print("\n请访问上述链接查看测试表格")
        print("如果能看到表格内容，说明配置正确")
        return True
    else:
        print("\n✗ 创建表格失败")
        return False


if __name__ == "__main__":
    success = test_google_sheets_connection()
    
    if success:
        print("\n" + "="*70)
        print("✅ Google Sheets 配置正确，可以正常使用")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ Google Sheets 配置有问题，请检查")
        print("="*70)
        print("\n配置步骤:")
        print("1. 访问 https://console.cloud.google.com")
        print("2. 创建项目并启用 Google Sheets API")
        print("3. 创建服务账号并下载 JSON 凭证")
        print("4. 将凭证重命名为 google_credentials.json")
        print("5. 放在 linkedin_recruiter/ 目录下")
