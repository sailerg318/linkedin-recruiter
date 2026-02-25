"""
搜索调度器 - 管理API配额和搜索频率
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from tavily_search import TavilySearcher


class SearchScheduler:
    """搜索调度器 - 管理API配额，避免超限"""
    
    def __init__(
        self,
        daily_limit: int = 100,
        state_file: str = "search_state.json"
    ):
        """
        初始化搜索调度器
        
        Args:
            daily_limit: 每日搜索限制
            state_file: 状态文件路径
        """
        self.daily_limit = daily_limit
        self.state_file = state_file
        self.searcher = TavilySearcher()
        
        # 加载状态
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载搜索状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    
                    # 检查日期是否是今天
                    last_date = state.get('date', '')
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    if last_date != today:
                        # 新的一天，重置计数
                        return {
                            'date': today,
                            'searches_today': 0,
                            'total_searches': state.get('total_searches', 0)
                        }
                    
                    return state
            except:
                pass
        
        # 默认状态
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'searches_today': 0,
            'total_searches': 0
        }
    
    def _save_state(self):
        """保存搜索状态"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠ 保存状态失败: {e}")
    
    def get_remaining_quota(self) -> int:
        """获取今日剩余配额"""
        return max(0, self.daily_limit - self.state['searches_today'])
    
    def can_search(self) -> bool:
        """检查是否可以继续搜索"""
        return self.state['searches_today'] < self.daily_limit
    
    def search_with_quota(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        max_results: int = 5
    ) -> Optional[List[Dict]]:
        """
        带配额管理的搜索
        
        Args:
            job_title: 岗位名称
            location: 地点
            keywords: 关键词
            company: 公司
            max_results: 最大结果数
            
        Returns:
            候选人列表，如果超限则返回None
        """
        if not self.can_search():
            print(f"⚠ 已达到每日搜索限制 ({self.daily_limit}次)")
            print(f"  今日已搜索: {self.state['searches_today']}次")
            print(f"  请明天再试")
            return None
        
        try:
            # 执行搜索
            results = self.searcher.search_linkedin_candidates(
                job_title=job_title,
                location=location,
                keywords=keywords,
                company=company,
                max_results=max_results
            )
            
            # 更新计数
            self.state['searches_today'] += 1
            self.state['total_searches'] += 1
            self._save_state()
            
            # 显示配额信息
            remaining = self.get_remaining_quota()
            print(f"  配额: 剩余 {remaining}/{self.daily_limit} 次")
            
            return results
            
        except Exception as e:
            print(f"✗ 搜索失败: {e}")
            return []
    
    def batch_search_with_quota(
        self,
        search_combinations: List[Dict],
        max_results_per_combo: int = 5
    ) -> List[Dict]:
        """
        批量搜索（带配额管理）
        
        Args:
            search_combinations: 搜索组合列表
            max_results_per_combo: 每个组合最多返回结果数
            
        Returns:
            所有候选人列表（已去重）
        """
        print(f"\n{'='*60}")
        print("批量搜索（配额管理）")
        print(f"{'='*60}")
        print(f"计划搜索: {len(search_combinations)} 个组合")
        print(f"今日配额: {self.get_remaining_quota()}/{self.daily_limit}")
        
        # 检查配额
        remaining = self.get_remaining_quota()
        if remaining == 0:
            print(f"\n⚠ 今日配额已用完，无法搜索")
            return []
        
        if len(search_combinations) > remaining:
            print(f"\n⚠ 搜索组合数({len(search_combinations)})超过剩余配额({remaining})")
            print(f"  将只执行前 {remaining} 个搜索")
            search_combinations = search_combinations[:remaining]
        
        all_candidates = []
        seen_urls = set()
        
        for i, combo in enumerate(search_combinations, 1):
            print(f"\n[{i}/{len(search_combinations)}] 搜索:")
            print(f"  岗位: {combo['job_title']}")
            print(f"  地点: {combo['location']}")
            if combo.get('keywords'):
                print(f"  关键词: {combo['keywords']}")
            if combo.get('company'):
                print(f"  公司: {combo['company']}")
            
            results = self.search_with_quota(
                job_title=combo['job_title'],
                location=combo['location'],
                keywords=combo.get('keywords', ''),
                company=combo.get('company', ''),
                max_results=max_results_per_combo
            )
            
            if results is None:
                # 配额用完
                break
            
            # 去重
            new_candidates = 0
            for candidate in results:
                url = candidate.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_candidates.append(candidate)
                    new_candidates += 1
            
            print(f"  本轮新增: {new_candidates} 位")
            print(f"  累计总数: {len(all_candidates)} 位")
        
        print(f"\n{'='*60}")
        print("批量搜索完成")
        print(f"{'='*60}")
        print(f"✓ 找到 {len(all_candidates)} 位不重复的候选人")
        print(f"✓ 今日剩余配额: {self.get_remaining_quota()}/{self.daily_limit}")
        
        return all_candidates
    
    def get_stats(self) -> Dict:
        """获取搜索统计信息"""
        return {
            "date": self.state['date'],
            "searches_today": self.state['searches_today'],
            "remaining_today": self.get_remaining_quota(),
            "daily_limit": self.daily_limit,
            "total_searches": self.state['total_searches']
        }
    
    def print_stats(self):
        """打印搜索统计信息"""
        stats = self.get_stats()
        print(f"\n{'='*60}")
        print("搜索配额统计")
        print(f"{'='*60}")
        print(f"日期: {stats['date']}")
        print(f"今日已用: {stats['searches_today']}/{stats['daily_limit']}")
        print(f"今日剩余: {stats['remaining_today']}")
        print(f"历史总计: {stats['total_searches']} 次")
        print(f"{'='*60}")


if __name__ == "__main__":
    # 测试代码
    scheduler = SearchScheduler(daily_limit=10)
    
    # 显示统计
    scheduler.print_stats()
    
    # 测试搜索
    print("\n测试搜索:")
    results = scheduler.search_with_quota(
        job_title="Product Manager",
        location="London",
        max_results=3
    )
    
    if results:
        print(f"\n找到 {len(results)} 位候选人")
    
    # 再次显示统计
    scheduler.print_stats()
