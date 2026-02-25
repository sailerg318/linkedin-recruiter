"""
完整流程示例 - 搜索 + 细筛 + 导出
演示如何使用 LinkedIn 招聘系统的完整功能
"""

from recruiter_pro import LinkedInRecruiterPro


def example_full_pipeline():
    """
    示例：完整流程
    搜索 → 细筛 → 导出到 Google Sheets
    """
    print("\n" + "="*70)
    print("示例：完整流程（搜索 + 细筛 + 导出）")
    print("="*70)
    
    # 创建招聘系统实例
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    # 用户需求
    user_input = "我想找 Base 上海的产品经理，5年经验，有大厂背景"
    
    # 执行完整流程
    result = recruiter.full_pipeline(
        user_input=user_input,
        engine="serper",
        flash_threshold=50,      # Flash 粗筛阈值
        pro_batch_size=10,       # Pro 精筛批次大小
        pro_threshold=70,        # Pro 最终阈值
        export_format="markdown",  # 导出格式: google_sheets/markdown/json
        share_emails=None        # Google Sheets 分享邮箱（如果使用）
    )
    
    print(f"\n最终结果:")
    print(f"  搜索到: {len(result['candidates'])} 位候选人")
    print(f"  细筛通过: {len(result['analyzed'])} 位候选人")
    if result['url']:
        print(f"  Google Sheets: {result['url']}")


def example_search_only():
    """
    示例：仅搜索
    端到端搜索，不进行细筛
    """
    print("\n" + "="*70)
    print("示例：仅搜索（端到端）")
    print("="*70)
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    # 端到端搜索
    candidates = recruiter.search_end_to_end(
        "上海的产品经理，5年经验",
        engine="serper"
    )
    
    # 导出为 Markdown
    recruiter.export_to_markdown(candidates, "search_results.md")
    
    print(f"\n找到 {len(candidates)} 位候选人")


def example_search_and_filter():
    """
    示例：搜索 + 粗筛
    使用简单的关键词筛选
    """
    print("\n" + "="*70)
    print("示例：搜索 + 粗筛")
    print("="*70)
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    # 搜索 + 筛选
    filter_requirements = {
        "required_keywords": ["Product", "Manager"],
        "min_score": 0.6,
        "min_experience": 3
    }
    
    candidates = recruiter.search_with_filter(
        job_title="Product Manager",
        location="Shanghai",
        num_results=100,
        filter_requirements=filter_requirements
    )
    
    # 导出
    recruiter.export_to_json(candidates, "filtered_results.json")
    
    print(f"\n筛选后: {len(candidates)} 位候选人")


def example_search_and_detailed_screening():
    """
    示例：搜索 + 细筛
    使用 Flash + Pro 组合分析
    """
    print("\n" + "="*70)
    print("示例：搜索 + 细筛")
    print("="*70)
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    # 1. 搜索
    user_input = "我想找 Base 伦敦的 OD 顾问，7-15年经验，有咨询背景"
    candidates = recruiter.search_end_to_end(user_input, engine="serper")
    
    print(f"\n搜索到 {len(candidates)} 位候选人")
    
    # 2. 解析需求
    requirement = recruiter.analyze_requirement(user_input)
    
    # 3. 细筛（两阶段）
    analyzed = recruiter.screen_candidates_two_stage(
        candidates=candidates,
        requirement=requirement,
        flash_threshold=50,
        pro_batch_size=10,
        pro_threshold=70
    )
    
    print(f"\n细筛通过 {len(analyzed)} 位候选人")
    
    # 4. 导出
    recruiter.export_to_markdown(analyzed, "detailed_screening_results.md")


def example_multi_engine_search():
    """
    示例：多引擎搜索
    同时使用 Serper + Gemini + Tavily
    """
    print("\n" + "="*70)
    print("示例：多引擎搜索")
    print("="*70)
    
    recruiter = LinkedInRecruiterPro()
    
    # 多引擎搜索
    candidates = recruiter.search_multi_engine(
        job_title="Product Manager",
        location="Shanghai",
        num_results=50
    )
    
    print(f"\n多引擎搜索找到 {len(candidates)} 位候选人")
    
    # 导出
    recruiter.export_to_json(candidates, "multi_engine_results.json")


def example_export_to_google_sheets():
    """
    示例：导出到 Google Sheets
    需要先配置 google_credentials.json
    """
    print("\n" + "="*70)
    print("示例：导出到 Google Sheets")
    print("="*70)
    
    recruiter = LinkedInRecruiterPro(
        default_engine="serper",
        google_credentials="google_credentials.json"
    )
    
    # 假设已经有细筛后的候选人
    # 这里使用模拟数据
    analyzed_candidates = [
        {
            "name": "张三",
            "final_score": 85,
            "flash_score": 75,
            "职位匹配": {"匹配": "✅"},
            "年限匹配": {"匹配": "✅"},
            "背景匹配": {"匹配": "✅", "咨询经验": "McKinsey 3年", "甲方经验": "Google 5年"},
            "地点匹配": {"匹配": "✅"},
            "current_title": "Senior Product Manager",
            "current_company": "Alibaba",
            "experience_years": 8,
            "url": "https://linkedin.com/in/zhangsan",
            "推荐理由": ["职位完全匹配", "大厂背景", "年限符合"]
        }
    ]
    
    # 导出到 Google Sheets
    url = recruiter.export_to_google_sheets(
        candidates=analyzed_candidates,
        requirement_text="上海的产品经理，5年经验，有大厂背景",
        job_title="Product Manager",
        share_emails=["client@example.com"]  # 可选：分享给客户
    )
    
    if url:
        print(f"\nGoogle Sheets URL: {url}")
    else:
        print("\n注意：需要先配置 google_credentials.json")


def main():
    """主函数 - 选择要运行的示例"""
    
    print("\n" + "#"*70)
    print("LinkedIn 招聘系统 - 完整流程示例")
    print("#"*70)
    
    print("\n请选择要运行的示例:")
    print("1. 完整流程（搜索 + 细筛 + 导出）")
    print("2. 仅搜索（端到端）")
    print("3. 搜索 + 粗筛")
    print("4. 搜索 + 细筛")
    print("5. 多引擎搜索")
    print("6. 导出到 Google Sheets")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    if choice == "1":
        example_full_pipeline()
    elif choice == "2":
        example_search_only()
    elif choice == "3":
        example_search_and_filter()
    elif choice == "4":
        example_search_and_detailed_screening()
    elif choice == "5":
        example_multi_engine_search()
    elif choice == "6":
        example_export_to_google_sheets()
    else:
        print("无效选择")
    
    print("\n" + "#"*70)
    print("示例完成")
    print("#"*70)


if __name__ == "__main__":
    main()
