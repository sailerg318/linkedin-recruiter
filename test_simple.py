"""
简化版系统测试 - 快速验证各模块是否正常工作
"""

from requirement_parser import RequirementParser
from job_expander import JobTitleExpander
from google_sheets_exporter import GoogleSheetsExporter


def test_requirement_parser():
    """测试需求解析模块"""
    print("\n" + "="*60)
    print("测试1: 需求解析模块")
    print("="*60)
    
    parser = RequirementParser()
    requirement_text = "我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
    
    try:
        parsed = parser.parse_requirement(requirement_text)
        print("\n✓ 需求解析成功")
        print(f"  岗位: {parsed.get('job_title', 'N/A')}")
        print(f"  地点: {parsed.get('location', 'N/A')}")
        print(f"  年限: {parsed.get('experience_years', 'N/A')}")
        return True
    except Exception as e:
        print(f"\n✗ 需求解析失败: {e}")
        return False


def test_job_expander():
    """测试岗位扩充模块"""
    print("\n" + "="*60)
    print("测试2: 岗位扩充模块")
    print("="*60)
    
    expander = JobTitleExpander()
    
    try:
        variants = expander.expand_job_title("OD", max_variants=3)
        print(f"\n✓ 岗位扩充成功，生成 {len(variants)} 个变体")
        return True
    except Exception as e:
        print(f"\n✗ 岗位扩充失败: {e}")
        return False


def test_google_sheets_exporter():
    """测试Google Sheets导出模块"""
    print("\n" + "="*60)
    print("测试3: Google Sheets导出模块")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    # 测试连接
    try:
        connected = exporter.connect()
        if connected:
            print("\n✓ Google Sheets连接成功")
            return True
        else:
            print("\n⚠ Google Sheets连接失败（可能缺少凭证文件）")
            return False
    except Exception as e:
        print(f"\n⚠ Google Sheets测试跳过: {e}")
        print("  提示: 需要配置 google_credentials.json")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 简化测试")
    print("="*60)
    
    results = []
    
    # 测试1: 需求解析
    results.append(("需求解析", test_requirement_parser()))
    
    # 测试2: 岗位扩充
    results.append(("岗位扩充", test_job_expander()))
    
    # 测试3: Google Sheets
    results.append(("Google Sheets", test_google_sheets_exporter()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统准备就绪。")
    else:
        print("\n⚠ 部分测试失败，请检查配置。")


if __name__ == "__main__":
    main()
