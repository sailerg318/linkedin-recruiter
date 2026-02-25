#!/usr/bin/env python3
"""
自动测试搜索和翻页功能
"""

from unified_searcher import UnifiedSearcher
from requirement_parser import RequirementParser
import json


def test_search_pagination():
    """测试搜索和翻页功能"""
    print("\n" + "="*70)
    print("测试搜索和翻页功能")
    print("="*70)
    
    # 测试需求
    user_input = "我想找 Base 上海的产品经理，5-8年经验，有大厂背景"
    engine = "serper"
    num_results = 100
    
    print(f"\n需求: {user_input}")
    print(f"搜索引擎: {engine}")
    print(f"结果数量: {num_results}")
    
    # 解析需求
    print("\n" + "="*70)
    print("步骤 1: 解析需求")
    print("="*70)
    parser = RequirementParser()
    requirement = parser.parse_requirement(user_input)
    
    # 搜索
    print("\n" + "="*70)
    print("步骤 2: 搜索候选人（观察翻页信息）")
    print("="*70)
    
    searcher = UnifiedSearcher(default_engine=engine, enable_job_expansion=False)
    
    job_title = requirement.get('job_title', '')
    location = requirement.get('location', '')
    
    print(f"\n职位: {job_title}")
    print(f"地点: {location}")
    print(f"目标数量: {num_results}")
    print("\n" + "-"*70)
    print("开始搜索...\n")
    
    candidates = searcher.search(
        job_title=job_title,
        location=location,
        num_results=num_results,
        engine=engine
    )
    
    # 显示结果
    print("\n" + "="*70)
    print("搜索完成")
    print("="*70)
    print(f"总共找到: {len(candidates)} 位候选人")
    
    if candidates:
        print("\n前5位候选人:")
        for i, candidate in enumerate(candidates[:5], 1):
            print(f"\n{i}. {candidate.get('name', 'N/A')}")
            print(f"   职位: {candidate.get('title', 'N/A')}")
            print(f"   URL: {candidate.get('url', 'N/A')}")
        
        # 保存结果
        output_file = f"search_results_auto.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到: {output_file}")
    else:
        print("\n⚠️ 没有找到任何候选人")


if __name__ == "__main__":
    test_search_pagination()
