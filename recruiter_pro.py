"""
LinkedIn 招聘系统 - 统一入口
整合所有搜索、筛选和导出功能
"""

import json
from typing import Dict, List, Optional
from linkedin_end_to_end import end_to_end_search, analyze_requirements
from unified_searcher import UnifiedSearcher, quick_search
from requirement_parser import RequirementParser
from candidate_filter import create_filter_from_requirements
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter


class LinkedInRecruiterPro:
    """LinkedIn 招聘系统专业版 - 统一接口"""
    
    def __init__(
        self,
        serper_key: str = "d88085d4543221682eecd92082f27247f71d902f",
        default_engine: str = "serper",
        google_credentials: str = "google_credentials.json"
    ):
        """
        初始化招聘系统
        
        Args:
            serper_key: Serper API Key
            default_engine: 默认搜索引擎 (serper/tavily/gemini)
            google_credentials: Google Sheets 凭证文件路径
        """
        self.searcher = UnifiedSearcher(
            serper_key=serper_key,
            default_engine=default_engine
        )
        self.parser = RequirementParser()
        self.screener = DetailedScreening()
        self.google_exporter = GoogleSheetsExporter(google_credentials)
        self.default_engine = default_engine
    
    def search_simple(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        num_results: int = 100,
        engine: str = None
    ) -> List[Dict]:
        """
        简单搜索 - 直接搜索候选人
        
        Args:
            job_title: 职位名称
            location: 地点
            keywords: 关键词
            company: 公司
            num_results: 结果数量
            engine: 搜索引擎
            
        Returns:
            候选人列表
        """
        print(f"\n{'='*70}")
        print("🔍 简单搜索模式")
        print(f"{'='*70}")
        print(f"职位: {job_title}")
        print(f"地点: {location}")
        print(f"关键词: {keywords}")
        print(f"公司: {company}")
        print(f"引擎: {engine or self.default_engine}")
        
        candidates = self.searcher.search(
            job_title=job_title,
            location=location,
            keywords=keywords,
            company=company,
            num_results=num_results,
            engine=engine
        )
        
        print(f"\n✓ 找到 {len(candidates)} 位候选人")
        return candidates
    
    def search_end_to_end(
        self,
        user_input: str,
        engine: str = None
    ) -> List[Dict]:
        """
        端到端搜索 - AI 分析 + 微切片搜索
        
        Args:
            user_input: 自然语言需求描述
            engine: 搜索引擎 (serper/tavily/gemini/multi)
            
        Returns:
            候选人列表
        """
        engine = engine or self.default_engine
        return end_to_end_search(user_input, engine)
    
    def search_with_filter(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        num_results: int = 100,
        filter_requirements: Dict = None,
        engine: str = None
    ) -> List[Dict]:
        """
        搜索 + 筛选
        
        Args:
            job_title: 职位名称
            location: 地点
            keywords: 关键词
            company: 公司
            num_results: 结果数量
            filter_requirements: 筛选条件
            engine: 搜索引擎
            
        Returns:
            筛选后的候选人列表
        """
        print(f"\n{'='*70}")
        print("🔍 搜索 + 筛选模式")
        print(f"{'='*70}")
        
        # 1. 搜索
        candidates = self.search_simple(
            job_title, location, keywords, company, num_results, engine
        )
        
        if not candidates:
            print("✗ 未找到候选人")
            return []
        
        # 2. 筛选
        if filter_requirements:
            print(f"\n{'='*70}")
            print("📋 应用筛选条件")
            print(f"{'='*70}")
            
            filter_obj = create_filter_from_requirements(filter_requirements)
            filtered = filter_obj.filter_candidates(candidates)
            
            print(f"\n✓ 筛选完成: {len(filtered)}/{len(candidates)} 位候选人通过")
            return filtered
        
        return candidates
    
    def search_multi_engine(
        self,
        job_title: str,
        location: str = "",
        keywords: str = "",
        company: str = "",
        num_results: int = 100
    ) -> List[Dict]:
        """
        多引擎搜索 - 同时使用多个引擎
        
        Returns:
            合并去重后的候选人列表
        """
        print(f"\n{'='*70}")
        print("🔍 多引擎搜索模式")
        print(f"{'='*70}")
        
        candidates = self.searcher.multi_engine_search(
            job_title=job_title,
            location=location,
            keywords=keywords,
            company=company,
            num_results=num_results
        )
        
        print(f"\n✓ 多引擎搜索完成: {len(candidates)} 位候选人")
        return candidates
    
    def analyze_requirement(self, user_input: str) -> Dict:
        """
        分析需求 - 仅执行 AI 分析，不搜索
        
        Args:
            user_input: 自然语言需求描述
            
        Returns:
            分析结果
        """
        return analyze_requirements(user_input)
    
    def export_to_json(
        self,
        candidates: List[Dict],
        filename: str = "candidates.json"
    ):
        """
        导出候选人到 JSON 文件
        
        Args:
            candidates: 候选人列表
            filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "total": len(candidates),
                "candidates": candidates
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 已导出 {len(candidates)} 位候选人到: {filename}")
    
    def export_to_markdown(
        self,
        candidates: List[Dict],
        filename: str = "candidates.md"
    ):
        """
        导出候选人到 Markdown 文件
        
        Args:
            candidates: 候选人列表
            filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# LinkedIn 候选人列表\n\n")
            f.write(f"总计: {len(candidates)} 位候选人\n\n")
            f.write("---\n\n")
            
            for i, candidate in enumerate(candidates, 1):
                f.write(f"## {i}. {candidate.get('name', 'N/A')}\n\n")
                f.write(f"- **职位**: {candidate.get('title', 'N/A')}\n")
                f.write(f"- **公司**: {candidate.get('company', 'N/A')}\n")
                f.write(f"- **地点**: {candidate.get('location', 'N/A')}\n")
                f.write(f"- **LinkedIn**: {candidate.get('url', 'N/A')}\n")
                f.write(f"- **简介**: {candidate.get('snippet', 'N/A')}\n")
                f.write(f"- **来源**: {candidate.get('source', 'N/A')}\n")
                f.write("\n---\n\n")
        
        print(f"\n✓ 已导出 {len(candidates)} 位候选人到: {filename}")


# ==================== 便捷函数 ====================

def quick_end_to_end(
    user_input: str,
    engine: str = "serper",
    export_format: str = None
) -> List[Dict]:
    """
    快速端到端搜索
    
    Args:
        user_input: 自然语言需求
        engine: 搜索引擎
        export_format: 导出格式 (json/markdown)
        
    Returns:
        候选人列表
    """
    recruiter = LinkedInRecruiterPro(default_engine=engine)
    candidates = recruiter.search_end_to_end(user_input, engine)
    
    if export_format == "json":
        recruiter.export_to_json(candidates, "candidates_output.json")
    elif export_format == "markdown":
        recruiter.export_to_markdown(candidates, "candidates_output.md")
    
    return candidates


def quick_multi_engine(
    job_title: str,
    location: str = "",
    export_format: str = None
) -> List[Dict]:
    """
    快速多引擎搜索
    
    Args:
        job_title: 职位名称
        location: 地点
        export_format: 导出格式
        
    Returns:
        候选人列表
    """
    recruiter = LinkedInRecruiterPro()
    candidates = recruiter.search_multi_engine(job_title, location)
    
    if export_format == "json":
        recruiter.export_to_json(candidates, "candidates_output.json")
    elif export_format == "markdown":
        recruiter.export_to_markdown(candidates, "candidates_output.md")
    
    return candidates


# ==================== 主函数 ====================

def main():
    """主函数 - 演示各种使用方式"""
    
    print("\n" + "="*70)
    print("LinkedIn 招聘系统 - 统一入口")
    print("="*70)
    
    # 创建招聘系统实例
    recruiter = LinkedInRecruiterPro(default_engine="serper")
    
    # 选择模式
    print("\n请选择搜索模式:")
    print("1. 简单搜索 - 直接搜索候选人")
    print("2. 端到端搜索 - AI 分析 + 微切片搜索")
    print("3. 搜索 + 筛选 - 搜索后应用筛选条件")
    print("4. 多引擎搜索 - 同时使用多个搜索引擎")
    print("5. 仅分析需求 - 不执行搜索")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == "1":
        # 简单搜索
        candidates = recruiter.search_simple(
            job_title="Product Manager",
            location="Shanghai",
            num_results=50
        )
        recruiter.export_to_markdown(candidates, "simple_search_results.md")
    
    elif choice == "2":
        # 端到端搜索
        user_input = input("\n请输入需求描述: ").strip()
        if not user_input:
            user_input = "我想找 Base 上海的产品经理，5年经验"
        
        candidates = recruiter.search_end_to_end(user_input, engine="serper")
        recruiter.export_to_json(candidates, "end_to_end_results.json")
    
    elif choice == "3":
        # 搜索 + 筛选
        filter_requirements = {
            "required_keywords": ["Product", "Manager"],
            "min_score": 0.6
        }
        
        candidates = recruiter.search_with_filter(
            job_title="Product Manager",
            location="Shanghai",
            num_results=50,
            filter_requirements=filter_requirements
        )
        recruiter.export_to_markdown(candidates, "filtered_results.md")
    
    elif choice == "4":
        # 多引擎搜索
        candidates = recruiter.search_multi_engine(
            job_title="Product Manager",
            location="Shanghai",
            num_results=30
        )
        recruiter.export_to_json(candidates, "multi_engine_results.json")
    
    elif choice == "5":
        # 仅分析需求
        user_input = input("\n请输入需求描述: ").strip()
        if not user_input:
            user_input = "我想找 Base 伦敦的 OD 顾问，7-15年经验，有咨询背景"
        
        analysis = recruiter.analyze_requirement(user_input)
        print("\n分析结果:")
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    else:
        print("无效选择")
    
    print("\n" + "="*70)
    print("完成")
    print("="*70)


if __name__ == "__main__":
    main()
