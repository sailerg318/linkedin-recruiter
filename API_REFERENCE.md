# API 参考文档

## 📚 目录

1. [核心 API](#核心-api)
2. [搜索模块](#搜索模块)
3. [筛选模块](#筛选模块)
4. [导出模块](#导出模块)
5. [工具函数](#工具函数)

---

## 核心 API

### quick_streaming_pipeline()

快速流式处理管道，一站式完成搜索、筛选、导出。

**位置**: [`streaming_pipeline.py`](streaming_pipeline.py:1)

**函数签名**:
```python
def quick_streaming_pipeline(
    user_input: str,
    search_batch_size: int = 50,
    screen_batch_size: int = 10,
    flash_threshold: int = 50,
    pro_threshold: int = 70,
    engine: str = "serper",
    share_emails: List[str] = None
) -> Dict
```

**参数**:
- `user_input` (str): 自然语言招聘需求
- `search_batch_size` (int): 搜索批次大小，默认 50
- `screen_batch_size` (int): 筛选批次大小，默认 10
- `flash_threshold` (int): Flash 评分阈值 (0-100)，默认 50
- `pro_threshold` (int): Pro 评分阈值 (0-100)，默认 70
- `engine` (str): 搜索引擎，可选 "serper"/"gemini"/"tavily"，默认 "serper"
- `share_emails` (List[str]): 分享邮箱列表，可选

**返回值**:
```python
{
    'total_searched': int,      # 搜索总数
    'flash_passed': int,        # Flash 通过数
    'pro_passed': int,          # Pro 通过数
    'exported': int,            # 导出数量
    'url': str,                 # Google Sheets URL
    'json_file': str,           # JSON 文件路径
    'markdown_file': str,       # Markdown 文件路径
    'error': str                # 错误信息（如有）
}
```

**示例**:
```python
result = quick_streaming_pipeline(
    user_input="Base 上海的产品经理，5-8年经验",
    search_batch_size=50,
    flash_threshold=50,
    pro_threshold=70,
    engine="serper"
)

print(f"找到 {result['pro_passed']} 位候选人")
print(f"Google Sheets: {result['url']}")
```

---

## 搜索模块

### SerperSearch

基于 Google 搜索的 Serper API 搜索引擎。

**位置**: [`serper_search.py`](serper_search.py:1)

#### `__init__()`

```python
def __init__(self, api_key: str = None)
```

**参数**:
- `api_key` (str): Serper API Key，可选（默认从环境变量读取）

#### `search_linkedin_profiles()`

搜索 LinkedIn 个人资料。

```python
def search_linkedin_profiles(
    self,
    job_title: str,
    location: str = None,
    keywords: List[str] = None,
    max_results: int = 50,
    page: int = 1
) -> List[Dict]
```

**参数**:
- `job_title` (str): 职位名称
- `location` (str): 地点，可选
- `keywords` (List[str]): 关键词列表，可选
- `max_results` (int): 最大结果数，默认 50
- `page` (int): 页码，默认 1

**返回值**:
```python
[
    {
        'name': str,           # 姓名
        'url': str,            # LinkedIn URL
        'title': str,          # 职位
        'location': str,       # 地点
        'snippet': str         # 简介
    },
    ...
]
```

**示例**:
```python
from serper_search import SerperSearch

searcher = SerperSearch(api_key="your_api_key")
results = searcher.search_linkedin_profiles(
    job_title="Product Manager",
    location="上海",
    max_results=50
)

for candidate in results:
    print(f"{candidate['name']} - {candidate['title']}")
```

#### `search_with_pagination()`

分页搜索。

```python
def search_with_pagination(
    self,
    job_title: str,
    location: str = None,
    keywords: List[str] = None,
    total_results: int = 100
) -> List[Dict]
```

**参数**:
- `job_title` (str): 职位名称
- `location` (str): 地点，可选
- `keywords` (List[str]): 关键词列表，可选
- `total_results` (int): 总结果数，默认 100

**返回值**: 同 `search_linkedin_profiles()`

**示例**:
```python
# 搜索 100 个结果，自动分页
results = searcher.search_with_pagination(
    job_title="Data Scientist",
    location="北京",
    total_results=100
)
```

---

### GeminiSearch

基于 Google Grounding 的 Gemini 搜索引擎。

**位置**: [`gemini_search.py`](gemini_search.py:1)

#### `search_linkedin_profiles()`

```python
def search_linkedin_profiles(
    self,
    job_title: str,
    location: str = None,
    keywords: List[str] = None,
    max_results: int = 50
) -> List[Dict]
```

**参数**: 同 SerperSearch

**示例**:
```python
from gemini_search import GeminiSearch

searcher = GeminiSearch()
results = searcher.search_linkedin_profiles(
    job_title="Frontend Engineer",
    location="深圳",
    max_results=50
)
```

---

## 筛选模块

### DetailedScreening

Flash + Pro 两阶段筛选器。

**位置**: [`detailed_screening.py`](detailed_screening.py:1)

#### `__init__()`

```python
def __init__(self, api_key: str = None)
```

**参数**:
- `api_key` (str): LLM API Key，可选

#### `screen_candidates_two_stage()`

两阶段筛选候选人。

```python
def screen_candidates_two_stage(
    self,
    candidates: List[Dict],
    requirement: Dict,
    flash_threshold: int = 50,
    pro_batch_size: int = 10,
    pro_threshold: int = 70
) -> List[Dict]
```

**参数**:
- `candidates` (List[Dict]): 候选人列表
- `requirement` (Dict): 岗位要求（解析后的）
- `flash_threshold` (int): Flash 阈值，默认 50
- `pro_batch_size` (int): Pro 批次大小，默认 10
- `pro_threshold` (int): Pro 阈值，默认 70

**返回值**:
```python
[
    {
        'name': str,
        'url': str,
        'title': str,
        'location': str,
        'flash_score': int,        # Flash 分数
        'final_score': int,        # Pro 最终分数
        '职位匹配': Dict,
        '年限匹配': Dict,
        '地点匹配': Dict,
        '背景匹配': Dict,
        '推荐理由': List[str]
    },
    ...
]
```

**示例**:
```python
from detailed_screening import DetailedScreening

screener = DetailedScreening()

# 候选人列表
candidates = [
    {
        'name': '张三',
        'url': 'https://linkedin.com/in/zhangsan',
        'title': 'Senior Product Manager',
        'location': '上海',
        'snippet': '10年产品经验...'
    }
]

# 岗位要求
requirement = {
    'job_title': 'Product Manager',
    'location': '上海',
    'years_min': 5,
    'years_max': 10
}

# 筛选
results = screener.screen_candidates_two_stage(
    candidates=candidates,
    requirement=requirement,
    flash_threshold=50,
    pro_threshold=70
)

for candidate in results:
    print(f"{candidate['name']}: {candidate['final_score']}分")
```

---

## 导出模块

### GoogleSheetsExporterOAuth

使用 OAuth 认证的 Google Sheets 导出器。

**位置**: [`google_sheets_exporter_oauth.py`](google_sheets_exporter_oauth.py:1)

#### `__init__()`

```python
def __init__(
    self,
    credentials_file: str = "oauth_credentials.json",
    token_file: str = "token.pickle"
)
```

**参数**:
- `credentials_file` (str): OAuth 凭证文件路径
- `token_file` (str): Token 缓存文件路径

#### `export_candidates()`

导出候选人到 Google Sheets。

```python
def export_candidates(
    self,
    candidates: List[Dict],
    sheet_name: str = None,
    share_emails: List[str] = None
) -> Dict
```

**参数**:
- `candidates` (List[Dict]): 候选人列表
- `sheet_name` (str): 表格名称，可选（默认自动生成）
- `share_emails` (List[str]): 分享邮箱列表，可选

**返回值**:
```python
{
    'url': str,              # Google Sheets URL
    'sheet_id': str,         # 表格 ID
    'sheet_name': str,       # 表格名称
    'exported': int,         # 导出数量
    'shared_with': List[str] # 分享给的邮箱
}
```

**示例**:
```python
from google_sheets_exporter_oauth import GoogleSheetsExporterOAuth

exporter = GoogleSheetsExporterOAuth()

result = exporter.export_candidates(
    candidates=analyzed_candidates,
    sheet_name="产品经理候选人_20260225",
    share_emails=["hr@company.com"]
)

print(f"导出成功: {result['url']}")
```

---

### MarkdownExporter

Markdown 格式导出器。

**位置**: [`markdown_exporter.py`](markdown_exporter.py:1)

#### `export_candidates()`

```python
def export_candidates(
    self,
    candidates: List[Dict],
    filename: str = None,
    requirement: Dict = None
) -> str
```

**参数**:
- `candidates` (List[Dict]): 候选人列表
- `filename` (str): 文件名，可选
- `requirement` (Dict): 岗位要求，可选

**返回值**: 文件路径 (str)

**示例**:
```python
from markdown_exporter import MarkdownExporter

exporter = MarkdownExporter()

filepath = exporter.export_candidates(
    candidates=analyzed_candidates,
    filename="candidates_20260225.md"
)

print(f"Markdown 文件: {filepath}")
```

---

## 工具函数

### RequirementParser

需求解析器。

**位置**: [`requirement_parser.py`](requirement_parser.py:1)

#### `parse()`

解析自然语言招聘需求。

```python
def parse(self, user_input: str) -> Dict
```

**参数**:
- `user_input` (str): 自然语言需求

**返回值**:
```python
{
    'job_title': str,        # 职位名称
    'location': str,         # 地点
    'years_min': int,        # 最小年限
    'years_max': int,        # 最大年限
    'keywords': List[str],   # 关键词
    'background': List[str], # 背景要求
    'skills': List[str]      # 技能要求
}
```

**示例**:
```python
from requirement_parser import RequirementParser

parser = RequirementParser()
requirement = parser.parse("Base 上海的产品经理，5-8年经验，有大厂背景")

print(f"职位: {requirement['job_title']}")
print(f"地点: {requirement['location']}")
print(f"年限: {requirement['years_min']}-{requirement['years_max']}")
```

---

### JobExpander

岗位关键词扩展器。

**位置**: [`job_expander.py`](job_expander.py:1)

#### `expand()`

生成岗位名称变体。

```python
def expand(self, job_title: str, max_variants: int = 5) -> List[str]
```

**参数**:
- `job_title` (str): 原始职位名称
- `max_variants` (int): 最大变体数，默认 5

**返回值**: 职位名称变体列表 (List[str])

**示例**:
```python
from job_expander import JobExpander

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

## 配置

### config.py

系统配置文件。

**位置**: [`config.py`](config.py:1)

**配置项**:
```python
# Serper API
SERPER_API_KEY = "your_serper_api_key"

# 搜索配置
SEARCH_INTERVAL = 120        # 搜索间隔（秒）
BATCH_SIZE = 10              # 批次大小
MAX_SEARCH_RESULTS = 100     # 最大搜索结果数

# LinkedIn 搜索模板
LINKEDIN_SEARCH_TEMPLATE = 'site:linkedin.com/in/ "{job_title}" {keywords}'
```

---

### llm_config.py

LLM 配置文件。

**位置**: [`llm_config.py`](llm_config.py:1)

**配置项**:
```python
# API 配置
API_BASE = "https://api.example.com/v1"
DEFAULT_KEY = "your_llm_api_key"

# 模型配置
FLASH_MODEL = "[福利]gemini-3-flash-preview"
PRO_MODEL = "[福利]gemini-3-flash-preview"
```

---

## 错误处理

### 常见错误

#### SearchError
搜索失败时抛出。

```python
try:
    results = searcher.search_linkedin_profiles(...)
except SearchError as e:
    print(f"搜索错误: {e}")
```

#### ScreeningError
筛选失败时抛出。

```python
try:
    analyzed = screener.screen_candidates_two_stage(...)
except ScreeningError as e:
    print(f"筛选错误: {e}")
```

#### ExportError
导出失败时抛出。

```python
try:
    result = exporter.export_candidates(...)
except ExportError as e:
    print(f"导出错误: {e}")
```

---

## 类型定义

### Candidate

候选人数据结构。

```python
{
    'name': str,              # 姓名
    'url': str,               # LinkedIn URL
    'title': str,             # 当前职位
    'location': str,          # 当前地点
    'snippet': str,           # 简介
    'flash_score': int,       # Flash 分数 (0-100)
    'final_score': int,       # Pro 最终分数 (0-100)
    '职位匹配': {
        '当前': str,
        '要求': str,
        '匹配': str,          # "✅" 或 "❌"
        '说明': str
    },
    '年限匹配': {
        '实际': str,
        '要求': str,
        '匹配': str,
        '说明': str
    },
    '地点匹配': {
        '当前地点': str,
        '要求': str,
        '匹配': str,
        '说明': str
    },
    '背景匹配': {
        '咨询经验': str,
        '甲方经验': str,
        '匹配': str,
        '说明': str
    },
    '工作经历': List[Dict],
    '推荐理由': List[str]
}
```

### Requirement

岗位要求数据结构。

```python
{
    'job_title': str,         # 职位名称
    'location': str,          # 地点
    'years_min': int,         # 最小年限
    'years_max': int,         # 最大年限
    'keywords': List[str],    # 关键词
    'background': List[str],  # 背景要求
    'skills': List[str],      # 技能要求
    'education': str,         # 学历要求
    'company_type': List[str] # 公司类型
}
```

---

## 完整示例

### 端到端流程

```python
from streaming_pipeline import quick_streaming_pipeline

# 1. 定义需求
user_input = """
招聘岗位：高级产品经理
工作地点：上海
工作年限：5-8年
必备背景：有大厂经验
优先条件：有咨询背景
"""

# 2. 执行搜索和筛选
result = quick_streaming_pipeline(
    user_input=user_input,
    search_batch_size=50,
    screen_batch_size=10,
    flash_threshold=50,
    pro_threshold=70,
    engine="serper",
    share_emails=["hr@company.com"]
)

# 3. 处理结果
if result.get('error'):
    print(f"错误: {result['error']}")
else:
    print(f"搜索: {result['total_searched']} 位")
    print(f"Flash 通过: {result['flash_passed']} 位")
    print(f"Pro 通过: {result['pro_passed']} 位")
    print(f"Google Sheets: {result['url']}")
    print(f"JSON 文件: {result['json_file']}")
    print(f"Markdown 文件: {result['markdown_file']}")
```

---

## 性能指标

### 搜索性能
- Serper: ~2-3 秒/批次（10 个结果）
- Gemini: ~5-8 秒/批次
- Tavily: ~3-5 秒/批次

### 筛选性能
- Flash: ~1-2 秒/候选人
- Pro: ~2-3 秒/候选人

### 导出性能
- Google Sheets: ~5-10 秒（首次认证）
- JSON: <1 秒
- Markdown: <1 秒

---

## 版本信息

- **当前版本**: 2.0
- **最后更新**: 2026-02-25
- **Python 版本**: 3.8+
- **依赖**: 见 [`requirements.txt`](requirements.txt:1)
