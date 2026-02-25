# API 和模型使用说明

## 📋 系统使用的 API 和模型

### 1. Serper API（搜索引擎）

**用途**: LinkedIn 候选人搜索

**配置位置**: 
- [`serper_search.py`](serper_search.py:14)
- [`unified_searcher.py`](unified_searcher.py:1)
- [`linkedin_end_to_end.py`](linkedin_end_to_end.py:14)

**API Key**: 
```python
SERPER_API_KEY = "d88085d4543221682eecd92082f27247f71d902f"
```

**使用方式**:
```python
import requests

url = "https://google.serper.dev/search"
headers = {
    'X-API-KEY': 'your_serper_key',
    'Content-Type': 'application/json'
}
payload = {
    'q': 'site:linkedin.com/in/ "Product Manager" "Shanghai"',
    'num': 100  # 每次返回 100 条结果
}

response = requests.post(url, headers=headers, json=payload)
```

**成本**: $5 / 1000 次搜索

**输出示例**:
```json
{
  "organic": [
    {
      "title": "张三 - Product Manager | LinkedIn",
      "link": "https://linkedin.com/in/zhangsan",
      "snippet": "Product Manager at Alibaba with 5+ years experience..."
    }
  ]
}
```

**搜索输出位置**: 
- 内存中的候选人列表
- 可导出到: `search_results.md`, `search_results.json`

---

### 2. Gemini API（AI 分析）

**用途**: 
- 需求分析
- Flash 粗筛
- Pro 精筛

**配置位置**: [`llm_config.py`](llm_config.py:1)

```python
API_BASE = "https://api.gemai.cc/v1"
DEFAULT_KEY = "sk-5gdJnwOpb24drogckyzMQg4mId442uXTl0V8JNYcQdHm1FZH"
```

#### 2.1 Gemini Flash（粗筛）

**模型**: `[福利]gemini-3-flash-preview`

**用途**: 快速评分（0-100 分）

**使用位置**: [`detailed_screening.py`](detailed_screening.py:19)

**Prompt 示例**:
```python
prompt = f"""
候选人信息:
- 姓名: {candidate['name']}
- 职位: {candidate['title']}
- 简介: {candidate['snippet']}

岗位要求:
- 职位: Product Manager
- 地点: Shanghai
- 年限: 5年以上

请评估候选人与岗位的匹配度，返回 0-100 分。
只返回数字，不要解释。
"""
```

**输出示例**: `75`

**成本**: 包含在 LLM API 套餐中

#### 2.2 Gemini Pro（精筛）

**模型**: `[官逆]gemini-3-pro-preview`

**用途**: 深度分析，生成详细匹配报告

**使用位置**: [`detailed_screening.py`](detailed_screening.py:20)

**Prompt 示例**:
```python
prompt = f"""
候选人信息:
{candidate}

岗位要求:
{requirement}

请详细分析候选人匹配度，返回 JSON 格式:
{{
  "职位匹配": {{"匹配": "✅/❌", "说明": "..."}},
  "年限匹配": {{"匹配": "✅/❌", "说明": "..."}},
  "背景匹配": {{
    "匹配": "✅/❌",
    "咨询经验": "...",
    "甲方经验": "..."
  }},
  "地点匹配": {{"匹配": "✅/❌", "说明": "..."}},
  "推荐理由": ["理由1", "理由2", "理由3"],
  "final_score": 85
}}
"""
```

**输出示例**:
```json
{
  "职位匹配": {"匹配": "✅", "说明": "职位完全匹配"},
  "年限匹配": {"匹配": "✅", "说明": "5年以上经验"},
  "背景匹配": {
    "匹配": "✅",
    "咨询经验": "McKinsey 3年",
    "甲方经验": "Alibaba 5年"
  },
  "地点匹配": {"匹配": "✅", "说明": "Base 上海"},
  "推荐理由": [
    "职位完全匹配",
    "大厂背景（Alibaba）",
    "年限符合要求",
    "地点匹配"
  ],
  "final_score": 85
}
```

**成本**: 包含在 LLM API 套餐中

---

### 3. Google Sheets API（导出）

**用途**: 将筛选结果导出到 Google Sheets

**配置位置**: [`google_sheets_exporter.py`](google_sheets_exporter.py:1)

**凭证文件**: `google_credentials.json`

**使用方式**:
```python
from google_sheets_exporter import GoogleSheetsExporter

exporter = GoogleSheetsExporter("google_credentials.json")
exporter.connect()

url = exporter.export_candidates(
    candidates=analyzed_candidates,
    requirement_text="上海的产品经理，5年经验",
    job_title="Product Manager",
    share_emails=["client@example.com"]
)
```

**输出**: Google Sheets URL

**表格结构**:
| 排名 | 姓名 | 总分 | 职位匹配 | 年限匹配 | 背景匹配 | 地点匹配 | 当前职位 | 当前公司 | 工作年限 | 咨询背景 | 甲方背景 | LinkedIn链接 | 推荐理由 | 客户备注 |
|------|------|------|----------|----------|----------|----------|----------|----------|----------|----------|----------|--------------|----------|----------|

**成本**: 免费（Google Sheets API）

---

## 📊 数据流和输出位置

### 完整数据流

```
用户输入
    ↓
AI 需求分析 (Gemini Flash)
    ↓ 输出: requirement.json (内存)
    ↓
搜索 (Serper API)
    ↓ 输出: candidates_raw.json (内存)
    ↓ 可导出: search_results.md, search_results.json
    ↓
Flash 粗筛 (Gemini Flash)
    ↓ 输出: candidates_flash.json (内存)
    ↓ 添加字段: flash_score
    ↓
Pro 精筛 (Gemini Pro)
    ↓ 输出: candidates_analyzed.json (内存)
    ↓ 添加字段: final_score, 职位匹配, 年限匹配, 背景匹配, 地点匹配, 推荐理由
    ↓
导出 (Google Sheets API)
    ↓ 输出: Google Sheets URL
    ↓ 可选导出: results.md, results.json
```

### 输出文件位置

#### 1. 搜索结果

**位置**: 
- `linkedin_recruiter/search_results.md` (Markdown 格式)
- `linkedin_recruiter/search_results.json` (JSON 格式)

**生成方式**:
```python
from recruiter_pro import LinkedInRecruiterPro

recruiter = LinkedInRecruiterPro()
candidates = recruiter.search_end_to_end("上海的产品经理")

# 导出
recruiter.export_to_markdown(candidates, "search_results.md")
recruiter.export_to_json(candidates, "search_results.json")
```

#### 2. 筛选结果

**位置**:
- `linkedin_recruiter/filtered_results.md`
- `linkedin_recruiter/filtered_results.json`

**生成方式**:
```python
analyzed = recruiter.screen_candidates_two_stage(
    candidates=candidates,
    requirement=requirement
)

recruiter.export_to_markdown(analyzed, "filtered_results.md")
```

#### 3. Google Sheets

**位置**: 在线 Google Sheets

**访问方式**: 
- 系统返回的 URL
- 示例: `https://docs.google.com/spreadsheets/d/xxx`

**生成方式**:
```python
url = recruiter.export_to_google_sheets(
    candidates=analyzed,
    requirement_text="上海的产品经理，5年经验",
    job_title="Product Manager"
)

print(f"Google Sheets: {url}")
```

---

## 🔧 API 配置检查清单

### 1. Serper API

- [ ] API Key 已配置
- [ ] 测试搜索成功
- [ ] 返回结果正常

**测试命令**:
```bash
cd linkedin_recruiter
python -c "from serper_search import SerperSearcher; s = SerperSearcher(); print(len(s.search_linkedin('site:linkedin.com/in/ \"Product Manager\"', 10)))"
```

### 2. Gemini API

- [ ] API Key 已配置
- [ ] API Base URL 正确
- [ ] 模型名称正确

**测试命令**:
```bash
python -c "from requirement_parser import RequirementParser; p = RequirementParser(); print(p.parse_requirement('上海的产品经理'))"
```

### 3. Google Sheets API

- [ ] google_credentials.json 已配置
- [ ] 服务账号权限正确
- [ ] 可以创建表格

**测试命令**:
```bash
python test_google_sheets.py
```

---

## 💰 成本估算

### 单次完整流程成本

假设搜索 2000 位候选人，Flash 筛选通过 200 位，Pro 精筛通过 50 位：

| 项目 | 数量 | 单价 | 成本 |
|------|------|------|------|
| Serper 搜索 | 56 次 | $0.005 | $0.28 |
| Gemini Flash | 2000 次 | 包含在套餐 | $0 |
| Gemini Pro | 200 次 | 包含在套餐 | $0 |
| Google Sheets | 1 个表格 | 免费 | $0 |
| **总计** | - | - | **$0.28** |

### 月度成本估算

假设每天处理 5 个职位：

| 项目 | 每天 | 每月 (30天) | 成本 |
|------|------|-------------|------|
| Serper 搜索 | 5 × $0.28 | $42 | $42 |
| LLM API | 套餐 | 套餐 | 已包含 |
| **总计** | $1.40 | $42 | **$42** |

---

## 📝 使用建议

### 1. 搜索阶段

- **推荐引擎**: Serper（覆盖率最高）
- **备用引擎**: Gemini（智能搜索）
- **批次大小**: 50 人/批（流式处理）

### 2. 筛选阶段

- **Flash 阈值**: 50 分（粗筛）
- **Pro 阈值**: 70 分（精筛）
- **批次大小**: 10 人/批（Pro 分析）

### 3. 导出阶段

- **推荐格式**: Google Sheets（实时协作）
- **备用格式**: Markdown（易读）
- **存档格式**: JSON（完整数据）

---

## 🔗 相关文档

- [流程详解](PROCESS_FLOW.md)
- [系统架构](ARCHITECTURE.md)
- [Google Sheets 配置](GOOGLE_SHEETS_SETUP.md)
- [测试脚本](test_google_sheets.py)
