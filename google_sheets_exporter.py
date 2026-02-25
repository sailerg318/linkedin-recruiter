"""
Google Sheets导出模块 - OAuth 版本
使用用户自己的 Google 账号，不受服务账号存储限制
"""

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from typing import List, Dict
from datetime import datetime


class GoogleSheetsExporter:
    """Google Sheets导出器 - OAuth版本"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_file: str = "oauth_credentials.json"):
        """
        初始化 OAuth 客户端
        
        Args:
            credentials_file: OAuth 客户端凭证文件（从 Google Cloud Console 下载）
        """
        self.credentials_file = credentials_file
        self.token_file = "token.pickle"
        self.client = None
    
    def authenticate(self):
        """OAuth 认证流程"""
        creds = None
        
        # 检查是否有已保存的 token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果没有有效凭证，进行认证
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("刷新访问令牌...")
                creds.refresh(Request())
            else:
                print("\n开始 OAuth 认证流程...")
                print("浏览器将打开，请登录您的 Google 账号并授权")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 保存凭证供下次使用
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            print("✓ 认证成功，凭证已保存")
        
        return creds
    
    def connect(self):
        """连接到 Google Sheets"""
        try:
            creds = self.authenticate()
            self.client = gspread.authorize(creds)
            print("✓ Google Sheets 连接成功")
            return True
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            return False
    
    def export_candidates(
        self,
        candidates: List[Dict],
        requirement_text: str = "",
        job_title: str = "",
        share_emails: List[str] = None
    ) -> str:
        """
        导出候选人到 Google Sheets
        
        Args:
            candidates: 候选人列表
            requirement_text: 原始需求描述
            job_title: 岗位名称
            share_emails: 要分享给的邮箱列表
            
        Returns:
            Google Sheets URL
        """
        if not self.client:
            if not self.connect():
                return None
        
        # 创建表格名称
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"{job_title}_候选人推荐_{timestamp}" if job_title else f"候选人推荐_{timestamp}"
        
        print(f"\n创建 Google Sheets: {sheet_name}")
        
        try:
            # 创建新表格（在用户自己的 Drive 中）
            spreadsheet = self.client.create(sheet_name)
            worksheet = spreadsheet.get_worksheet(0)
            
            # 设置表头和元信息
            self._setup_header(worksheet, requirement_text, len(candidates))
            
            # 添加候选人数据
            self._add_candidates(worksheet, candidates)
            
            # 格式化表格
            self._format_sheet(worksheet, len(candidates))
            
            # 分享表格
            if share_emails:
                for email in share_emails:
                    try:
                        spreadsheet.share(email, perm_type='user', role='writer')
                        print(f"  ✓ 已分享给: {email}")
                    except Exception as e:
                        print(f"  ⚠ 分享失败 ({email}): {e}")
            
            url = spreadsheet.url
            print(f"\n✓ Google Sheets 创建成功")
            print(f"  链接: {url}")
            
            return url
            
        except Exception as e:
            print(f"✗ 导出失败: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def _setup_header(self, worksheet, requirement_text: str, candidate_count: int):
        """设置表头和元信息"""
        # 元信息行
        worksheet.update('A1', [['候选人推荐表']])
        worksheet.update('A2', [[f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}']])
        worksheet.update('A3', [[f'候选人数量: {candidate_count}']])
        if requirement_text:
            worksheet.update('A4', [[f'岗位要求: {requirement_text}']])
        
        # 表头（从第6行开始）
        headers = [
            '排名',
            '姓名',
            '总分',
            '职位匹配',
            '年限匹配',
            '背景匹配',
            '地点匹配',
            '当前职位',
            '当前公司',
            '工作年限',
            '咨询背景',
            '甲方背景',
            'LinkedIn链接',
            '推荐理由',
            '客户备注'
        ]
        
        worksheet.update('A6:O6', [headers])
    
    def _add_candidates(self, worksheet, candidates: List[Dict]):
        """添加候选人数据"""
        start_row = 7
        
        for i, candidate in enumerate(candidates, 1):
            row_data = [
                i,
                candidate.get('name', ''),
                candidate.get('final_score', candidate.get('flash_score', 0)),
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
                ''
            ]
            
            worksheet.update(f'A{start_row + i - 1}:O{start_row + i - 1}', [row_data])
    
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
        return '\n'.join(f"• {r}" for r in reasons)
    
    def _format_sheet(self, worksheet, candidate_count: int):
        """格式化表格样式"""
        try:
            # 格式化标题行
            worksheet.format('A1:O1', {
                "textFormat": {
                    "bold": True,
                    "fontSize": 14
                }
            })
            
            # 格式化表头
            worksheet.format('A6:O6', {
                "backgroundColor": {
                    "red": 0.2,
                    "green": 0.6,
                    "blue": 0.9
                },
                "textFormat": {
                    "bold": True,
                    "foregroundColor": {
                        "red": 1,
                        "green": 1,
                        "blue": 1
                    }
                },
                "horizontalAlignment": "CENTER"
            })
            
            # 冻结表头
            worksheet.freeze(rows=6)
            
        except Exception as e:
            print(f"  ⚠ 格式化失败: {e}")


if __name__ == "__main__":
    print("\nGoogle Sheets 导出器 (OAuth 版本)")
    print("="*70)
    print("\n使用前请确保:")
    print("1. 已从 Google Cloud Console 下载 OAuth 客户端凭证")
    print("2. 将凭证保存为 oauth_credentials.json")
    print("3. 首次使用会打开浏览器进行授权")
    print("\n详细设置说明请查看 OAUTH_SETUP.md")
