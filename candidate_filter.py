"""
候选人筛选模块 - 根据精细化条件筛选候选人
"""

from typing import List, Dict, Callable
import re


class CandidateFilter:
    """候选人筛选器"""
    
    def __init__(self):
        self.filters = []
    
    def add_filter(self, filter_func: Callable, description: str = ""):
        """
        添加筛选条件
        
        Args:
            filter_func: 筛选函数，接收候选人字典，返回True/False
            description: 筛选条件描述
        """
        self.filters.append({
            "func": filter_func,
            "description": description
        })
    
    def filter_candidates(
        self, 
        candidates: List[Dict],
        batch_size: int = 10
    ) -> List[Dict]:
        """
        筛选候选人
        
        Args:
            candidates: 候选人列表
            batch_size: 每批处理数量
            
        Returns:
            筛选后的候选人列表
        """
        filtered = []
        
        print(f"\n开始筛选 {len(candidates)} 位候选人...")
        print(f"应用 {len(self.filters)} 个筛选条件")
        print("-" * 50)
        
        for i, candidate in enumerate(candidates, 1):
            # 应用所有筛选条件
            passed = True
            for filter_item in self.filters:
                try:
                    if not filter_item["func"](candidate):
                        passed = False
                        break
                except Exception as e:
                    print(f"⚠ 筛选条件执行错误: {e}")
                    passed = False
                    break
            
            if passed:
                filtered.append(candidate)
                print(f"✓ [{i}/{len(candidates)}] {candidate['name']} - 通过筛选")
            else:
                print(f"✗ [{i}/{len(candidates)}] {candidate['name']} - 未通过筛选")
            
            # 批次控制
            if len(filtered) >= batch_size:
                print(f"\n已筛选出 {batch_size} 位候选人，停止筛选")
                break
        
        print(f"\n筛选完成: {len(filtered)}/{len(candidates)} 位候选人通过")
        return filtered
    
    def clear_filters(self):
        """清空所有筛选条件"""
        self.filters = []


# 预定义的筛选函数
class FilterFunctions:
    """常用筛选函数集合"""
    
    @staticmethod
    def keyword_in_title(keywords: List[str]):
        """职位标题包含关键词"""
        def filter_func(candidate: Dict) -> bool:
            title = candidate.get("title", "").lower()
            return any(kw.lower() in title for kw in keywords)
        return filter_func
    
    @staticmethod
    def keyword_in_snippet(keywords: List[str]):
        """简介包含关键词"""
        def filter_func(candidate: Dict) -> bool:
            snippet = candidate.get("snippet", "").lower()
            return any(kw.lower() in snippet for kw in keywords)
        return filter_func
    
    @staticmethod
    def exclude_keywords(keywords: List[str]):
        """排除包含特定关键词的候选人"""
        def filter_func(candidate: Dict) -> bool:
            text = (candidate.get("title", "") + " " + 
                   candidate.get("snippet", "")).lower()
            return not any(kw.lower() in text for kw in keywords)
        return filter_func
    
    @staticmethod
    def min_score(threshold: float):
        """最低相关度分数"""
        def filter_func(candidate: Dict) -> bool:
            return candidate.get("score", 0) >= threshold
        return filter_func
    
    @staticmethod
    def has_experience(years: int):
        """至少有N年经验（从简介中提取）"""
        def filter_func(candidate: Dict) -> bool:
            snippet = candidate.get("snippet", "")
            # 查找"X年经验"、"X+ years"等模式
            patterns = [
                r'(\d+)\+?\s*年',
                r'(\d+)\+?\s*years?',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, snippet, re.IGNORECASE)
                if matches:
                    exp_years = max([int(m) for m in matches])
                    return exp_years >= years
            return False
        return filter_func
    
    @staticmethod
    def location_match(locations: List[str]):
        """地理位置匹配"""
        def filter_func(candidate: Dict) -> bool:
            text = (candidate.get("title", "") + " " + 
                   candidate.get("snippet", "")).lower()
            return any(loc.lower() in text for loc in locations)
        return filter_func
    
    @staticmethod
    def company_match(companies: List[str]):
        """公司背景匹配"""
        def filter_func(candidate: Dict) -> bool:
            text = (candidate.get("title", "") + " " + 
                   candidate.get("snippet", "")).lower()
            return any(comp.lower() in text for comp in companies)
        return filter_func


def create_filter_from_requirements(requirements: Dict) -> CandidateFilter:
    """
    根据岗位需求创建筛选器
    
    Args:
        requirements: 岗位需求字典，可包含：
            - required_keywords: 必须包含的关键词列表
            - exclude_keywords: 排除的关键词列表
            - min_score: 最低相关度分数
            - min_experience: 最少工作年限
            - preferred_locations: 优选地点列表
            - preferred_companies: 优选公司列表
    
    Returns:
        配置好的筛选器
    """
    filter_obj = CandidateFilter()
    
    # 必须包含的关键词
    if "required_keywords" in requirements:
        keywords = requirements["required_keywords"]
        filter_obj.add_filter(
            FilterFunctions.keyword_in_snippet(keywords),
            f"简介包含关键词: {', '.join(keywords)}"
        )
    
    # 排除的关键词
    if "exclude_keywords" in requirements:
        keywords = requirements["exclude_keywords"]
        filter_obj.add_filter(
            FilterFunctions.exclude_keywords(keywords),
            f"排除关键词: {', '.join(keywords)}"
        )
    
    # 最低分数
    if "min_score" in requirements:
        score = requirements["min_score"]
        filter_obj.add_filter(
            FilterFunctions.min_score(score),
            f"最低相关度分数: {score}"
        )
    
    # 最少工作年限
    if "min_experience" in requirements:
        years = requirements["min_experience"]
        filter_obj.add_filter(
            FilterFunctions.has_experience(years),
            f"至少 {years} 年经验"
        )
    
    # 优选地点
    if "preferred_locations" in requirements:
        locations = requirements["preferred_locations"]
        filter_obj.add_filter(
            FilterFunctions.location_match(locations),
            f"地点匹配: {', '.join(locations)}"
        )
    
    # 优选公司
    if "preferred_companies" in requirements:
        companies = requirements["preferred_companies"]
        filter_obj.add_filter(
            FilterFunctions.company_match(companies),
            f"公司背景: {', '.join(companies)}"
        )
    
    return filter_obj


if __name__ == "__main__":
    # 测试代码
    test_candidates = [
        {
            "name": "张三",
            "title": "Senior Python Engineer at Google",
            "snippet": "5年Python开发经验，专注于AI和机器学习",
            "score": 0.85,
            "url": "https://linkedin.com/in/zhangsan"
        },
        {
            "name": "李四",
            "title": "Junior Developer",
            "snippet": "1年开发经验",
            "score": 0.45,
            "url": "https://linkedin.com/in/lisi"
        },
        {
            "name": "王五",
            "title": "Python Developer at Alibaba",
            "snippet": "3年Python经验，熟悉Django和Flask",
            "score": 0.75,
            "url": "https://linkedin.com/in/wangwu"
        }
    ]
    
    # 创建筛选条件
    requirements = {
        "required_keywords": ["Python", "经验"],
        "min_score": 0.7,
        "min_experience": 3
    }
    
    filter_obj = create_filter_from_requirements(requirements)
    filtered = filter_obj.filter_candidates(test_candidates, batch_size=10)
    
    print(f"\n最终筛选结果:")
    for candidate in filtered:
        print(f"- {candidate['name']}: {candidate['title']}")
