"""
主程序 - LinkedIn人才搜索和筛选系统
"""

import time
from typing import Dict, List
from tavily_search import TavilySearcher
from candidate_filter import create_filter_from_requirements
from feishu_table import FeishuTableClient
from config import SEARCH_INTERVAL, BATCH_SIZE


class LinkedInRecruiter:
    """LinkedIn招聘助手主类"""
    
    def __init__(self):
        self.searcher = TavilySearcher()
        self.feishu_client = FeishuTableClient()
        
    def run_single_search(
        self, 
        job_requirements: Dict,
        filter_requirements: Dict = None
    ) -> int:
        """
        执行单次搜索和筛选
        
        Args:
            job_requirements: 岗位需求，包含：
                - job_title: 岗位名称（必填）
                - keywords: 搜索关键词（可选）
            filter_requirements: 筛选条件，包含：
                - required_keywords: 必须包含的关键词
                - exclude_keywords: 排除的关键词
                - min_score: 最低相关度分数
                - min_experience: 最少工作年限
                - preferred_locations: 优选地点
                - preferred_companies: 优选公司
        
        Returns:
            添加到表格的候选人数量
        """
        print("\n" + "=" * 60)
        print("开始新一轮搜索")
        print("=" * 60)
        
        # 步骤1: 使用Tavily搜索LinkedIn候选人
        print("\n【步骤1】搜索LinkedIn候选人...")
        candidates = self.searcher.batch_search(job_requirements)
        
        if not candidates:
            print("✗ 未找到候选人，本轮结束")
            return 0
        
        # 步骤2: 应用筛选条件
        print("\n【步骤2】应用筛选条件...")
        if filter_requirements:
            filter_obj = create_filter_from_requirements(filter_requirements)
            filtered_candidates = filter_obj.filter_candidates(
                candidates, 
                batch_size=BATCH_SIZE
            )
        else:
            # 如果没有筛选条件，取前N个
            filtered_candidates = candidates[:BATCH_SIZE]
            print(f"未设置筛选条件，取前 {len(filtered_candidates)} 位候选人")
        
        if not filtered_candidates:
            print("✗ 没有候选人通过筛选，本轮结束")
            return 0
        
        # 步骤3: 去重
        print("\n【步骤3】检查重复...")
        unique_candidates = self.feishu_client.deduplicate_candidates(
            filtered_candidates
        )
        
        if not unique_candidates:
            print("✗ 所有候选人都已存在，本轮结束")
            return 0
        
        # 步骤4: 添加到飞书表格
        print("\n【步骤4】添加到飞书表格...")
        success = self.feishu_client.add_records(unique_candidates)
        
        if success:
            print(f"\n✓ 本轮完成: 成功添加 {len(unique_candidates)} 位候选人")
            return len(unique_candidates)
        else:
            print("\n✗ 添加到飞书表格失败")
            return 0
    
    def run_continuous(
        self,
        job_requirements: Dict,
        filter_requirements: Dict = None,
        max_rounds: int = None
    ):
        """
        持续运行搜索任务
        
        Args:
            job_requirements: 岗位需求
            filter_requirements: 筛选条件
            max_rounds: 最大运行轮数，None表示无限运行
        """
        print("\n" + "=" * 60)
        print("LinkedIn人才搜索系统启动")
        print("=" * 60)
        print(f"岗位: {job_requirements.get('job_title')}")
        print(f"搜索间隔: {SEARCH_INTERVAL}秒 ({SEARCH_INTERVAL/60}分钟)")
        print(f"每批筛选: {BATCH_SIZE}人")
        if max_rounds:
            print(f"最大轮数: {max_rounds}")
        else:
            print("运行模式: 持续运行（按Ctrl+C停止）")
        print("=" * 60)
        
        round_count = 0
        total_added = 0
        
        try:
            while True:
                round_count += 1
                
                if max_rounds and round_count > max_rounds:
                    print(f"\n已完成 {max_rounds} 轮搜索，程序结束")
                    break
                
                print(f"\n\n{'='*60}")
                print(f"第 {round_count} 轮搜索")
                print(f"{'='*60}")
                
                # 执行搜索
                added = self.run_single_search(
                    job_requirements,
                    filter_requirements
                )
                total_added += added
                
                # 显示统计
                print(f"\n【统计】")
                print(f"- 已完成轮数: {round_count}")
                print(f"- 累计添加: {total_added} 位候选人")
                
                # 检查是否继续
                if max_rounds and round_count >= max_rounds:
                    break
                
                # 等待下一轮
                print(f"\n等待 {SEARCH_INTERVAL} 秒后开始下一轮...")
                time.sleep(SEARCH_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n收到停止信号，程序退出")
            print(f"总计完成 {round_count} 轮搜索，添加 {total_added} 位候选人")
        except Exception as e:
            print(f"\n✗ 程序异常: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数 - 示例用法"""
    
    # 创建招聘助手实例
    recruiter = LinkedInRecruiter()
    
    # 定义岗位需求
    job_requirements = {
        "job_title": "Python Engineer",  # 岗位名称
        "keywords": "AI Machine Learning"  # 额外关键词
    }
    
    # 定义筛选条件（可选）
    filter_requirements = {
        "required_keywords": ["Python", "AI"],  # 必须包含的关键词
        "exclude_keywords": ["intern", "实习"],  # 排除的关键词
        "min_score": 0.6,  # 最低相关度分数
        "min_experience": 3,  # 最少3年经验
        # "preferred_locations": ["Beijing", "Shanghai", "北京", "上海"],
        # "preferred_companies": ["Google", "Microsoft", "Alibaba", "Tencent"]
    }
    
    # 选择运行模式
    
    # 模式1: 单次运行（测试用）
    # recruiter.run_single_search(job_requirements, filter_requirements)
    
    # 模式2: 持续运行，指定轮数
    # recruiter.run_continuous(job_requirements, filter_requirements, max_rounds=5)
    
    # 模式3: 持续运行，直到手动停止
    recruiter.run_continuous(job_requirements, filter_requirements)


if __name__ == "__main__":
    main()
