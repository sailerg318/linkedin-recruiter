"""
统一搜索器 - 整合所有搜索方式
支持 Serper, Tavily, Gemini 三种搜索引擎
"""

import time
from typing import List, Dict, Optional
from serper_search import SerperSearcher
from job_expander import JobTitleExpander
from llm_config import DEFAULT_KEY


class UnifiedSearcher:
    """统一搜索器 - 提供多种搜索引擎的统一接口"""
    
    def __init__(
        self,
        serper_key: str = "d88085d4543221682eecd92082f27247f71d902f",
        llm_key: str = DEFAULT_KEY,
        default_engine: str = "serper",
        enable_job_expansion: bool = True
    ):
        """
        初始化统一搜索器
        
        Args:
            serper_key: Serper API Key
            llm_key: LLM API Key (用于 Gemini)
            default_engine: 默认搜索引擎 (serper/tavily/gemini)
            enable_job_expansion: 是否启用岗位关键词扩展
        """
        self.default_engine = default_engine
        self.enable_job_expansion = enable_job_expansion
        
        # 初始化岗位扩展器
        if enable_job_expansion:
            try:
                self.job_expander = JobTitleExpander(api_key=llm_key)
                print("✓ 岗位关键词扩展已启用")
            except:
                self.job_expander = None
                print("⚠ 岗位关键词扩展初始化失败")
        else:
            self.job_expander = None
        
        # 初始化 Serper
        try:
            self.serper = SerperSearcher(api_key=serper_key)
        except:
            self.serper = None
        
        # 初始化 Tavily
        try:
            from tavily_search import TavilySearcher
            self.tavily = TavilySearcher()
        except:
            self.tavily = None
        
        # 初始化 Gemini
        try:
            from gemini_search import GeminiSearcher
            self.gemini = GeminiSearcher(api_key=llm_key)
        except:
            self.gemini = None
    
    def search(
        self,
        query: str = None,
        job_title: str = "",
        location: str = "",
        keywords: str = "",
        company: str = "",
        num_results: int = 100,
        engine: str = None,
        expand_job_title: bool = None
    ) -> List[Dict]:
        """
        统一搜索接口
        
        Args:
            query: 直接搜索查询（用于 Serper）
            job_title: 职位名称
            location: 地点
            keywords: 关键词
            company: 公司
            num_results: 结果数量
            engine: 指定搜索引擎 (serper/tavily/gemini)，None 则使用默认
            expand_job_title: 是否扩展岗位关键词，None 则使用初始化时的设置
            
        Returns:
            候选人列表
        """
        engine = engine or self.default_engine
        
        # 岗位关键词扩展
        if expand_job_title is None:
            expand_job_title = self.enable_job_expansion
        
        if expand_job_title and self.job_expander and job_title and not query:
            print(f"\n🔍 扩展岗位关键词: {job_title} (地点: {location or '未指定'})")
            job_variants = self.job_expander.expand_job_title(job_title, location=location, max_variants=15)
            
            # 使用扩展后的岗位名称进行多次搜索
            all_candidates = []
            seen_urls = set()
            
            for i, variant in enumerate(job_variants, 1):
                print(f"\n  [{i}/{len(job_variants)}] 搜索变体: {variant}")
                
                candidates = self._search_single(
                    engine, query, variant, location, keywords, company,
                    num_results // len(job_variants)  # 平分结果数量
                )
                
                # 去重
                for candidate in candidates:
                    url = candidate.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_candidates.append(candidate)
                
                time.sleep(0.5)  # 避免请求过快
            
            print(f"\n✓ 岗位扩展搜索完成，共找到 {len(all_candidates)} 位候选人（已去重）")
            return all_candidates
        else:
            # 不扩展，直接搜索
            return self._search_single(
                engine, query, job_title, location, keywords, company, num_results
            )
    
    def _search_single(
        self,
        engine: str,
        query: str,
        job_title: str,
        location: str,
        keywords: str,
        company: str,
        num_results: int
    ) -> List[Dict]:
        """单次搜索"""
        if engine == "serper" and self.serper:
            return self._search_with_serper(
                query, job_title, location, keywords, company, num_results
            )
        elif engine == "tavily" and self.tavily:
            return self._search_with_tavily(
                job_title, location, keywords, company, num_results
            )
        elif engine == "gemini" and self.gemini:
            return self._search_with_gemini(
                job_title, location, keywords, company, num_results
            )
        else:
            # 回退到可用的引擎
            return self._search_with_fallback(
                query, job_title, location, keywords, company, num_results
            )
    
    def _search_with_serper(
        self,
        query: str,
        job_title: str,
        location: str,
        keywords: str,
        company: str,
        num_results: int
    ) -> List[Dict]:
        """使用 Serper 搜索"""
        if query:
            # 直接使用提供的查询
            return self.serper.search_linkedin(query, num_results)
        else:
            # 构建查询
            query = self._build_serper_query(job_title, location, keywords, company)
            return self.serper.search_linkedin(query, num_results)
    
    def _search_with_tavily(
        self,
        job_title: str,
        location: str,
        keywords: str,
        company: str,
        num_results: int
    ) -> List[Dict]:
        """使用 Tavily 搜索"""
        return self.tavily.search_linkedin_candidates(
            job_title=job_title,
            location=location,
            keywords=keywords,
            company=company,
            max_results=num_results
        )
    
    def _search_with_gemini(
        self,
        job_title: str,
        location: str,
        keywords: str,
        company: str,
        num_results: int
    ) -> List[Dict]:
        """使用 Gemini 搜索"""
        return self.gemini.search_linkedin_with_gemini(
            job_title=job_title,
            location=location,
            keywords=keywords,
            company=company,
            max_results=num_results
        )
    
    def _search_with_fallback(
        self,
        query: str,
        job_title: str,
        location: str,
        keywords: str,
        company: str,
        num_results: int
    ) -> List[Dict]:
        """回退搜索 - 尝试所有可用的引擎"""
        # 优先级: Serper > Gemini > Tavily
        if self.serper:
            try:
                return self._search_with_serper(
                    query, job_title, location, keywords, company, num_results
                )
            except:
                pass
        
        if self.gemini:
            try:
                return self._search_with_gemini(
                    job_title, location, keywords, company, num_results
                )
            except:
                pass
        
        if self.tavily:
            try:
                return self._search_with_tavily(
                    job_title, location, keywords, company, num_results
                )
            except:
                pass
        
        return []
    
    def _build_serper_query(
        self,
        job_title: str,
        location: str,
        keywords: str,
        company: str
    ) -> str:
        """构建 Serper 搜索查询"""
        parts = ['site:linkedin.com/in/']
        
        if job_title:
            parts.append(f'"{job_title}"')
        
        if location:
            parts.append(f'"{location}"')
        
        if keywords:
            parts.append(f'"{keywords}"')
        
        if company:
            parts.append(f'"{company}"')
        
        parts.append('-intitle:jobs')
        
        return ' '.join(parts)
    
    def batch_search(
        self,
        queries: List[Dict],
        engine: str = None,
        delay: float = 0.5
    ) -> List[Dict]:
        """
        批量搜索
        
        Args:
            queries: 查询列表，每个查询是一个字典
            engine: 搜索引擎
            delay: 每次搜索之间的延迟（秒）
            
        Returns:
            去重后的候选人列表
        """
        all_candidates = []
        seen_urls = set()
        
        for i, query_dict in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] 搜索中...")
            
            candidates = self.search(engine=engine, **query_dict)
            
            # 去重
            new_count = 0
            for candidate in candidates:
                url = candidate.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_candidates.append(candidate)
                    new_count += 1
            
            print(f"    新增 {new_count} 位 (总计: {len(all_candidates)})")
            
            # 延迟
            if i < len(queries):
                time.sleep(delay)
        
        return all_candidates
    
    def multi_engine_search(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        num_results: int = 100
    ) -> List[Dict]:
        """
        多引擎搜索 - 同时使用多个引擎并合并结果
        
        Returns:
            合并去重后的候选人列表
        """
        print("  使用多引擎搜索...")
        
        all_candidates = []
        seen_urls = set()
        
        engines = []
        if self.serper:
            engines.append("serper")
        if self.gemini:
            engines.append("gemini")
        if self.tavily:
            engines.append("tavily")
        
        for engine in engines:
            print(f"    {engine.capitalize()} 搜索中...")
            try:
                candidates = self.search(
                    job_title=job_title,
                    location=location,
                    keywords=keywords,
                    company=company,
                    num_results=num_results,
                    engine=engine
                )
                
                new_count = 0
                for candidate in candidates:
                    url = candidate.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_candidates.append(candidate)
                        new_count += 1
                
                print(f"      {engine.capitalize()}: {len(candidates)} 位，新增 {new_count} 位")
            except Exception as e:
                print(f"      {engine.capitalize()} 失败: {e}")
        
        print(f"  ✓ 多引擎搜索完成: {len(all_candidates)} 位（已去重）")
        return all_candidates


# 便捷函数
def quick_search(
    job_title: str,
    location: str = "",
    keywords: str = "",
    company: str = "",
    num_results: int = 100,
    engine: str = "serper"
) -> List[Dict]:
    """
    快速搜索 - 便捷函数
    
    Args:
        job_title: 职位名称
        location: 地点
        keywords: 关键词
        company: 公司
        num_results: 结果数量
        engine: 搜索引擎
        
    Returns:
        候选人列表
    """
    searcher = UnifiedSearcher(default_engine=engine)
    return searcher.search(
        job_title=job_title,
        location=location,
        keywords=keywords,
        company=company,
        num_results=num_results
    )


if __name__ == "__main__":
    # 测试统一搜索器
    print("="*70)
    print("测试统一搜索器")
    print("="*70)
    
    searcher = UnifiedSearcher(default_engine="serper")
    
    # 测试 1: 单次搜索
    print("\n测试 1: 单次搜索")
    candidates = searcher.search(
        job_title="Product Manager",
        location="Shanghai",
        num_results=10
    )
    print(f"找到 {len(candidates)} 位候选人")
    
    # 测试 2: 多引擎搜索
    print("\n测试 2: 多引擎搜索")
    candidates = searcher.multi_engine_search(
        job_title="Product Manager",
        location="Shanghai",
        num_results=5
    )
    print(f"多引擎搜索找到 {len(candidates)} 位候选人")
