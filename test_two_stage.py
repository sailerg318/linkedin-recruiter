"""
两阶段细筛测试 - Flash50分筛选 + Pro10人批次深度分析
"""

from requirement_parser import RequirementParser
from exhaustive_search import ExhaustiveSearchStrategy
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_two_stage_screening():
    """测试两阶段细筛策略"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 两阶段细筛测试")
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
    
    # 步骤2：穷尽搜索（测试模式）
    print("\n" + "="*60)
    print("步骤2：穷尽搜索LinkedIn")
    print("="*60)
    print("⚠ 测试模式：限制搜索组合数=3，每组结果数=5")
    
    strategy = ExhaustiveSearchStrategy()
    candidates = strategy.execute_exhaustive_search(
        requirement_text,
        max_combinations=3,  # 搜索3个组合
        max_results_per_combo=5  # 每组5个结果
    )
    
    if not candidates:
        print("\n✗ 未找到候选人，测试结束")
        print("提示：请检查Tavily API配置")
        return False
    
    print(f"\n✓ 粗筛完成，找到 {len(candidates)} 位候选人")
    
    # 显示候选人信息
    print("\n候选人列表（前10位）：")
    for i, c in enumerate(candidates[:10], 1):
        print(f"  {i}. {c.get('name', 'Unknown')} - {c.get('title', 'N/A')}")
    
    # 步骤3：两阶段细筛
    print("\n" + "="*60)
    print("步骤3：两阶段细筛分析")
    print("="*60)
    print("策略：")
    print("  - 阶段1: Flash 50分快速筛选")
    print("  - 阶段2: Pro 10人一批深度分析")
    print("  - 最终阈值: 70分")
    
    screening = DetailedScreening()
    final_candidates = screening.screen_candidates_two_stage(
        candidates,
        parsed_req,
        flash_threshold=50,  # Flash阈值50分
        pro_batch_size=10,   # Pro每批10人
        pro_threshold=70     # 最终阈值70分
    )
    
    if not final_candidates:
        print("\n⚠ 没有候选人通过两阶段筛选")
        print("提示：可以降低阈值或扩大搜索范围")
        return False
    
    print(f"\n✓ 两阶段筛选完成，{len(final_candidates)} 位候选人通过")
    
    # 显示最终结果
    print("\n最终候选人详情：")
    for i, c in enumerate(final_candidates[:5], 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        print(f"   Flash分数: {c.get('flash_score', 0)}")
        print(f"   Pro分数: {c.get('final_score', 0)}")
        print(f"   职位: {c.get('current_title') or c.get('title', 'N/A')}")
        print(f"   公司: {c.get('current_company') or c.get('company', 'N/A')}")
        reasons = c.get('推荐理由', [])
        if reasons:
            print(f"   推荐理由: {', '.join(reasons[:2])}")
    
    # 步骤4：导出Google Sheets
    print("\n" + "="*60)
    print("步骤4：批量导出到Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            final_candidates,
            requirement_text=requirement_text,
            job_title="OD_TwoStage_Test",
            share_emails=["sailerg318@gmail.com"]
        )
        
        if url:
            print(f"\n{'='*60}")
            print("✅ 测试完成！")
            print(f"{'='*60}")
            print(f"\n✓ Google Sheets链接: {url}")
            print(f"✓ 已分享给: sailerg318@gmail.com")
            print(f"✓ 导出候选人数: {len(final_candidates)}")
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
        success = test_two_stage_screening()
        
        if success:
            print("\n" + "="*60)
            print("🎉 两阶段细筛测试成功完成！")
            print("="*60)
            print("\n两阶段策略优势：")
            print("✓ Flash快速筛选，节省Pro成本")
            print("✓ Pro分批处理，避免超时")
            print("✓ 双重阈值，确保质量")
            print("✓ 批量导出，高效管理")
        else:
            print("\n" + "="*60)
            print("⚠ 测试未完全成功")
            print("="*60)
            print("\n可能的原因：")
            print("- Tavily API配置问题")
            print("- 候选人数量不足")
            print("- 阈值设置过高")
            print("- Google Sheets凭证问题")
            
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
    except Exception as e:
        print(f"\n\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
