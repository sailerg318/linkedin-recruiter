# LinkedIn 智能招聘系统

## 📖 项目简介

这是一个基于 AI 的 LinkedIn 候选人智能搜索和筛选系统，能够自动化完成从需求解析、候选人搜索、智能筛选到结果导出的完整招聘流程。

## ✨ 核心特性

### 1. 智能需求解析
- 自然语言输入招聘需求
- AI 自动提取职位、地点、年限、背景等关键信息
- 生成结构化的搜索策略

### 2. 多引擎搜索
- **Serper**（推荐）：基于 Google 搜索，支持分页和切片策略
- **Gemini**：使用 Google Grounding 技术
- **Tavily**：专业搜索 API

### 3. 岗位关键词扩展
- AI 自动生成岗位名称变体
- 扩大搜索覆盖范围
- 支持中英文岗位名称

### 4. 两阶段智能筛选

#### Flash 快速筛选（第一阶段）
- 使用 Gemini Flash 模型
- 快速评分 0-100 分
- 默认阈值：50 分
- 批量处理，高效快速

#### Pro 深度分析（第二阶段）
- 对 Flash 通过的候选人进行深度分析
- 评估 4 个硬性匹配维度：
  - ✅ **职位匹配**：当前职位 vs 要求职位
  - ✅ **年限匹配**：实际年限 vs 要求范围
  - ✅ **地点匹配**：当前所在地（严格匹配）
  - ✅ **背景匹配**：咨询经验、甲方经验
- 输出详细分析报告和推荐理由
- 默认阈值：70 分

### 5. 流式处理架构
- 边搜索边筛选边导出
- 内存占用低
- 实时反馈进度
- 支持大规模候选人处理

### 6. 多格式导出
- **Google Sheets**：OAuth 认证，使用您的 Google Drive（2TB）
- **JSON**：结构化数据，便于二次处理
- **Markdown**：可读性强的报告格式

### 7. 严格地点匹配
- 只匹配候选人当前所在地
- 不考虑历史工作地点
- 避免误匹配

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/Desktop/linkedin_recruiter
pip3 install -r requirements.txt
```

### 2. 配置 API Key

创建 `.env` 文件或直接修改 [`config.py`](config.py:1)：

```python
# Serper API（推荐）
SERPER_API_KEY = "your_serper_api_key"

# LLM API（用于 AI 分析）
LLM_API_KEY = "your_llm_api_key"
```

### 3. 配置 OAuth（首次使用）

详细步骤见 [`OAUTH_SETUP.md`](OAUTH_SETUP.md:1)

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 启用 Google Sheets API 和 Drive API
3. 创建 OAuth 客户端凭证（桌面应用）
4. 下载凭证文件并重命名为 `oauth_credentials.json`
5. 放到项目目录下

### 4. 运行系统

```bash
python3 quick_run.py
```

首次运行会打开浏览器进行 OAuth 认证，授权后即可使用。

## 📊 使用示例

### 示例 1：基础搜索

```python
from streaming_pipeline import quick_streaming_pipeline

# 输入招聘需求
result = quick_streaming_pipeline(
    user_input="我想找 Base 上海的产品经理，5-8年经验，有大厂背景",
    search_batch_size=50,      # 搜索批次
    screen_batch_size=10,      # 筛选批次
    flash_threshold=50,        # Flash 阈值
    pro_threshold=70,          # Pro 阈值
    engine="serper"            # 搜索引擎
)

# 查看结果
print(f"搜索: {result['total_searched']} 位")
print(f"Flash 通过: {result['flash_passed']} 位")
print(f"Pro 通过: {result['pro_passed']} 位")
print(f"Google Sheets: {result['url']}")
```

### 示例 2：自定义需求

```python
# 复杂需求
result = quick_streaming_pipeline(
    user_input="""
    招聘要求：
    - 职位：高级数据科学家
    - 地点：北京或上海
    - 年限：8-12年
    - 背景：必须有 BAT 或 TMD 经验
    - 技能：Python、机器学习、深度学习
    - 学历：硕士及以上
    """,
    search_batch_size=100,
    flash_threshold=60,
    pro_threshold=75,
    engine="serper"
)
```

### 示例 3：分享给团队

```python
# 导出并分享给团队成员
result = quick_streaming_pipeline(
    user_input="Base 深圳的前端工程师，3-5年 React 经验",
    share_emails=["hr@company.com", "manager@company.com"]
)
```

## 🏗️ 系统架构

```
用户输入
    ↓
需求解析 (requirement_parser.py)
    ↓
岗位扩展 (job_expander.py)
    ↓
多引擎搜索 (serper_search.py / gemini_search.py / tavily_search.py)
    ↓
Flash 快速筛选 (detailed_screening.py)
    ↓
Pro 深度分析 (detailed_screening.py)
    ↓
结果导出 (google_sheets_exporter_oauth.py / markdown_exporter.py)
```

## 📁 核心文件说明

### 主程序
- [`quick_run.py`](quick_run.py:1) - 快速运行脚本（推荐）
- [`streaming_pipeline.py`](streaming_pipeline.py:1) - 流式处理管道
- [`main.py`](main.py:1) - 主程序入口

### 搜索模块
- [`serper_search.py`](serper_search.py:1) - Serper 搜索引擎（推荐）
- [`gemini_search.py`](gemini_search.py:1) - Gemini 搜索引擎
- [`tavily_search.py`](tavily_search.py:1) - Tavily 搜索引擎
- [`unified_searcher.py`](unified_searcher.py:1) - 统一搜索接口

### 分析模块
- [`requirement_parser.py`](requirement_parser.py:1) - 需求解析器
- [`job_expander.py`](job_expander.py:1) - 岗位关键词扩展
- [`detailed_screening.py`](detailed_screening.py:1) - Flash + Pro 筛选
- [`candidate_filter.py`](candidate_filter.py:1) - 候选人过滤器

### 导出模块
- [`google_sheets_exporter_oauth.py`](google_sheets_exporter_oauth.py:1) - Google Sheets 导出（OAuth）
- [`markdown_exporter.py`](markdown_exporter.py:1) - Markdown 导出

### 配置文件
- [`config.py`](config.py:1) - 系统配置
- [`llm_config.py`](llm_config.py:1) - LLM 配置
- [`.env.example`](.env.example:1) - 环境变量示例

### 文档
- [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md:1) - 完整使用指南
- [`OAUTH_SETUP.md`](OAUTH_SETUP.md:1) - OAuth 设置指南
- [`OAUTH_QUICKSTART.md`](OAUTH_QUICKSTART.md:1) - OAuth 快速开始
- [`ARCHITECTURE.md`](ARCHITECTURE.md:1) - 系统架构文档

## 🎯 Pro 分析标准详解

### 评分维度

#### 1. 职位匹配（25%）
```json
{
  "职位匹配": {
    "当前": "Senior Product Manager",
    "要求": "Product Manager",
    "匹配": "✅",
    "说明": "职位完全匹配，级别更高"
  }
}
```

#### 2. 年限匹配（25%）
```json
{
  "年限匹配": {
    "实际": "7年",
    "要求": "5-10年",
    "匹配": "✅",
    "说明": "年限在要求范围内"
  }
}
```

#### 3. 地点匹配（25%）- 严格匹配
```json
{
  "地点匹配": {
    "当前地点": "上海",
    "要求": "上海",
    "匹配": "✅",
    "说明": "必须是当前所在地，不看历史地点"
  }
}
```

**重要规则**：
- ✅ 要求上海，候选人当前在上海 → 匹配
- ❌ 要求上海，候选人曾在上海但现在北京 → 不匹配
- ❌ 要求上海，候选人在北京但愿意relocate → 不匹配

#### 4. 背景匹配（25%）
```json
{
  "背景匹配": {
    "咨询经验": "McKinsey 3年 (2018-2021)",
    "甲方经验": "Google 5年 (2021-现在)",
    "匹配": "✅",
    "说明": "有咨询和大厂背景"
  }
}
```

### 评分逻辑

```python
final_score = (
    职位匹配分数 * 0.25 +
    年限匹配分数 * 0.25 +
    地点匹配分数 * 0.25 +
    背景匹配分数 * 0.25
)

# 通过标准
if final_score >= pro_threshold:  # 默认 70 分
    status = "通过"
else:
    status = "不通过"
```

### 输出格式

```json
{
  "final_score": 85,
  "职位匹配": {...},
  "年限匹配": {...},
  "地点匹配": {...},
  "背景匹配": {...},
  "工作经历": [
    {
      "公司": "Google",
      "职位": "Senior PM",
      "时间": "2020-现在",
      "类型": "甲方"
    }
  ],
  "推荐理由": [
    "职位完全匹配",
    "工作年限符合要求",
    "当前在目标城市",
    "有大厂和咨询背景"
  ]
}
```

## ⚙️ 配置参数

### 搜索配置
```python
search_batch_size = 50      # 每批搜索数量
engine = "serper"           # 搜索引擎：serper/gemini/tavily
```

### 筛选配置
```python
screen_batch_size = 10      # 每批筛选数量
flash_threshold = 50        # Flash 阈值（0-100）
pro_threshold = 70          # Pro 阈值（0-100）
```

### 导出配置
```python
share_emails = [            # 分享给团队成员
    "hr@company.com",
    "manager@company.com"
]
```

## 🔧 常见问题

### Q1: Pro 分析为什么没有通过？

**可能原因**：
1. **地点不匹配**：候选人当前不在目标城市（最常见）
2. **年限不符**：工作年限不在要求范围内
3. **职位不匹配**：当前职位与要求职位差异较大
4. **背景不符**：缺少要求的咨询或甲方经验

**诊断方法**：
```bash
python3 test_pro_analysis.py
```

查看详细的 Pro 分析结果，包括每个维度的匹配情况。

### Q2: 如何调整筛选标准？

修改阈值参数：
```python
# 更宽松的筛选
flash_threshold = 40
pro_threshold = 60

# 更严格的筛选
flash_threshold = 60
pro_threshold = 80
```

### Q3: 搜索结果太少怎么办？

1. **增加搜索批次**：`search_batch_size = 100`
2. **降低 Flash 阈值**：`flash_threshold = 40`
3. **使用岗位扩展**：系统会自动生成更多关键词变体
4. **尝试不同搜索引擎**：Serper/Gemini/Tavily

### Q4: OAuth 认证失败？

详见 [`OAUTH_SETUP.md`](OAUTH_SETUP.md:1)，确保：
1. 已启用 Google Sheets API 和 Drive API
2. OAuth 凭证文件正确放置
3. 授权范围包含 Sheets 和 Drive

### Q5: 如何查看候选人详细信息？

查看导出的文件：
- **Google Sheets**：在线查看和编辑
- **JSON 文件**：`candidates_review/candidates_YYYYMMDD_HHMMSS.json`
- **Markdown 文件**：`candidates_review/candidates_YYYYMMDD_HHMMSS.md`

## 📈 性能优化

### 1. 搜索优化
- 使用 Serper 引擎（最快）
- 合理设置 `search_batch_size`（推荐 50-100）
- 启用岗位关键词扩展

### 2. 筛选优化
- Flash 阈值不要太低（推荐 ≥ 50）
- Pro 批次大小适中（推荐 10-20）
- 使用流式处理避免内存溢出

### 3. 导出优化
- 使用 OAuth 认证（比服务账号更稳定）
- 批量导出而非逐条导出
- 启用自动去重

## 🛠️ 技术栈

- **Python 3.8+**
- **Google Gemini API** - AI 分析
- **Serper API** - Google 搜索
- **Google Sheets API** - 数据导出
- **OAuth 2.0** - 身份认证

## 📝 更新日志

### v2.0 (2026-02-25)
- ✅ 完整的 OAuth 认证流程
- ✅ Serper 分页搜索
- ✅ 岗位关键词扩展
- ✅ 严格地点匹配
- ✅ Flash + Pro 两阶段筛选
- ✅ 流式处理架构
- ✅ 自动去重
- ✅ 多格式导出

### v1.0 (2026-01-15)
- ✅ 基础搜索功能
- ✅ 简单筛选逻辑
- ✅ JSON 导出

## 📞 支持

如有问题，请查看：
- [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md:1) - 完整使用指南
- [`OAUTH_SETUP.md`](OAUTH_SETUP.md:1) - OAuth 设置
- [`ARCHITECTURE.md`](ARCHITECTURE.md:1) - 系统架构

## 📄 许可证

MIT License
