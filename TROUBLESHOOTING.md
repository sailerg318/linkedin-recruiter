# 故障排查指南

## 📋 目录

1. [常见问题](#常见问题)
2. [OAuth 问题](#oauth-问题)
3. [搜索问题](#搜索问题)
4. [筛选问题](#筛选问题)
5. [导出问题](#导出问题)
6. [性能问题](#性能问题)
7. [诊断工具](#诊断工具)

---

## 常见问题

### Q1: Pro 分析为什么没有通过？

**症状**: 候选人 Flash 通过了，但 Pro 分析没有通过

**可能原因**:

1. **地点不匹配**（最常见）
   - 候选人当前不在目标城市
   - 系统只看当前地点，不看历史地点
   
2. **年限不符**
   - 工作年限不在要求范围内
   - 计算方式可能有偏差
   
3. **职位不匹配**
   - 当前职位与要求职位差异较大
   - 职位级别不符
   
4. **背景不符**
   - 缺少要求的咨询经验
   - 缺少要求的甲方经验

**解决方法**:

```bash
# 运行诊断脚本
python3 test_pro_analysis.py

# 查看详细分析结果
cat candidates_review/candidates_*.json | jq '.[] | select(.final_score < 70)'
```

**调整阈值**:

```python
# 降低 Pro 阈值
result = quick_streaming_pipeline(
    user_input="...",
    pro_threshold=60  # 从 70 降到 60
)
```

---

### Q2: 搜索结果太少

**症状**: 搜索只返回很少的候选人

**可能原因**:

1. **搜索关键词太具体**
2. **地点限制太严格**
3. **搜索批次太小**
4. **搜索引擎限制**

**解决方法**:

```python
# 1. 增加搜索批次
result = quick_streaming_pipeline(
    user_input="...",
    search_batch_size=100  # 从 50 增加到 100
)

# 2. 使用岗位扩展
from job_expander import JobExpander
expander = JobExpander()
variants = expander.expand("Product Manager")
print(f"生成了 {len(variants)} 个岗位变体")

# 3. 尝试不同搜索引擎
result = quick_streaming_pipeline(
    user_input="...",
    engine="gemini"  # 尝试 Gemini
)

# 4. 放宽地点限制
# 修改需求，不指定具体城市
user_input = "产品经理，5-8年经验"  # 不指定地点
```

---

### Q3: Flash 筛选通过率太低

**症状**: 大量候选人被 Flash 筛选过滤掉

**可能原因**:

1. **Flash 阈值太高**
2. **需求描述太严格**
3. **候选人质量确实不符合**

**解决方法**:

```python
# 1. 降低 Flash 阈值
result = quick_streaming_pipeline(
    user_input="...",
    flash_threshold=40  # 从 50 降到 40
)

# 2. 简化需求描述
# 不好的需求：
user_input = "Base 上海的高级产品经理，必须有 BAT 背景，8-10年经验，硕士以上学历"

# 好的需求：
user_input = "上海的产品经理，5-10年经验，有大厂背景"

# 3. 查看 Flash 分数分布
import json
with open('candidates_review/candidates_*.json') as f:
    data = json.load(f)
    scores = [c.get('flash_score', 0) for c in data]
    print(f"Flash 分数范围: {min(scores)} - {max(scores)}")
    print(f"平均分: {sum(scores)/len(scores):.1f}")
```

---

## OAuth 问题

### 问题 1: OAuth 认证失败

**错误信息**:
```
Error: invalid_grant
The OAuth client was not found.
```

**解决方法**:

```bash
# 1. 检查凭证文件
ls -la oauth_credentials.json

# 2. 验证凭证格式
python3 -c "
import json
with open('oauth_credentials.json') as f:
    creds = json.load(f)
    print('Client ID:', creds['installed']['client_id'][:20] + '...')
"

# 3. 删除旧 token 重新认证
rm token.pickle
python3 test_oauth.py

# 4. 检查 Google Cloud Console 配置
# - 确认 OAuth 客户端 ID 类型为"桌面应用"
# - 确认已启用 Google Sheets API 和 Drive API
```

---

### 问题 2: 权限不足

**错误信息**:
```
HttpError 403: Insufficient Permission
```

**解决方法**:

```bash
# 1. 删除旧 token
rm token.pickle

# 2. 重新认证（会请求完整权限）
python3 test_oauth.py

# 3. 检查授权范围
python3 -c "
import pickle
with open('token.pickle', 'rb') as f:
    creds = pickle.load(f)
    print('Scopes:', creds.scopes)
"

# 应该包含:
# - https://www.googleapis.com/auth/spreadsheets
# - https://www.googleapis.com/auth/drive
```

---

### 问题 3: Token 过期

**错误信息**:
```
Error: Token has been expired or revoked
```

**解决方法**:

```bash
# 删除过期 token
rm token.pickle

# 重新认证
python3 test_oauth.py

# 或在代码中自动刷新
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth

exporter = GoogleSheetsExporterOAuth()
# 会自动刷新 token
```

---

## 搜索问题

### 问题 1: Serper API 限流

**错误信息**:
```
Error 429: Too Many Requests
```

**解决方法**:

```python
# 1. 增加请求间隔
import time

def search_with_retry(searcher, **kwargs):
    max_retries = 3
    for i in range(max_retries):
        try:
            return searcher.search_linkedin_profiles(**kwargs)
        except Exception as e:
            if "429" in str(e) and i < max_retries - 1:
                wait_time = (i + 1) * 5
                print(f"限流，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                raise

# 2. 减小批次大小
result = quick_streaming_pipeline(
    user_input="...",
    search_batch_size=30  # 减小批次
)

# 3. 切换到其他搜索引擎
result = quick_streaming_pipeline(
    user_input="...",
    engine="gemini"  # 使用 Gemini
)
```

---

### 问题 2: 搜索结果重复

**症状**: 同一个候选人出现多次

**解决方法**:

系统已内置去重功能，但如果仍有重复：

```python
# 手动去重
def deduplicate_candidates(candidates):
    seen_urls = set()
    unique = []
    for c in candidates:
        url = c.get('url', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique.append(c)
    return unique

# 使用
candidates = deduplicate_candidates(candidates)
```

---

### 问题 3: 搜索超时

**错误信息**:
```
TimeoutError: Request timed out
```

**解决方法**:

```python
# 1. 增加超时时间
import requests

session = requests.Session()
session.timeout = 30  # 30 秒超时

# 2. 使用重试机制
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 3. 检查网络连接
import subprocess
result = subprocess.run(['ping', '-c', '3', 'google.com'], capture_output=True)
print(result.stdout.decode())
```

---

## 筛选问题

### 问题 1: LLM API 调用失败

**错误信息**:
```
Error: API request failed with status 401
```

**解决方法**:

```bash
# 1. 检查 API Key
python3 -c "
from llm_config import DEFAULT_KEY
print('API Key:', DEFAULT_KEY[:10] + '...')
"

# 2. 测试 API 连接
curl -X POST https://api.example.com/v1/chat/completions \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "[福利]gemini-3-flash-preview",
    "messages": [{"role": "user", "content": "test"}]
  }'

# 3. 检查 API Base URL
python3 -c "
from llm_config import API_BASE
print('API Base:', API_BASE)
"
```

---

### 问题 2: 分析结果格式错误

**错误信息**:
```
JSONDecodeError: Expecting value
```

**解决方法**:

```python
# 添加错误处理
import json
import re

def safe_parse_json(text):
    """安全解析 JSON"""
    try:
        # 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试提取 JSON 部分
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None

# 使用
result = safe_parse_json(llm_response)
if result is None:
    print("无法解析 LLM 响应")
```

---

### 问题 3: 分析速度太慢

**症状**: Pro 分析每个候选人需要很长时间

**解决方法**:

```python
# 1. 使用 Flash 模型（已默认）
# 系统已经将 Pro 模型改为 Flash，速度更快

# 2. 减小 Pro 批次
result = quick_streaming_pipeline(
    user_input="...",
    screen_batch_size=5  # 减小批次
)

# 3. 限制 Pro 分析数量
# 只对 Flash 分数最高的候选人进行 Pro 分析
from detailed_screening import DetailedScreening

screener = DetailedScreening()
results = screener.screen_candidates(
    candidates=candidates,
    requirement=requirement,
    flash_threshold=50,
    max_pro_analysis=20  # 最多分析 20 人
)

# 4. 并发处理（高级）
from concurrent.futures import ThreadPoolExecutor

def analyze_candidate(candidate):
    return screener._pro_analyze_single(candidate, requirement)

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(analyze_candidate, candidates))
```

---

## 导出问题

### 问题 1: Google Sheets 创建失败

**错误信息**:
```
HttpError 403: The caller does not have permission
```

**解决方法**:

```bash
# 1. 重新认证
rm token.pickle
python3 test_oauth.py

# 2. 检查 Drive API 是否启用
# 访问 https://console.cloud.google.com/apis/library/drive.googleapis.com

# 3. 测试创建表格
python3 test_google_sheets.py

# 4. 检查存储空间
# 访问 https://drive.google.com/drive/quota
```

---

### 问题 2: 分享失败

**错误信息**:
```
HttpError 400: Bad Request - Invalid email address
```

**解决方法**:

```python
# 1. 验证邮箱格式
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

emails = ["hr@company.com", "invalid-email"]
valid_emails = [e for e in emails if validate_email(e)]

# 2. 使用验证后的邮箱
result = quick_streaming_pipeline(
    user_input="...",
    share_emails=valid_emails
)

# 3. 手动分享
# 如果自动分享失败，可以手动分享 Google Sheets
print(f"请手动分享此链接: {result['url']}")
```

---

### 问题 3: 导出数据不完整

**症状**: Google Sheets 中缺少某些字段

**解决方法**:

```python
# 1. 检查候选人数据结构
import json

with open('candidates_review/candidates_*.json') as f:
    data = json.load(f)
    if data:
        print("候选人字段:", data[0].keys())

# 2. 验证导出逻辑
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth

exporter = GoogleSheetsExporterOAuth()

# 检查导出的列
print("导出列:", exporter.get_export_columns())

# 3. 手动导出测试
test_candidate = {
    'name': '测试',
    'url': 'https://linkedin.com/in/test',
    'title': 'PM',
    'location': '上海',
    'final_score': 85
}

result = exporter.export_candidates([test_candidate])
print(f"测试导出: {result['url']}")
```

---

## 性能问题

### 问题 1: 内存占用过高

**症状**: 程序运行时内存持续增长

**解决方法**:

```python
# 1. 使用流式处理（已默认）
# 系统已经使用流式处理，避免一次性加载所有数据

# 2. 手动清理内存
import gc

def process_batch(batch):
    # 处理批次
    results = []
    for item in batch:
        result = process_item(item)
        results.append(result)
    
    # 清理内存
    gc.collect()
    return results

# 3. 减小批次大小
result = quick_streaming_pipeline(
    user_input="...",
    search_batch_size=30,   # 减小
    screen_batch_size=5     # 减小
)

# 4. 监控内存使用
import psutil
import os

process = psutil.Process(os.getpid())
print(f"内存使用: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

---

### 问题 2: 处理速度慢

**症状**: 整个流程需要很长时间

**优化方法**:

```python
# 1. 使用最快的搜索引擎
result = quick_streaming_pipeline(
    user_input="...",
    engine="serper"  # Serper 最快
)

# 2. 提高 Flash 阈值（减少 Pro 分析数量）
result = quick_streaming_pipeline(
    user_input="...",
    flash_threshold=60,  # 提高阈值
    pro_threshold=70
)

# 3. 减小搜索范围
result = quick_streaming_pipeline(
    user_input="...",
    search_batch_size=30  # 减小搜索量
)

# 4. 跳过某些步骤
# 如果不需要 Google Sheets，使用 quick_run_no_sheets.py
python3 quick_run_no_sheets.py
```

---

## 诊断工具

### 1. 系统诊断

```bash
# 运行完整诊断
python3 diagnose_system.py
```

创建 `diagnose_system.py`：

```python
#!/usr/bin/env python3
"""系统诊断工具"""

import sys
import os
import json

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️  需要 Python 3.8 或更高版本")
        return False
    print("  ✓ Python 版本符合要求")
    return True

def check_dependencies():
    """检查依赖"""
    required = ['requests', 'google-auth', 'google-api-python-client']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} 未安装")
            missing.append(package)
    
    return len(missing) == 0

def check_config():
    """检查配置"""
    try:
        from config import SERPER_API_KEY
        from llm_config import DEFAULT_KEY
        
        if SERPER_API_KEY and SERPER_API_KEY != "your_serper_api_key":
            print("  ✓ Serper API Key 已配置")
        else:
            print("  ⚠️  Serper API Key 未配置")
        
        if DEFAULT_KEY and DEFAULT_KEY != "your_llm_api_key":
            print("  ✓ LLM API Key 已配置")
        else:
            print("  ⚠️  LLM API Key 未配置")
        
        return True
    except Exception as e:
        print(f"  ✗ 配置检查失败: {e}")
        return False

def check_oauth():
    """检查 OAuth"""
    if os.path.exists('oauth_credentials.json'):
        print("  ✓ OAuth 凭证文件存在")
        try:
            with open('oauth_credentials.json') as f:
                creds = json.load(f)
                if 'installed' in creds:
                    print("  ✓ OAuth 凭证格式正确")
                else:
                    print("  ⚠️  OAuth 凭证格式可能不正确")
        except:
            print("  ⚠️  OAuth 凭证文件无法解析")
    else:
        print("  ⚠️  OAuth 凭证文件不存在")
    
    if os.path.exists('token.pickle'):
        print("  ✓ Token 文件存在")
    else:
        print("  ⚠️  Token 文件不存在（首次使用需要认证）")

def main():
    print("="*60)
    print("LinkedIn 招聘系统 - 系统诊断")
    print("="*60)
    
    print("\n1. Python 版本检查")
    check_python_version()
    
    print("\n2. 依赖检查")
    check_dependencies()
    
    print("\n3. 配置检查")
    check_config()
    
    print("\n4. OAuth 检查")
    check_oauth()
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

### 2. API 测试

```bash
# 测试 Serper API
python3 test_serper_api.py

# 测试 LLM API
python3 test_llm_api.py

# 测试 Google Sheets
python3 test_google_sheets.py
```

---

### 3. 日志分析

```bash
# 查看错误日志
grep "ERROR" linkedin_recruiter.log

# 查看最近的错误
tail -n 100 linkedin_recruiter.log | grep "ERROR"

# 统计错误类型
grep "ERROR" linkedin_recruiter.log | awk '{print $NF}' | sort | uniq -c
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. **查看文档**
   - [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md:1) - 完整使用指南
   - [`API_REFERENCE.md`](API_REFERENCE.md:1) - API 参考
   - [`DEPLOYMENT.md`](DEPLOYMENT.md:1) - 部署指南

2. **运行诊断**
   ```bash
   python3 diagnose_system.py
   ```

3. **查看日志**
   ```bash
   tail -f linkedin_recruiter.log
   ```

4. **提交 Issue**
   - 包含错误信息
   - 包含系统环境
   - 包含复现步骤
