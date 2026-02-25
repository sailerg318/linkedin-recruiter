"""
完整系统测试 - 从需求输入到Google Sheets导出
"""

from requirement_parser import RequirementParser
from exhaustive_search import ExhaustiveSearchStrategy
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_complete_workflow():
    """测试完整工作流程"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 完整流程测试")
    print("="*60)
    
    # 需求输入
    requirement_text = "我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
    
    print(f"\n需求：{requirement_text}")
    
    # 步骤1：解析需求
    print("\n" + "="*60)
    print("步骤1：智能需求解析")
    print("="*60)
    parser = RequirementParser()
    parsed_req = parser.parse_requirement(requirement_text)
    
    # 步骤2：穷尽搜索（测试模式：限制组合数）
    print("\n" + "="*60)
    print("步骤2：穷尽搜索LinkedIn")
    print("="*60)
    strategy = ExhaustiveSearchStrategy()
    candidates = strategy.execute_exhaustive_search(
        requirement_text,
        max_combinations=5,  # 测试模式：只搜索5个组合
        max_results_per_combo=5
    )
    
    if not candidates:
        print("\n✗ 未找到候选人，测试结束")
        return
    
    print(f"\n✓ 粗筛完成，找到 {len(candidates)} 位候选人")
    
    # 步骤3：细筛分析
    print("\n" + "="*60)
    print("步骤3：Flash + Pro 细筛分析")
    print("="*60)
    screening = DetailedScreening()
    analyzed = screening.screen_candidates(
        candidates,
        parsed_req,
        flash_threshold=60,  # 测试模式：降低阈值
        max_pro_analysis=5,  # 测试模式：最多分析5人
        use_pro_for_all=False
    )
    
    print(f"\n✓ 细筛完成，分析了 {len(analyzed)} 位候选人")
    
    # 步骤4：导出Google Sheets
    print("\n" + "="*60)
    print("步骤4：导出到Google Sheets")
    print("="*60)
    exporter = GoogleSheetsExporter()
    
    url = exporter.export_candidates(
        analyzed,
        requirement_text=requirement_text,
        job_title="OD_Test",
        share_emails=["sailerg318@gmail.com"]
    )
    
    if url:
        print(f"\n{'='*60}")
        print("测试完成！")
        print(f"{'='*60}")
        print(f"\n✓ Google Sheets链接: {url}")
        print(f"✓ 已分享给: sailerg318@gmail.com")
        print(f"\n请在浏览器中打开链接查看结果")
    else:
        print("\n✗ Google Sheets导出失败")


if __name__ == "__main__":
    test_complete_workflow()
