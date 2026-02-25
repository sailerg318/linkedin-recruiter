"""
Gemini Search完整测试 - 使用Gemini替代Tavily
"""

from requirement_parser import RequirementParser
from optimized_search import OptimizedSearchStrategy
from csv_importer import CandidateImporter
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_gemini_complete_workflow():
    """测试使用Gemini Search的完整工作流程"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - Gemini Search测试")
    print("="*60)
    print("\n使用Gemini 2.5 Pro Search替代Tavily")
    print("优势：无配额限制，理解复杂查询，实时搜索")
    
    # 需求输入
    requirement_text = "我要找Base伦敦的OD，甲乙方经验或者新零售、物流的纯甲方经验，7-15年"
    
    print(f"\n需求：{requirement_text}")
    
    # 步骤1：解析需求
    print("\n" + "="*60)
    print("步骤1：智能需求解析")
    print("="*60)
    parser = RequirementParser()
    parsed_req = parser.parse_requirement(requirement_text)
    
    # 步骤2：Gemini优化搜索
    print("\n" + "="*60)
    print("步骤2：Gemini优化搜索")
    print("="*60)
    print("⚠ 注意：Gemini搜索较慢（5-15秒/次），请耐心等待")
    
    strategy = OptimizedSearchStrategy()
    
    # 使用较少的搜索组合（因为Gemini较慢）
    gemini_candidates = strategy.execute_optimized_search(
        requirement_text,
        max_combinations=10,  # Gemini较慢，减少组合数
        max_results_per_combo=5
    )
    
    print(f"\n✓ Gemini搜索完成，找到 {len(gemini_candidates)} 位候选人")
    
    # 步骤3：CSV导入（可选）
    print("\n" + "="*60)
    print("步骤3：CSV导入（手动补充）")
    print("="*60)
    
    importer = CandidateImporter()
    csv_file = "linkedin_recruiter/candidates_template.csv"
    
    import os
    if os.path.exists(csv_file):
        csv_candidates = importer.import_from_csv(csv_file)
        print(f"✓ CSV导入完成，找到 {len(csv_candidates)} 位候选人")
    else:
        print(f"⚠ CSV文件不存在，跳过CSV导入")
        csv_candidates = []
    
    # 合并候选人
    all_candidates = importer.merge_candidates(gemini_candidates, csv_candidates)
    
    if not all_candidates:
        print("\n✗ 未找到候选人，测试结束")
        print("\n可能的原因：")
        print("- Gemini搜索结果较少")
        print("- 搜索条件过于严格")
        print("- 网络连接问题")
        return False
    
    print(f"\n✓ 总计 {len(all_candidates)} 位候选人")
    
    # 显示候选人信息
    print("\n候选人列表（前10位）：")
    for i, c in enumerate(all_candidates[:10], 1):
        source = c.get('source', 'gemini')
        print(f"  {i}. {c.get('name', 'Unknown')} [{source}]")
        print(f"     职位: {c.get('title', 'N/A')}")
        print(f"     公司: {c.get('company', 'N/A')}")
        if c.get('url'):
            print(f"     URL: {c['url'][:50]}...")
    
    # 步骤4：两阶段细筛
    print("\n" + "="*60)
    print("步骤4：两阶段细筛分析")
    print("="*60)
    
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
        print("提示：可以降低阈值")
        
        # 显示Flash评分情况
        if all_candidates:
            print("\nFlash评分分布：")
            for c in all_candidates[:10]:
                if 'flash_score' in c:
                    print(f"  {c.get('name', 'Unknown')}: {c['flash_score']}分")
        
        return False
    
    print(f"\n✓ 两阶段筛选完成，{len(final_candidates)} 位候选人通过")
    
    # 显示最终结果
    print("\n" + "="*60)
    print("最终候选人详情")
    print("="*60)
    
    for i, c in enumerate(final_candidates[:5], 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        print(f"   来源: {c.get('source', 'gemini')}")
        print(f"   Flash分数: {c.get('flash_score', 0)}")
        print(f"   Pro分数: {c.get('final_score', 0)}")
        print(f"   职位: {c.get('current_title') or c.get('title', 'N/A')}")
        print(f"   公司: {c.get('current_company') or c.get('company', 'N/A')}")
        
        reasons = c.get('推荐理由', [])
        if reasons:
            print(f"   推荐理由:")
            for reason in reasons[:3]:
                print(f"     • {reason}")
    
    # 步骤5：导出Google Sheets
    print("\n" + "="*60)
    print("步骤5：批量导出到Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            final_candidates,
            requirement_text=requirement_text,
            job_title="OD_Gemini",
            share_emails=["sailerg318@gmail.com"]
        )
        
        if url:
            print(f"\n{'='*60}")
            print("✅ 测试完成！")
            print(f"{'='*60}")
            print(f"\n✓ Google Sheets链接: {url}")
            print(f"✓ 已分享给: sailerg318@gmail.com")
            print(f"✓ 导出候选人数: {len(final_candidates)}")
            
            # 显示统计
            print(f"\n{'='*60}")
            print("统计信息")
            print(f"{'='*60}")
            print(f"Gemini搜索: {len(gemini_candidates)} 位")
            print(f"CSV导入: {len(csv_candidates)} 位")
            print(f"合并总数: {len(all_candidates)} 位")
            print(f"最终通过: {len(final_candidates)} 位")
            
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
        success = test_gemini_complete_workflow()
        
        if success:
            print("\n" + "="*60)
            print("🎉 Gemini Search测试成功完成！")
            print("="*60)
            print("\nGemini Search优势：")
            print("✓ 无固定配额限制")
            print("✓ 理解复杂自然语言查询")
            print("✓ 实时搜索，覆盖面更广")
            print("✓ 按使用量付费，灵活可控")
        else:
            print("\n" + "="*60)
            print("⚠ 测试未完全成功")
            print("="*60)
            print("\n可能的原因：")
            print("- Gemini搜索结果较少")
            print("- 候选人不符合筛选条件")
            print("- 阈值设置过高")
            print("\n建议：")
            print("- 降低Flash阈值（如改为40分）")
            print("- 增加搜索组合数量")
            print("- 结合CSV手动补充候选人")
            
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
    except Exception as e:
        print(f"\n\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
