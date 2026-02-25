"""
测试搜索功能 - 验证是否能获取完整LinkedIn主页内容
"""

from tavily_search import TavilySearcher
import json


def test_search():
    """测试搜索功能"""
    print("="*60)
    print("测试LinkedIn搜索功能")
    print("="*60)
    
    searcher = TavilySearcher()
    
    # 测试搜索Python工程师
    job_requirements = {
        "job_title": "Python Engineer",
        "keywords": "AI",
        "location": "San Francisco"
    }
    
    print(f"\n搜索条件:")
    print(f"- 岗位: {job_requirements['job_title']}")
    print(f"- 关键词: {job_requirements['keywords']}")
    print(f"- 地点: {job_requirements['location']}")
    print("\n开始搜索...\n")
    
    candidates = searcher.batch_search(job_requirements)
    
    if not candidates:
        print("\n✗ 未找到候选人")
        return
    
    print(f"\n{'='*60}")
    print(f"找到 {len(candidates)} 位候选人")
    print(f"{'='*60}\n")
    
    # 显示前3个候选人的详细信息
    for i, candidate in enumerate(candidates[:3], 1):
        print(f"\n【候选人 {i}】")
        print(f"姓名: {candidate.get('name', 'N/A')}")
        print(f"职位: {candidate.get('title', 'N/A')}")
        print(f"公司: {candidate.get('company', 'N/A')}")
        print(f"地点: {candidate.get('location', 'N/A')}")
        print(f"LinkedIn: {candidate.get('url', 'N/A')}")
        print(f"相关度分数: {candidate.get('score', 0):.2f}")
        print(f"\n简介片段:")
        print(f"{candidate.get('snippet', 'N/A')[:200]}...")
        
        # 显示原始内容长度
        raw_content = candidate.get('raw_content', '')
        if raw_content:
            print(f"\n✓ 获取到完整内容，长度: {len(raw_content)} 字符")
            print(f"内容预览（前500字符）:")
            print("-" * 60)
            print(raw_content[:500])
            print("-" * 60)
        else:
            print(f"\n⚠ 未获取到完整内容（raw_content为空）")
        
        print("\n" + "="*60)
    
    # 保存第一个候选人的完整数据到文件
    if candidates:
        with open('test_result.json', 'w', encoding='utf-8') as f:
            json.dump(candidates[0], f, ensure_ascii=False, indent=2)
        print(f"\n✓ 第一个候选人的完整数据已保存到 test_result.json")


if __name__ == "__main__":
    test_search()
