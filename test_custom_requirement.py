"""
自定义需求测试
需求：Base伦敦的OD，甲乙方经验或者新零售、物流的纯甲方经验，7-15年
"""

from requirement_parser import RequirementParser
from exhaustive_search import ExhaustiveSearchStrategy
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


def test_custom_requirement():
    """测试自定义需求"""
    
    print("\n" + "="*60)
    print("LinkedIn智能招聘系统 - 自定义需求测试")
    print("="*60)
    
    # 需求输入
    requirement_text = "我要找Base伦敦的OD，甲乙方经验或者新零售、物流的纯甲方经验，7-15年"
    
    print(f"\n需求：{requirement_text}")
    
    # 步骤1：解析需求
    print("\n" + "="*60)
    print("步骤1：智能需求解析")
    print("="*60)
    parser = RequirementParser()
    parsed_req = parser.parse_requirement(requirement_text)
    
    print("\n解析结果：")
    print(f"  职位: {parsed_req.get('job_title')}")
    print(f"  地点: {parsed_req.get('location')}")
    print(f"  年限: {parsed_req.get('experience_years')}")
    print(f"  背景: {parsed_req.get('background')}")
    print(f"  行业: {parsed_req.get('company_type')}")
    print(f"  其他要求: {parsed_req.get('other_requirements')}")
    
    # 步骤2：穷尽搜索
    print("\n" + "="*60)
    print("步骤2：穷尽搜索LinkedIn")
    print("="*60)
    print("⚠ 测试模式：限制搜索组合数=3，每组结果数=5")
    
    strategy = ExhaustiveSearchStrategy()
    candidates = strategy.execute_exhaustive_search(
        requirement_text,
        max_combinations=3,
        max_results_per_combo=5
    )
    
    if not candidates:
        print("\n✗ 未找到候选人，测试结束")
        print("提示：请检查Tavily API配置")
        return False
    
    print(f"\n✓ 粗筛完成，找到 {len(candidates)} 位候选人")
    
    # 显示候选人信息
    print("\n候选人列表（前10位）：")
    for i, c in enumerate(candidates[:10], 1):
        print(f"  {i}. {c.get('name', 'Unknown')}")
        print(f"     职位: {c.get('title', 'N/A')}")
        print(f"     公司: {c.get('company', 'N/A')}")
        print(f"     简介: {c.get('snippet', '')[:100]}...")
        print()
    
    # 步骤3：两阶段细筛
    print("\n" + "="*60)
    print("步骤3：两阶段细筛分析")
    print("="*60)
    print("策略：")
    print("  - 阶段1: Flash 50分快速筛选")
    print("    * 评估职位、年限、地点匹配")
    print("    * 识别甲乙方背景")
    print("    * 识别新零售/物流行业经验")
    print("  - 阶段2: Pro 10人一批深度分析")
    print("  - 最终阈值: 70分")
    
    screening = DetailedScreening()
    final_candidates = screening.screen_candidates_two_stage(
        candidates,
        parsed_req,
        flash_threshold=50,
        pro_batch_size=10,
        pro_threshold=70
    )
    
    if not final_candidates:
        print("\n⚠ 没有候选人通过两阶段筛选")
        print("提示：可以降低阈值或扩大搜索范围")
        
        # 显示Flash评分情况
        print("\nFlash评分分布：")
        flash_scores = [(c.get('name', 'Unknown'), c.get('flash_score', 0)) 
                       for c in candidates if 'flash_score' in c]
        flash_scores.sort(key=lambda x: x[1], reverse=True)
        for name, score in flash_scores[:10]:
            print(f"  {name}: {score}分")
        
        return False
    
    print(f"\n✓ 两阶段筛选完成，{len(final_candidates)} 位候选人通过")
    
    # 显示最终结果
    print("\n" + "="*60)
    print("最终候选人详情")
    print("="*60)
    
    for i, c in enumerate(final_candidates, 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        print(f"   Flash分数: {c.get('flash_score', 0)}")
        print(f"   Pro分数: {c.get('final_score', 0)}")
        print(f"   职位: {c.get('current_title') or c.get('title', 'N/A')}")
        print(f"   公司: {c.get('current_company') or c.get('company', 'N/A')}")
        print(f"   地点: {c.get('location', 'N/A')}")
        
        # 匹配信息
        if '职位匹配' in c:
            print(f"   职位匹配: {c['职位匹配'].get('匹配', '❓')}")
        if '年限匹配' in c:
            print(f"   年限匹配: {c['年限匹配'].get('匹配', '❓')}")
        if '背景匹配' in c:
            bg = c['背景匹配']
            print(f"   背景匹配: {bg.get('匹配', '❓')}")
            if bg.get('咨询经验'):
                print(f"     咨询经验: {bg['咨询经验']}")
            if bg.get('甲方经验'):
                print(f"     甲方经验: {bg['甲方经验']}")
        
        reasons = c.get('推荐理由', [])
        if reasons:
            print(f"   推荐理由:")
            for reason in reasons[:3]:
                print(f"     • {reason}")
    
    # 步骤4：导出Google Sheets
    print("\n" + "="*60)
    print("步骤4：批量导出到Google Sheets")
    print("="*60)
    
    exporter = GoogleSheetsExporter()
    
    try:
        url = exporter.export_candidates(
            final_candidates,
            requirement_text=requirement_text,
            job_title="OD_London_Custom",
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
        success = test_custom_requirement()
        
        if success:
            print("\n" + "="*60)
            print("🎉 自定义需求测试成功完成！")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠ 测试未完全成功")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n\n⚠ 测试被用户中断")
    except Exception as e:
        print(f"\n\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
