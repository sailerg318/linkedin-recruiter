"""
岗位近义词扩充模块 - 使用大模型生成岗位相关的近义词和变体
"""

import requests
import json
from typing import List, Dict
from llm_config import API_BASE, MODEL_NAME, DEFAULT_KEY


class JobTitleExpander:
    """使用大模型扩充岗位关键词"""
    
    def __init__(self, api_key: str = DEFAULT_KEY):
        self.api_key = api_key
        self.api_base = API_BASE
        self.model_name = MODEL_NAME
        
    def expand_job_title(self, job_title: str, location: str = "", max_variants: int = 15) -> List[str]:
        """
        扩充岗位名称，生成近义词和变体
        
        Args:
            job_title: 原始岗位名称，如"org development"
            location: 地点（用于判断是否生成中文关键词）
            max_variants: 最多返回的变体数量（默认15个）
            
        Returns:
            岗位名称变体列表，包含原始名称
        """
        # 判断是否为中国地区
        is_china = any(city in location.lower() for city in [
            '中国', 'china', '北京', 'beijing', '上海', 'shanghai',
            '深圳', 'shenzhen', '广州', 'guangzhou', '杭州', 'hangzhou',
            '成都', 'chengdu', '南京', 'nanjing', '武汉', 'wuhan'
        ]) if location else True  # 默认包含中文
        
        chinese_instruction = """
   - 中英文对照（如"产品经理" → "Product Manager", "PM"）
   - 中文职位名称（如"OD" → "组织效能", "组织发展", "组织变革"）""" if is_china else """
   - 只使用英文表达，不要生成中文关键词"""
        
        prompt = f"""你是一个专业的招聘专家。请为以下岗位名称生成尽可能多的相关同义词、相关职位和职能名称。

岗位名称：{job_title}
地点：{location or '未指定'}

要求：
1. **至少生成 15 个**相关的岗位名称变体，越多越好
2. **重点关注多样化**：
   - 同义词和相关表达（如"OD" → "Organizational Development", "Organization Development"）
   - 常见缩写和全称（如"PM" → "Product Manager", "Project Manager"）
   - 相关职位名称（如"OD" → "OD Consultant", "OD Specialist", "Talent Development"）
   - 相关职能领域（如"OD" → "Organizational Effectiveness", "Change Management", "People Development"）{chinese_instruction}
   - 相关专业领域（如"OD" → "Organization Design", "Talent Management", "Learning and Development"）
3. **不要添加**：
   - 职级前缀（如 Senior, Lead, Principal, Junior 等）
   - 职级后缀（如 I, II, III 等）
   - 地点限制
4. 只返回岗位名称，每行一个
5. 不要添加编号、解释或其他内容
6. 按相关性从高到低排序
7. **尽可能多样化和全面**，覆盖该职位的所有可能表达方式

请直接输出岗位名称列表（至少15个）："""

        try:
            response = self._call_llm(prompt)
            variants = self._parse_response(response)
            
            # 确保原始岗位名称在列表中
            if job_title not in variants:
                variants.insert(0, job_title)
            
            # 限制数量
            variants = variants[:max_variants]
            
            print(f"✓ 岗位扩充完成: {job_title}")
            print(f"  生成了 {len(variants)} 个变体:")
            for i, variant in enumerate(variants, 1):
                print(f"  {i}. {variant}")
            
            return variants
            
        except Exception as e:
            print(f"✗ 岗位扩充失败: {e}")
            print(f"  使用原始岗位名称: {job_title}")
            return [job_title]
    
    def expand_with_context(
        self, 
        job_title: str, 
        industry: str = "",
        skills: List[str] = None,
        max_variants: int = 10
    ) -> List[str]:
        """
        根据上下文扩充岗位名称
        
        Args:
            job_title: 岗位名称
            industry: 行业领域，如"Tech"、"Finance"
            skills: 相关技能列表
            max_variants: 最多返回的变体数量
            
        Returns:
            岗位名称变体列表
        """
        context_parts = [f"岗位名称：{job_title}"]
        
        if industry:
            context_parts.append(f"行业领域：{industry}")
        
        if skills:
            context_parts.append(f"相关技能：{', '.join(skills)}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""你是一个专业的招聘专家。请根据以下信息生成相关的岗位名称变体。

{context}

要求：
1. 生成{max_variants}个相关的岗位名称
2. 考虑行业特点和技能要求
3. 包括不同职级和相关职位
4. 只返回岗位名称，每行一个
5. 按相关性从高到低排序

请直接输出岗位名称列表："""

        try:
            response = self._call_llm(prompt)
            variants = self._parse_response(response)
            
            if job_title not in variants:
                variants.insert(0, job_title)
            
            variants = variants[:max_variants]
            
            print(f"✓ 上下文岗位扩充完成: {job_title}")
            print(f"  生成了 {len(variants)} 个变体")
            
            return variants
            
        except Exception as e:
            print(f"✗ 上下文岗位扩充失败: {e}")
            return [job_title]
    
    def _call_llm(self, prompt: str) -> str:
        """调用大模型API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> List[str]:
        """解析大模型返回的岗位列表"""
        # 移除思考标签
        import re
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = re.sub(r'\*\*.*?\*\*', '', response)  # 移除加粗标记
        
        lines = response.strip().split("\n")
        variants = []
        
        for line in lines:
            # 清理行内容
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 跳过包含特殊标签的行
            if '<' in line or '>' in line or '*' in line:
                continue
            
            # 移除编号（如"1. "、"- "等）
            line = re.sub(r'^[\d\.\-•*\s]+', '', line)
            line = line.strip()
            
            # 跳过太短或太长的内容
            if len(line) < 3 or len(line) > 100:
                continue
            
            # 跳过明显不是岗位名称的内容
            skip_keywords = ['要求', '说明', '注意', '以下', '列表', 'list', 'note']
            if any(kw in line.lower() for kw in skip_keywords):
                continue
            
            variants.append(line)
        
        return variants
    
    def generate_search_queries(
        self, 
        job_title: str,
        location: str = "",
        company: str = "",
        max_queries: int = 5
    ) -> List[Dict[str, str]]:
        """
        生成多个搜索查询组合
        
        Args:
            job_title: 岗位名称
            location: 地点
            company: 公司
            max_queries: 最多生成的查询数量
            
        Returns:
            搜索查询列表，每个查询包含job_title、location、company
        """
        # 扩充岗位名称
        job_variants = self.expand_job_title(job_title, max_variants=max_queries)
        
        # 生成查询组合
        queries = []
        for variant in job_variants:
            query = {
                "job_title": variant,
                "location": location,
                "company": company
            }
            queries.append(query)
        
        print(f"\n✓ 生成了 {len(queries)} 个搜索查询")
        return queries


if __name__ == "__main__":
    # 测试代码
    expander = JobTitleExpander()
    
    # 测试1：基础扩充
    print("="*60)
    print("测试1：基础岗位扩充")
    print("="*60)
    variants = expander.expand_job_title("org development", max_variants=8)
    
    # 测试2：带上下文的扩充
    print("\n" + "="*60)
    print("测试2：带上下文的岗位扩充")
    print("="*60)
    variants = expander.expand_with_context(
        job_title="Python Engineer",
        industry="Tech",
        skills=["AI", "Machine Learning", "Deep Learning"],
        max_variants=8
    )
    
    # 测试3：生成搜索查询
    print("\n" + "="*60)
    print("测试3：生成搜索查询组合")
    print("="*60)
    queries = expander.generate_search_queries(
        job_title="Data Scientist",
        location="San Francisco",
        company="",
        max_queries=5
    )
    
    for i, query in enumerate(queries, 1):
        print(f"\n查询 {i}:")
        print(f"  岗位: {query['job_title']}")
        print(f"  地点: {query['location']}")
