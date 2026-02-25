"""
CSV导入模块 - 支持从CSV文件导入候选人信息
"""

import csv
from typing import List, Dict
import os


class CandidateImporter:
    """候选人导入器 - 从CSV导入候选人信息"""
    
    def __init__(self):
        pass
    
    def import_from_csv(self, csv_file: str) -> List[Dict]:
        """
        从CSV文件导入候选人
        
        CSV格式要求：
        - name: 姓名（必填）
        - title: 职位
        - company: 公司
        - location: 地点
        - url: LinkedIn链接
        - snippet: 简介
        - experience_years: 工作年限
        
        Args:
            csv_file: CSV文件路径
            
        Returns:
            候选人列表
        """
        if not os.path.exists(csv_file):
            print(f"✗ 文件不存在: {csv_file}")
            return []
        
        candidates = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # 构建候选人字典
                    candidate = {
                        "name": row.get('name', '').strip(),
                        "title": row.get('title', '').strip(),
                        "current_title": row.get('title', '').strip(),
                        "company": row.get('company', '').strip(),
                        "current_company": row.get('company', '').strip(),
                        "location": row.get('location', '').strip(),
                        "url": row.get('url', '').strip(),
                        "snippet": row.get('snippet', '').strip(),
                        "experience_years": self._parse_experience(row.get('experience_years', '')),
                        "source": "csv_import"
                    }
                    
                    # 验证必填字段
                    if candidate['name']:
                        candidates.append(candidate)
                    else:
                        print(f"  ⚠ 跳过无效行（缺少姓名）")
            
            print(f"✓ 从CSV导入 {len(candidates)} 位候选人")
            return candidates
            
        except Exception as e:
            print(f"✗ CSV导入失败: {e}")
            return []
    
    def _parse_experience(self, exp_str: str) -> int:
        """解析工作年限"""
        try:
            # 尝试提取数字
            import re
            match = re.search(r'\d+', str(exp_str))
            if match:
                return int(match.group())
        except:
            pass
        return 0
    
    def create_template_csv(self, output_file: str = "candidates_template.csv"):
        """
        创建CSV模板文件
        
        Args:
            output_file: 输出文件路径
        """
        headers = [
            'name',
            'title',
            'company',
            'location',
            'url',
            'snippet',
            'experience_years'
        ]
        
        # 示例数据
        example_data = [
            {
                'name': '张三',
                'title': 'Senior OD Manager',
                'company': 'Google',
                'location': 'London',
                'url': 'https://linkedin.com/in/zhangsan',
                'snippet': '10年OD经验，McKinsey 3年，Google 5年',
                'experience_years': '10'
            },
            {
                'name': '李四',
                'title': 'Organizational Development Lead',
                'company': 'Amazon',
                'location': 'London',
                'url': 'https://linkedin.com/in/lisi',
                'snippet': '12年HR经验，专注组织发展',
                'experience_years': '12'
            }
        ]
        
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(example_data)
            
            print(f"✓ CSV模板已创建: {output_file}")
            print(f"\n使用说明:")
            print(f"1. 打开 {output_file}")
            print(f"2. 删除示例数据，填入真实候选人信息")
            print(f"3. 保存文件")
            print(f"4. 使用 import_from_csv() 导入")
            
        except Exception as e:
            print(f"✗ 创建模板失败: {e}")
    
    def merge_candidates(
        self,
        tavily_candidates: List[Dict],
        csv_candidates: List[Dict]
    ) -> List[Dict]:
        """
        合并Tavily搜索结果和CSV导入的候选人
        
        Args:
            tavily_candidates: Tavily搜索的候选人
            csv_candidates: CSV导入的候选人
            
        Returns:
            合并后的候选人列表（已去重）
        """
        print(f"\n{'='*60}")
        print("合并候选人数据")
        print(f"{'='*60}")
        print(f"Tavily候选人: {len(tavily_candidates)} 位")
        print(f"CSV候选人: {len(csv_candidates)} 位")
        
        # 使用URL和姓名进行去重
        seen = set()
        merged = []
        
        # 先添加Tavily候选人
        for candidate in tavily_candidates:
            key = (candidate.get('url', ''), candidate.get('name', ''))
            if key not in seen and (key[0] or key[1]):
                seen.add(key)
                merged.append(candidate)
        
        # 再添加CSV候选人
        new_from_csv = 0
        for candidate in csv_candidates:
            key = (candidate.get('url', ''), candidate.get('name', ''))
            if key not in seen and (key[0] or key[1]):
                seen.add(key)
                merged.append(candidate)
                new_from_csv += 1
        
        print(f"\n✓ 合并完成")
        print(f"  总计: {len(merged)} 位候选人")
        print(f"  其中CSV新增: {new_from_csv} 位")
        
        return merged


if __name__ == "__main__":
    # 测试代码
    importer = CandidateImporter()
    
    # 创建模板
    print("="*60)
    print("创建CSV模板")
    print("="*60)
    importer.create_template_csv("linkedin_recruiter/candidates_template.csv")
    
    # 测试导入
    print("\n" + "="*60)
    print("测试导入")
    print("="*60)
    candidates = importer.import_from_csv("linkedin_recruiter/candidates_template.csv")
    
    if candidates:
        print(f"\n导入的候选人:")
        for i, c in enumerate(candidates, 1):
            print(f"{i}. {c['name']} - {c['title']} @ {c['company']}")
