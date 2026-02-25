#!/usr/bin/env python3
"""
快速运行脚本 - 流式处理
"""

from streaming_pipeline import quick_streaming_pipeline


def main():
    """快速运行"""
    print("\n" + "="*70)
    print("LinkedIn 招聘系统 - 流式处理")
    print("="*70)
    
    # 获取用户输入
    print("\n请输入招聘需求（直接回车使用默认示例）:")
    user_input = input("> ").strip()
    
    if not user_input:
        user_input = "我想找 Base 上海的产品经理，5-8年经验，有大厂背景，最好有咨询经验"
        print(f"\n使用默认需求: {user_input}")
    
    # 配置参数
    print("\n配置参数（直接回车使用默认值）:")
    
    engine_input = input("搜索引擎 (serper/gemini/tavily) [serper]: ").strip()
    engine = engine_input if engine_input else "serper"
    
    batch_input = input("搜索批次大小 [50]: ").strip()
    search_batch_size = int(batch_input) if batch_input else 50
    
    screen_input = input("筛选批次大小 [10]: ").strip()
    screen_batch_size = int(screen_input) if screen_input else 10
    
    flash_input = input("Flash 阈值 [50]: ").strip()
    flash_threshold = int(flash_input) if flash_input else 50
    
    pro_input = input("Pro 阈值 [70]: ").strip()
    pro_threshold = int(pro_input) if pro_input else 70
    
    share_input = input("分享邮箱（可选，直接回车跳过）: ").strip()
    share_emails = [share_input] if share_input else None
    
    # 确认
    print("\n" + "="*70)
    print("配置总结:")
    print("="*70)
    print(f"需求: {user_input}")
    print(f"搜索引擎: {engine}")
    print(f"搜索批次: {search_batch_size}")
    print(f"筛选批次: {screen_batch_size}")
    print(f"Flash 阈值: {flash_threshold}")
    print(f"Pro 阈值: {pro_threshold}")
    if share_emails:
        print(f"分享给: {share_emails[0]}")
    
    confirm = input("\n确认开始？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("已取消")
        return
    
    # 执行流式处理
    print("\n" + "="*70)
    print("开始流式处理...")
    print("="*70)
    
    try:
        result = quick_streaming_pipeline(
            user_input=user_input,
            search_batch_size=search_batch_size,
            screen_batch_size=screen_batch_size,
            flash_threshold=flash_threshold,
            pro_threshold=pro_threshold,
            engine=engine,
            share_emails=share_emails
        )
        
        # 显示结果
        print("\n" + "="*70)
        print("处理完成！")
        print("="*70)
        
        if result.get('error'):
            print(f"\n✗ 错误: {result['error']}")
            return
        
        print(f"\n统计:")
        print(f"  搜索: {result.get('total_searched', 0)} 位")
        print(f"  Flash 通过: {result.get('flash_passed', 0)} 位")
        print(f"  Pro 通过: {result.get('pro_passed', 0)} 位")
        print(f"  已导出: {result.get('exported', 0)} 位")
        
        if result.get('url'):
            print(f"\n✓ Google Sheets: {result['url']}")
        
        if result.get('json_file'):
            print(f"✓ JSON 文件: {result['json_file']}")
        
        if result.get('markdown_file'):
            print(f"✓ Markdown 文件: {result['markdown_file']}")
        
        print("\n" + "="*70)
        print("完成！")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
