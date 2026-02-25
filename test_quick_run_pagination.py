"""
测试 quick_run 中的翻页功能
"""

from unified_searcher import UnifiedSearcher


def test_unified_searcher_pagination():
    """测试 UnifiedSearcher 的翻页功能"""
    print("=" * 70)
    print("测试 UnifiedSearcher 翻页功能")
    print("=" * 70)
    
    searcher = UnifiedSearcher(
        default_engine="serper",
        enable_job_expansion=False  # 关闭岗位扩展，简化测试
    )
    
    # 测试直接查询
    query = 'site:linkedin.com/in/ "Product Manager" "San Francisco"'
    print(f"\n搜索查询: {query}")
    print(f"目标结果数: 100")
    print("\n" + "-" * 70)
    
    results = searcher.search(
        query=query,
        num_results=100,
        engine="serper"
    )
    
    print("\n" + "=" * 70)
    print("搜索结果")
    print("=" * 70)
    print(f"总共找到: {len(results)} 位候选人")
    
    if results:
        print(f"\n前3位候选人:")
        for i, candidate in enumerate(results[:3], 1):
            print(f"{i}. {candidate.get('name', 'N/A')}")
            print(f"   URL: {candidate.get('url', 'N/A')}")


if __name__ == "__main__":
    test_unified_searcher_pagination()
