#!/usr/bin/env python3
"""
快速运行脚本 - 无 Google Sheets 版本（仅测试搜索和翻页）
"""

from streaming_pipeline import StreamingPipeline
from requirement_parser import RequirementParser
from unified_searcher import UnifiedSearcher
import json


def main():
    """快速运行 - 不使用 Google Sheets"""
    print("\n" + "="*70)
    print("LinkedIn 招聘系统 - 搜索测试（无 Google Sheets）")
    print("="*70)
    
    # 获取用户输入
    print("\n请输入招聘需求（直接回车使用默认示例）:")
    user_input = input("> ").strip()
    
    if not user_input:
        user_input = "我想找 Base 上海的产品经理，5-8年经验，有大厂背景"
        print(f"\n使用默认需求: {user_input}")
    
    # 配置参数
    print("\n配置参数（直接回车使用默认值）:")
    
    engine_input = input("搜索引擎 (serper/gemini/tavily) [serper]: ").strip()
    engine = engine_input if engine_input else "serper"
    
    num_input = input("搜索结果数量 [100]: ").strip()
    num_results = int(num_input) if num_input else 100
    
    # 确认
    print("\n" + "="*70)
    print("配置总结:")
    print("="*70)
    print(f"需求: {user_input}")
    print(f"搜索引擎: {engine}")
    print(f"结果数量: {num_results}")
    
    confirm = input("\n确认开始？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    # 解析需求
    print("\n" + "="*70)
    print("步骤 1: 解析需求")
    print("="*70)
    parser = RequirementParser()
    requirement = parser.parse_requirement(user_input)
    
    # 搜索
    print("\n" + "="*70)
    print("步骤 2: 搜索候选人")
    print("="*70)
    
    searcher = UnifiedSearcher(default_engine=engine, enable_job_expansion=False)
    
    # 构建搜索查询
    job_title = requirement.get('job_title', '')
    location = requirement.get('location', '')
    
    print(f"\n职位: {job_title}")
    print(f"地点: {location}")
    print(f"目标数量: {num_results}")
    print("\n" + "-"*70)
    
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
        print("\n前10位候选人:")
        for i, candidate in enumerate(candidates[:10], 1):
            print(f"\n{i}. {candidate.get('name', 'N/A')}")
            print(f"   职位: {candidate.get('title', 'N/A')}")
            print(f"   公司: {candidate.get('company', 'N/A')}")
            print(f"   URL: {candidate.get('url', 'N/A')}")
        
        # 保存结果
        output_file = f"search_results_{engine}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到: {output_file}")
    else:
        print("\n⚠️ 没有找到任何候选人")


if __name__ == "__main__":
    main()
