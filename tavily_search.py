"""
Tavily搜索模块 - 使用Tavily API搜索LinkedIn人选
"""

import requests
import re
from typing import List, Dict, Optional
from config import (
    TAVILY_API_KEY,
    LINKEDIN_SEARCH_TEMPLATE,
    LINKEDIN_ADVANCED_SEARCH_TEMPLATE,
    MAX_SEARCH_RESULTS
)


class TavilySearcher:
    """使用Tavily API进行LinkedIn人才搜索"""
    
    def __init__(self, api_key: str = TAVILY_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        
    def search_linkedin_candidates(
        self,
        job_title: str,
        keywords: str = "",
        location: str = "",
        company: str = "",
        max_results: int = MAX_SEARCH_RESULTS
    ) -> List[Dict]:
        """
        搜索LinkedIn上符合岗位要求的候选人
        
        Args:
            job_title: 岗位名称，如"Python工程师"、"产品经理"
            keywords: 额外的关键词，如"AI"、"区块链"等
            location: 地点，如"San Francisco"、"北京"
            company: 公司，如"Google"、"阿里巴巴"
            max_results: 最大返回结果数
            
        Returns:
            候选人信息列表，每个元素包含：
            - name: 姓名（从页面内容提取）
            - url: LinkedIn个人主页URL
            - title: 当前职位
            - company: 当前公司
            - location: 地点
            - snippet: 完整简介
            - raw_content: 原始页面内容
        """
        # 构建搜索查询 - 使用高级模板
        if location or company:
            query = LINKEDIN_ADVANCED_SEARCH_TEMPLATE.format(
                job_title=job_title,
                location=location,
                company=company,
                keywords=keywords
            )
        else:
            query = LINKEDIN_SEARCH_TEMPLATE.format(
                job_title=job_title,
                keywords=keywords
            )
        
        # 准备API请求
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",  # 使用高级搜索获取更多结果
            "max_results": max_results,
            "include_domains": ["linkedin.com"],  # 只搜索LinkedIn
            "include_answer": False,  # 不需要AI总结
            "include_raw_content": True,  # 获取完整页面内容
            "include_images": False  # 不需要图片
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            candidates = self._parse_search_results(data)
            
            print(f"✓ 搜索完成，找到 {len(candidates)} 位候选人")
            return candidates
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Tavily搜索失败: {e}")
            return []
    
    def _parse_search_results(self, data: Dict) -> List[Dict]:
        """解析Tavily搜索结果，提取完整信息"""
        candidates = []
        
        results = data.get("results", [])
        for result in results:
            url = result.get("url", "")
            
            # 确保是LinkedIn个人主页
            if "/in/" not in url:
                continue
            
            # 获取原始内容和摘要
            raw_content = result.get("raw_content", "")
            snippet = result.get("content", "")
            title = result.get("title", "")
            
            # 从内容中提取结构化信息
            extracted_info = self._extract_profile_info(
                raw_content if raw_content else snippet,
                title,
                url
            )
                
            candidate = {
                "name": extracted_info.get("name", "Unknown"),
                "url": url,
                "title": extracted_info.get("title", ""),
                "company": extracted_info.get("company", ""),
                "location": extracted_info.get("location", ""),
                "snippet": snippet,
                "raw_content": raw_content,
                "score": result.get("score", 0)
            }
            
            candidates.append(candidate)
        
        return candidates
    
    def _extract_profile_info(self, content: str, title: str, url: str) -> Dict:
        """
        从LinkedIn页面内容中提取结构化信息
        
        Args:
            content: 页面内容
            title: 页面标题
            url: LinkedIn URL
            
        Returns:
            包含name, title, company, location的字典
        """
        info = {
            "name": "",
            "title": "",
            "company": "",
            "location": ""
        }
        
        # 1. 从标题中提取姓名和职位
        # LinkedIn标题格式通常是: "Name - Title at Company | LinkedIn"
        if title:
            # 移除 "| LinkedIn" 后缀
            title_clean = re.sub(r'\s*\|\s*LinkedIn.*$', '', title)
            
            # 尝试分割姓名和职位
            if ' - ' in title_clean:
                parts = title_clean.split(' - ', 1)
                info["name"] = parts[0].strip()
                
                # 从职位部分提取职位和公司
                if len(parts) > 1:
                    job_part = parts[1]
                    # 匹配 "Title at Company" 格式
                    at_match = re.search(r'(.+?)\s+at\s+(.+)', job_part, re.IGNORECASE)
                    if at_match:
                        info["title"] = at_match.group(1).strip()
                        info["company"] = at_match.group(2).strip()
                    else:
                        info["title"] = job_part.strip()
            else:
                # 如果没有 " - "，整个标题可能就是姓名
                info["name"] = title_clean.strip()
        
        # 2. 如果没有从标题提取到姓名，尝试从URL提取
        if not info["name"]:
            info["name"] = self._extract_name_from_url(url)
        
        # 3. 从内容中提取更多信息
        if content:
            # 提取地点信息
            # 常见模式: "Location: San Francisco", "Based in Beijing", "北京市"
            location_patterns = [
                r'Location[:\s]+([^\n\|]+)',
                r'Based in\s+([^\n\|]+)',
                r'(?:位于|所在地)[:\s]*([^\n\|]+)',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    info["location"] = match.group(1).strip()
                    break
            
            # 如果标题中没有提取到公司，从内容中提取
            if not info["company"]:
                company_patterns = [
                    r'(?:at|@)\s+([A-Z][^\n\|,]{2,50})',
                    r'Company[:\s]+([^\n\|]+)',
                    r'(?:公司|企业)[:\s]*([^\n\|]+)',
                ]
                for pattern in company_patterns:
                    match = re.search(pattern, content)
                    if match:
                        info["company"] = match.group(1).strip()
                        break
            
            # 如果标题中没有提取到职位，从内容中提取
            if not info["title"]:
                title_patterns = [
                    r'(?:Title|Position|Role)[:\s]+([^\n\|]+)',
                    r'(?:职位|岗位)[:\s]*([^\n\|]+)',
                ]
                for pattern in title_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        info["title"] = match.group(1).strip()
                        break
        
        return info
    
    def _extract_name_from_url(self, url: str) -> str:
        """从LinkedIn URL中提取姓名（备用方法）"""
        try:
            # LinkedIn URL格式: https://www.linkedin.com/in/john-doe-123456/
            parts = url.split("/in/")
            if len(parts) > 1:
                name_part = parts[1].rstrip("/").split("-")
                # 移除数字后缀
                name_parts = [p for p in name_part if not p.isdigit()]
                return " ".join(name_parts).title()
        except:
            pass
        return "Unknown"
    
    def batch_search(
        self, 
        job_requirements: Dict[str, str]
    ) -> List[Dict]:
        """
        批量搜索多个岗位需求
        
        Args:
            job_requirements: 岗位需求字典，格式如：
                {
                    "job_title": "Python工程师",
                    "keywords": "AI 机器学习 深度学习"
                }
        
        Returns:
            所有候选人列表
        """
        job_title = job_requirements.get("job_title", "")
        keywords = job_requirements.get("keywords", "")
        location = job_requirements.get("location", "")
        company = job_requirements.get("company", "")
        
        if not job_title:
            print("✗ 错误：必须提供岗位名称")
            return []
        
        print(f"\n开始搜索岗位: {job_title}")
        if keywords:
            print(f"关键词: {keywords}")
        if location:
            print(f"地点: {location}")
        if company:
            print(f"公司: {company}")
        print("-" * 50)
        
        candidates = self.search_linkedin_candidates(
            job_title=job_title,
            keywords=keywords,
            location=location,
            company=company
        )
        
        return candidates


if __name__ == "__main__":
    # 测试代码
    searcher = TavilySearcher()
    
    # 示例：搜索Python工程师
    test_requirements = {
        "job_title": "Python Engineer",
        "keywords": "AI Machine Learning"
    }
    
    results = searcher.batch_search(test_requirements)
    
    print(f"\n找到 {len(results)} 位候选人:")
    for i, candidate in enumerate(results[:5], 1):
        print(f"{i}. {candidate['name']}")
        print(f"   职位: {candidate['title']}")
        print(f"   链接: {candidate['url']}")
        print()
