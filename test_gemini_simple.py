"""
Gemini Search简单测试 - 测试单次搜索功能
"""

from gemini_search import GeminiSearcher


def test_single_gemini_search():
    """测试单次Gemini搜索"""
    
    print("\n" + "="*60)
    print("Gemini Search简单测试")
    print("="*60)
    
    searcher = GeminiSearcher()
    
    # 测试搜索
    print("\n搜索条件:")
    print("  岗位: Organizational Development")
    print("  地点: London")
    print("  最大结果: 5")
    
    print("\n⚠ Gemini搜索需要5-15秒，请耐心等待...")
    
    try:
        candidates = searcher.search_linkedin_with_gemini(
            job_title="Organizational Development",
            location="London",
            max_results=5
        )
        
        if candidates:
            print(f"\n✓ 搜索成功！找到 {len(candidates)} 位候选人")
            print("\n候选人列表:")
            print("="*60)
            
            for i, c in enumerate(candidates, 1):
                print(f"\n{i}. {c.get('name', 'Unknown')}")
                print(f"   职位: {c.get('title', 'N/A')}")
                print(f"   公司: {c.get('company', 'N/A')}")
                print(f"   地点: {c.get('location', 'N/A')}")
                if c.get('url'):
                    print(f"   LinkedIn: {c['url']}")
                if c.get('snippet'):
                    snippet = c['snippet'][:150]
                    print(f"   简介: {snippet}...")
            
            print("\n" + "="*60)
            print("✅ 测试成功！")
            print("="*60)
            print("\nGemini Search可以正常工作")
            print("可以继续使用完整的测试流程")
            
            return True
        else:
            print("\n⚠ 未找到候选人")
            print("\n可能的原因:")
            print("- Gemini搜索结果为空")
            print("- 搜索条件过于严格")
            print("- LinkedIn内容限制")
            
            return False
            
    except Exception as e:
        print(f"\n✗ 搜索失败: {e}")
        print("\n可能的原因:")
        print("- API密钥配置问题")
        print("- 网络连接问题")
        print("- Gemini API服务问题")
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    test_single_gemini_search()
