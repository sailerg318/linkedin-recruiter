"""
穷尽搜索策略模块 - 根据解析的需求生成所有可能的搜索组合
"""

from typing import List, Dict, Any
from itertools import product
from requirement_parser import RequirementParser
from job_expander import JobTitleExpander
from tavily_search import TavilySearcher


class ExhaustiveSearchStrategy:
    """穷尽搜索策略生成器"""
    
    def __init__(self):
        self.parser = RequirementParser()
        self.expander = JobTitleExpander()
        self.searcher = TavilySearcher()
    
    def generate_search_combinations(
        self, 
        parsed_requirement: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        根据解析的需求生成所有搜索组合
        
        Args:
            parsed_requirement: 解析后的需求字典
            
        Returns:
            搜索组合列表
        """
        print(f"\n{'='*60}")
        print("生成穷尽搜索组合")
        print(f"{'='*60}\n")
        
        # 1. 扩充岗位名称
        job_title = parsed_requirement.get("job_title", "")
        job_variants = self.expander.expand_job_title(job_title, max_variants=5)
        print(f"✓ 岗位变体: {len(job_variants)} 个")
        
        # 2. 地点关键词
        location_keywords = parsed_requirement.get("location_keywords", [])
        if not location_keywords:
            location_keywords = [""]
        print(f"✓ 地点关键词: {len(location_keywords)} 个")
        
        # 3. 年限关键词
        experience_years_list = parsed_requirement.get("experience_years_list", [])
        if not experience_years_list:
            experience_years_list = [""]
        else:
            # 转换为字符串关键词
            experience_years_list = [f"{y} years" for y in experience_years_list]
        print(f"✓ 年限关键词: {len(experience_years_list)} 个")
        
        # 4. 公司关键词（咨询公司）
        consulting_companies = parsed_requirement.get("consulting_companies", [])
        if not consulting_companies:
            consulting_companies = [""]
        print(f"✓ 咨询公司: {len(consulting_companies)} 个")
        
        # 5. 生成所有组合
        combinations = []
        
        # 组合策略：
        # - 岗位变体 x 地点 x 年限
        # - 岗位变体 x 地点 x 公司
        
        # 策略1：岗位 + 地点 + 年限
        for job in job_variants:
            for location in location_keywords:
                for exp in experience_years_list[:3]:  # 限制年限组合数量
                    combo = {
                        "job_title": job,
                        "location": location,
                        "keywords": exp,
                        "company": ""
                    }
                    combinations.append(combo)
        
        # 策略2：岗位 + 地点 + 公司
        for job in job_variants:
            for location in location_keywords:
                for company in consulting_companies[:5]:  # 限制公司组合数量
                    combo = {
                        "job_title": job,
                        "location": location,
                        "keywords": "",
                        "company": company
                    }
                    combinations.append(combo)
        
        print(f"\n✓ 总共生成 {len(combinations)} 个搜索组合")
        
        return combinations
    
    def execute_exhaustive_search(
        self,
        requirement_text: str,
        max_combinations: int = 50,
        max_results_per_combo: int = 10
    ) -> List[Dict]:
        """
        执行穷尽搜索
        
        Args:
            requirement_text: 自然语言需求
            max_combinations: 最多执行的搜索组合数
            max_results_per_combo: 每个组合最多返回的结果数
            
        Returns:
            所有候选人列表（已去重）
        """
        print(f"\n{'='*60}")
        print("穷尽搜索执行")
        print(f"{'='*60}")
        
        # 1. 解析需求
        parsed = self.parser.parse_requirement(requirement_text)
        
        # 2. 生成搜索组合
        combinations = self.generate_search_combinations(parsed)
        
        # 限制组合数量
        if len(combinations) > max_combinations:
            print(f"\n⚠ 组合数量过多，限制为前 {max_combinations} 个")
            combinations = combinations[:max_combinations]
        
        # 3. 执行搜索
        all_candidates = []
        seen_urls = set()
        
        print(f"\n{'='*60}")
        print(f"开始执行 {len(combinations)} 个搜索组合")
        print(f"{'='*60}\n")
        
        for i, combo in enumerate(combinations, 1):
            print(f"\n[{i}/{len(combinations)}] 搜索组合:")
            print(f"  岗位: {combo['job_title']}")
            print(f"  地点: {combo['location']}")
            print(f"  关键词: {combo['keywords']}")
            print(f"  公司: {combo['company']}")
            
            try:
                candidates = self.searcher.search_linkedin_candidates(
                    job_title=combo['job_title'],
                    keywords=combo['keywords'],
                    location=combo['location'],
                    company=combo['company'],
                    max_results=max_results_per_combo
                )
                
                # 去重
                new_count = 0
                for candidate in candidates:
                    url = candidate.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_candidates.append(candidate)
                        new_count += 1
                
                print(f"  本轮新增: {new_count} 位")
                print(f"  累计总数: {len(all_candidates)} 位")
                
            except Exception as e:
                print(f"  ✗ 搜索失败: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"穷尽搜索完成")
        print(f"{'='*60}")
        print(f"✓ 总共找到 {len(all_candidates)} 位不重复的候选人")
        
        # 4. 应用甲乙方背景筛选
        if parsed.get("require_corporate_experience"):
            print(f"\n应用甲乙方背景筛选...")
            filtered = self._filter_by_background(
                all_candidates,
                parsed.get("consulting_companies", [])
            )
            print(f"✓ 筛选后剩余 {len(filtered)} 位候选人")
            return filtered
        
        return all_candidates
    
    def _filter_by_background(
        self,
        candidates: List[Dict],
        consulting_companies: List[str]
    ) -> List[Dict]:
        """
        筛选甲乙方背景
        
        要求：
        - 必须有咨询公司（乙方）经验
        - 必须有非咨询公司（甲方）经验
        """
        filtered = []
        
        for candidate in candidates:
            raw_content = candidate.get('raw_content', '')
            snippet = candidate.get('snippet', '')
            content = raw_content if raw_content else snippet
            
            if not content:
                continue
            
            # 检查是否有咨询公司经验
            has_consulting = any(
                company.lower() in content.lower()
                for company in consulting_companies
            )
            
            # 检查是否有其他公司经验（简单判断：Experience部分有多个公司）
            # 这里简化处理，实际应该更精细
            has_corporate = "Experience" in content or "experience" in content
            
            if has_consulting and has_corporate:
                filtered.append(candidate)
        
        return filtered


if __name__ == "__main__":
    # 测试代码
    strategy = ExhaustiveSearchStrategy()
    
    # 测试需求
    requirement = "我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
    
    # 执行穷尽搜索（限制组合数量用于测试）
    candidates = strategy.execute_exhaustive_search(
        requirement,
        max_combinations=10,  # 测试时限制为10个组合
        max_results_per_combo=5
    )
    
    print(f"\n{'='*60}")
    print("搜索结果")
    print(f"{'='*60}")
    print(f"找到 {len(candidates)} 位候选人\n")
    
    # 显示前5位
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"{i}. {candidate['name']}")
        print(f"   职位: {candidate['title']}")
        print(f"   公司: {candidate.get('company', 'N/A')}")
        print(f"   链接: {candidate['url']}")
        print()
