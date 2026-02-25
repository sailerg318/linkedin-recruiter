"""
测试Serper翻页功能
"""

import sys
import json
from serper_search import SerperSearcher


def test_pagination():
    """测试翻页功能"""
    print("=" * 60)
    print("测试 Serper 翻页功能")
    print("=" * 60)
    
    searcher = SerperSearcher()
    
    # 测试查询
    query = 'site:linkedin.com/in/ "Product Manager" "San Francisco"'
    print(f"\n搜索查询: {query}")
    print(f"目标结果数: 30 (预期3页)")
    print(f"最大翻页数: 5")
    print("\n" + "-" * 60)
    
    # 执行搜索
    results = searcher.search_linkedin(
        query=query,
        num_results=30,
        max_pages=5
    )
    
    print("\n" + "=" * 60)
    print("搜索结果汇总")
    print("=" * 60)
    print(f"总共找到: {len(results)} 位候选人")
    
    if results:
        print("\n前5位候选人:")
        for i, candidate in enumerate(results[:5], 1):
            print(f"\n{i}. {candidate.get('name', 'N/A')}")
            print(f"   职位: {candidate.get('title', 'N/A')}")
            print(f"   URL: {candidate.get('url', 'N/A')}")
            print(f"   简介: {candidate.get('snippet', 'N/A')[:100]}...")
        
        # 保存完整结果
        output_file = "serper_pagination_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n完整结果已保存到: {output_file}")
    else:
        print("\n⚠️ 没有找到任何结果")
        print("\n可能的原因:")
        print("1. API Key 无效或已过期")
        print("2. 搜索查询没有匹配结果")
        print("3. API 请求失败")
        print("4. 网络连接问题")


def test_single_page():
    """测试单页请求"""
    print("\n" + "=" * 60)
    print("测试单页请求（调试模式）")
    print("=" * 60)
    
    import requests
    
    api_key = "d88085d4543221682eecd92082f27247f71d902f"
    url = "https://google.serper.dev/search"
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # 测试第1页
    print("\n测试第1页 (start=0):")
    payload = {
        'q': 'site:linkedin.com/in/ "Product Manager" "San Francisco"',
        'num': 10,
        'start': 0,
        'gl': 'cn',
        'hl': 'zh-cn'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            organic = data.get('organic', [])
            print(f"返回结果数: {len(organic)}")
            
            if organic:
                print("\n前3个结果:")
                for i, result in enumerate(organic[:3], 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   URL: {result.get('link', 'N/A')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试第2页
    print("\n测试第2页 (start=10):")
    payload['start'] = 10
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            organic = data.get('organic', [])
            print(f"返回结果数: {len(organic)}")
            
            if organic:
                print("\n前3个结果:")
                for i, result in enumerate(organic[:3], 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   URL: {result.get('link', 'N/A')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")


if __name__ == "__main__":
    # 测试翻页功能
    test_pagination()
    
    # 测试单页请求（调试）
    test_single_page()
