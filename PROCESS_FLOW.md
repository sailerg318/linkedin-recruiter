# LinkedIn 招聘系统 - 搜索筛选流程详解

## 完整流程图

```
用户输入需求
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤 1: AI 需求分析 (requirement_parser.py)                 │
│ ─────────────────────────────────────────────────────────   │
│ 输入: "我想找 Base 上海的产品经理，5年经验，有大厂背景"      │
│                                                              │
│ AI 提取:                                                     │
│ - base_keyword: "Product Manager"                           │
│ - location: "Shanghai"                                       │
│ - target_companies: ["Alibaba", "Tencent", "ByteDance"...] │
│ - experience_years: {"min": 5}                              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤 2: 微切片搜索 (unified_searcher.py)                    │
│ ─────────────────────────────────────────────────────────   │
│ 策略 1: 公司切片                                             │
│   Query 1: site:linkedin.com/in/ "Product Manager"          │
│            "Shanghai" "Alibaba" -intitle:jobs               │
│   → Serper API 返回 100 条结果                               │
│                                                              │
│   Query 2: ... "Tencent" ...                                │
│   → Serper API 返回 100 条结果                               │
│                                                              │
│   ... (30 家公司)                                            │
│                                                              │
│ 策略 2: 字母切片                                             │
│   Query 31: ... intitle:a ...                               │
│   Query 32: ... intitle:b ...                               │
│   ... (a-z, 26 个字母)                                       │
│                                                              │
│ 实时去重: 使用 set() 存储已见过的 URL                        │
│                                                              │
│ 输出: 500-2000 位候选人（去重后）                            │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤 3: Flash 粗筛 (detailed_screening.py)                  │
│ ─────────────────────────────────────────────────────────   │
│ 对每位候选人:                                                │
│   1. 提取 LinkedIn 信息 (title, snippet)                    │
│   2. 调用 Gemini Flash 模型快速评分                         │
│   3. Prompt: "评估候选人与岗位的匹配度，返回 0-100 分"       │
│   4. 阈值筛选: score >= 50 分通过                            │
│                                                              │
│ 示例:                                                        │
│   候选人 A: Flash 评分 75 → 通过                             │
│   候选人 B: Flash 评分 45 → 淘汰                             │
│   候选人 C: Flash 评分 82 → 通过                             │
│                                                              │
│ 输出: 100-300 位候选人（Flash 通过）                         │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤 4: Pro 精筛 (detailed_screening.py)                    │
│ ─────────────────────────────────────────────────────────   │
│ 分批处理 (每批 10 人):                                       │
│                                                              │
│ 批次 1 (10 人):                                              │
│   对每位候选人:                                              │
│     1. 调用 Gemini Pro 模型深度分析                          │
│     2. Prompt: "详细分析候选人匹配度，包括:                  │
│        - 职位匹配 (✅/❌)                                     │
│        - 年限匹配 (✅/❌)                                     │
│        - 背景匹配 (✅/❌)                                     │
│        - 地点匹配 (✅/❌)                                     │
│        - 推荐理由 (列表)                                     │
│        - 最终评分 (0-100)"                                   │
│     3. 阈值筛选: final_score >= 70 分通过                    │
│     4. 通过的候选人 → 立即写入 Google Sheets                 │
│                                                              │
│ 批次 2 (10 人):                                              │
│   ... 重复上述过程                                           │
│                                                              │
│ 输出: 20-50 位候选人（Pro 通过）                             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤 5: 实时写入 Google Sheets (google_sheets_exporter.py)  │
│ ─────────────────────────────────────────────────────────   │
│ 每通过一批 Pro 筛选:                                         │
│   1. 连接 Google Sheets API                                 │
│   2. 追加行到表格                                            │
│   3. 写入数据:                                               │
│      - 排名                                                  │
│      - 姓名                                                  │
│      - 总分 (Pro 评分)                                       │
│      - 职位匹配 (✅/❌)                                       │
│      - 年限匹配 (✅/❌)                                       │
│      - 背景匹配 (✅/❌)                                       │
│      - 地点匹配 (✅/❌)                                       │
│      - 当前职位                                              │
│      - 当前公司                                              │
│      - 工作年限                                              │
│      - LinkedIn 链接                                         │
│      - 推荐理由                                              │
│      - 客户备注栏 (空白)                                     │
│                                                              │
│ 输出: Google Sheets URL                                     │
└─────────────────────────────────────────────────────────────┘
```

## 详细代码流程

### 1. 搜索阶段

**文件**: `unified_searcher.py` + `linkedin_end_to_end.py`

```python
# 生成搜索查询
for company in target_companies:
    query = f'site:linkedin.com/in/ "{keyword}" "{location}" "{company}" -intitle:jobs'
    
    # 调用 Serper API
    response = requests.post(
        "https://google.serper.dev/search",
        headers={'X-API-KEY': SERPER_KEY},
        json={'q': query, 'num': 100}
    )
    
    # 解析结果
    candidates = parse_results(response.json())
    
    # 去重
    for candidate in candidates:
        if candidate['url'] not in seen_urls:
            seen_urls.add(candidate['url'])
            all_candidates.append(candidate)
```

### 2. Flash 粗筛阶段

**文件**: `detailed_screening.py`

```python
def _flash_score_single(candidate, requirement):
    # 构建 Prompt
    prompt = f"""
    候选人信息:
    - 姓名: {candidate['name']}
    - 职位: {candidate['title']}
    - 简介: {candidate['snippet']}
    
    岗位要求:
    - 职位: {requirement['job_title']}
    - 地点: {requirement['location']}
    - 年限: {requirement['experience_years']}
    
    请评估匹配度，返回 0-100 分。
    """
    
    # 调用 Gemini Flash
    response = call_llm(prompt, model="gemini-flash")
    
    # 提取分数
    score = extract_score(response)
    
    return score
```

### 3. Pro 精筛阶段

**文件**: `detailed_screening.py`

```python
def _pro_analyze_single(candidate, requirement):
    # 构建详细 Prompt
    prompt = f"""
    候选人信息:
    {candidate}
    
    岗位要求:
    {requirement}
    
    请详细分析匹配度，返回 JSON:
    {{
      "职位匹配": {{"匹配": "✅/❌", "说明": "..."}},
      "年限匹配": {{"匹配": "✅/❌", "说明": "..."}},
      "背景匹配": {{"匹配": "✅/❌", "咨询经验": "...", "甲方经验": "..."}},
      "地点匹配": {{"匹配": "✅/❌", "说明": "..."}},
      "推荐理由": ["理由1", "理由2", ...],
      "final_score": 85
    }}
    """
    
    # 调用 Gemini Pro
    response = call_llm(prompt, model="gemini-pro")
    
    # 解析 JSON
    analysis = json.loads(response)
    
    return analysis
```

### 4. 实时写入 Google Sheets

**文件**: `streaming_pipeline.py`

```python
def _append_to_sheet(candidates):
    for candidate in candidates:
        # 构建行数据
        row_data = [
            candidate['name'],
            candidate['final_score'],
            candidate['职位匹配']['匹配'],
            candidate['年限匹配']['匹配'],
            # ... 其他字段
        ]
        
        # 写入 Google Sheets
        worksheet.update(f'A{current_row}:O{current_row}', [row_data])
        current_row += 1
```

## 流式处理的优势

### 传统批量处理

```
搜索 2000 人 (5 分钟)
    ↓
Flash 筛选 2000 人 (10 分钟)
    ↓
Pro 筛选 200 人 (20 分钟)
    ↓
写入 Google Sheets (1 分钟)
    ↓
总耗时: 36 分钟
```

### 流式处理

```
搜索批次 1 (50 人, 15 秒)
    ↓
Flash 筛选 (30 秒) → 通过 20 人
    ↓
Pro 筛选 (2 分钟) → 通过 8 人
    ↓
写入 Google Sheets (5 秒) ← 立即可见结果！
    ↓
搜索批次 2 (50 人, 15 秒)
    ↓
... 并行处理

总耗时: 约 15-20 分钟
优势: 提前看到结果，可随时中断
```

## 数据流示例

### 输入
```
"我想找 Base 上海的产品经理，5年经验，有大厂背景"
```

### AI 分析输出
```json
{
  "base_keyword": "Product Manager",
  "location": "Shanghai",
  "target_companies": [
    "Alibaba", "Tencent", "ByteDance", "Meituan", 
    "Pinduoduo", "JD.com", "Baidu", ...
  ],
  "experience_years": {"min": 5}
}
```

### 搜索输出（部分）
```json
[
  {
    "name": "张三",
    "title": "Senior Product Manager",
    "company": "Alibaba",
    "url": "https://linkedin.com/in/zhangsan",
    "snippet": "5+ years experience in product management..."
  },
  {
    "name": "李四",
    "title": "Product Manager",
    "company": "Tencent",
    "url": "https://linkedin.com/in/lisi",
    "snippet": "Product manager with 7 years experience..."
  }
]
```

### Flash 筛选输出
```json
[
  {
    "name": "张三",
    "flash_score": 75,
    "title": "Senior Product Manager",
    ...
  },
  {
    "name": "李四",
    "flash_score": 82,
    "title": "Product Manager",
    ...
  }
]
```

### Pro 筛选输出
```json
[
  {
    "name": "张三",
    "flash_score": 75,
    "final_score": 85,
    "职位匹配": {"匹配": "✅", "说明": "职位完全匹配"},
    "年限匹配": {"匹配": "✅", "说明": "5年以上经验"},
    "背景匹配": {"匹配": "✅", "咨询经验": "", "甲方经验": "Alibaba 5年"},
    "地点匹配": {"匹配": "✅", "说明": "Base 上海"},
    "推荐理由": [
      "职位完全匹配",
      "大厂背景（Alibaba）",
      "年限符合要求",
      "地点匹配"
    ]
  }
]
```

### Google Sheets 输出

| 排名 | 姓名 | 总分 | 职位匹配 | 年限匹配 | 背景匹配 | 地点匹配 | 当前职位 | 当前公司 | LinkedIn | 推荐理由 |
|------|------|------|----------|----------|----------|----------|----------|----------|----------|----------|
| 1 | 张三 | 85 | ✅ | ✅ | ✅ | ✅ | Senior PM | Alibaba | [链接] | • 职位完全匹配<br>• 大厂背景 |
| 2 | 李四 | 88 | ✅ | ✅ | ✅ | ✅ | PM | Tencent | [链接] | • 职位匹配<br>• 腾讯背景 |

## 总结

整个流程是完全自动化的：
1. **搜索**: 使用 Serper API 批量搜索 LinkedIn
2. **粗筛**: 使用 Gemini Flash 快速评分
3. **精筛**: 使用 Gemini Pro 深度分析
4. **导出**: 实时写入 Google Sheets

你只需要：
1. 配置 Google Sheets API 凭证
2. 运行 `python start.py`
3. 输入需求
4. 等待结果自动写入 Google Sheets
