"""
细筛模块 - Flash + Pro 组合分析候选人匹配度
只分析硬性匹配：职位、年限、背景、地点、技能
"""

import requests
import json
import re
from typing import List, Dict
from llm_config import API_BASE, DEFAULT_KEY


class DetailedScreening:
    """细筛分析器 - Flash快速评分 + Pro深度分析"""
    
    def __init__(self, api_key: str = DEFAULT_KEY):
        self.api_key = api_key
        self.api_base = API_BASE
        self.flash_model = "[福利]gemini-3-flash-preview"
        self.pro_model = "[福利]gemini-3-flash-preview"  # 改为 Flash，更快更稳定
    
    def screen_candidates(
        self,
        candidates: List[Dict],
        requirement: Dict,
        flash_threshold: int = 70,
        max_pro_analysis: int = None,
        use_pro_for_all: bool = False
    ) -> List[Dict]:
        """
        细筛候选人
        
        Args:
            candidates: 候选人列表
            requirement: 岗位要求（解析后的）
            flash_threshold: Flash评分阈值
            max_pro_analysis: Pro分析最大数量
            use_pro_for_all: 是否全部用Pro
            
        Returns:
            带有详细分析的候选人列表
        """
        print(f"\n{'='*60}")
        print("细筛分析")
        print(f"{'='*60}")
        print(f"候选人总数: {len(candidates)}")
        print(f"Flash阈值: {flash_threshold}")
        if max_pro_analysis:
            print(f"Pro分析上限: {max_pro_analysis}")
        
        if use_pro_for_all:
            # 全部用Pro分析
            print("\n使用全Pro模式")
            analyzed = self._pro_analyze_batch(candidates, requirement)
        else:
            # Flash + Pro组合
            print("\n阶段1: Flash快速评分")
            flash_scored = self._flash_score_batch(candidates, requirement)
            
            # 筛选高分候选人
            high_score = [c for c in flash_scored if c.get('flash_score', 0) >= flash_threshold]
            print(f"✓ Flash评分完成，{len(high_score)} 位候选人≥{flash_threshold}分")
            
            if max_pro_analysis and len(high_score) > max_pro_analysis:
                # 按Flash分数排序，取Top N
                high_score.sort(key=lambda x: x.get('flash_score', 0), reverse=True)
                high_score = high_score[:max_pro_analysis]
                print(f"  限制Pro分析数量为 {max_pro_analysis} 位")
            
            print(f"\n阶段2: Pro深度分析 ({len(high_score)} 位)")
            analyzed = self._pro_analyze_batch(high_score, requirement)
        
        # 按最终分数排序
        analyzed.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        print(f"\n{'='*60}")
        print(f"细筛完成")
        print(f"{'='*60}")
        print(f"✓ 分析完成 {len(analyzed)} 位候选人")
        
        return analyzed
    
    def screen_candidates_two_stage(
        self,
        candidates: List[Dict],
        requirement: Dict,
        flash_threshold: int = 50,
        pro_batch_size: int = 10,
        pro_threshold: int = 70
    ) -> List[Dict]:
        """
        两阶段细筛策略
        
        阶段1: Flash 50分一批快速筛选
        阶段2: Pro 10人一批深度分析
        
        Args:
            candidates: 候选人列表
            requirement: 岗位要求（解析后的）
            flash_threshold: Flash评分阈值（默认50分）
            pro_batch_size: Pro分析批次大小（默认10人）
            pro_threshold: Pro最终阈值（默认70分）
            
        Returns:
            通过两阶段筛选的候选人列表
        """
        print(f"\n{'='*60}")
        print("两阶段细筛策略")
        print(f"{'='*60}")
        print(f"候选人总数: {len(candidates)}")
        print(f"阶段1 - Flash阈值: {flash_threshold}分")
        print(f"阶段2 - Pro批次大小: {pro_batch_size}人")
        print(f"阶段2 - Pro最终阈值: {pro_threshold}分")
        
        # 阶段1: Flash快速筛选
        print(f"\n{'='*60}")
        print("阶段1: Flash快速筛选")
        print(f"{'='*60}")
        
        flash_scored = self._flash_score_batch(candidates, requirement)
        
        # 筛选出≥flash_threshold的候选人
        flash_passed = [c for c in flash_scored if c.get('flash_score', 0) >= flash_threshold]
        flash_passed.sort(key=lambda x: x.get('flash_score', 0), reverse=True)
        
        print(f"\n✓ Flash筛选完成")
        print(f"  通过人数: {len(flash_passed)}/{len(candidates)}")
        print(f"  通过率: {len(flash_passed)/len(candidates)*100:.1f}%")
        
        if not flash_passed:
            print("\n⚠ 没有候选人通过Flash筛选")
            return []
        
        # 阶段2: Pro深度分析（分批处理）
        print(f"\n{'='*60}")
        print(f"阶段2: Pro深度分析（{len(flash_passed)}人，每批{pro_batch_size}人）")
        print(f"{'='*60}")
        
        pro_analyzed = []
        total_batches = (len(flash_passed) + pro_batch_size - 1) // pro_batch_size
        
        for batch_idx in range(0, len(flash_passed), pro_batch_size):
            batch = flash_passed[batch_idx:batch_idx + pro_batch_size]
            batch_num = batch_idx // pro_batch_size + 1
            
            print(f"\n批次 {batch_num}/{total_batches} ({len(batch)}人)")
            print("-" * 60)
            
            for i, candidate in enumerate(batch, 1):
                print(f"  [{i}/{len(batch)}] Pro分析: {candidate.get('name', 'Unknown')}")
                
                analysis = self._pro_analyze_single(candidate, requirement)
                candidate.update(analysis)
                pro_analyzed.append(candidate)
        
        # 筛选出≥pro_threshold的候选人
        final_candidates = [c for c in pro_analyzed if c.get('final_score', 0) >= pro_threshold]
        final_candidates.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        print(f"\n{'='*60}")
        print("两阶段筛选完成")
        print(f"{'='*60}")
        print(f"✓ Flash通过: {len(flash_passed)}人")
        print(f"✓ Pro分析: {len(pro_analyzed)}人")
        print(f"✓ 最终通过: {len(final_candidates)}人（≥{pro_threshold}分）")
        
        if final_candidates:
            print(f"\n最终候选人（Top 5）:")
            for i, c in enumerate(final_candidates[:5], 1):
                score = c.get('final_score', 0)
                flash_score = c.get('flash_score', 0)
                print(f"  {i}. {c.get('name', 'Unknown')} - Flash:{flash_score} Pro:{score}")
        
        return final_candidates
    
    def _flash_score_batch(self, candidates: List[Dict], requirement: Dict) -> List[Dict]:
        """Flash批量快速评分"""
        scored = []
        
        for i, candidate in enumerate(candidates, 1):
            print(f"  [{i}/{len(candidates)}] Flash评分: {candidate.get('name', 'Unknown')}")
            
            score = self._flash_score_single(candidate, requirement)
            candidate['flash_score'] = score
            scored.append(candidate)
        
        return scored
    
    def _flash_score_single(self, candidate: Dict, requirement: Dict) -> int:
        """Flash单个候选人快速评分"""
        # 构建岗位要求描述
        requirement_parts = []
        requirement_parts.append(f"- 职位：{requirement.get('job_title')}")
        requirement_parts.append(f"- 地点：{requirement.get('location')}")
        requirement_parts.append(f"- 年限：{requirement.get('experience_years', {})}")
        
        # 背景要求
        background = requirement.get('background', {})
        if background.get('consulting'):
            requirement_parts.append("- 需要咨询公司背景")
        if background.get('corporate'):
            requirement_parts.append("- 需要甲方公司背景")
        
        # 行业/公司类型要求
        company_type = requirement.get('company_type')
        if company_type:
            requirement_parts.append(f"- 行业要求：{company_type}")
        
        # 其他要求
        other_req = requirement.get('other_requirements')
        if other_req:
            requirement_parts.append(f"- 其他要求：{other_req}")
        
        requirement_text = "\n".join(requirement_parts)
        
        prompt = f"""快速评估候选人与岗位的匹配度（0-100分）。

候选人信息：
- 姓名：{candidate.get('name')}
- 当前职位：{candidate.get('current_title') or candidate.get('title')}
- 当前公司：{candidate.get('current_company') or candidate.get('company')}
- 地点：{candidate.get('location')}
- 工作年限：{candidate.get('experience_years')}年
- 简介：{candidate.get('snippet', '')[:300]}

岗位要求：
{requirement_text}

评分重点：
1. 职位匹配度
2. 工作年限是否符合
3. 地点是否匹配
4. 如果有行业要求，重点评估候选人过往公司是否属于该行业
5. 如果需要咨询/甲方背景，评估候选人是否有相关经验

只返回一个0-100的数字，不要解释："""

        try:
            response = self._call_llm(prompt, self.flash_model)
            # 提取数字
            score_match = re.search(r'\d+', response)
            if score_match:
                return int(score_match.group())
        except:
            pass
        
        return 50  # 默认分数
    
    def _pro_analyze_batch(self, candidates: List[Dict], requirement: Dict) -> List[Dict]:
        """Pro批量深度分析"""
        analyzed = []
        
        for i, candidate in enumerate(candidates, 1):
            print(f"  [{i}/{len(candidates)}] Pro分析: {candidate.get('name', 'Unknown')}")
            
            analysis = self._pro_analyze_single(candidate, requirement)
            candidate.update(analysis)
            analyzed.append(candidate)
        
        return analyzed
    
    def _pro_analyze_single(self, candidate: Dict, requirement: Dict) -> Dict:
        """Pro单个候选人深度分析"""
        content = candidate.get('raw_content', '') or candidate.get('snippet', '')
        
        prompt = f"""分析候选人与岗位的硬性匹配度，只分析LinkedIn主页呈现的内容。

候选人LinkedIn信息：
姓名：{candidate.get('name')}
当前职位：{candidate.get('current_title') or candidate.get('title')}
当前公司：{candidate.get('current_company') or candidate.get('company')}
当前地点：{candidate.get('location')}
主页内容：
{content[:2000]}

岗位要求：
- 职位：{requirement.get('job_title')}
- 地点：{requirement.get('location_keywords')} **（必须是当前所在地，不是历史地点）**
- 年限：{requirement.get('experience_years_list')}
- 背景：{'需要咨询公司经验' if requirement.get('background', {}).get('consulting') else ''}{'需要甲方公司经验' if requirement.get('background', {}).get('corporate') else ''}
- 咨询公司列表：{requirement.get('consulting_companies', [])}

**重要：地点匹配规则**
- 只看候选人的"当前地点"（Current Location），不看历史工作地点
- 如果要求"伦敦"，候选人必须当前在伦敦，曾经在伦敦工作过但现在不在伦敦的不算匹配
- 地点匹配必须严格，当前地点不符合要求直接标记为❌

请分析并返回JSON格式（不要markdown代码块）：
{{
  "final_score": 85,
  "职位匹配": {{"当前": "...", "要求": "...", "匹配": "✅/❌", "说明": "..."}},
  "年限匹配": {{"实际": "X年", "要求": "...", "匹配": "✅/❌"}},
  "地点匹配": {{"当前地点": "...", "要求": "...", "匹配": "✅/❌", "说明": "必须是当前所在地"}},
  "背景匹配": {{
    "咨询经验": "公司名 X年",
    "甲方经验": "公司名 X年",
    "匹配": "✅/❌"
  }},
  "工作经历": [
    {{"公司": "...", "职位": "...", "时间": "...", "类型": "甲方/乙方"}}
  ],
  "推荐理由": ["理由1", "理由2"]
}}"""

        try:
            response = self._call_llm(prompt, self.pro_model)
            # 提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
        except Exception as e:
            print(f"    ⚠ Pro分析失败: {e}")
        
        return {"final_score": 50, "推荐理由": ["分析失败"]}
    
    def _call_llm(self, prompt: str, model: str, max_retries: int = 3) -> str:
        """调用LLM API（带重试机制）"""
        url = f"{self.api_base}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60  # 增加到60秒
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"    ⚠ 超时，重试 {attempt + 1}/{max_retries - 1}...")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    ⚠ 错误: {e}，重试 {attempt + 1}/{max_retries - 1}...")
                    time.sleep(2)
                else:
                    raise


if __name__ == "__main__":
    # 测试代码
    screening = DetailedScreening()
    
    # 测试数据
    test_candidates = [
        {
            "name": "张三",
            "current_title": "Senior OD Manager",
            "current_company": "Google",
            "location": "London",
            "experience_years": 10,
            "snippet": "10年OD经验，McKinsey 3年，Google 5年"
        }
    ]
    
    test_requirement = {
        "job_title": "OD",
        "location": "London",
        "location_keywords": ["London"],
        "experience_years": {"min": 7, "max": 15},
        "experience_years_list": [7,8,9,10,11,12,13,14,15],
        "background": {"consulting": True, "corporate": True},
        "consulting_companies": ["McKinsey", "BCG", "Bain"]
    }
    
    results = screening.screen_candidates(
        test_candidates,
        test_requirement,
        flash_threshold=70,
        use_pro_for_all=True
    )
    
    print("\n分析结果:")
    for r in results:
        print(f"- {r['name']}: {r.get('final_score', 0)}分")
