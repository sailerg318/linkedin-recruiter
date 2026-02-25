"""
Serper X-Ray搜索完整测试
"""

from serper_search import SerperSearcher
from xray_search import XRaySearchStrategy
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter
from requirement_parser import RequirementParser


def test_serper_xray_complete():
    """测试Serper X-Ray完整流程"""
    
    print("\n" + "="*60)
    print("Serper X-Ray搜索完整测试")
    print("="*60)
    
    # 需求
    requirement_text = "我要找Base上海的Product Manager，新零售行业，5-10年经验"
    
    print(f"\n需求：{requirement_text}")
    
    # 步骤1：解析需求
    print("\n" + "="*60)
    print("步骤1：解析需求")
    print("="*60)
    parser = RequirementParser()
    parsed_req = parser.parse_requirement(requirement_text)
    
    # 步骤2：X-Ray切片搜索
    print("\n" + "="*60)
    print("步骤2：X-Ray切片搜索（使用Serper）")
    print("="*60)
    
    xray = XRaySearchStrategy()
    
    candidates = xray.execute_xray_search(
        base_keyword="Product Manager",
        location="Shanghai",
        industry="新零售",
        min_years=5,
        max_years=10,
        max_results_per_query=100,  # 每次搜索100个结果，最大化产出
        delay_range=(2, 5)  # Serper更快，可以缩短延时
    )
    
    if not candidates:
        print("\n✗ 未找到候选人")
        return False
    
    print(f"\n✓ X-Ray搜索完成，找到 {len(candidates)} 位候选人")
    
    # 保存搜索结果
    xray.save_to_csv()
    
    # 显示候选人示例
    print("\n候选人示例（前10位）：")
    for i, c in enumerate(candidates[:10], 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        print(f"   职位: {c.get('title', 'N/A')}")
        print(f"   URL: {c.get('url', 'N/A')[:60]}...")
        print(f"   来源: {c.get('slice_type', 'N/A')}")
    
    # 步骤3：两阶段细筛
    print("\n" + "="*60)
    print("步骤3：两阶段细筛")
    print("="*60)
    
    screening = DetailedScreening()
    final_candidates = screening.screen_candidates_two_stage(
        candidates,
        parsed_req,
        flash_threshold=50,
        pro_batch_size=10,
        pro_threshold=70
    )
    
    if not final_candidates:
        print("\n⚠ 没有候选人通过细筛")
        return False
    
    print(f"\n✓ 细筛完成，{len(final_candidates)} 位候选人通过")
    
    # 步骤4：导出Google Sheets
    print("\n" + "="*60)
    print("步骤4：导出Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            final_candidates,
            requirement_text=requirement_text,
            job_title="PM_Serper_XRay",
            share_emails=["sailerg318@gmail.com"]
        )
        
        if url:
            print(f"\n{'='*60}")
            print("✅ 测试完成！")
            print(f"{'='*60}")
            print(f"\n✓ Google Sheets: {url}")
            print(f"✓ 搜索候选人: {len(candidates)} 位")
            print(f"✓ 最终通过: {len(final_candidates)} 位")
            return True
        else:
            print("\n✗ Google Sheets导出失败")
            return False
            
    except Exception as e:
        print(f"\n✗ 导出失败: {e}")
        return False


if __name__ == "__main__":
    test_serper_xray_complete()
