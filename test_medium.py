"""
中等规模系统测试 - 测试完整流程但限制规模
适合快速验证系统功能
"""

from requirement_parser import RequirementParser
from exhaustive_search import ExhaustiveSearchStrategy
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_medium_workflow():
    """测试中等规模的完整工作流程"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 中等规模测试")
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
    
    # 步骤2：穷尽搜索（限制规模）
    print("\n" + "="*60)
    print("步骤2：穷尽搜索LinkedIn（限制规模）")
    print("="*60)
    print("⚠ 测试模式：限制搜索组合数=2，每组结果数=3")
    
    strategy = ExhaustiveSearchStrategy()
    candidates = strategy.execute_exhaustive_search(
        requirement_text,
        max_combinations=2,  # 只搜索2个组合
        max_results_per_combo=3  # 每组最多3个结果
    )
    
    if not candidates:
        print("\n✗ 未找到候选人，测试结束")
        print("提示：这可能是因为搜索限制太严格，或者Tavily API配置问题")
        return False
    
    print(f"\n✓ 粗筛完成，找到 {len(candidates)} 位候选人")
    
    # 显示候选人信息
    print("\n候选人列表：")
    for i, c in enumerate(candidates[:5], 1):
        print(f"  {i}. {c.get('name', 'Unknown')} - {c.get('title', 'N/A')}")
    
    # 步骤3：细筛分析（限制规模）
    print("\n" + "="*60)
    print("步骤3：Flash + Pro 细筛分析（限制规模）")
    print("="*60)
    print("⚠ 测试模式：Flash阈值=50，Pro分析上限=3")
    
    screening = DetailedScreening()
    analyzed = screening.screen_candidates(
        candidates,
        parsed_req,
        flash_threshold=50,  # 降低阈值
        max_pro_analysis=3,  # 最多分析3人
        use_pro_for_all=False
    )
    
    print(f"\n✓ 细筛完成，分析了 {len(analyzed)} 位候选人")
    
    # 显示分析结果
    if analyzed:
        print("\n分析结果（Top 3）：")
        for i, c in enumerate(analyzed[:3], 1):
            score = c.get('final_score', c.get('flash_score', 0))
            print(f"  {i}. {c.get('name', 'Unknown')} - 分数: {score}")
    
    # 步骤4：导出Google Sheets
    print("\n" + "="*60)
    print("步骤4：导出到Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            analyzed,
            requirement_text=requirement_text,
            job_title="OD_Medium_Test",
            share_emails=["sailerg318@gmail.com"]
        )
        
        if url:
            print(f"\n{'='*60}")
            print("✅ 测试完成！")
            print(f"{'='*60}")
            print(f"\n✓ Google Sheets链接: {url}")
            print(f"✓ 已分享给: sailerg318@gmail.com")
            print(f"\n请在浏览器中打开链接查看结果")
            return True
        else:
            print("\n✗ Google Sheets导出失败")
            return False
            
    except Exception as e:
        print(f"\n✗ Google Sheets导出失败: {e}")
        return False


def main():
    """主函数"""
    try:
        success = test_medium_workflow()
        
        if success:
            print("\n" + "="*60)
            print("🎉 中等规模测试成功完成！")
            print("="*60)
            print("\n提示：")
            print("- 如需完整测试，运行: python3 test_complete_system.py")
            print("- 完整测试会搜索更多组合，需要更长时间")
        else:
            print("\n" + "="*60)
            print("⚠ 测试未完全成功")
            print("="*60)
            print("\n可能的原因：")
            print("- Tavily API配置问题")
            print("- Google Sheets凭证问题")
            print("- 网络连接问题")
            
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
    except Exception as e:
        print(f"\n\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
