#!/usr/bin/env python3
"""
诊断 Pro 分析功能
测试 LLM API 调用和 Pro 分析流程
"""

from detailed_screening import DetailedScreening
import json


def test_pro_analysis():
    """测试 Pro 分析"""
    print("\n" + "="*70)
    print("Pro 分析诊断")
    print("="*70)
    
    # 初始化筛选器
    screening = DetailedScreening()
    
    print(f"\n配置信息:")
    print(f"  API Base: {screening.api_base}")
    print(f"  Flash Model: {screening.flash_model}")
    print(f"  Pro Model: {screening.pro_model}")
    print(f"  API Key: {screening.api_key[:20]}...")
    
    # 测试候选人
    test_candidate = {
        "name": "张三",
        "current_title": "Senior Product Manager",
        "current_company": "Google",
        "location": "上海",
        "experience_years": 7,
        "snippet": "7年产品经验，曾在阿里巴巴、腾讯工作，现任 Google 高级产品经理",
        "url": "https://linkedin.com/in/test"
    }
    
    # 测试需求
    test_requirement = {
        "job_title": "Product Manager",
        "location": "上海",
        "location_keywords": ["上海", "Shanghai"],
        "experience_years": {"min": 5, "max": 10},
        "experience_years_list": [5, 6, 7, 8, 9, 10],
        "background": {"consulting": False, "corporate": True},
        "consulting_companies": []
    }
    
    print("\n" + "="*70)
    print("测试 1: Flash 分析")
    print("="*70)
    
    try:
        flash_result = screening._flash_analyze_single(test_candidate, test_requirement)
        print(f"\n✓ Flash 分析成功")
        print(f"  Flash 分数: {flash_result.get('flash_score', 'N/A')}")
        print(f"  结果: {json.dumps(flash_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"\n✗ Flash 分析失败: {e}")
        import traceback
        print(f"\n详细错误:\n{traceback.format_exc()}")
        return
    
    print("\n" + "="*70)
    print("测试 2: Pro 分析")
    print("="*70)
    
    try:
        pro_result = screening._pro_analyze_single(test_candidate, test_requirement)
        print(f"\n✓ Pro 分析成功")
        print(f"  Final 分数: {pro_result.get('final_score', 'N/A')}")
        print(f"  结果: {json.dumps(pro_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"\n✗ Pro 分析失败: {e}")
        import traceback
        print(f"\n详细错误:\n{traceback.format_exc()}")
        
        # 分析错误类型
        error_str = str(e).lower()
        print("\n可能的原因:")
        
        if "timeout" in error_str or "timed out" in error_str:
            print("  • API 超时")
            print("    解决: 增加超时时间或切换 LLM 提供商")
        
        elif "503" in error_str or "service unavailable" in error_str:
            print("  • 服务不可用")
            print("    解决: 等待服务恢复或切换 LLM 提供商")
        
        elif "401" in error_str or "unauthorized" in error_str:
            print("  • API Key 无效")
            print("    解决: 检查 llm_config.py 中的 API Key")
        
        elif "429" in error_str or "rate limit" in error_str:
            print("  • 速率限制")
            print("    解决: 等待或升级 API 计划")
        
        else:
            print("  • 未知错误")
            print("    建议: 查看上面的详细错误信息")
        
        return
    
    print("\n" + "="*70)
    print("测试 3: 完整流程")
    print("="*70)
    
    try:
        candidates = [test_candidate]
        result = screening.screen_candidates(
            candidates=candidates,
            requirement=test_requirement,
            flash_threshold=50,
            max_pro_analysis=1
        )
        
        print(f"\n✓ 完整流程成功")
        print(f"  通过筛选: {len(result)} 位")
        if result:
            print(f"  第一位候选人:")
            print(f"    Flash 分数: {result[0].get('flash_score', 'N/A')}")
            print(f"    Final 分数: {result[0].get('final_score', 'N/A')}")
            
    except Exception as e:
        print(f"\n✗ 完整流程失败: {e}")
        import traceback
        print(f"\n详细错误:\n{traceback.format_exc()}")
    
    print("\n" + "="*70)
    print("诊断完成")
    print("="*70)


if __name__ == "__main__":
    test_pro_analysis()
