"""
完整优化测试 - 整合所有短期优化方案
包括：优化搜索、CSV导入、配额管理、两阶段细筛
"""

from requirement_parser import RequirementParser
from optimized_search import OptimizedSearchStrategy
from csv_importer import CandidateImporter
from search_scheduler import SearchScheduler
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_complete_optimized_workflow():
    """测试完整的优化工作流程"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 完整优化测试")
    print("="*60)
    print("\n优化功能：")
    print("✓ 优化搜索策略（增加搜索组合）")
    print("✓ CSV导入（手动补充候选人）")
    print("✓ 配额管理（避免API超限）")
    print("✓ 两阶段细筛（Flash + Pro）")
    print("✓ 批量导出Google Sheets")
    
    # 需求输入
    requirement_text = "我要找Base伦敦的OD，甲乙方经验或者新零售、物流的纯甲方经验，7-15年"
    
    print(f"\n需求：{requirement_text}")
    
    # 步骤1：解析需求
    print("\n" + "="*60)
    print("步骤1：智能需求解析")
    print("="*60)
    parser = RequirementParser()
    parsed_req = parser.parse_requirement(requirement_text)
    
    # 步骤2：优化搜索（带配额管理）
    print("\n" + "="*60)
    print("步骤2：优化搜索（配额管理）")
    print("="*60)
    
    # 创建搜索调度器
    scheduler = SearchScheduler(daily_limit=50)  # 设置每日限制50次
    scheduler.print_stats()
    
    # 使用优化搜索策略
    strategy = OptimizedSearchStrategy()
    combinations = strategy.generate_optimized_combinations(
        parsed_req,
        max_combinations=20  # 生成20个搜索组合
    )
    
    # 使用调度器执行搜索
    tavily_candidates = scheduler.batch_search_with_quota(
        combinations,
        max_results_per_combo=5
    )
    
    print(f"\n✓ Tavily搜索完成，找到 {len(tavily_candidates)} 位候选人")
    
    # 步骤3：CSV导入（可选）
    print("\n" + "="*60)
    print("步骤3：CSV导入（手动补充）")
    print("="*60)
    
    importer = CandidateImporter()
    csv_file = "linkedin_recruiter/candidates_template.csv"
    
    # 检查CSV文件是否存在
    import os
    if os.path.exists(csv_file):
        csv_candidates = importer.import_from_csv(csv_file)
        print(f"✓ CSV导入完成，找到 {len(csv_candidates)} 位候选人")
    else:
        print(f"⚠ CSV文件不存在: {csv_file}")
        print(f"  提示：运行 python3 csv_importer.py 创建模板")
        csv_candidates = []
    
    # 合并候选人
    all_candidates = importer.merge_candidates(tavily_candidates, csv_candidates)
    
    if not all_candidates:
        print("\n✗ 未找到候选人，测试结束")
        return False
    
    print(f"\n✓ 总计 {len(all_candidates)} 位候选人")
    
    # 显示候选人信息
    print("\n候选人列表（前10位）：")
    for i, c in enumerate(all_candidates[:10], 1):
        source = c.get('source', 'tavily')
        print(f"  {i}. {c.get('name', 'Unknown')} [{source}]")
        print(f"     职位: {c.get('title', 'N/A')}")
        print(f"     公司: {c.get('company', 'N/A')}")
    
    # 步骤4：两阶段细筛
    print("\n" + "="*60)
    print("步骤4：两阶段细筛分析")
    print("="*60)
    print("策略：")
    print("  - 阶段1: Flash 50分快速筛选")
    print("  - 阶段2: Pro 10人一批深度分析")
    print("  - 最终阈值: 70分")
    
    screening = DetailedScreening()
    final_candidates = screening.screen_candidates_two_stage(
        all_candidates,
        parsed_req,
        flash_threshold=50,
        pro_batch_size=10,
        pro_threshold=70
    )
    
    if not final_candidates:
        print("\n⚠ 没有候选人通过两阶段筛选")
        print("提示：可以降低阈值或扩大搜索范围")
        return False
    
    print(f"\n✓ 两阶段筛选完成，{len(final_candidates)} 位候选人通过")
    
    # 显示最终结果
    print("\n" + "="*60)
    print("最终候选人详情")
    print("="*60)
    
    for i, c in enumerate(final_candidates[:5], 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        print(f"   来源: {c.get('source', 'tavily')}")
        print(f"   Flash分数: {c.get('flash_score', 0)}")
        print(f"   Pro分数: {c.get('final_score', 0)}")
        print(f"   职位: {c.get('current_title') or c.get('title', 'N/A')}")
        print(f"   公司: {c.get('current_company') or c.get('company', 'N/A')}")
        
        reasons = c.get('推荐理由', [])
        if reasons:
            print(f"   推荐理由: {', '.join(reasons[:2])}")
    
    # 步骤5：导出Google Sheets
    print("\n" + "="*60)
    print("步骤5：批量导出到Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            final_candidates,
            requirement_text=requirement_text,
            job_title="OD_Optimized",
            share_emails=["sailerg318@gmail.com"]
        )
        
        if url:
            print(f"\n{'='*60}")
            print("✅ 测试完成！")
            print(f"{'='*60}")
            print(f"\n✓ Google Sheets链接: {url}")
            print(f"✓ 已分享给: sailerg318@gmail.com")
            print(f"✓ 导出候选人数: {len(final_candidates)}")
            
            # 显示最终统计
            print(f"\n{'='*60}")
            print("最终统计")
            print(f"{'='*60}")
            print(f"Tavily搜索: {len(tavily_candidates)} 位")
            print(f"CSV导入: {len(csv_candidates)} 位")
            print(f"合并总数: {len(all_candidates)} 位")
            print(f"Flash通过: {len([c for c in all_candidates if c.get('flash_score', 0) >= 50])} 位")
            print(f"最终通过: {len(final_candidates)} 位")
            
            # 显示配额使用情况
            scheduler.print_stats()
            
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
        success = test_complete_optimized_workflow()
        
        if success:
            print("\n" + "="*60)
            print("🎉 完整优化测试成功完成！")
            print("="*60)
            print("\n优化效果：")
            print("✓ 搜索组合增加，候选人发现率提升")
            print("✓ CSV导入补充，数据来源多样化")
            print("✓ 配额管理，避免API超限")
            print("✓ 两阶段细筛，提高筛选效率")
            print("✓ 批量导出，便捷管理")
        else:
            print("\n" + "="*60)
            print("⚠ 测试未完全成功")
            print("="*60)
            print("\n可能的原因：")
            print("- Tavily API配额不足")
            print("- 候选人数量较少")
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
