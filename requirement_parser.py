"""
智能需求解析模块 - 使用大模型解析自然语言招聘需求
"""

import requests
import json
import re
from typing import Dict, List, Any
from llm_config import API_BASE, DEFAULT_KEY


class RequirementParser:
    """智能需求解析器"""
    
    def __init__(self, api_key: str = DEFAULT_KEY):
        self.api_key = api_key
        self.api_base = API_BASE
        self.flash_model = "[福利]gemini-3-flash-preview"  # 用于快速解析
        
        # 预定义的公司列表
        self.consulting_firms = {
            "MBB": ["McKinsey", "BCG", "Bain"],
            "人力四大": ["Mercer", "Aon", "Willis Towers Watson", "WTW", "Korn Ferry"],
            "四大": ["Deloitte", "PwC", "EY", "KPMG", "德勤", "普华永道", "安永", "毕马威"]
        }
    
    def parse_requirement(self, requirement_text: str) -> Dict[str, Any]:
        """
        解析自然语言招聘需求
        
        Args:
            requirement_text: 自然语言描述，如"我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
            
        Returns:
            结构化的需求字典
        """
        print(f"\n{'='*60}")
        print("智能需求解析")
        print(f"{'='*60}")
        print(f"原始需求：{requirement_text}\n")
        
        # 使用大模型解析需求
        parsed = self._call_llm_parse(requirement_text)
        
        # 后处理和增强
        enhanced = self._enhance_parsed_requirement(parsed)
        
        print(f"\n{'='*60}")
        print("解析结果")
        print(f"{'='*60}")
        print(json.dumps(enhanced, ensure_ascii=False, indent=2))
        
        return enhanced
    
    def _call_llm_parse(self, requirement_text: str) -> Dict:
        """使用大模型解析需求"""
        prompt = f"""你是一个专业的招聘需求分析专家。请将以下自然语言描述的招聘需求解析为结构化的JSON格式。

招聘需求：{requirement_text}

请提取以下信息（如果有的话）：
1. job_title: 岗位名称（如"OD"、"Python Engineer"等）
2. location: 工作地点（如"伦敦"、"London"、"北京"等）
3. experience_years: 工作年限要求
   - 如果是范围（如"7-15年"），返回 {{"min": 7, "max": 15}}
   - 如果是单个数字（如"5年以上"），返回 {{"min": 5}}
4. background: 背景要求
   - consulting: 是否需要咨询背景（乙方）
   - corporate: 是否需要企业背景（甲方）
   - both: 是否需要甲乙方都有
5. skills: 技能要求列表
6. company_type: 公司类型偏好
7. other_requirements: 其他特殊要求

请直接返回JSON格式，不要添加任何解释：
```json
{{
  "job_title": "...",
  "location": "...",
  "experience_years": {{"min": ..., "max": ...}},
  "background": {{
    "consulting": true/false,
    "corporate": true/false,
    "both": true/false
  }},
  "skills": [...],
  "company_type": "...",
  "other_requirements": "..."
}}
```"""

        response = self._call_llm(prompt, self.flash_model)
        
        # 提取JSON
        try:
            # 尝试从markdown代码块中提取
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response
            
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠ JSON解析失败: {e}")
            print(f"原始响应: {response}")
            return {}
    
    def _enhance_parsed_requirement(self, parsed: Dict) -> Dict:
        """增强解析结果"""
        enhanced = parsed.copy()
        
        # 1. 标准化地点
        if "location" in enhanced and enhanced["location"]:
            enhanced["location_keywords"] = self._standardize_location(enhanced["location"])
        
        # 2. 展开年限范围
        if "experience_years" in enhanced:
            exp = enhanced["experience_years"]
            if isinstance(exp, dict):
                min_years = exp.get("min", 0)
                max_years = exp.get("max", min_years)
                enhanced["experience_years_list"] = list(range(min_years, max_years + 1))
        
        # 3. 展开公司背景
        if "background" in enhanced:
            bg = enhanced["background"]
            enhanced["consulting_companies"] = []
            enhanced["require_corporate_experience"] = False
            
            if bg.get("consulting") or bg.get("both"):
                # 添加咨询公司列表
                for category, companies in self.consulting_firms.items():
                    enhanced["consulting_companies"].extend(companies)
            
            if bg.get("corporate") or bg.get("both"):
                enhanced["require_corporate_experience"] = True
        
        return enhanced
    
    def _standardize_location(self, location: str) -> List[str]:
        """标准化地点名称"""
        location_map = {
            "伦敦": ["London", "伦敦"],
            "london": ["London", "伦敦"],
            "北京": ["Beijing", "北京"],
            "beijing": ["Beijing", "北京"],
            "上海": ["Shanghai", "上海"],
            "shanghai": ["Shanghai", "上海"],
            "深圳": ["Shenzhen", "深圳"],
            "shenzhen": ["Shenzhen", "深圳"],
            "旧金山": ["San Francisco", "旧金山"],
            "san francisco": ["San Francisco", "旧金山"],
            "纽约": ["New York", "纽约"],
            "new york": ["New York", "纽约"]
        }
        
        location_lower = location.lower().strip()
        return location_map.get(location_lower, [location])
    
    def _call_llm(self, prompt: str, model: str) -> str:
        """调用大模型API"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # 降低温度以获得更稳定的输出
            "max_tokens": 1000
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


if __name__ == "__main__":
    # 测试代码
    parser = RequirementParser()
    
    # 测试案例1：复杂需求
    test_requirement = "我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
    
    result = parser.parse_requirement(test_requirement)
    
    print(f"\n{'='*60}")
    print("关键信息提取")
    print(f"{'='*60}")
    print(f"岗位: {result.get('job_title')}")
    print(f"地点: {result.get('location_keywords')}")
    print(f"年限范围: {result.get('experience_years_list')}")
    print(f"咨询公司: {result.get('consulting_companies')}")
    print(f"需要甲方经验: {result.get('require_corporate_experience')}")
