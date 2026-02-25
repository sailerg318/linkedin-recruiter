"""
Google Sheets 导出器 - 支持环境变量配置
兼容 Render 部署环境
"""

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import base64
import json
from typing import List, Dict
from datetime import datetime


class GoogleSheetsExporterOAuth:
    """Google Sheets导出器 - OAuth版本（支持环境变量）"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_file: str = "oauth_credentials.json"):
        """
        初始化 OAuth 客户端
        
        支持两种方式：
        1. 从文件读取（本地开发）
        2. 从环境变量读取（Render 部署）
        
        Args:
            credentials_file: OAuth 客户端凭证文件
        """
        self.credentials_file = credentials_file
        self.token_file = "token.pickle"
        self.client = None
    
    def authenticate(self):
        """OAuth 认证流程（支持环境变量）"""
        creds = None
        
        # 方式 1: 从环境变量读取 token（Render 部署）
        token_base64 = os.getenv('GOOGLE_TOKEN_BASE64')
        if token_base64:
            try:
                print("从环境变量读取 OAuth token...")
                token_bytes = base64.b64decode(token_base64)
                creds = pickle.loads(token_bytes)
                print("✓ Token 加载成功")
            except Exception as e:
                print(f"⚠️  环境变量 token 加载失败: {e}")
                creds = None
        
        # 方式 2: 从文件读取 token（本地开发）
        if not creds and os.path.exists(self.token_file):
            try:
                print(f"从文件读取 OAuth token: {self.token_file}")
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                print("✓ Token 加载成功")
            except Exception as e:
                print(f"⚠️  文件 token 加载失败: {e}")
                creds = None
        
        # 如果没有有效凭证，尝试刷新或重新认证
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("刷新访问令牌...")
                try:
                    creds.refresh(Request())
                    print("✓ Token 刷新成功")
                except Exception as e:
                    print(f"✗ Token 刷新失败: {e}")
                    return False
            else:
                # 需要重新认证（仅在本地环境）
                if not os.getenv('GOOGLE_TOKEN_BASE64'):
                    print("\n⚠️  需要重新认证，但当前环境不支持交互式认证")
                    print("请在本地运行认证流程，然后将 token 上传到 Render")
                    return False
                else:
                    print("✗ Token 无效且无法刷新")
                    return False
            
            # 保存刷新后的 token（仅在本地）
            if not os.getenv('GOOGLE_TOKEN_BASE64'):
                try:
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    print(f"✓ Token 已保存到 {self.token_file}")
                except Exception as e:
                    print(f"⚠️  Token 保存失败: {e}")
        
        # 创建 gspread 客户端
        try:
            self.client = gspread.authorize(creds)
            print("✓ Google Sheets 客户端创建成功")
            return True
        except Exception as e:
            print(f"✗ 客户端创建失败: {e}")
            return False
    
    def connect(self):
        """连接到 Google Sheets"""
        return self.authenticate()
    
    def create_spreadsheet(self, title: str, share_emails: List[str] = None) -> str:
        """
        创建新的 Google Sheets
        
        Args:
            title: 表格标题
            share_emails: 分享邮箱列表
            
        Returns:
            表格 URL
        """
        if not self.client:
            if not self.connect():
                return None
        
        try:
            spreadsheet = self.client.create(title)
            
            # 分享给指定邮箱
            if share_emails:
                for email in share_emails:
                    try:
                        spreadsheet.share(email, perm_type='user', role='writer')
                        print(f"  ✓ 已分享给: {email}")
                    except Exception as e:
                        print(f"  ⚠️  分享失败 ({email}): {e}")
            
            return spreadsheet.url
            
        except Exception as e:
            print(f"✗ 创建表格失败: {e}")
            return None
    
    def _setup_header(self, worksheet, requirement_text: str, candidate_count: int):
        """设置表头"""
        # 第1行：标题
        worksheet.update('A1:O1', [[
            f'LinkedIn 候选人筛选结果 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        ]])
        
        # 第2行：需求
        worksheet.update('A2:O2', [[f'需求：{requirement_text}']])
        
        # 第3行：统计
        worksheet.update('A3:O3', [[f'候选人数量：{candidate_count} 位']])
        
        # 第5-6行：列标题
        headers = [
            ['排名', '姓名', '综合评分', '职位匹配', '年限匹配', '背景匹配', '地点匹配',
             '当前职位', '当前公司', '工作年限', '咨询背景', '甲方背景', 'LinkedIn', '推荐理由', '客户备注']
        ]
        worksheet.update('A6:O6', headers)
        
        # 格式化
        worksheet.format('A1:O1', {
            'textFormat': {'bold': True, 'fontSize': 14},
            'horizontalAlignment': 'CENTER'
        })
        worksheet.format('A6:O6', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })


# 向后兼容：保持原有的类名
GoogleSheetsExporter = GoogleSheetsExporterOAuth


if __name__ == "__main__":
    # 测试
    print("="*70)
    print("测试 Google Sheets 导出器（环境变量支持）")
    print("="*70)
    
    exporter = GoogleSheetsExporterOAuth()
    
    if exporter.connect():
        print("\n✅ 连接成功！")
        
        # 测试创建表格
        url = exporter.create_spreadsheet(
            title="测试表格_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            share_emails=None
        )
        
        if url:
            print(f"\n✅ 表格创建成功！")
            print(f"URL: {url}")
        else:
            print("\n✗ 表格创建失败")
    else:
        print("\n✗ 连接失败")
        print("\n提示：")
        print("1. 本地开发：确保 oauth_credentials.json 和 token.pickle 存在")
        print("2. Render 部署：设置环境变量 GOOGLE_TOKEN_BASE64")
