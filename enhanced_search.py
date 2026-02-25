"""
增强版搜索器 - 集成岗位扩充功能的LinkedIn搜索
"""

from typing import List, Dict
from tavily_search import TavilySearcher
from job_expander import JobTitleExpander
from config import MAX_SEARCH_RESULTS


class EnhancedLinkedInSearcher:
    """增强版LinkedIn搜索器，支持岗位近义词扩充"""
    
    def __init__(self):
        self.tavily_searcher = TavilySearcher()
        self.job_expander = JobTitleExpander()
    
    def search_with_expansion(
        self,
        job_title: str,
        keywords: str = "",
        location: str = "",
        company: str = "",
        expand_job_title: bool = True,
        max_variants: int = 5,
        max_results_per_variant: int = 20
    ) -> List[Dict]:
        """
        使用岗位扩充进行搜索
        
        Args:
            job_title: 原始岗位名称
            keywords: 额外关键词
            location: 地点
            company: 公司
            expand_job_title: 是否扩充岗位名称
            max_variants: 最多扩充几个岗位变体
            max_results_per_variant: 每个变体最多返回多少结果
            
        Returns:
            所有候选人列表（已去重）
        """
        all_candidates = []
        seen_urls = set()
        
        if expand_job_title:
            print(f"\n{'='*60}")
            print(f"步骤1：岗位近义词扩充")
            print(f"{'='*60}")
            
            # 扩充岗位名称
            job_variants = self.job_expander.expand_job_title(
                job_title, 
                max_variants=max_variants
            )
        else:
            job_variants = [job_title]
        
        print(f"\n{'='*60}")
        print(f"步骤2：多维度搜索")
        print(f"{'='*60}")
        print(f"将使用 {len(job_variants)} 个岗位变体进行搜索\n")
        
        # 对每个岗位变体进行搜索
        for i, variant in enumerate(job_variants, 1):
            print(f"\n[{i}/{len(job_variants)}] 搜索岗位变体: {variant}")
            print("-" * 60)
            
            candidates = self.tavily_searcher.search_linkedin_candidates(
                job_title=variant,
                keywords=keywords,
                location=location,
                company=company,
                max_results=max_results_per_variant
            )
            
            # 去重
            new_candidates = 0
            for candidate in candidates:
                url = candidate.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_candidates.append(candidate)
                    new_candidates += 1
            
            print(f"  本轮新增: {new_candidates} 位候选人")
            print(f"  累计总数: {len(all_candidates)} 位候选人")
        
        print(f"\n{'='*60}")
        print(f"搜索完成")
        print(f"{'='*60}")
        print(f"✓ 总共找到 {len(all_candidates)} 位不重复的候选人")
        
        return all_candidates
    
    def batch_search_with_expansion(
        self,
        job_requirements: Dict[str, str]
    ) -> List[Dict]:
        """
        批量搜索（支持岗位扩充）
        
        Args:
            job_requirements: 岗位需求字典，包含：
                - job_title: 岗位名称（必填）
                - keywords: 关键词（可选）
                - location: 地点（可选）
                - company: 公司（可选）
                - expand_job_title: 是否扩充岗位（可选，默认True）
                - max_variants: 最多扩充几个变体（可选，默认5）
        
        Returns:
            候选人列表
        """
        job_title = job_requirements.get("job_title", "")
        keywords = job_requirements.get("keywords", "")
        location = job_requirements.get("location", "")
        company = job_requirements.get("company", "")
        expand_job_title = job_requirements.get("expand_job_title", True)
        max_variants = job_requirements.get("max_variants", 5)
        
        if not job_title:
            print("✗ 错误：必须提供岗位名称")
            return []
        
        print(f"\n{'='*60}")
        print(f"增强版LinkedIn搜索")
        print(f"{'='*60}")
        print(f"原始岗位: {job_title}")
        if keywords:
            print(f"关键词: {keywords}")
        if location:
            print(f"地点: {location}")
        if company:
            print(f"公司: {company}")
        print(f"岗位扩充: {'启用' if expand_job_title else '禁用'}")
        
        candidates = self.search_with_expansion(
            job_title=job_title,
            keywords=keywords,
            location=location,
            company=company,
            expand_job_title=expand_job_title,
            max_variants=max_variants
        )
        
        return candidates


if __name__ == "__main__":
    # 测试代码
    searcher = EnhancedLinkedInSearcher()
    
    # 测试：搜索org development专家
    job_requirements = {
        "job_title": "org development",
        "location": "San Francisco",
        "expand_job_title": True,
        "max_variants": 3
    }
    
    candidates = searcher.batch_search_with_expansion(job_requirements)
    
    print(f"\n{'='*60}")
    print(f"搜索结果汇总")
    print(f"{'='*60}")
    print(f"找到 {len(candidates)} 位候选人\n")
    
    # 显示前5位
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"{i}. {candidate['name']}")
        print(f"   职位: {candidate['title']}")
        print(f"   公司: {candidate.get('company', 'N/A')}")
        print(f"   地点: {candidate.get('location', 'N/A')}")
        print(f"   链接: {candidate['url']}")
        print(f"   分数: {candidate['score']:.2f}")
        print()
