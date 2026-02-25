"""
Gemini搜索模块 - 使用Gemini 2.5 Pro Search进行LinkedIn搜索
作为Tavily的替代方案
"""

import requests
import json
import re
from typing import List, Dict
from llm_config import API_BASE, DEFAULT_KEY


class GeminiSearcher:
    """使用Gemini 2.5 Pro Search进行LinkedIn人才搜索"""
    
    def __init__(self, api_key: str = DEFAULT_KEY):
        self.api_key = api_key
        self.api_base = API_BASE
        self.model = "[满血A]gemini-2.5-pro-search-maxthinking"
    
    def search_linkedin_with_gemini(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        max_results: int = 10
    ) -> List[Dict]:
        """
        使用Gemini搜索LinkedIn候选人
        
        Args:
            job_title: 岗位名称
            location: 地点
            keywords: 关键词
            company: 公司
            max_results: 最大结果数
            
        Returns:
            候选人列表
        """
        # 构建搜索查询
        search_query = self._build_search_query(
            job_title, location, keywords, company
        )
        
        print(f"  搜索查询: {search_query}")
        
        # 构建prompt - 优化版，要求尽可能多的结果
        prompt = f"""请在LinkedIn上搜索符合以下条件的候选人：

{search_query}

搜索策略：
1. 使用 site:linkedin.com/in 搜索LinkedIn个人主页
2. 尽可能找到更多符合条件的候选人（目标{max_results}位以上）
3. 搜索时使用多种关键词组合：
   - 职位的不同表达方式
   - 相关的职位名称
   - 行业关键词
4. 不要限制搜索结果数量，返回所有找到的候选人

对每位候选人，提取以下信息：
- 姓名
- 当前职位
- 当前公司
- 地点
- LinkedIn URL（完整URL）
- 简介（工作经历摘要，包括过往公司和年限）

请以JSON格式返回结果（不要markdown代码块）：
[
  {{
    "name": "姓名",
    "title": "职位",
    "company": "公司",
    "location": "地点",
    "url": "LinkedIn URL",
    "snippet": "简介"
  }}
]

重要：请返回所有找到的候选人，不要限制数量。"""
        
        try:
            response = self._call_gemini(prompt)
            candidates = self._parse_response(response)
            
            print(f"✓ Gemini搜索完成，找到 {len(candidates)} 位候选人")
            return candidates
            
        except Exception as e:
            print(f"✗ Gemini搜索失败: {e}")
            return []
    
    def _build_search_query(
        self,
        job_title: str,
        location: str,
        keywords: str,
        company: str
    ) -> str:
        """构建搜索查询"""
        parts = []
        
        if job_title:
            parts.append(f"职位：{job_title}")
        
        if location:
            parts.append(f"地点：{location}")
        
        if keywords:
            parts.append(f"关键词：{keywords}")
        
        if company:
            parts.append(f"公司：{company}")
        
        return "\n".join(parts)
    
    def _call_gemini(self, prompt: str) -> str:
        """调用Gemini API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120  # 增加到120秒，支持更复杂的搜索
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> List[Dict]:
        """解析Gemini返回的候选人列表"""
        try:
            # 移除思考标签
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            
            # 尝试提取JSON
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                candidates = json.loads(json_match.group())
                
                # 标准化字段
                standardized = []
                for c in candidates:
                    standardized.append({
                        "name": c.get('name', ''),
                        "title": c.get('title', ''),
                        "current_title": c.get('title', ''),
                        "company": c.get('company', ''),
                        "current_company": c.get('company', ''),
                        "location": c.get('location', ''),
                        "url": c.get('url', ''),
                        "snippet": c.get('snippet', ''),
                        "source": "gemini_search"
                    })
                
                return standardized
        except Exception as e:
            print(f"  ⚠ 解析失败: {e}")
        
        return []


class HybridSearcher:
    """混合搜索器 - 结合Tavily和Gemini"""
    
    def __init__(self):
        try:
            from tavily_search import TavilySearcher
            self.tavily = TavilySearcher()
        except:
            self.tavily = None
        
        self.gemini = GeminiSearcher()
    
    def search_with_fallback(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        max_results: int = 10,
        prefer_gemini: bool = False
    ) -> List[Dict]:
        """
        混合搜索 - 优先使用一种方式，失败时回退到另一种
        
        Args:
            job_title: 岗位名称
            location: 地点
            keywords: 关键词
            company: 公司
            max_results: 最大结果数
            prefer_gemini: 是否优先使用Gemini
            
        Returns:
            候选人列表
        """
        if prefer_gemini:
            # 优先使用Gemini
            print("  尝试使用Gemini搜索...")
            candidates = self.gemini.search_linkedin_with_gemini(
                job_title, location, keywords, company, max_results
            )
            
            if candidates:
                return candidates
            
            # Gemini失败，回退到Tavily
            if self.tavily:
                print("  Gemini失败，回退到Tavily...")
                return self.tavily.search_linkedin_candidates(
                    job_title, location, keywords, company, max_results
                )
        else:
            # 优先使用Tavily
            if self.tavily:
                print("  尝试使用Tavily搜索...")
                candidates = self.tavily.search_linkedin_candidates(
                    job_title, location, keywords, company, max_results
                )
                
                if candidates:
                    return candidates
            
            # Tavily失败，回退到Gemini
            print("  Tavily失败，回退到Gemini...")
            return self.gemini.search_linkedin_with_gemini(
                job_title, location, keywords, company, max_results
            )
        
        return []
    
    def search_both_and_merge(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        max_results: int = 10
    ) -> List[Dict]:
        """
        同时使用两种搜索方式，合并结果
        
        Returns:
            合并后的候选人列表（已去重）
        """
        print("  使用Tavily和Gemini双重搜索...")
        
        all_candidates = []
        seen_urls = set()
        
        # Tavily搜索
        if self.tavily:
            tavily_results = self.tavily.search_linkedin_candidates(
                job_title, location, keywords, company, max_results
            )
            print(f"    Tavily: {len(tavily_results)} 位")
            
            for c in tavily_results:
                url = c.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_candidates.append(c)
        
        # Gemini搜索
        gemini_results = self.gemini.search_linkedin_with_gemini(
            job_title, location, keywords, company, max_results
        )
        print(f"    Gemini: {len(gemini_results)} 位")
        
        for c in gemini_results:
            url = c.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_candidates.append(c)
        
        print(f"  ✓ 合并后: {len(all_candidates)} 位（已去重）")
        return all_candidates


if __name__ == "__main__":
    # 测试Gemini搜索
    print("="*60)
    print("测试Gemini搜索")
    print("="*60)
    
    searcher = GeminiSearcher()
    
    candidates = searcher.search_linkedin_with_gemini(
        job_title="Product Manager",
        location="London",
        max_results=5
    )
    
    if candidates:
        print(f"\n找到 {len(candidates)} 位候选人:")
        for i, c in enumerate(candidates, 1):
            print(f"\n{i}. {c['name']}")
            print(f"   职位: {c['title']}")
            print(f"   公司: {c['company']}")
            print(f"   URL: {c['url']}")
    
    # 测试混合搜索
    print("\n" + "="*60)
    print("测试混合搜索")
    print("="*60)
    
    hybrid = HybridSearcher()
    
    candidates = hybrid.search_both_and_merge(
        job_title="Organizational Development",
        location="London",
        max_results=5
    )
    
    print(f"\n混合搜索找到 {len(candidates)} 位候选人")
