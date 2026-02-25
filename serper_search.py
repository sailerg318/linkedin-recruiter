"""
Serper搜索模块 - 使用Serper.dev API进行Google搜索
官方文档: https://serper.dev/docs
"""

import requests
import time
from typing import List, Dict


class SerperSearcher:
    """使用Serper.dev API进行Google搜索"""
    
    def __init__(self, api_key: str = "d88085d4543221682eecd92082f27247f71d902f"):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search_linkedin(
        self,
        query: str,
        num_results: int = 50,
        max_pages: int = 5
    ) -> List[Dict]:
        """
        使用Serper搜索LinkedIn（分页策略）
        
        Args:
            query: 搜索查询，如 'site:linkedin.com/in/ "Product Manager" "Shanghai"'
            num_results: 期望返回结果数量（通过分页实现）
            max_pages: 最大翻页数（默认5页，每页10条）
            
        Returns:
            候选人列表
        """
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        all_candidates = []
        seen_urls = set()  # 用于去重
        results_per_page = 10  # Serper API 限制
        
        # 计算需要的页数
        pages_needed = min(max_pages, (num_results + results_per_page - 1) // results_per_page)
        
        print(f"\n{'='*60}")
        print(f"🔍 Serper 搜索 - 翻页模式")
        print(f"{'='*60}")
        print(f"目标结果数: {num_results}")
        print(f"预计翻页数: {pages_needed}")
        print(f"{'='*60}\n")
        
        try:
            for page in range(pages_needed):
                start_index = page * results_per_page
                
                print(f"📄 正在请求第 {page + 1} 页 (start={start_index})...")
                
                payload = {
                    'q': query,
                    'num': results_per_page,
                    'start': start_index,
                    'gl': 'cn',
                    'hl': 'zh-cn'
                }
                
                try:
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    candidates = self._parse_results(data)
                    
                    if not candidates:
                        # 没有更多结果，停止翻页
                        break
                    
                    # 去重：只添加未见过的URL
                    new_candidates = []
                    for candidate in candidates:
                        url = candidate.get('url', '')
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            new_candidates.append(candidate)
                    
                    all_candidates.extend(new_candidates)
                    print(f"✓ 第 {page + 1} 页: 找到 {len(candidates)} 位候选人 (去重后 {len(new_candidates)} 位) | 累计: {len(all_candidates)} 位")
                    
                    # 如果返回结果少于10条，说明已经到底了
                    if len(candidates) < results_per_page:
                        print(f"⚠️  返回结果少于 {results_per_page} 条，已到底")
                        break
                    
                    # 如果已经达到目标数量，停止翻页
                    if len(all_candidates) >= num_results:
                        print(f"✓ 已达到目标数量 {num_results}，停止翻页")
                        break
                    
                    # 防止请求过快
                    if page < pages_needed - 1:
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"  ✗ 第 {page + 1} 页失败: {e}")
                    break
            
            print(f"✓ Serper搜索完成，共找到 {len(all_candidates)} 位候选人（已去重）")
            return all_candidates
            
        except Exception as e:
            print(f"✗ Serper搜索失败: {e}")
            return all_candidates if all_candidates else []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        """解析Serper返回的结果"""
        candidates = []
        
        organic_results = data.get('organic', [])
        
        for result in organic_results:
            # 只处理LinkedIn个人主页
            link = result.get('link', '')
            if 'linkedin.com/in/' in link:
                candidate = {
                    'name': self._extract_name(result.get('title', '')),
                    'title': self._extract_title(result.get('title', '')),
                    'url': link,
                    'snippet': result.get('snippet', ''),
                    'source': 'serper'
                }
                candidates.append(candidate)
        
        return candidates
    
    def _extract_name(self, title: str) -> str:
        """从标题提取姓名"""
        # LinkedIn标题格式通常是: "Name - Title | LinkedIn"
        if ' - ' in title:
            name = title.split(' - ')[0].strip()
            return name
        return title.split('|')[0].strip()
    
    def _extract_title(self, title: str) -> str:
        """从标题提取职位"""
        # LinkedIn标题格式通常是: "Name - Title | LinkedIn"
        if ' - ' in title and '|' in title:
            parts = title.split(' - ')
            if len(parts) > 1:
                title_part = parts[1].split('|')[0].strip()
                return title_part
        return ''


# 测试代码
if __name__ == "__main__":
    searcher = SerperSearcher()
    
    # 测试搜索
    query = 'site:linkedin.com/in/ "Product Manager" "Shanghai"'
    print(f"搜索查询: {query}\n")
    
    results = searcher.search_linkedin(query, num_results=10)
    
    if results:
        print(f"\n找到 {len(results)} 位候选人:\n")
        for i, candidate in enumerate(results, 1):
            print(f"{i}. {candidate['name']}")
            print(f"   职位: {candidate['title']}")
            print(f"   URL: {candidate['url']}")
            print(f"   简介: {candidate['snippet'][:100]}...")
            print()
