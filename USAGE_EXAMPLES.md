# 使用示例集合

## 📚 目录

1. [基础示例](#基础示例)
2. [高级示例](#高级示例)
3. [自定义配置](#自定义配置)
4. [批量处理](#批量处理)
5. [错误处理](#错误处理)

---

## 基础示例

### 示例 1：最简单的使用方式

```python
from streaming_pipeline import quick_streaming_pipeline

# 一行代码完成搜索和筛选
result = quick_streaming_pipeline(
    user_input="Base 上海的产品经理，5-8年经验"
)

print(f"找到 {result['pro_passed']} 位合适的候选人")
print(f"Google Sheets: {result['url']}")
```

### 示例 2：指定搜索引擎

```python
# 使用 Serper（推荐，最快）
result = quick_streaming_pipeline(
    user_input="北京的 Java 工程师",
    engine="serper"
)

# 使用 Gemini（Google Grounding）
result = quick_streaming_pipeline(
    user_input="深圳的前端工程师",
    engine="gemini"
)

# 使用 Tavily
result = quick_streaming_pipeline(
    user_input="杭州的数据分析师",
    engine="tavily"
)
```

### 示例 3：调整筛选阈值

```python
# 更宽松的筛选（找更多候选人）
result = quick_streaming_pipeline(
    user_input="上海的运营经理",
    flash_threshold=40,  # 降低 Flash 阈值
    pro_threshold=60     # 降低 Pro 阈值
)

# 更严格的筛选（只要最匹配的）
result = quick_streaming_pipeline(
    user_input="北京的技术总监",
    flash_threshold=60,  # 提高 Flash 阈值
    pro_threshold=80     # 提高 Pro 阈值
)
```

---

## 高级示例

### 示例 4：复杂招聘需求

```python
# 多条件复杂需求
complex_requirement = """
招聘岗位：高级数据科学家
工作地点：北京或上海
工作年限：8-12年
必备背景：
  - BAT 或 TMD 大厂经验
  - 有咨询公司经历优先
必备技能：
  - Python、SQL
  - 机器学习、深度学习
  - 数据可视化
学历要求：硕士及以上
"""

result = quick_streaming_pipeline(
    user_input=complex_requirement,
    search_batch_size=100,  # 增加搜索量
    flash_threshold=55,
    pro_threshold=75
)
```

### 示例 5：分享给团队

```python
# 导出并自动分享给团队成员
result = quick_streaming_pipeline(
    user_input="深圳的产品经理，有 B 端经验",
    share_emails=[
        "hr@company.com",
        "hiring.manager@company.com",
        "team.lead@company.com"
    ]
)

print(f"已分享给 {len(result.get('shared_with', []))} 位成员")
```

### 示例 6：大规模搜索

```python
# 搜索大量候选人
result = quick_streaming_pipeline(
    user_input="全国的 Python 工程师，3-5年经验",
    search_batch_size=200,   # 大批次搜索
    screen_batch_size=20,    # 大批次筛选
    flash_threshold=50,
    pro_threshold=70
)

print(f"搜索了 {result['total_searched']} 位候选人")
print(f"Flash 通过 {result['flash_passed']} 位")
print(f"Pro 通过 {result['pro_passed']} 位")
```

---

## 自定义配置

### 示例 7：使用自定义 API Key

```python
import os
from streaming_pipeline import quick_streaming_pipeline

# 设置环境变量
os.environ['SERPER_API_KEY'] = 'your_serper_key'
os.environ['LLM_API_KEY'] = 'your_llm_key'

result = quick_streaming_pipeline(
    user_input="上海的设计师"
)
```

### 示例 8：自定义需求解析

```python
from requirement_parser import RequirementParser

# 手动解析需求
parser = RequirementParser()
requirement = parser.parse("Base 北京的 AI 工程师，5年以上经验")

print(f"职位: {requirement['job_title']}")
print(f"地点: {requirement['location']}")
print(f"年限: {requirement['years_min']}-{requirement['years_max']}")

# 使用解析后的需求
from streaming_pipeline import streaming_pipeline

result = streaming_pipeline(
    requirement=requirement,
    search_batch_size=50
)
```

### 示例 9：自定义岗位扩展

```python
from job_expander import JobExpander

# 生成岗位关键词变体
expander = JobExpander()
variants = expander.expand("Product Manager")

print("岗位变体:")
for v in variants:
    print(f"  - {v}")

# 输出:
# - Product Manager
# - PM
# - Senior Product Manager
# - Product Lead
# - Product Owner
```

---

## 批量处理

### 示例 10：批量处理多个岗位

```python
from streaming_pipeline import quick_streaming_pipeline

# 多个岗位需求
positions = [
    "上海的产品经理，5-8年经验",
    "北京的 Java 工程师，3-5年经验",
    "深圳的前端工程师，React 技术栈",
    "杭州的数据分析师，SQL + Python"
]

results = []
for position in positions:
    print(f"\n处理: {position}")
    result = quick_streaming_pipeline(
        user_input=position,
        search_batch_size=50
    )
    results.append({
        'position': position,
        'found': result['pro_passed'],
        'url': result['url']
    })

# 汇总结果
print("\n" + "="*70)
print("批量处理结果汇总")
print("="*70)
for r in results:
    print(f"{r['position']}: 找到 {r['found']} 位")
    print(f"  链接: {r['url']}")
```

### 示例 11：从 CSV 导入需求

```python
import csv
from streaming_pipeline import quick_streaming_pipeline

# 从 CSV 读取招聘需求
with open('positions.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        requirement = f"{row['location']}的{row['title']}"
        if row.get('years'):
            requirement += f"，{row['years']}年经验"
        
        print(f"\n处理: {requirement}")
        result = quick_streaming_pipeline(
            user_input=requirement,
            search_batch_size=50
        )
        
        print(f"  找到 {result['pro_passed']} 位候选人")
```

---

## 错误处理

### 示例 12：完整的错误处理

```python
from streaming_pipeline import quick_streaming_pipeline
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

def safe_search(user_input, max_retries=3):
    """带重试的安全搜索"""
    for attempt in range(max_retries):
        try:
            result = quick_streaming_pipeline(
                user_input=user_input,
                search_batch_size=50,
                flash_threshold=50,
                pro_threshold=70
            )
            
            # 检查是否有错误
            if result.get('error'):
                print(f"错误: {result['error']}")
                if attempt < max_retries - 1:
                    print(f"重试 {attempt + 1}/{max_retries}...")
                    continue
                return None
            
            return result
            
        except Exception as e:
            print(f"异常: {str(e)}")
            if attempt < max_retries - 1:
                print(f"重试 {attempt + 1}/{max_retries}...")
                continue
            return None
    
    return None

# 使用
result = safe_search("上海的产品经理")
if result:
    print(f"成功找到 {result['pro_passed']} 位候选人")
else:
    print("搜索失败")
```

### 示例 13：验证结果

```python
def validate_result(result):
    """验证搜索结果"""
    if not result:
        return False, "结果为空"
    
    if result.get('error'):
        return False, f"错误: {result['error']}"
    
    if result.get('total_searched', 0) == 0:
        return False, "没有搜索到任何候选人"
    
    if result.get('pro_passed', 0) == 0:
        return False, "没有候选人通过筛选"
    
    if not result.get('url'):
        return False, "未生成 Google Sheets"
    
    return True, "验证通过"

# 使用
result = quick_streaming_pipeline(
    user_input="北京的 AI 工程师"
)

is_valid, message = validate_result(result)
if is_valid:
    print(f"✓ {message}")
    print(f"  找到 {result['pro_passed']} 位候选人")
    print(f"  链接: {result['url']}")
else:
    print(f"✗ {message}")
```

---

## 性能优化示例

### 示例 14：快速模式（优先速度）

```python
# 快速搜索，降低精度
result = quick_streaming_pipeline(
    user_input="上海的工程师",
    search_batch_size=30,    # 小批次
    screen_batch_size=10,    # 小批次
    flash_threshold=60,      # 高阈值，快速过滤
    pro_threshold=70,
    engine="serper"          # 最快的引擎
)
```

### 示例 15：精准模式（优先质量）

```python
# 精准搜索，提高质量
result = quick_streaming_pipeline(
    user_input="北京的技术专家，10年以上经验",
    search_batch_size=100,   # 大批次
    screen_batch_size=20,    # 大批次
    flash_threshold=40,      # 低阈值，保留更多
    pro_threshold=80,        # 高阈值，严格筛选
    engine="serper"
)
```

---

## 调试示例

### 示例 16：查看详细日志

```python
import logging
from streaming_pipeline import quick_streaming_pipeline

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

result = quick_streaming_pipeline(
    user_input="上海的产品经理"
)
```

### 示例 17：测试单个候选人分析

```python
from detailed_screening import DetailedScreening

# 创建筛选器
screener = DetailedScreening()

# 测试候选人
test_candidate = {
    'name': '张三',
    'url': 'https://linkedin.com/in/zhangsan',
    'title': 'Senior Product Manager',
    'location': '上海',
    'snippet': '10年产品经验，曾在阿里巴巴、腾讯工作...'
}

# 测试需求
test_requirement = {
    'job_title': 'Product Manager',
    'location': '上海',
    'years_min': 5,
    'years_max': 10,
    'keywords': ['产品', '互联网']
}

# Flash 分析
flash_result = screener._flash_score_single(test_candidate, test_requirement)
print(f"Flash 分数: {flash_result.get('flash_score')}")

# Pro 分析
pro_result = screener._pro_analyze_single(test_candidate, test_requirement)
print(f"Pro 分数: {pro_result.get('final_score')}")
print(f"推荐理由: {pro_result.get('推荐理由')}")
```

---

## 集成示例

### 示例 18：与现有系统集成

```python
from streaming_pipeline import quick_streaming_pipeline
import requests

def integrate_with_ats(position_id):
    """与 ATS 系统集成"""
    # 1. 从 ATS 获取岗位需求
    ats_api = "https://your-ats.com/api/positions"
    response = requests.get(f"{ats_api}/{position_id}")
    position = response.json()
    
    # 2. 构建搜索需求
    requirement = f"{position['location']}的{position['title']}"
    if position.get('years_required'):
        requirement += f"，{position['years_required']}年经验"
    
    # 3. 执行搜索
    result = quick_streaming_pipeline(
        user_input=requirement,
        search_batch_size=50
    )
    
    # 4. 将结果推送回 ATS
    if result.get('pro_passed', 0) > 0:
        candidates_data = {
            'position_id': position_id,
            'candidates_count': result['pro_passed'],
            'sheet_url': result['url']
        }
        requests.post(f"{ats_api}/candidates", json=candidates_data)
    
    return result

# 使用
result = integrate_with_ats(position_id="12345")
```

---

## 最佳实践

### 1. 合理设置批次大小
```python
# 小规模搜索（< 100 人）
search_batch_size = 30
screen_batch_size = 10

# 中等规模（100-500 人）
search_batch_size = 50
screen_batch_size = 15

# 大规模搜索（> 500 人）
search_batch_size = 100
screen_batch_size = 20
```

### 2. 根据岗位调整阈值
```python
# 稀缺岗位（降低阈值）
flash_threshold = 40
pro_threshold = 60

# 常见岗位（标准阈值）
flash_threshold = 50
pro_threshold = 70

# 高级岗位（提高阈值）
flash_threshold = 60
pro_threshold = 80
```

### 3. 选择合适的搜索引擎
```python
# Serper - 推荐，最快最稳定
engine = "serper"

# Gemini - 适合需要深度理解的场景
engine = "gemini"

# Tavily - 备用选项
engine = "tavily"
```

---

## 完整工作流示例

```python
from streaming_pipeline import quick_streaming_pipeline
import json
from datetime import datetime

def complete_recruitment_workflow(position_name, location, years, background):
    """完整的招聘工作流"""
    
    # 1. 构建需求
    requirement = f"Base {location}的{position_name}"
    if years:
        requirement += f"，{years}年经验"
    if background:
        requirement += f"，{background}"
    
    print(f"\n{'='*70}")
    print(f"开始招聘流程: {position_name}")
    print(f"{'='*70}")
    print(f"需求: {requirement}")
    
    # 2. 执行搜索和筛选
    result = quick_streaming_pipeline(
        user_input=requirement,
        search_batch_size=50,
        screen_batch_size=10,
        flash_threshold=50,
        pro_threshold=70,
        engine="serper",
        share_emails=["hr@company.com"]
    )
    
    # 3. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"recruitment_{position_name}_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 4. 生成报告
    print(f"\n{'='*70}")
    print("招聘结果报告")
    print(f"{'='*70}")
    print(f"岗位: {position_name}")
    print(f"地点: {location}")
    print(f"搜索: {result.get('total_searched', 0)} 位")
    print(f"Flash 通过: {result.get('flash_passed', 0)} 位")
    print(f"Pro 通过: {result.get('pro_passed', 0)} 位")
    print(f"通过率: {result.get('pro_passed', 0) / max(result.get('total_searched', 1), 1) * 100:.1f}%")
    print(f"\nGoogle Sheets: {result.get('url', 'N/A')}")
    print(f"结果文件: {result_file}")
    
    return result

# 使用示例
result = complete_recruitment_workflow(
    position_name="高级产品经理",
    location="上海",
    years="5-8",
    background="有大厂背景"
)
```
