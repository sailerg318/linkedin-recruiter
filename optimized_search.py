"""
优化的搜索策略 - 使用Gemini Search，增加搜索组合，提高候选人发现率
"""

from typing import List, Dict, Any
from requirement_parser import RequirementParser
from job_expander import JobTitleExpander
from gemini_search import GeminiSearcher


class OptimizedSearchStrategy:
    """优化的搜索策略 - 使用Gemini Search生成更多搜索组合"""
    
    def __init__(self):
        self.parser = RequirementParser()
        self.expander = JobTitleExpander()
        self.searcher = GeminiSearcher()
    
    def generate_optimized_combinations(
        self, 
        parsed_requirement: Dict[str, Any],
        max_combinations: int = 30
    ) -> List[Dict[str, str]]:
        """
        生成优化的搜索组合
        
        策略：
        1. 只用岗位 + 地点（不加年限限制）
        2. 岗位 + 地点 + 行业关键词
        3. 岗位 + 地点 + 知名公司
        
        Args:
            parsed_requirement: 解析后的需求字典
            max_combinations: 最大组合数量
            
        Returns:
            搜索组合列表
        """
        print(f"\n{'='*60}")
        print("生成优化搜索组合")
        print(f"{'='*60}\n")
        
        combinations = []
        
        # 1. 扩充岗位名称（增加到10个变体）
        job_title = parsed_requirement.get("job_title", "")
        job_variants = self.expander.expand_job_title(job_title, max_variants=10)
        print(f"✓ 岗位变体: {len(job_variants)} 个")
        
        # 2. 地点关键词
        location_keywords = parsed_requirement.get("location_keywords", [])
        if not location_keywords:
            location_keywords = [""]
        print(f"✓ 地点关键词: {len(location_keywords)} 个")
        
        # 3. 行业关键词
        company_type = parsed_requirement.get("company_type", "")
        industry_keywords = []
        if company_type:
            # 将行业拆分为关键词
            industry_keywords = [kw.strip() for kw in company_type.split("、") if kw.strip()]
        print(f"✓ 行业关键词: {len(industry_keywords)} 个")
        
        # 4. 知名公司列表
        consulting_companies = parsed_requirement.get("consulting_companies", [])[:10]
        print(f"✓ 目标公司: {len(consulting_companies)} 个")
        
        # 策略1: 岗位 + 地点（最宽泛，覆盖所有候选人）
        print("\n策略1: 岗位 + 地点（穷尽搜索）")
        for job in job_variants:
            for location in location_keywords:
                combo = {
                    "job_title": job,
                    "location": location,
                    "keywords": "",
                    "company": ""
                }
                combinations.append(combo)
        print(f"  生成 {len(combinations)} 个组合")
        print(f"  说明：不加行业限制，在Flash细筛时识别行业背景")
        
        # 策略2: 岗位 + 地点 + 知名公司（补充搜索）
        if consulting_companies:
            print("\n策略2: 岗位 + 地点 + 知名公司")
            strategy2_start = len(combinations)
            for job in job_variants[:5]:  # 使用前5个岗位变体
                for location in location_keywords:
                    for company in consulting_companies[:10]:  # 增加到10个公司
                        combo = {
                            "job_title": job,
                            "location": location,
                            "keywords": "",
                            "company": company
                        }
                        combinations.append(combo)
            print(f"  生成 {len(combinations) - strategy2_start} 个组合")
            print(f"  说明：针对性搜索知名公司的候选人")
        
        # 注意：不在搜索时加行业关键词
        # 原因：
        # 1. LinkedIn上行业标签不准确
        # 2. 候选人可能没有在简介中提到行业关键词
        # 3. Flash可以从公司名称智能识别行业背景
        # 4. 先穷尽搜索，再细筛行业，覆盖面更广
        
        if industry_keywords:
            print(f"\n⚠ 行业关键词 ({', '.join(industry_keywords)}) 将在Flash细筛时使用")
            print(f"  Flash会智能识别候选人的行业背景")
        
        # 限制总数
        if len(combinations) > max_combinations:
            print(f"\n⚠ 组合数量过多，限制为前 {max_combinations} 个")
            combinations = combinations[:max_combinations]
        
        print(f"\n✓ 总共生成 {len(combinations)} 个搜索组合")
        
        return combinations
    
    def execute_optimized_search(
        self,
        requirement_text: str,
        max_combinations: int = 30,
        max_results_per_combo: int = 5
    ) -> List[Dict]:
        """
        执行优化的穷尽搜索
        
        Args:
            requirement_text: 需求文本
            max_combinations: 最大搜索组合数
            max_results_per_combo: 每个组合最多返回结果数
            
        Returns:
            去重后的候选人列表
        """
        print(f"\n{'='*60}")
        print("优化穷尽搜索执行")
        print(f"{'='*60}\n")
        
        # 1. 解析需求
        parsed_req = self.parser.parse_requirement(requirement_text)
        
        # 2. 生成优化的搜索组合
        combinations = self.generate_optimized_combinations(
            parsed_req,
            max_combinations=max_combinations
        )
        
        # 3. 执行搜索
        print(f"\n{'='*60}")
        print(f"开始执行 {len(combinations)} 个搜索组合")
        print(f"{'='*60}\n")
        
        all_candidates = []
        seen_urls = set()
        
        for i, combo in enumerate(combinations, 1):
            print(f"\n[{i}/{len(combinations)}] 搜索组合:")
            print(f"  岗位: {combo['job_title']}")
            print(f"  地点: {combo['location']}")
            if combo['keywords']:
                print(f"  关键词: {combo['keywords']}")
            if combo['company']:
                print(f"  公司: {combo['company']}")
            
            try:
                results = self.searcher.search_linkedin_with_gemini(
                    job_title=combo['job_title'],
                    location=combo['location'],
                    keywords=combo['keywords'],
                    company=combo['company'],
                    max_results=max_results_per_combo
                )
                
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
                
            except Exception as e:
                print(f"  ✗ 搜索失败: {e}")
                continue
        
        print(f"\n{'='*60}")
        print("优化搜索完成")
        print(f"{'='*60}")
        print(f"✓ 总共找到 {len(all_candidates)} 位不重复的候选人")
        
        return all_candidates


if __name__ == "__main__":
    # 测试代码
    strategy = OptimizedSearchStrategy()
    
    requirement = "我要找Base伦敦的OD，甲乙方经验或者新零售、物流的纯甲方经验，7-15年"
    
    candidates = strategy.execute_optimized_search(
        requirement,
        max_combinations=20,
        max_results_per_combo=5
    )
    
    print(f"\n找到 {len(candidates)} 位候选人")
