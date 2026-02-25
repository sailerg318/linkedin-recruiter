"""
流式处理模块 - 搜索、筛选、导出流水线
边搜索边筛选边导出，提升效率
"""

import time
from typing import Dict, List, Generator
from unified_searcher import UnifiedSearcher
from detailed_screening import DetailedScreening
from google_sheets_exporter import GoogleSheetsExporter
from requirement_parser import RequirementParser


class StreamingPipeline:
    """流式处理流水线"""
    
    def __init__(
        self,
        serper_key: str = "d88085d4543221682eecd92082f27247f71d902f",
        google_credentials: str = "oauth_credentials.json",
        default_engine: str = "serper"
    ):
        """
        初始化流式处理流水线
        
        Args:
            serper_key: Serper API Key
            google_credentials: OAuth 凭证文件（默认 oauth_credentials.json）
            default_engine: 默认搜索引擎
        """
        self.searcher = UnifiedSearcher(
            serper_key=serper_key,
            default_engine=default_engine
        )
        self.screener = DetailedScreening()
        
        # 尝试初始化 Google Sheets，如果失败则禁用导出功能
        try:
            import os
            if os.path.exists(google_credentials):
                self.google_exporter = GoogleSheetsExporter(google_credentials)
                self.sheets_enabled = True
            else:
                print(f"⚠️  未找到 {google_credentials}，Google Sheets 导出功能已禁用")
                self.google_exporter = None
                self.sheets_enabled = False
        except Exception as e:
            print(f"⚠️  Google Sheets 初始化失败: {e}")
            self.google_exporter = None
            self.sheets_enabled = False
        
        self.parser = RequirementParser()
        
        self.spreadsheet = None
        self.worksheet = None
        self.current_row = 7  # 从第7行开始写入数据（前6行是表头）
    
    def streaming_search_screen_export(
        self,
        user_input: str,
        search_batch_size: int = 50,
        screen_batch_size: int = 10,
        flash_threshold: int = 50,
        pro_threshold: int = 70,
        engine: str = None,
        share_emails: List[str] = None
    ) -> Dict:
        """
        流式处理：搜索 → 筛选 → 导出
        
        流程：
        1. 搜索一批候选人（如50人）
        2. Flash 粗筛这批候选人
        3. Pro 精筛通过的候选人（如10人一批）
        4. 实时写入 Google Sheets
        5. 继续下一批搜索
        
        Args:
            user_input: 用户需求
            search_batch_size: 搜索批次大小
            screen_batch_size: 筛选批次大小
            flash_threshold: Flash 阈值
            pro_threshold: Pro 阈值
            engine: 搜索引擎
            share_emails: 分享邮箱
            
        Returns:
            统计信息
        """
        print(f"\n{'#'*70}")
        print("🚀 流式处理流水线")
        print(f"{'#'*70}")
        print(f"搜索批次: {search_batch_size} 人")
        print(f"筛选批次: {screen_batch_size} 人")
        print(f"Flash 阈值: {flash_threshold}")
        print(f"Pro 阈值: {pro_threshold}")
        
        # 1. 解析需求
        print(f"\n{'='*70}")
        print("步骤 1: 解析需求")
        print(f"{'='*70}")
        requirement = self.parser.parse_requirement(user_input)
        
        # 2. 初始化 Google Sheets（如果启用）
        sheet_url = None
        if self.sheets_enabled:
            print(f"\n{'='*70}")
            print("步骤 2: 初始化 Google Sheets")
            print(f"{'='*70}")
            
            sheet_url = self._init_google_sheet(
                requirement_text=user_input,
                job_title=requirement.get('job_title', ''),
                share_emails=share_emails
            )
            
            if not sheet_url:
                print("⚠️  Google Sheets 初始化失败，将继续处理但不导出")
                self.sheets_enabled = False
        else:
            print(f"\n{'='*70}")
            print("步骤 2: Google Sheets 导出已禁用")
            print(f"{'='*70}")
            print("⚠️  未配置 Google Sheets OAuth，结果将仅显示在日志中")
        
        # 3. 流式处理
        print(f"\n{'='*70}")
        print("步骤 3: 流式处理（搜索 → 筛选 → 导出）")
        print(f"{'='*70}")
        
        stats = {
            "total_searched": 0,
            "flash_passed": 0,
            "pro_passed": 0,
            "exported": 0,
            "url": sheet_url
        }
        
        # 生成搜索批次
        for batch_num, search_batch in enumerate(
            self._generate_search_batches(
                user_input, 
                requirement, 
                search_batch_size,
                engine
            ), 
            1
        ):
            print(f"\n{'─'*70}")
            print(f"批次 {batch_num}: 搜索到 {len(search_batch)} 位候选人")
            print(f"{'─'*70}")
            
            stats["total_searched"] += len(search_batch)
            
            # Flash 粗筛
            print(f"\n  Flash 粗筛中...")
            flash_passed = []
            for candidate in search_batch:
                score = self.screener._flash_score_single(candidate, requirement)
                candidate['flash_score'] = score
                
                if score >= flash_threshold:
                    flash_passed.append(candidate)
            
            print(f"  ✓ Flash 通过: {len(flash_passed)}/{len(search_batch)} 位")
            stats["flash_passed"] += len(flash_passed)
            
            if not flash_passed:
                print(f"  ⚠ 本批次无候选人通过 Flash 筛选")
                continue
            
            # Pro 精筛（分小批次）
            print(f"\n  Pro 精筛中（{len(flash_passed)} 位，每批 {screen_batch_size} 位）...")
            
            for i in range(0, len(flash_passed), screen_batch_size):
                screen_batch = flash_passed[i:i + screen_batch_size]
                
                pro_passed = []
                for candidate in screen_batch:
                    analysis = self.screener._pro_analyze_single(candidate, requirement)
                    candidate.update(analysis)
                    
                    if candidate.get('final_score', 0) >= pro_threshold:
                        pro_passed.append(candidate)
                
                if pro_passed:
                    print(f"    ✓ Pro 通过: {len(pro_passed)} 位")
                    stats["pro_passed"] += len(pro_passed)
                    
                    # 实时写入 Google Sheets（如果启用）
                    if self.sheets_enabled and self.worksheet:
                        self._append_to_sheet(pro_passed)
                        stats["exported"] += len(pro_passed)
                        print(f"    ✓ 已写入 Google Sheets: {len(pro_passed)} 位")
                    else:
                        # 在日志中显示候选人信息
                        for candidate in pro_passed:
                            print(f"      - {candidate.get('name', 'Unknown')} | {candidate.get('title', '')} @ {candidate.get('company', '')} | 分数: {candidate.get('final_score', 0)}")
            
            # 显示累计统计
            print(f"\n  累计统计:")
            print(f"    搜索: {stats['total_searched']} 位")
            print(f"    Flash 通过: {stats['flash_passed']} 位")
            print(f"    Pro 通过: {stats['pro_passed']} 位")
            print(f"    已导出: {stats['exported']} 位")
        
        print(f"\n{'#'*70}")
        print("✅ 流式处理完成")
        print(f"{'#'*70}")
        print(f"最终统计:")
        print(f"  搜索: {stats['total_searched']} 位")
        if stats['total_searched'] > 0:
            print(f"  Flash 通过: {stats['flash_passed']} 位 ({stats['flash_passed']/stats['total_searched']*100:.1f}%)")
        else:
            print(f"  Flash 通过: {stats['flash_passed']} 位")
        
        if stats['flash_passed'] > 0:
            print(f"  Pro 通过: {stats['pro_passed']} 位 ({stats['pro_passed']/stats['flash_passed']*100:.1f}% of Flash)")
        else:
            print(f"  Pro 通过: {stats['pro_passed']} 位")
        
        if self.sheets_enabled and stats['url']:
            print(f"  已导出: {stats['exported']} 位")
            print(f"  Google Sheets: {stats['url']}")
        else:
            print(f"  ⚠️  Google Sheets 导出未启用")
        
        return stats
    
    def _generate_search_batches(
        self,
        user_input: str,
        requirement: Dict,
        batch_size: int,
        engine: str
    ) -> Generator[List[Dict], None, None]:
        """
        生成搜索批次
        
        策略：
        1. 先搜索目标公司（每家公司一批）
        2. 再搜索字母切片（每个字母一批）
        
        Yields:
            候选人批次
        """
        from linkedin_end_to_end import analyze_requirements
        
        # 获取 AI 分析结果
        analysis = analyze_requirements(user_input)
        
        base_keyword = analysis["base_keyword"]
        location = analysis["location"]
        target_companies = analysis["target_companies"]
        
        seen_urls = set()
        
        # 阶段 1: 公司切片
        print(f"\n  阶段 1: 公司切片搜索")
        for i, company in enumerate(target_companies, 1):
            print(f"    [{i}/{len(target_companies)}] 搜索公司: {company}")
            
            candidates = self.searcher.search(
                job_title=base_keyword,
                location=location,
                company=company,
                num_results=100,
                engine=engine
            )
            
            # 去重
            batch = []
            for candidate in candidates:
                url = candidate.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    batch.append(candidate)
            
            if batch:
                yield batch
            
            time.sleep(0.5)  # 避免请求过快
        
        # 阶段 2: 字母切片（仅 Serper 支持）
        if engine == "serper" or engine is None:
            print(f"\n  阶段 2: 字母切片搜索")
            import string
            for i, char in enumerate(string.ascii_lowercase, 1):
                print(f"    [{i}/26] 搜索字母: {char}")
                
                query = f'site:linkedin.com/in/ "{base_keyword}" "{location}" intitle:{char} -intitle:jobs'
                candidates = self.searcher.search(
                    query=query,
                    num_results=100,
                    engine="serper"
                )
                
                # 去重
                batch = []
                for candidate in candidates:
                    url = candidate.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        batch.append(candidate)
                
                if batch:
                    yield batch
                
                time.sleep(0.5)
    
    def _init_google_sheet(
        self,
        requirement_text: str,
        job_title: str,
        share_emails: List[str]
    ) -> str:
        """初始化 Google Sheets"""
        if not self.google_exporter.client:
            if not self.google_exporter.connect():
                return None
        
        from datetime import datetime
        
        # 创建表格
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"{job_title}_流式处理_{timestamp}" if job_title else f"流式处理_{timestamp}"
        
        try:
            self.spreadsheet = self.google_exporter.client.create(sheet_name)
            self.worksheet = self.spreadsheet.get_worksheet(0)
            
            # 设置表头
            self.google_exporter._setup_header(
                self.worksheet,
                requirement_text,
                0  # 候选人数量暂时为0
            )
            
            # 分享
            if share_emails:
                for email in share_emails:
                    self.spreadsheet.share(email, perm_type='user', role='writer')
                    print(f"  ✓ 已分享给: {email}")
            
            url = self.spreadsheet.url
            print(f"  ✓ Google Sheets 创建成功")
            print(f"  链接: {url}")
            
            return url
            
        except Exception as e:
            print(f"  ✗ 创建失败: {e}")
            import traceback
            print(f"\n详细错误:\n{traceback.format_exc()}")
            return None
    
    def _append_to_sheet(self, candidates: List[Dict]):
        """追加候选人到 Google Sheets"""
        if not self.worksheet:
            return
        
        for candidate in candidates:
            row_data = [
                self.current_row - 6,  # 排名（从1开始）
                candidate.get('name', ''),
                candidate.get('final_score', 0),
                self._get_match_status(candidate, '职位匹配'),
                self._get_match_status(candidate, '年限匹配'),
                self._get_match_status(candidate, '背景匹配'),
                self._get_match_status(candidate, '地点匹配'),
                candidate.get('current_title') or candidate.get('title', ''),
                candidate.get('current_company') or candidate.get('company', ''),
                f"{candidate.get('experience_years', '')}年" if candidate.get('experience_years') else '',
                self._get_background_info(candidate, 'consulting'),
                self._get_background_info(candidate, 'corporate'),
                candidate.get('url', ''),
                self._format_reasons(candidate.get('推荐理由', [])),
                ''  # 客户备注栏
            ]
            
            try:
                self.worksheet.update(f'A{self.current_row}:O{self.current_row}', [row_data])
                self.current_row += 1
            except Exception as e:
                print(f"    ⚠ 写入失败: {e}")
    
    def _get_match_status(self, candidate: Dict, field: str) -> str:
        """获取匹配状态"""
        match_info = candidate.get(field, {})
        if isinstance(match_info, dict):
            return match_info.get('匹配', '❓')
        return '❓'
    
    def _get_background_info(self, candidate: Dict, bg_type: str) -> str:
        """获取背景信息"""
        bg_match = candidate.get('背景匹配', {})
        if isinstance(bg_match, dict):
            if bg_type == 'consulting':
                return bg_match.get('咨询经验', '')
            elif bg_type == 'corporate':
                return bg_match.get('甲方经验', '')
        return ''
    
    def _format_reasons(self, reasons: List[str]) -> str:
        """格式化推荐理由"""
        if not reasons:
            return ''
        return '\\n'.join(f"• {r}" for r in reasons)


# 便捷函数
def quick_streaming_pipeline(
    user_input: str,
    search_batch_size: int = 50,
    screen_batch_size: int = 10,
    flash_threshold: int = 50,
    pro_threshold: int = 70,
    engine: str = "serper",
    share_emails: List[str] = None
) -> Dict:
    """
    快速流式处理
    
    Args:
        user_input: 用户需求
        search_batch_size: 搜索批次大小
        screen_batch_size: 筛选批次大小
        flash_threshold: Flash 阈值
        pro_threshold: Pro 阈值
        engine: 搜索引擎
        share_emails: 分享邮箱
        
    Returns:
        统计信息
    """
    pipeline = StreamingPipeline(default_engine=engine)
    
    return pipeline.streaming_search_screen_export(
        user_input=user_input,
        search_batch_size=search_batch_size,
        screen_batch_size=screen_batch_size,
        flash_threshold=flash_threshold,
        pro_threshold=pro_threshold,
        engine=engine,
        share_emails=share_emails
    )


if __name__ == "__main__":
    # 测试流式处理
    print("="*70)
    print("测试流式处理流水线")
    print("="*70)
    
    # 示例：流式处理
    result = quick_streaming_pipeline(
        user_input="我想找 Base 上海的产品经理，5年经验，有大厂背景",
        search_batch_size=50,
        screen_batch_size=10,
        flash_threshold=50,
        pro_threshold=70,
        engine="serper",
        share_emails=None  # ["client@example.com"]
    )
    
    print(f"\n最终结果:")
    print(f"  搜索: {result['total_searched']} 位")
    print(f"  Flash 通过: {result['flash_passed']} 位")
    print(f"  Pro 通过: {result['pro_passed']} 位")
    print(f"  已导出: {result['exported']} 位")
    if result.get('url'):
        print(f"  Google Sheets: {result['url']}")
