"""
LinkedIn 端到端候选人挖掘系统
融合 AI 智能分析 + 统一搜索器（支持 Serper/Tavily/Gemini）
"""

import requests
import json
import time
import string
from typing import List, Dict, Any
from llm_config import API_BASE, DEFAULT_KEY
from unified_searcher import UnifiedSearcher

# ==================== 配置区 ====================
SERPER_API_KEY = "d88085d4543221682eecd92082f27247f71d902f"
LLM_API_KEY = DEFAULT_KEY
LLM_API_BASE = API_BASE
LLM_MODEL = "[福利]gemini-3-flash-preview"
DEFAULT_SEARCH_ENGINE = "serper"  # 默认搜索引擎: serper/tavily/gemini

# ==================== Module A: AI 需求分析 ====================

def analyze_requirements(user_input: str) -> Dict[str, Any]:
    """
    Module A: AI Brain - 智能分析用户需求
    
    Args:
        user_input: 用户的原始职位描述（JD）
        
    Returns:
        结构化的分析结果:
        {
            "base_keyword": "核心职位词",
            "location": "目标城市",
            "target_companies": ["公司1", "公司2", ...]  # 30家
        }
    """
    print(f"\n{'='*70}")
    print("🧠 Module A: AI 需求分析")
    print(f"{'='*70}")
    print(f"原始需求: {user_input}\n")
    
    # 构建 Prompt
    prompt = f"""你是一个专业的猎头助手。请分析用户输入的职位需求，返回以下 JSON 格式数据：

用户需求：{user_input}

请提取以下信息：
1. base_keyword: 最核心的职位词（英文，如 'Org Development' 或 'Algorithmic Trader'）
2. location: 目标城市/地区（英文，如 'London', 'Shanghai', 'New York'）
3. target_companies: 根据职位和背景要求，列出该地区最知名的 30 家相关公司英文名（List）

**重要：公司列表生成规则**
- 分析用户的背景要求（咨询背景/甲方背景/两者都要）
- **如果要求"甲乙方都要"或"咨询+甲方"**：只生成**乙方公司**（咨询公司）列表
  * 例如：McKinsey, BCG, Bain, Deloitte, PwC, EY, KPMG, Accenture, Oliver Wyman 等
  * 原因：搜索乙方公司的人，筛选时判断是否有甲方经验
- **如果只要求咨询背景**：生成咨询公司列表
- **如果只要求甲方背景**：生成甲方公司列表（如 Google, Amazon, Alibaba 等）
- **如果没有背景要求**：根据职位生成相关行业公司
- 公司名称必须是英文，且是在该地区有业务的公司

请直接返回 JSON 格式，不要添加任何解释：
```json
{{
  "base_keyword": "...",
  "location": "...",
  "target_companies": ["公司1", "公司2", ..., "公司30"]
}}
```"""

    try:
        # 调用 LLM
        response = _call_llm(prompt)
        
        # 解析 JSON
        result = _extract_json(response)
        
        if not result:
            raise ValueError("LLM 返回的 JSON 解析失败")
        
        # 验证必需字段
        required_fields = ["base_keyword", "location", "target_companies"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"缺少必需字段: {field}")
        
        print("✓ AI 分析完成")
        print(f"  核心关键词: {result['base_keyword']}")
        print(f"  目标地点: {result['location']}")
        print(f"  目标公司数: {len(result['target_companies'])}")
        print(f"  公司列表: {', '.join(result['target_companies'][:5])}...")
        
        return result
        
    except Exception as e:
        print(f"✗ AI 分析失败: {e}")
        # 返回默认值
        return {
            "base_keyword": "Product Manager",
            "location": "Shanghai",
            "target_companies": ["Alibaba", "Tencent", "ByteDance"]
        }


def _call_llm(prompt: str) -> str:
    """调用 LLM API"""
    url = f"{LLM_API_BASE}/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
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


def _extract_json(text: str) -> Dict:
    """从文本中提取 JSON"""
    import re
    
    # 尝试从 markdown 代码块中提取
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 尝试直接解析
        json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 尝试查找 JSON 对象
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return {}


# ==================== Module B: Serper 微切片搜索 ====================

def micro_slicing_search(
    analysis_result: Dict[str, Any],
    search_engine: str = DEFAULT_SEARCH_ENGINE
) -> List[Dict]:
    """
    Module B: 微切片大规模搜索（支持多种搜索引擎）
    
    Args:
        analysis_result: Module A 的输出
        search_engine: 搜索引擎 (serper/tavily/gemini)
        
    Returns:
        去重后的候选人列表
    """
    print(f"\n{'='*70}")
    print(f"🔍 Module B: 微切片搜索 (引擎: {search_engine.upper()})")
    print(f"{'='*70}")
    
    base_keyword = analysis_result["base_keyword"]
    location = analysis_result["location"]
    target_companies = analysis_result["target_companies"]
    
    # 初始化统一搜索器
    searcher = UnifiedSearcher(
        serper_key=SERPER_API_KEY,
        llm_key=LLM_API_KEY,
        default_engine=search_engine
    )
    
    all_candidates = []
    seen_urls = set()  # 用于去重
    
    # 1. 公司切片搜索
    print(f"\n📊 阶段 1: 公司切片搜索 (共 {len(target_companies)} 家公司)")
    for i, company in enumerate(target_companies, 1):
        print(f"  [{i}/{len(target_companies)}] 搜索: {company}")
        
        try:
            candidates = searcher.search(
                job_title=base_keyword,
                location=location,
                company=company,
                num_results=100
            )
            
            # 去重
            new_count = 0
            for candidate in candidates:
                url = candidate.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_candidates.append(candidate)
                    new_count += 1
            
            print(f"    ✓ 新增 {new_count} 位候选人 (总计: {len(all_candidates)})")
        except Exception as e:
            print(f"    ✗ 搜索失败: {e}")
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 2. 字母切片搜索（长尾补充，仅 Serper 支持）
    if search_engine == "serper":
        print(f"\n📊 阶段 2: 字母切片搜索 (a-z)")
        alphabet = string.ascii_lowercase
        for i, char in enumerate(alphabet, 1):
            query = f'site:linkedin.com/in/ "{base_keyword}" "{location}" intitle:{char} -intitle:jobs'
            print(f"  [{i}/{len(alphabet)}] 搜索: 字母 '{char}'")
            
            try:
                candidates = searcher.search(query=query, num_results=100)
                
                # 去重
                new_count = 0
                for candidate in candidates:
                    url = candidate.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_candidates.append(candidate)
                        new_count += 1
                
                print(f"    ✓ 新增 {new_count} 位候选人 (总计: {len(all_candidates)})")
            except Exception as e:
                print(f"    ✗ 搜索失败: {e}")
            
            # 避免请求过快
            time.sleep(0.5)
    
    print(f"\n{'='*70}")
    print(f"✓ 搜索完成！共找到 {len(all_candidates)} 位去重后的候选人")
    print(f"{'='*70}")
    
    return all_candidates


# ==================== 端到端主函数 ====================

def end_to_end_search(user_input: str) -> List[Dict]:
    """
    端到端 LinkedIn 候选人挖掘
    
    Args:
        user_input: 用户的原始职位描述
        
    Returns:
        候选人列表
    """
    print(f"\n{'#'*70}")
    print("🚀 LinkedIn 端到端候选人挖掘系统")
    print(f"{'#'*70}")
    
    # Module A: AI 分析
    analysis_result = analyze_requirements(user_input)
    
    # Module B: Serper 搜索
    candidates = serper_micro_slicing(analysis_result)
    
    print(f"\n{'#'*70}")
    print(f"✅ 挖掘完成！共找到 {len(candidates)} 位候选人")
    print(f"{'#'*70}\n")
    
    return candidates


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 测试案例 1: 组织发展顾问
    test_input_1 = "我想找 Base 伦敦的 Org Development 顾问，7-15年经验，有咨询背景的"
    
    # 测试案例 2: 算法交易员
    test_input_2 = "寻找纽约的算法交易员，5年以上经验，来自顶级投行或对冲基金"
    
    # 测试案例 3: 电商运营
    test_input_3 = "上海的电商运营专家，3-8年经验，有大厂背景"
    
    # 选择测试案例
    test_input = test_input_1
    
    print(f"测试输入: {test_input}\n")
    
    # 执行端到端搜索
    candidates = end_to_end_search(test_input)
    
    # 显示前 10 位候选人
    if candidates:
        print("\n" + "="*70)
        print("前 10 位候选人:")
        print("="*70)
        for i, candidate in enumerate(candidates[:10], 1):
            print(f"\n{i}. {candidate['name']}")
            print(f"   职位: {candidate['title']}")
            print(f"   URL: {candidate['url']}")
            print(f"   简介: {candidate['snippet'][:100]}...")
