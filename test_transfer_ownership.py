"""
测试创建表格并转移所有权
"""

from google_sheets_exporter import GoogleSheetsExporter


def test_create_and_transfer():
    """测试创建表格并转移所有权"""
    print("\n" + "="*70)
    print("测试创建表格并转移所有权")
    print("="*70)
    
    exporter = GoogleSheetsExporter("google_credentials.json")
    
    # 非常简单的测试数据（最小化）
    test_candidates = [
        {
            "name": "测试",
            "final_score": 85,
            "职位匹配": {"匹配": "✅"},
            "年限匹配": {"匹配": "✅"},
            "背景匹配": {"匹配": "✅"},
            "地点匹配": {"匹配": "✅"},
            "current_title": "PM",
            "current_company": "Test",
            "experience_years": 5,
            "url": "https://linkedin.com/in/test",
            "推荐理由": ["测试"]
        }
    ]
    
    print("\n尝试创建表格并转移给: sailerg318@gmail.com")
    
    url = exporter.export_candidates(
        candidates=test_candidates,
        requirement_text="测试",
        job_title="Test",
        share_emails=["sailerg318@gmail.com"]
    )
    
    if url:
        print(f"\n✓ 成功！")
        print(f"  表格 URL: {url}")
        print(f"  所有权已转移给: sailerg318@gmail.com")
        print(f"\n请检查你的邮箱，应该会收到通知")
    else:
        print(f"\n✗ 失败")
        print(f"  可能原因: 服务账号存储空间不足")
        print(f"  解决方案: 运行 python3 cleanup_drive.py 清理空间")


if __name__ == "__main__":
    test_create_and_transfer()
