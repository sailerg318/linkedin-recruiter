"""
搜索诊断工具 - 测试Tavily搜索是否正常工作
"""

from tavily_search import TavilySearcher


def test_tavily_search():
    """测试Tavily搜索功能"""
    
    print("\n" + "="*60)
    print("Tavily搜索诊断")
    print("="*60)
    
    searcher = TavilySearcher()
    
    # 测试1: 简单搜索
    print("\n测试1: 简单LinkedIn搜索")
    print("-" * 60)
    
    test_queries = [
        {
            "job_title": "Product Manager",
            "location": "London",
            "keywords": "",
            "company": ""
        },
        {
            "job_title": "OD",
            "location": "London",
            "keywords": "",
            "company": ""
        },
        {
            "job_title": "Organizational Development",
            "location": "London",
            "keywords": "",
            "company": ""
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n查询 {i}:")
        print(f"  岗位: {query['job_title']}")
        print(f"  地点: {query['location']}")
        
        try:
            results = searcher.search_linkedin_candidates(
                job_title=query['job_title'],
                location=query['location'],
                keywords=query['keywords'],
                company=query['company'],
                max_results=3
            )
            
            print(f"  结果数: {len(results)}")
            
            if results:
                print(f"  示例结果:")
                for j, r in enumerate(results[:2], 1):
                    print(f"    {j}. {r.get('name', 'Unknown')}")
                    print(f"       职位: {r.get('title', 'N/A')}")
                    print(f"       公司: {r.get('company', 'N/A')}")
            else:
                print(f"  ⚠ 未找到结果")
                
        except Exception as e:
            print(f"  ✗ 搜索失败: {e}")
    
    # 测试2: 检查API配置
    print("\n" + "="*60)
    print("测试2: API配置检查")
    print("="*60)
    
    try:
        # 尝试一个通用搜索
        print("\n执行通用搜索测试...")
        results = searcher.search_linkedin_candidates(
            job_title="Manager",
            location="London",
            max_results=1
        )
        
        if results:
            print("✓ Tavily API配置正常")
            print(f"  找到 {len(results)} 个结果")
        else:
            print("⚠ Tavily API可能配置有问题或搜索限制")
            print("  建议检查:")
            print("  1. TAVILY_API_KEY是否正确配置")
            print("  2. API配额是否充足")
            print("  3. 网络连接是否正常")
            
    except Exception as e:
        print(f"✗ API测试失败: {e}")
        print("\n可能的原因:")
        print("  1. TAVILY_API_KEY未配置或无效")
        print("  2. 网络连接问题")
        print("  3. API服务不可用")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)


if __name__ == "__main__":
    test_tavily_search()
