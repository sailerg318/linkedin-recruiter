#!/usr/bin/env python3
"""
快速启动脚本 - 交互式配置和运行
"""

import sys
import os


def check_config():
    """检查配置是否完整"""
    try:
        from config import (
            TAVILY_API_KEY,
            FEISHU_APP_ID,
            FEISHU_APP_SECRET,
            FEISHU_TABLE_ID,
            FEISHU_TABLE_APP_TOKEN
        )
        
        missing = []
        if TAVILY_API_KEY == "your_tavily_api_key_here":
            missing.append("TAVILY_API_KEY")
        if FEISHU_APP_ID == "your_feishu_app_id_here":
            missing.append("FEISHU_APP_ID")
        if FEISHU_APP_SECRET == "your_feishu_app_secret_here":
            missing.append("FEISHU_APP_SECRET")
        if FEISHU_TABLE_ID == "your_table_id_here":
            missing.append("FEISHU_TABLE_ID")
        if FEISHU_TABLE_APP_TOKEN == "your_app_token_here":
            missing.append("FEISHU_TABLE_APP_TOKEN")
        
        return missing
    except ImportError as e:
        print(f"✗ 配置文件导入失败: {e}")
        return ["配置文件"]


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*60)
    print("    LinkedIn人才搜索系统")
    print("="*60)


def get_job_requirements():
    """交互式获取岗位需求"""
    print("\n【步骤1】配置岗位需求")
    print("-" * 60)
    
    job_title = input("请输入岗位名称 (例如: Python Engineer): ").strip()
    if not job_title:
        print("✗ 岗位名称不能为空")
        sys.exit(1)
    
    keywords = input("请输入额外关键词 (可选，例如: AI Machine Learning): ").strip()
    
    return {
        "job_title": job_title,
        "keywords": keywords
    }


def get_filter_requirements():
    """交互式获取筛选条件"""
    print("\n【步骤2】配置筛选条件")
    print("-" * 60)
    
    use_filter = input("是否使用筛选条件? (y/n, 默认: y): ").strip().lower()
    if use_filter == 'n':
        return None
    
    filter_req = {}
    
    # 必须包含的关键词
    required = input("必须包含的关键词 (用逗号分隔，可选): ").strip()
    if required:
        filter_req["required_keywords"] = [k.strip() for k in required.split(",")]
    
    # 排除的关键词
    exclude = input("排除的关键词 (用逗号分隔，可选): ").strip()
    if exclude:
        filter_req["exclude_keywords"] = [k.strip() for k in exclude.split(",")]
    
    # 最低分数
    min_score = input("最低相关度分数 (0-1，默认: 0.6): ").strip()
    if min_score:
        try:
            filter_req["min_score"] = float(min_score)
        except ValueError:
            print("⚠ 分数格式错误，使用默认值 0.6")
            filter_req["min_score"] = 0.6
    else:
        filter_req["min_score"] = 0.6
    
    # 最少经验年限
    min_exp = input("最少工作年限 (可选): ").strip()
    if min_exp:
        try:
            filter_req["min_experience"] = int(min_exp)
        except ValueError:
            print("⚠ 年限格式错误，已忽略")
    
    return filter_req if filter_req else None


def get_run_mode():
    """获取运行模式"""
    print("\n【步骤3】选择运行模式")
    print("-" * 60)
    print("1. 单次运行（测试用）")
    print("2. 持续运行，指定轮数")
    print("3. 持续运行，直到手动停止")
    
    choice = input("\n请选择运行模式 (1-3, 默认: 1): ").strip()
    
    if choice == "2":
        rounds = input("请输入运行轮数: ").strip()
        try:
            return "continuous", int(rounds)
        except ValueError:
            print("⚠ 轮数格式错误，使用单次运行")
            return "single", None
    elif choice == "3":
        return "continuous", None
    else:
        return "single", None


def main():
    """主函数"""
    print_banner()
    
    # 检查配置
    print("\n检查配置...")
    missing = check_config()
    if missing:
        print(f"\n✗ 缺少以下配置项: {', '.join(missing)}")
        print("\n请编辑 config.py 文件，填入正确的API密钥和配置信息")
        print("或者复制 .env.example 为 .env 并填写配置")
        sys.exit(1)
    
    print("✓ 配置检查通过")
    
    # 获取岗位需求
    job_requirements = get_job_requirements()
    
    # 获取筛选条件
    filter_requirements = get_filter_requirements()
    
    # 获取运行模式
    run_mode, max_rounds = get_run_mode()
    
    # 确认配置
    print("\n" + "="*60)
    print("配置确认")
    print("="*60)
    print(f"岗位名称: {job_requirements['job_title']}")
    print(f"关键词: {job_requirements.get('keywords', '无')}")
    if filter_requirements:
        print(f"筛选条件: 已配置 {len(filter_requirements)} 项")
    else:
        print("筛选条件: 未配置")
    print(f"运行模式: {'单次运行' if run_mode == 'single' else f'持续运行({max_rounds}轮)' if max_rounds else '持续运行(无限)'}")
    
    confirm = input("\n确认开始运行? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        sys.exit(0)
    
    # 导入并运行
    try:
        from main import LinkedInRecruiter
        
        recruiter = LinkedInRecruiter()
        
        if run_mode == "single":
            recruiter.run_single_search(job_requirements, filter_requirements)
        else:
            recruiter.run_continuous(
                job_requirements,
                filter_requirements,
                max_rounds=max_rounds
            )
            
    except KeyboardInterrupt:
        print("\n\n程序已停止")
    except Exception as e:
        print(f"\n✗ 运行错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
