"""
候选人Markdown导出模块 - 生成交互式审阅文件
"""

from typing import List, Dict
from datetime import datetime
import os


class CandidateMarkdownExporter:
    """候选人Markdown导出器"""
    
    def __init__(self, output_dir: str = "candidates_review"):
        self.output_dir = output_dir
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def export_candidates(
        self,
        candidates: List[Dict],
        requirement_text: str = "",
        job_title: str = "",
        filename: str = None
    ) -> str:
        """
        导出候选人到交互式Markdown文件
        
        Args:
            candidates: 候选人列表
            requirement_text: 原始需求描述
            job_title: 岗位名称（用于生成文件名）
            filename: 输出文件名（可选）
            
        Returns:
            生成的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 使用岗位名称作为文件名
            if job_title:
                # 清理岗位名称，移除特殊字符
                safe_job_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_job_title = safe_job_title.replace(' ', '_')
                filename = f"{safe_job_title}_{timestamp}.md"
            else:
                filename = f"candidates_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 生成Markdown内容
        content = self._generate_markdown(candidates, requirement_text)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✓ 候选人已导出到: {filepath}")
        print(f"  总计: {len(candidates)} 位候选人")
        
        return filepath
    
    def _generate_markdown(
        self, 
        candidates: List[Dict],
        requirement_text: str
    ) -> str:
        """生成Markdown内容"""
        lines = []
        
        # 标题和元信息
        lines.append("# 候选人审阅清单")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**候选人数量**: {len(candidates)}")
        if requirement_text:
            lines.append(f"**原始需求**: {requirement_text}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 使用说明
        lines.append("## 📋 使用说明")
        lines.append("")
        lines.append("- [ ] 未审阅")
        lines.append("- [x] 通过")
        lines.append("- [~] 待定")
        lines.append("- [-] 拒绝")
        lines.append("")
        lines.append("**操作方式**：")
        lines.append("1. 在每个候选人前的复选框中标记状态")
        lines.append("2. 在备注栏添加评论")
        lines.append("3. 保存文件后可以用脚本统计结果")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 统计信息
        lines.append("## 📊 统计信息")
        lines.append("")
        
        # 按背景分类
        consulting_count = sum(1 for c in candidates if c.get('has_consulting_background'))
        corporate_count = sum(1 for c in candidates if c.get('has_corporate_background'))
        both_count = sum(1 for c in candidates if c.get('has_consulting_background') and c.get('has_corporate_background'))
        
        lines.append(f"- 咨询背景: {consulting_count} 位")
        lines.append(f"- 甲方背景: {corporate_count} 位")
        lines.append(f"- 甲乙方兼有: {both_count} 位")
        lines.append("")
        
        # 按相关度分类
        high_score = sum(1 for c in candidates if c.get('score', 0) >= 0.8)
        medium_score = sum(1 for c in candidates if 0.5 <= c.get('score', 0) < 0.8)
        low_score = sum(1 for c in candidates if c.get('score', 0) < 0.5)
        
        lines.append(f"- 高相关度(≥0.8): {high_score} 位")
        lines.append(f"- 中相关度(0.5-0.8): {medium_score} 位")
        lines.append(f"- 低相关度(<0.5): {low_score} 位")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 候选人列表
        lines.append("## 👥 候选人列表")
        lines.append("")
        
        # 按相关度分数排序
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        for i, candidate in enumerate(sorted_candidates, 1):
            lines.extend(self._format_candidate(i, candidate))
            lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("")
        lines.append("## 📝 审阅记录")
        lines.append("")
        lines.append("| 审阅人 | 日期 | 通过数 | 拒绝数 | 备注 |")
        lines.append("|--------|------|--------|--------|------|")
        lines.append("| | | | | |")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_candidate(self, index: int, candidate: Dict) -> List[str]:
        """格式化单个候选人信息"""
        lines = []
        
        # 候选人标题（带复选框）
        name = candidate.get('name', 'Unknown')
        score = candidate.get('score', 0)
        
        # 根据分数添加标签
        score_label = ""
        if score >= 0.8:
            score_label = "🔥 高匹配"
        elif score >= 0.5:
            score_label = "⭐ 中匹配"
        else:
            score_label = "💡 低匹配"
        
        lines.append(f"### - [ ] {index}. {name} {score_label}")
        lines.append("")
        
        # 基本信息卡片
        lines.append("**基本信息**")
        lines.append("")
        lines.append(f"- **LinkedIn**: [{candidate.get('url', 'N/A')}]({candidate.get('url', '#')})")
        lines.append(f"- **当前职位**: {candidate.get('current_title') or candidate.get('title', 'N/A')}")
        lines.append(f"- **当前公司**: {candidate.get('current_company') or candidate.get('company', 'N/A')}")
        lines.append(f"- **地点**: {candidate.get('location', 'N/A')}")
        lines.append(f"- **工作年限**: {candidate.get('experience_years', 'N/A')} 年")
        lines.append(f"- **相关度分数**: {score:.2f}")
        lines.append("")
        
        # 背景标签
        tags = []
        if candidate.get('has_consulting_background'):
            tags.append("🏢 咨询背景")
        if candidate.get('has_corporate_background'):
            tags.append("🏭 甲方背景")
        if candidate.get('has_consulting_background') and candidate.get('has_corporate_background'):
            tags.append("⭐ 甲乙方兼有")
        
        if tags:
            lines.append(f"**标签**: {' | '.join(tags)}")
            lines.append("")
        
        # 工作经历
        companies = candidate.get('companies', [])
        if companies:
            lines.append("**工作过的公司**:")
            lines.append("")
            for company in companies[:5]:  # 最多显示5个
                lines.append(f"- {company}")
            lines.append("")
        
        # 关键技能
        skills = candidate.get('key_skills', [])
        if skills:
            lines.append(f"**关键技能**: {', '.join(skills[:10])}")
            lines.append("")
        
        # 简介
        snippet = candidate.get('snippet', '')
        if snippet:
            lines.append("**简介**:")
            lines.append("")
            lines.append(f"> {snippet[:300]}...")
            lines.append("")
        
        # 审阅区域
        lines.append("<details>")
        lines.append("<summary>📝 审阅备注（点击展开）</summary>")
        lines.append("")
        lines.append("**优点**:")
        lines.append("- ")
        lines.append("")
        lines.append("**疑虑**:")
        lines.append("- ")
        lines.append("")
        lines.append("**决策**:")
        lines.append("- [ ] 推荐面试")
        lines.append("- [ ] 需要更多信息")
        lines.append("- [ ] 不合适")
        lines.append("")
        lines.append("**备注**:")
        lines.append("")
        lines.append("")
        lines.append("</details>")
        lines.append("")
        lines.append("---")
        
        return lines
    
    def parse_review_results(self, filepath: str) -> Dict:
        """
        解析审阅结果
        
        Args:
            filepath: Markdown文件路径
            
        Returns:
            审阅统计结果
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 统计不同状态的候选人
        import re
        
        passed = len(re.findall(r'###\s*-\s*\[x\]', content, re.IGNORECASE))
        pending = len(re.findall(r'###\s*-\s*\[~\]', content, re.IGNORECASE))
        rejected = len(re.findall(r'###\s*-\s*\[-\]', content, re.IGNORECASE))
        unreviewed = len(re.findall(r'###\s*-\s*\[\s\]', content, re.IGNORECASE))
        
        total = passed + pending + rejected + unreviewed
        
        results = {
            "total": total,
            "passed": passed,
            "pending": pending,
            "rejected": rejected,
            "unreviewed": unreviewed,
            "reviewed_percentage": ((total - unreviewed) / total * 100) if total > 0 else 0
        }
        
        return results


if __name__ == "__main__":
    # 测试代码
    exporter = CandidateMarkdownExporter()
    
    # 测试数据
    test_candidates = [
        {
            "name": "张三",
            "url": "https://linkedin.com/in/zhangsan",
            "current_title": "Senior OD Manager",
            "current_company": "Google",
            "location": "London, UK",
            "experience_years": 10,
            "score": 0.95,
            "has_consulting_background": True,
            "has_corporate_background": True,
            "companies": ["Google", "McKinsey", "Alibaba"],
            "key_skills": ["Organizational Development", "Change Management", "Leadership"],
            "snippet": "10年组织发展经验，曾在McKinsey担任顾问，现任Google OD Manager..."
        },
        {
            "name": "李四",
            "url": "https://linkedin.com/in/lisi",
            "current_title": "OD Specialist",
            "current_company": "Microsoft",
            "location": "London, UK",
            "experience_years": 7,
            "score": 0.82,
            "has_consulting_background": False,
            "has_corporate_background": True,
            "companies": ["Microsoft", "Amazon"],
            "key_skills": ["HR", "Training", "Development"],
            "snippet": "7年人力资源和组织发展经验..."
        }
    ]
    
    # 导出
    filepath = exporter.export_candidates(
        test_candidates,
        requirement_text="我想要Base伦敦的OD，7-15年经验，甲乙方背景的"
    )
    
    print(f"\n生成的文件: {filepath}")
    print("\n可以在VSCode或任何Markdown编辑器中打开并审阅")
