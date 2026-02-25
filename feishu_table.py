"""
飞书多维表格集成模块 - 将候选人信息添加到飞书多维表格
"""

import requests
import time
from typing import List, Dict, Optional
from config import (
    FEISHU_APP_ID, 
    FEISHU_APP_SECRET, 
    FEISHU_TABLE_ID,
    FEISHU_TABLE_APP_TOKEN
)


class FeishuTableClient:
    """飞书多维表格客户端"""
    
    def __init__(
        self, 
        app_id: str = FEISHU_APP_ID,
        app_secret: str = FEISHU_APP_SECRET,
        app_token: str = FEISHU_TABLE_APP_TOKEN,
        table_id: str = FEISHU_TABLE_ID
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.table_id = table_id
        self.access_token = None
        self.token_expire_time = 0
        
    def _get_tenant_access_token(self) -> Optional[str]:
        """
        获取tenant_access_token
        文档: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0QjL5QzM/auth-v3/auth/tenant_access_token_internal
        """
        # 检查token是否过期
        if self.access_token and time.time() < self.token_expire_time:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                self.access_token = data.get("tenant_access_token")
                # token有效期2小时，提前5分钟刷新
                self.token_expire_time = time.time() + data.get("expire", 7200) - 300
                return self.access_token
            else:
                print(f"✗ 获取飞书token失败: {data.get('msg')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求飞书API失败: {e}")
            return None
    
    def add_records(self, candidates: List[Dict]) -> bool:
        """
        批量添加候选人记录到多维表格
        
        Args:
            candidates: 候选人列表，每个候选人包含：
                - name: 姓名
                - url: LinkedIn URL
                - title: 职位
                - snippet: 简介
                - score: 相关度分数
        
        Returns:
            是否添加成功
        """
        token = self._get_tenant_access_token()
        if not token:
            return False
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/batch_create"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 构建记录数据
        records = []
        for candidate in candidates:
            record = {
                "fields": {
                    "姓名": candidate.get("name", ""),
                    "LinkedIn链接": candidate.get("url", ""),
                    "职位": candidate.get("title", ""),
                    "公司": candidate.get("company", ""),
                    "地点": candidate.get("location", ""),
                    "简介": candidate.get("snippet", ""),
                    "相关度分数": candidate.get("score", 0),
                    "添加时间": int(time.time() * 1000)  # 毫秒时间戳
                }
            }
            records.append(record)
        
        payload = {
            "records": records
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                print(f"✓ 成功添加 {len(candidates)} 条记录到飞书表格")
                return True
            else:
                print(f"✗ 添加记录失败: {data.get('msg')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求飞书API失败: {e}")
            return False
    
    def add_single_record(self, candidate: Dict) -> bool:
        """
        添加单条候选人记录
        
        Args:
            candidate: 候选人信息字典
            
        Returns:
            是否添加成功
        """
        return self.add_records([candidate])
    
    def get_records(self, page_size: int = 100) -> List[Dict]:
        """
        获取表格中的记录（用于去重）
        
        Args:
            page_size: 每页记录数
            
        Returns:
            记录列表
        """
        token = self._get_tenant_access_token()
        if not token:
            return []
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "page_size": page_size
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("items", [])
                print(f"✓ 获取到 {len(items)} 条现有记录")
                return items
            else:
                print(f"✗ 获取记录失败: {data.get('msg')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求飞书API失败: {e}")
            return []
    
    def deduplicate_candidates(
        self, 
        new_candidates: List[Dict]
    ) -> List[Dict]:
        """
        去重：过滤掉已存在于表格中的候选人
        
        Args:
            new_candidates: 新候选人列表
            
        Returns:
            去重后的候选人列表
        """
        existing_records = self.get_records()
        
        # 提取已存在的LinkedIn URL
        existing_urls = set()
        for record in existing_records:
            fields = record.get("fields", {})
            url = fields.get("LinkedIn链接", "")
            if url:
                existing_urls.add(url)
        
        # 过滤新候选人
        unique_candidates = []
        for candidate in new_candidates:
            url = candidate.get("url", "")
            if url not in existing_urls:
                unique_candidates.append(candidate)
            else:
                print(f"⊘ 跳过重复候选人: {candidate.get('name')}")
        
        print(f"✓ 去重完成: {len(unique_candidates)}/{len(new_candidates)} 位新候选人")
        return unique_candidates


if __name__ == "__main__":
    # 测试代码
    client = FeishuTableClient()
    
    # 测试添加记录
    test_candidates = [
        {
            "name": "测试候选人",
            "url": "https://linkedin.com/in/test-user",
            "title": "Python Engineer",
            "snippet": "5年Python开发经验",
            "score": 0.85
        }
    ]
    
    # 注意：需要先配置正确的飞书应用信息才能运行
    # success = client.add_records(test_candidates)
    # print(f"添加结果: {'成功' if success else '失败'}")
    
    print("飞书表格客户端已就绪")
    print("请在config.py中配置以下信息:")
    print("- FEISHU_APP_ID")
    print("- FEISHU_APP_SECRET")
    print("- FEISHU_TABLE_APP_TOKEN")
    print("- FEISHU_TABLE_ID")
