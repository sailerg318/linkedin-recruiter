"""
测试端到端 LinkedIn 候选人挖掘系统
"""

import json
from linkedin_end_to_end import end_to_end_search, analyze_requirements


def test_ai_analysis():
    """测试 Module A: AI 需求分析"""
    print("\n" + "="*70)
    print("测试 1: AI 需求分析模块")
    print("="*70)
    
    test_cases = [
        "我想找 Base 伦敦的 Org Development 顾问，7-15年经验，有咨询背景的",
        "寻找纽约的算法交易员，5年以上经验，来自顶级投行或对冲基金",
        "上海的电商运营专家，3-8年经验，有大厂背景"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}: {test_input}")
        result = analyze_requirements(test_input)
        
        print(f"\n分析结果:")
        print(f"  核心关键词: {result.get('base_keyword')}")
        print(f"  目标地点: {result.get('location')}")
        print(f"  目标公司数: {len(result.get('target_companies', []))}")
        print(f"  前5家公司: {', '.join(result.get('target_companies', [])[:5])}")


def test_end_to_end_simple():
    """测试端到端搜索 - 简单案例"""
    print("\n" + "="*70)
    print("测试 2: 端到端搜索 - 简单案例")
    print("="*70)
    
    # 使用一个简单的测试案例，限制搜索范围
    test_input = "上海的产品经理，5年经验"
    
    print(f"\n测试输入: {test_input}")
    
    # 执行搜索
    candidates = end_to_end_search(test_input)
    
    # 显示结果
    print(f"\n搜索结果统计:")
    print(f"  总候选人数: {len(candidates)}")
    
    if candidates:
        print(f"\n前 5 位候选人:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"\n{i}. {candidate['name']}")
            print(f"   职位: {candidate['title']}")
            print(f"   URL: {candidate['url']}")
            print(f"   简介: {candidate['snippet'][:80]}...")
    
    return candidates


def test_end_to_end_full():
    """测试端到端搜索 - 完整案例"""
    print("\n" + "="*70)
    print("测试 3: 端到端搜索 - 完整案例")
    print("="*70)
    
    test_input = "我想找 Base 伦敦的 Org Development 顾问，7-15年经验，有咨询背景的"
    
    print(f"\n测试输入: {test_input}")
    
    # 执行搜索
    candidates = end_to_end_search(test_input)
    
    # 保存结果到 JSON
    output_file = "linkedin_recruiter/test_end_to_end_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "query": test_input,
            "total_candidates": len(candidates),
            "candidates": candidates
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    
    # 显示统计
    print(f"\n搜索结果统计:")
    print(f"  总候选人数: {len(candidates)}")
    
    if candidates:
        print(f"\n前 10 位候选人:")
        for i, candidate in enumerate(candidates[:10], 1):
            print(f"\n{i}. {candidate['name']}")
            print(f"   职位: {candidate['title']}")
            print(f"   URL: {candidate['url']}")
    
    return candidates


def test_deduplication():
    """测试去重功能"""
    print("\n" + "="*70)
    print("测试 4: 去重功能验证")
    print("="*70)
    
    test_input = "上海的产品经理"
    
    candidates = end_to_end_search(test_input)
    
    # 检查是否有重复的 URL
    urls = [c['url'] for c in candidates]
    unique_urls = set(urls)
    
    print(f"\n去重验证:")
    print(f"  总候选人数: {len(candidates)}")
    print(f"  唯一 URL 数: {len(unique_urls)}")
    print(f"  是否有重复: {'否' if len(urls) == len(unique_urls) else '是'}")
    
    if len(urls) != len(unique_urls):
        print(f"  重复数量: {len(urls) - len(unique_urls)}")


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("LinkedIn 端到端系统测试套件")
    print("#"*70)
    
    # 选择要运行的测试
    print("\n请选择测试:")
    print("1. 测试 AI 需求分析模块")
    print("2. 测试端到端搜索 - 简单案例")
    print("3. 测试端到端搜索 - 完整案例")
    print("4. 测试去重功能")
    print("5. 运行所有测试")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == "1":
        test_ai_analysis()
    elif choice == "2":
        test_end_to_end_simple()
    elif choice == "3":
        test_end_to_end_full()
    elif choice == "4":
        test_deduplication()
    elif choice == "5":
        test_ai_analysis()
        test_end_to_end_simple()
        test_deduplication()
    else:
        print("无效选择，运行默认测试...")
        test_ai_analysis()
    
    print("\n" + "#"*70)
    print("测试完成")
    print("#"*70)
