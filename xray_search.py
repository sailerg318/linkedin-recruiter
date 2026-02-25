"""
Google X-Ray搜索策略 - 使用Serper.dev实现切片搜索
基于Google Dorking技术，通过Serper API合法访问Google搜索
"""

from typing import List, Dict
from serper_search import SerperSearcher
from llm_config import API_BASE, DEFAULT_KEY
import requests
import json
import re
import time
import random


class XRaySearchStrategy:
    """X-Ray切片搜索策略 - 穷尽搜索候选人"""
    
    def __init__(self, serper_api_key: str = "d88085d4543221682eecd92082f27247f71d902f"):
        self.searcher = SerperSearcher(api_key=serper_api_key)
        self.all_candidates = []
        self.seen_urls = set()
        self.api_key = DEFAULT_KEY
        self.api_base = API_BASE
    
    def generate_top_companies(
        self,
        industry: str,
        location: str,
        top_n: int = 20
    ) -> List[str]:
        """
        使用Gemini Flash生成行业头部公司列表
        
        Args:
            industry: 行业，如"新零售"、"物流"
            location: 地点，如"上海"
            top_n: 返回公司数量
            
        Returns:
            公司名称列表
        """
        print(f"\n使用Gemini Flash生成{location}{industry}行业头部公司...")
        
        prompt = f"""请列出{location}地区{industry}行业的前{top_n}家头部公司。

要求：
1. 只返回公司名称，每行一个
2. 包括中文名和英文名（如果有）
3. 按知名度和规模排序
4. 不要添加编号、解释或其他内容

示例格式：
阿里巴巴
Alibaba
京东
JD.com

请直接输出公司列表："""
        
        try:
            response = self._call_gemini_flash(prompt)
            
            # 解析公司列表
            companies = []
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                # 跳过空行和包含特殊字符的行
                if line and not any(char in line for char in ['<', '>', '*', '#', ':', '。']):
                    # 移除编号
                    line = re.sub(r'^\d+[\.\)、]\s*', '', line)
                    if line:
                        companies.append(line)
            
            companies = companies[:top_n]
            print(f"✓ 生成了 {len(companies)} 家公司")
            for i, company in enumerate(companies[:10], 1):
                print(f"  {i}. {company}")
            if len(companies) > 10:
                print(f"  ... 还有 {len(companies)-10} 家")
            
            return companies
            
        except Exception as e:
            print(f"✗ 生成公司列表失败: {e}")
            return []
    
    def generate_titles_from_experience(
        self,
        base_keyword: str,
        min_years: int,
        max_years: int
    ) -> List[str]:
        """
        根据年限要求生成职级列表
        
        Args:
            base_keyword: 基础岗位，如"Product Manager"
            min_years: 最小年限
            max_years: 最大年限
            
        Returns:
            职级列表
        """
        print(f"\n根据年限要求({min_years}-{max_years}年)生成职级列表...")
        
        # 根据年限映射职级
        titles = []
        
        if min_years <= 3:
            titles.extend(["Junior", "Associate"])
        
        if min_years <= 5 and max_years >= 3:
            titles.extend(["", "Mid-level"])  # 空字符串代表无职级前缀
        
        if min_years <= 8 and max_years >= 5:
            titles.extend(["Senior", "Sr"])
        
        if min_years <= 12 and max_years >= 8:
            titles.extend(["Lead", "Staff", "Principal"])
        
        if max_years >= 10:
            titles.extend(["Manager", "Director"])
        
        print(f"✓ 生成了 {len(titles)} 个职级")
        for title in titles:
            display_title = title if title else "(无职级前缀)"
            print(f"  - {display_title}")
        
        return titles
    
    def _call_gemini_flash(self, prompt: str) -> str:
        """调用Gemini Flash"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "[福利]gemini-3-flash-preview",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def generate_search_queries(
        self,
        base_keyword: str,
        location: str,
        companies: List[str] = None,
        titles: List[str] = None
    ) -> List[Dict]:
        """
        生成切片搜索指令
        
        Args:
            base_keyword: 核心关键词，如"Product Manager"
            location: 地点，如"Shanghai"
            companies: 公司列表，如["拼多多", "携程"]
            titles: 职级列表，如["Senior", "Lead"]
            
        Returns:
            搜索指令列表
        """
        queries = []
        
        print(f"\n{'='*60}")
        print("生成X-Ray切片搜索指令")
        print(f"{'='*60}")
        print(f"核心关键词: {base_keyword}")
        print(f"目标地点: {location}")
        
        # Phase 1: 包含切片 (Inclusion Slicing) - 头部公司优先
        if companies:
            print(f"\n策略1: 包含切片（头部公司优先）")
            for company in companies:
                query = {
                    "type": "inclusion",
                    "keyword": base_keyword,
                    "location": location,
                    "company": company,
                    "search_string": f'site:linkedin.com/in/ "{base_keyword}" "{location}" "{company}"'
                }
                queries.append(query)
            print(f"  生成 {len(companies)} 个头部公司切片")
        
        # Phase 2: 职级切片 (Title Slicing)
        if titles:
            print(f"\n策略2: 职级切片")
            for title in titles:
                query = {
                    "type": "title",
                    "keyword": f"{title} {base_keyword}",
                    "location": location,
                    "company": "",
                    "search_string": f'site:linkedin.com/in/ "{title} {base_keyword}" "{location}"'
                }
                queries.append(query)
            print(f"  生成 {len(titles)} 个职级切片")
        
        # Phase 3: 基础切片（不限制公司）
        # 注意：不使用排除切片，因为：
        # 1. 中小公司候选人质量参差不齐
        # 2. 我们有Flash细筛可以过滤
        # 3. 专注于头部公司和职级切片更高效
        print(f"\n策略3: 基础切片（不限制公司）")
        query = {
            "type": "basic",
            "keyword": base_keyword,
            "location": location,
            "company": "",
            "search_string": f'site:linkedin.com/in/ "{base_keyword}" "{location}"'
        }
        queries.append(query)
        print(f"  生成 1 个基础切片（覆盖所有公司）")
        
        print(f"\n✓ 总共生成 {len(queries)} 个切片搜索指令")
        return queries
    
    def execute_xray_search(
        self,
        base_keyword: str,
        location: str,
        industry: str = None,
        min_years: int = None,
        max_years: int = None,
        companies: List[str] = None,
        titles: List[str] = None,
        max_results_per_query: int = 10,
        delay_range: tuple = (5, 15)
    ) -> List[Dict]:
        """
        执行X-Ray切片搜索
        
        Args:
            base_keyword: 核心关键词
            location: 地点
            industry: 行业（如果提供，会自动生成头部公司）
            min_years: 最小年限（如果提供，会自动生成职级）
            max_years: 最大年限
            companies: 公司列表（手动指定）
            titles: 职级列表（手动指定）
            max_results_per_query: 每个查询最多返回结果数
            delay_range: 延时范围（秒）
            
        Returns:
            去重后的候选人列表
        """
        print(f"\n{'='*60}")
        print("执行X-Ray切片搜索")
        print(f"{'='*60}\n")
        
        # 自动生成公司列表（如果提供了行业）
        if industry and not companies:
            companies = self.generate_top_companies(industry, location, top_n=20)
        
        # 自动生成职级列表（如果提供了年限）
        if min_years is not None and max_years is not None and not titles:
            titles = self.generate_titles_from_experience(
                base_keyword, min_years, max_years
            )
        
        # 生成搜索指令
        queries = self.generate_search_queries(
            base_keyword, location, companies, titles
        )
        
        # 执行搜索
        print(f"\n{'='*60}")
        print(f"开始执行 {len(queries)} 个切片搜索")
        print(f"{'='*60}\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] 切片类型: {query['type']}")
            print(f"  搜索指令: {query['search_string']}")
            
            try:
                # 使用Gemini Search执行
                results = self.searcher.search_linkedin_with_gemini(
                    job_title=query['keyword'],
                    location=query['location'],
                    company=query['company'],
                    max_results=max_results_per_query
                )
                
                # 去重
                new_count = 0
                for candidate in results:
                    url = candidate.get('url', '')
                    if url and url not in self.seen_urls:
                        self.seen_urls.add(url)
                        candidate['keyword_source'] = query['search_string']
                        candidate['slice_type'] = query['type']
                        self.all_candidates.append(candidate)
                        new_count += 1
                
                print(f"  本轮找到: {len(results)} 位")
                print(f"  新增候选人: {new_count} 位")
                print(f"  累计总数: {len(self.all_candidates)} 位")
                
                # 随机延时（模拟人类行为）
                if i < len(queries):
                    delay = random.uniform(*delay_range)
                    print(f"  等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"  ✗ 搜索失败: {e}")
                # 如果是超时或限流，等待更长时间
                if "timeout" in str(e).lower() or "429" in str(e):
                    print(f"  ⚠ 检测到限流，等待60秒...")
                    time.sleep(60)
                continue
        
        print(f"\n{'='*60}")
        print("X-Ray切片搜索完成")
        print(f"{'='*60}")
        print(f"✓ 总共找到 {len(self.all_candidates)} 位不重复的候选人")
        
        # 统计各切片的贡献
        self._print_statistics()
        
        return self.all_candidates
    
    def _print_statistics(self):
        """打印统计信息"""
        print(f"\n切片贡献统计:")
        
        slice_stats = {}
        for candidate in self.all_candidates:
            slice_type = candidate.get('slice_type', 'unknown')
            slice_stats[slice_type] = slice_stats.get(slice_type, 0) + 1
        
        for slice_type, count in slice_stats.items():
            percentage = (count / len(self.all_candidates)) * 100
            print(f"  {slice_type}: {count} 位 ({percentage:.1f}%)")
    
    def save_to_csv(self, filename: str = None):
        """保存结果到CSV"""
        import pandas as pd
        from datetime import datetime
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_candidates_{timestamp}.csv"
        
        df = pd.DataFrame(self.all_candidates)
        
        # 选择关键字段
        columns = [
            'keyword_source',
            'slice_type', 
            'name',
            'title',
            'company',
            'location',
            'url',
            'snippet'
        ]
        
        # 只保留存在的列
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✓ 结果已保存到: {filename}")
        return filename


# 使用示例
if __name__ == "__main__":
    # 初始化X-Ray搜索
    xray = XRaySearchStrategy()
    
    # 定义搜索参数
    base_keyword = "Product Manager"
    location = "Shanghai"
    
    # 大厂列表
    companies = [
        "拼多多", "Pinduoduo",
        "携程", "Ctrip",
        "小红书", "Xiaohongshu",
        "bilibili", "哔哩哔哩"
    ]
    
    # 职级列表
    titles = [
        "Senior",
        "Lead", 
        "Principal",
        "Staff"
    ]
    
    # 执行X-Ray切片搜索
    candidates = xray.execute_xray_search(
        base_keyword=base_keyword,
        location=location,
        companies=companies,
        titles=titles,
        max_results_per_query=10,
        delay_range=(5, 15)
    )
    
    # 保存结果
    if candidates:
        xray.save_to_csv()
        
        print(f"\n找到的候选人示例（前5位）:")
        for i, c in enumerate(candidates[:5], 1):
            print(f"\n{i}. {c.get('name', 'Unknown')}")
            print(f"   职位: {c.get('title', 'N/A')}")
            print(f"   公司: {c.get('company', 'N/A')}")
            print(f"   来源: {c.get('slice_type', 'N/A')}")
