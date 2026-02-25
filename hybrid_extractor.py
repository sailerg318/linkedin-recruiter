"""
混合模式信息提取模块 - 代码提取 + LLM辅助
"""

import requests
import re
from typing import Dict, Optional
from llm_config import API_BASE, DEFAULT_KEY


class HybridProfileExtractor:
    """混合模式LinkedIn主页信息提取器"""
    
    def __init__(self, api_key: str = DEFAULT_KEY):
        self.api_key = api_key
        self.api_base = API_BASE
        self.flash_model = "[福利]gemini-3-flash-preview"
    
    def extract_profile_info(
        self, 
        raw_content: str, 
        title: str, 
        url: str,
        use_llm_fallback: bool = True
    ) -> Dict:
        """
        混合模式提取LinkedIn主页信息
        
        Args:
            raw_content: LinkedIn主页完整内容
            title: 页面标题
            url: LinkedIn URL
            use_llm_fallback: 代码提取失败时是否使用LLM
            
        Returns:
            提取的信息字典
        """
        # 1. 先用代码提取（快速、免费）
        info = self._extract_by_code(raw_content, title, url)
        
        # 2. 检查提取质量
        quality_score = self._assess_extraction_quality(info)
        
        # 3. 如果质量不够且允许使用LLM，则用LLM补充
        if quality_score < 0.7 and use_llm_fallback and raw_content:
            print(f"  ⚠ 代码提取质量较低({quality_score:.2f})，使用LLM辅助")
            llm_info = self._extract_by_llm(raw_content, title)
            # 合并结果，LLM结果优先
            info = self._merge_info(info, llm_info)
        
        return info
    
    def _extract_by_code(self, content: str, title: str, url: str) -> Dict:
        """使用代码提取信息（正则表达式和字符串匹配）"""
        info = {
            "name": "",
            "current_title": "",
            "current_company": "",
            "location": "",
            "experience_years": 0,
            "companies": [],
            "has_consulting_background": False,
            "has_corporate_background": False,
            "key_skills": [],
            "education": "",
            "extraction_method": "code"
        }
        
        # 1. 从标题提取姓名和职位
        if title:
            title_clean = re.sub(r'\s*\|\s*LinkedIn.*$', '', title)
            if ' - ' in title_clean:
                parts = title_clean.split(' - ', 1)
                info["name"] = parts[0].strip()
                if len(parts) > 1:
                    job_part = parts[1]
                    at_match = re.search(r'(.+?)\s+at\s+(.+)', job_part, re.IGNORECASE)
                    if at_match:
                        info["current_title"] = at_match.group(1).strip()
                        info["current_company"] = at_match.group(2).strip()
                    else:
                        info["current_title"] = job_part.strip()
            else:
                info["name"] = title_clean.strip()
        
        # 2. 如果没有从标题提取到姓名，从URL提取
        if not info["name"]:
            info["name"] = self._extract_name_from_url(url)
        
        if not content:
            return info
        
        # 3. 提取地点
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
        
        # 4. 提取公司列表
        company_patterns = [
            r'###\s+([A-Z][^\n]+?)\s+\[',  # Markdown格式
            r'at\s+([A-Z][^\n,]{2,50})',
            r'@\s+([A-Z][^\n,]{2,50})',
        ]
        companies = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                company = match.strip()
                if len(company) > 2 and len(company) < 50:
                    companies.add(company)
        info["companies"] = list(companies)[:10]  # 限制数量
        
        # 5. 检查咨询背景
        consulting_keywords = [
            "McKinsey", "BCG", "Bain", "Mercer", "Aon", 
            "Willis Towers Watson", "WTW", "Korn Ferry",
            "Deloitte", "PwC", "EY", "KPMG",
            "德勤", "普华永道", "安永", "毕马威"
        ]
        info["has_consulting_background"] = any(
            kw.lower() in content.lower() for kw in consulting_keywords
        )
        
        # 6. 检查甲方背景（有多个公司经验）
        info["has_corporate_background"] = len(info["companies"]) > 1
        
        # 7. 提取技能
        skills_section = re.search(r'## Skills(.*?)(?=##|$)', content, re.DOTALL)
        if skills_section:
            skills_text = skills_section.group(1)
            # 简单提取（实际可以更复杂）
            skills = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', skills_text)
            info["key_skills"] = list(set(skills))[:10]
        
        # 8. 估算工作年限
        years_patterns = [
            r'(\d+)\+?\s*年',
            r'(\d+)\+?\s*years?',
        ]
        years_found = []
        for pattern in years_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            years_found.extend([int(m) for m in matches])
        if years_found:
            info["experience_years"] = max(years_found)
        
        return info
    
    def _extract_by_llm(self, content: str, title: str) -> Dict:
        """使用LLM提取信息"""
        # 限制内容长度以节省成本
        content_preview = content[:3000] if len(content) > 3000 else content
        
        prompt = f"""请从以下LinkedIn个人主页内容中提取关键信息，返回JSON格式。

标题：{title}

内容：
{content_preview}

请提取：
1. name: 姓名
2. current_title: 当前职位
3. current_company: 当前公司
4. location: 地点
5. experience_years: 总工作年限（估算）
6. companies: 工作过的所有公司列表（最多10个）
7. has_consulting_background: 是否有咨询公司背景（McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG等）
8. has_corporate_background: 是否有企业（甲方）背景
9. key_skills: 关键技能列表（最多10个）
10. education: 最高学历

直接返回JSON，不要解释：
```json
{{
  "name": "...",
  "current_title": "...",
  "current_company": "...",
  "location": "...",
  "experience_years": 0,
  "companies": [...],
  "has_consulting_background": true/false,
  "has_corporate_background": true/false,
  "key_skills": [...],
  "education": "..."
}}
```"""

        try:
            response = self._call_llm(prompt)
            
            # 提取JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                import json
                info = json.loads(json_match.group(1))
                info["extraction_method"] = "llm"
                return info
        except Exception as e:
            print(f"  ✗ LLM提取失败: {e}")
        
        return {}
    
    def _assess_extraction_quality(self, info: Dict) -> float:
        """评估提取质量（0-1）"""
        score = 0.0
        weights = {
            "name": 0.3,
            "current_title": 0.2,
            "current_company": 0.15,
            "location": 0.1,
            "companies": 0.15,
            "experience_years": 0.1
        }
        
        if info.get("name") and info["name"] != "Unknown":
            score += weights["name"]
        if info.get("current_title"):
            score += weights["current_title"]
        if info.get("current_company"):
            score += weights["current_company"]
        if info.get("location"):
            score += weights["location"]
        if info.get("companies") and len(info["companies"]) > 0:
            score += weights["companies"]
        if info.get("experience_years") and info["experience_years"] > 0:
            score += weights["experience_years"]
        
        return score
    
    def _merge_info(self, code_info: Dict, llm_info: Dict) -> Dict:
        """合并代码提取和LLM提取的结果"""
        merged = code_info.copy()
        
        # LLM结果优先，但只覆盖空值
        for key, value in llm_info.items():
            if value and (not merged.get(key) or merged.get(key) == "Unknown"):
                merged[key] = value
        
        merged["extraction_method"] = "hybrid"
        return merged
    
    def _extract_name_from_url(self, url: str) -> str:
        """从URL提取姓名（备用）"""
        try:
            parts = url.split("/in/")
            if len(parts) > 1:
                name_part = parts[1].rstrip("/").split("-")
                name_parts = [p for p in name_part if not p.isdigit()]
                return " ".join(name_parts).title()
        except:
            pass
        return "Unknown"
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.flash_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # 测试代码
    extractor = HybridProfileExtractor()
    
    # 测试数据
    test_title = "John Doe - Senior Python Engineer at Google | LinkedIn"
    test_content = """
    # John Doe
    **Senior Python Engineer at Google**
    San Francisco, California, United States
    
    ## About
    10 years of experience in software development...
    
    ## Experience
    ### Google
    Senior Python Engineer
    2020 - Present
    
    ### McKinsey & Company
    Software Consultant
    2015 - 2020
    
    ## Skills
    Python, Machine Learning, AWS, Docker
    """
    test_url = "https://linkedin.com/in/john-doe-123"
    
    info = extractor.extract_profile_info(test_content, test_title, test_url)
    
    print("\n提取结果:")
    print(f"姓名: {info['name']}")
    print(f"职位: {info['current_title']}")
    print(f"公司: {info['current_company']}")
    print(f"地点: {info['location']}")
    print(f"年限: {info['experience_years']}")
    print(f"公司列表: {info['companies']}")
    print(f"咨询背景: {info['has_consulting_background']}")
    print(f"甲方背景: {info['has_corporate_background']}")
    print(f"提取方式: {info['extraction_method']}")
