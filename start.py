#!/usr/bin/env python3
"""
LinkedIn 招聘系统 - 启动脚本
快速启动各种功能
"""

import sys


def show_menu():
    """显示主菜单"""
    print("\n" + "="*70)
    print("LinkedIn 招聘系统")
    print("="*70)
    print("\n请选择功能:")
    print("\n【推荐】流式处理（效率最高）")
    print("  1. 流式处理 - 边搜索边筛选边导出")
    print("\n【标准】批量处理")
    print("  2. 完整流程 - 搜索 + 细筛 + 导出")
    print("  3. 端到端搜索 - 仅搜索，不筛选")
    print("  4. 搜索 + 粗筛 - 简单关键词筛选")
    print("\n【高级】自定义")
    print("  5. 多引擎搜索 - 使用所有搜索引擎")
    print("  6. 仅需求分析 - 不执行搜索")
    print("\n【其他】")
    print("  7. 查看示例")
    print("  0. 退出")
    print("\n" + "="*70)


def streaming_mode():
    """流式处理模式"""
    from streaming_pipeline import quick_streaming_pipeline
    
    print("\n" + "="*70)
    print("流式处理模式")
    print("="*70)
    
    # 获取用户输入
    user_input = input("\n请输入需求描述: ").strip()
    if not user_input:
        user_input = "我想找 Base 上海的产品经理，5年经验，有大厂背景"
        print(f"使用默认需求: {user_input}")
    
    # 配置参数
    print("\n配置参数（直接回车使用默认值）:")
    
    search_batch = input("搜索批次大小 [50]: ").strip()
    search_batch_size = int(search_batch) if search_batch else 50
    
    screen_batch = input("筛选批次大小 [10]: ").strip()
    screen_batch_size = int(screen_batch) if screen_batch else 10
    
    flash_th = input("Flash 阈值 [50]: ").strip()
    flash_threshold = int(flash_th) if flash_th else 50
    
    pro_th = input("Pro 阈值 [70]: ").strip()
    pro_threshold = int(pro_th) if pro_th else 70
    
    engine = input("搜索引擎 (serper/gemini/tavily) [serper]: ").strip()
    engine = engine if engine else "serper"
    
    share_email = input("分享邮箱（可选，直接回车跳过）: ").strip()
    share_emails = [share_email] if share_email else None
    
    # 执行流式处理
    print("\n开始流式处理...")
    result = quick_streaming_pipeline(
        user_input=user_input,
        search_batch_size=search_batch_size,
        screen_batch_size=screen_batch_size,
        flash_threshold=flash_threshold,
        pro_threshold=pro_threshold,
        engine=engine,
        share_emails=share_emails
    )
    
    print("\n" + "="*70)
    print("处理完成！")
    print("="*70)
    print(f"搜索: {result['total_searched']} 位")
    print(f"Flash 通过: {result['flash_passed']} 位")
    print(f"Pro 通过: {result['pro_passed']} 位")
    print(f"已导出: {result['exported']} 位")
    if result.get('url'):
        print(f"\nGoogle Sheets: {result['url']}")


def full_pipeline_mode():
    """完整流程模式"""
    from recruiter_pro import LinkedInRecruiterPro
    
    print("\n" + "="*70)
    print("完整流程模式")
    print("="*70)
    
    user_input = input("\n请输入需求描述: ").strip()
    if not user_input:
        user_input = "上海的产品经理，5年经验"
        print(f"使用默认需求: {user_input}")
    
    export_format = input("导出格式 (google_sheets/markdown/json) [markdown]: ").strip()
    export_format = export_format if export_format else "markdown"
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    print("\n开始处理...")
    result = recruiter.full_pipeline(
        user_input=user_input,
        engine="serper",
        flash_threshold=50,
        pro_batch_size=10,
        pro_threshold=70,
        export_format=export_format
    )
    
    print("\n" + "="*70)
    print("处理完成！")
    print("="*70)
    print(f"搜索: {len(result['candidates'])} 位")
    print(f"细筛通过: {len(result['analyzed'])} 位")


def end_to_end_mode():
    """端到端搜索模式"""
    from recruiter_pro import LinkedInRecruiterPro
    
    print("\n" + "="*70)
    print("端到端搜索模式")
    print("="*70)
    
    user_input = input("\n请输入需求描述: ").strip()
    if not user_input:
        user_input = "上海的产品经理，5年经验"
        print(f"使用默认需求: {user_input}")
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    print("\n开始搜索...")
    candidates = recruiter.search_end_to_end(user_input, engine="serper")
    
    print(f"\n找到 {len(candidates)} 位候选人")
    
    # 导出
    recruiter.export_to_markdown(candidates, "search_results.md")
    print("已导出到: search_results.md")


def search_with_filter_mode():
    """搜索 + 粗筛模式"""
    from recruiter_pro import LinkedInRecruiterPro
    
    print("\n" + "="*70)
    print("搜索 + 粗筛模式")
    print("="*70)
    
    job_title = input("\n职位名称: ").strip()
    if not job_title:
        job_title = "Product Manager"
        print(f"使用默认职位: {job_title}")
    
    location = input("地点: ").strip()
    if not location:
        location = "Shanghai"
        print(f"使用默认地点: {location}")
    
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    filter_requirements = {
        "required_keywords": ["Product", "Manager"],
        "min_score": 0.6
    }
    
    print("\n开始搜索和筛选...")
    candidates = recruiter.search_with_filter(
        job_title=job_title,
        location=location,
        num_results=100,
        filter_requirements=filter_requirements
    )
    
    print(f"\n筛选后: {len(candidates)} 位候选人")
    
    # 导出
    recruiter.export_to_json(candidates, "filtered_results.json")
    print("已导出到: filtered_results.json")


def multi_engine_mode():
    """多引擎搜索模式"""
    from recruiter_pro import LinkedInRecruiterPro
    
    print("\n" + "="*70)
    print("多引擎搜索模式")
    print("="*70)
    
    job_title = input("\n职位名称: ").strip()
    if not job_title:
        job_title = "Product Manager"
        print(f"使用默认职位: {job_title}")
    
    location = input("地点: ").strip()
    if not location:
        location = "Shanghai"
        print(f"使用默认地点: {location}")
    
    recruiter = LinkedInRecruiterPro()
    
    print("\n开始多引擎搜索...")
    candidates = recruiter.search_multi_engine(
        job_title=job_title,
        location=location,
        num_results=50
    )
    
    print(f"\n找到 {len(candidates)} 位候选人")
    
    # 导出
    recruiter.export_to_markdown(candidates, "multi_engine_results.md")
    print("已导出到: multi_engine_results.md")


def analyze_only_mode():
    """仅需求分析模式"""
    from recruiter_pro import LinkedInRecruiterPro
    
    print("\n" + "="*70)
    print("需求分析模式")
    print("="*70)
    
    user_input = input("\n请输入需求描述: ").strip()
    if not user_input:
        user_input = "我想找 Base 伦敦的 OD 顾问，7-15年经验，有咨询背景"
        print(f"使用默认需求: {user_input}")
    
    recruiter = LinkedInRecruiterPro()
    
    print("\n分析中...")
    analysis = recruiter.analyze_requirement(user_input)
    
    import json
    print("\n分析结果:")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


def show_examples():
    """显示示例"""
    print("\n" + "="*70)
    print("使用示例")
    print("="*70)
    
    print("\n示例 1: 流式处理（推荐）")
    print("  需求: 我想找 Base 上海的产品经理，5年经验，有大厂背景")
    print("  特点: 边搜索边筛选边导出，效率最高")
    
    print("\n示例 2: 完整流程")
    print("  需求: 上海的产品经理，5年经验")
    print("  特点: 一次性完成搜索、细筛、导出")
    
    print("\n示例 3: 端到端搜索")
    print("  需求: 寻找纽约的算法交易员，5年以上经验")
    print("  特点: 快速获取候选人列表，不进行细筛")
    
    print("\n示例 4: 多引擎搜索")
    print("  职位: Product Manager")
    print("  地点: Shanghai")
    print("  特点: 同时使用 Serper + Gemini + Tavily，覆盖率最高")
    
    input("\n按回车键返回主菜单...")


def main():
    """主函数"""
    while True:
        show_menu()
        
        choice = input("\n请选择 (0-7): ").strip()
        
        try:
            if choice == "0":
                print("\n再见！")
                sys.exit(0)
            elif choice == "1":
                streaming_mode()
            elif choice == "2":
                full_pipeline_mode()
            elif choice == "3":
                end_to_end_mode()
            elif choice == "4":
                search_with_filter_mode()
            elif choice == "5":
                multi_engine_mode()
            elif choice == "6":
                analyze_only_mode()
            elif choice == "7":
                show_examples()
            else:
                print("\n无效选择，请重试")
                continue
            
            # 默认继续，按回车返回主菜单
            input("\n按回车键返回主菜单...")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            cont = input("是否退出？(y/n) [n]: ").strip().lower()
            if cont == 'y':
                print("\n再见！")
                break
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()
